"""
scripts/reconcile_full_benchmark.py
Rigorous Master Reconciliation of the 6-Model Benchmark Suite:
Evaluates ALL 6 models across the EXACT SAME 3,293 test observations for BOTH horizons:
- 30-minute ahead forecasting (y30)
- 60-minute ahead forecasting (y60)

Outputs exported directly from execution variables:
- results/benchmark_30min_y30.csv
- results/benchmark_60min_y60.csv
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import glob
import copy
import warnings
import multiprocessing
import numpy as np
import pandas as pd
import torch
import xgboost as xgb
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from src.models import AttentionLSTM, StandardLSTM, compute_metrics
from src.federated_trainer import FederatedClient

device = "cpu"


def eval_arima_series(series):
    """Forecast 30 and 60 minutes ahead, with persistence fallback on warning/non-convergence."""
    last_value = float(series[-1])
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = ARIMA(series, order=(2, 1, 1)).fit()

        converged = getattr(result, "mle_retvals", {}).get("converged", True)
        convergence_warning = any(
            issubclass(w.category, ConvergenceWarning) for w in caught
        )
        if not converged or convergence_warning:
            return last_value, last_value

        forecast = np.asarray(result.forecast(steps=2), dtype=float)
        if not np.isfinite(forecast).all():
            return last_value, last_value

        return (
            float(np.clip(forecast[0], 0.0, 1.0)),
            float(np.clip(forecast[1], 0.0, 1.0)),
        )
    except Exception:
        return last_value, last_value


def main():
    print("=" * 80)
    print("EXECUTING RIGOROUS FULL-TEST RECONCILIATION BENCHMARK (N=3,293)")
    print("=" * 80)

    os.makedirs("results", exist_ok=True)
    client_files = sorted(glob.glob("data/processed/client_*.npz"))
    global_data = np.load("data/processed/global_dataset.npz")
    num_total_test = len(global_data["X_test"])

    print(f"Loaded {len(client_files)} clients. Total test instances: {num_total_test}")

    # =========================================================================
    # STEP 1: PARALLEL ARIMA ON FULL TEST SET (3,293 SAMPLES)
    # =========================================================================
    print(f"\n[1/6] Running parallel ARIMA(2,1,1) across all {num_total_test} test samples...")
    t0 = time.time()
    series_list = [global_data["X_test"][i, :, 0] for i in range(num_total_test)]
    with multiprocessing.Pool(processes=8) as pool:
        arima_results = pool.map(eval_arima_series, series_list)
    arima_p30_all = np.array([r[0] for r in arima_results], dtype=np.float32)
    arima_p60_all = np.array([r[1] for r in arima_results], dtype=np.float32)
    print(f"  -> Completed full ARIMA evaluation in {time.time() - t0:.1f} seconds.")

    # =========================================================================
    # STEP 2: LOAD & TRAIN XGBOOST BASELINES
    # =========================================================================
    print("\n[2/6] Fitting centralized XGBoost regressors (30m & 60m)...")
    X_tr_flat = global_data["X_train"].reshape(len(global_data["X_train"]), -1)
    X_val_flat = global_data["X_val"].reshape(len(global_data["X_val"]), -1)

    xgb_30 = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.05,
                               subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1)
    xgb_30.fit(X_tr_flat, global_data["y30_train"], eval_set=[(X_val_flat, global_data["y30_val"])], verbose=False)

    xgb_60 = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.05,
                               subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1)
    xgb_60.fit(X_tr_flat, global_data["y60_train"], eval_set=[(X_val_flat, global_data["y60_val"])], verbose=False)

    # =========================================================================
    # STEP 3: LOAD CENTRALIZED & FEDERATED DEEP LEARNING MODELS
    # =========================================================================
    print("\n[3/6] Loading PyTorch neural network checkpoints...")
    cent_lstm_30 = StandardLSTM(4, 64, 2)
    cent_lstm_30.load_state_dict(torch.load("models/centralized_lstm_30.pt", map_location=device))
    cent_lstm_30.eval()

    cent_lstm_60 = StandardLSTM(4, 64, 2)
    cent_lstm_60.load_state_dict(torch.load("models/centralized_lstm_60.pt", map_location=device))
    cent_lstm_60.eval()

    cent_att_30 = AttentionLSTM(4, 64, 2)
    cent_att_30.load_state_dict(torch.load("models/centralized_att_lstm_30.pt", map_location=device))
    cent_att_30.eval()

    cent_att_60 = AttentionLSTM(4, 64, 2)
    cent_att_60.load_state_dict(torch.load("models/centralized_att_lstm_60.pt", map_location=device))
    cent_att_60.eval()

    fed_state_30 = torch.load("models/fedavg_att_lstm_30min.pt", map_location=device)
    fed_att_30 = AttentionLSTM(4, 64, 2)
    fed_att_30.load_state_dict(fed_state_30)
    fed_att_30.eval()

    fed_state_60 = torch.load("models/fedavg_att_lstm_60min.pt", map_location=device)
    fed_att_60 = AttentionLSTM(4, 64, 2)
    fed_att_60.load_state_dict(fed_state_60)
    fed_att_60.eval()

    # =========================================================================
    # STEP 4: PER-CLIENT EVALUATION LOOP ACROSS ALL 30 CLIENTS
    # =========================================================================
    print("\n[4/6] Evaluating all models client-by-client on identical test slices...")
    model_names = [
        "ARIMA(2, 1, 1)",
        "XGBoost",
        "Centralized Standard LSTM",
        "Centralized Attention-LSTM",
        "Global FedAvg (R=8)",
        "Personalized FedAvg (Ours)"
    ]

    # Dictionaries to accumulate metrics per horizon
    horizons = {
        "30min": {
            "target": "y30",
            "records": {m: {"all_y": [], "all_p": [], "lot_maes": [], "lot_spaces": []} for m in model_names}
        },
        "60min": {
            "target": "y60",
            "records": {m: {"all_y": [], "all_p": [], "lot_maes": [], "lot_spaces": []} for m in model_names}
        }
    }

    test_slice_start = 0

    for idx, f in enumerate(client_files):
        cid = os.path.basename(f).replace(".npz", "")
        c_data = np.load(f)
        c_len = len(c_data["X_test"])
        cap = int(c_data["capacity"])
        X_test = c_data["X_test"]
        X_test_tensor = torch.tensor(X_test)
        X_test_flat = X_test.reshape(c_len, -1)

        y30_test = c_data["y30_test"]
        y60_test = c_data["y60_test"]

        # 1. ARIMA slice
        arima_30 = arima_p30_all[test_slice_start : test_slice_start + c_len]
        arima_60 = arima_p60_all[test_slice_start : test_slice_start + c_len]

        # 2. XGBoost
        xgb_p30 = np.clip(xgb_30.predict(X_test_flat), 0.0, 1.0)
        xgb_p60 = np.clip(xgb_60.predict(X_test_flat), 0.0, 1.0)

        # 3. Centralized Standard LSTM
        with torch.no_grad():
            clstm_p30 = np.clip(cent_lstm_30(X_test_tensor).numpy(), 0.0, 1.0)
            clstm_p60 = np.clip(cent_lstm_60(X_test_tensor).numpy(), 0.0, 1.0)

        # 4. Centralized Attention-LSTM
        with torch.no_grad():
            catt_p30 = np.clip(cent_att_30(X_test_tensor).numpy(), 0.0, 1.0)
            catt_p60 = np.clip(cent_att_60(X_test_tensor).numpy(), 0.0, 1.0)

        # 5. Global FedAvg
        with torch.no_grad():
            fed_p30 = np.clip(fed_att_30(X_test_tensor).numpy(), 0.0, 1.0)
            fed_p60 = np.clip(fed_att_60(X_test_tensor).numpy(), 0.0, 1.0)

        # 6. Personalized FedAvg
        # 30m: load pre-saved client checkpoint
        pers_30 = AttentionLSTM(4, 64, 2)
        pers_30.load_state_dict(torch.load(f"models/personalized/{cid}_personalized.pt", map_location=device))
        pers_30.eval()
        with torch.no_grad():
            pers_p30 = np.clip(pers_30(X_test_tensor).numpy(), 0.0, 1.0)

        # 60m: client fine-tunes locally from fed_state_60 on y60_train
        client_60 = FederatedClient(cid, f, target_key="y60")
        pers_60_model = client_60.fine_tune_personalized(fed_state_60, epochs=3, lr=0.0003)
        with torch.no_grad():
            pers_p60 = np.clip(pers_60_model(X_test_tensor).numpy(), 0.0, 1.0)

        # Pack predictions for this client
        preds_map = {
            "30min": {
                "y": y30_test,
                "ARIMA(2, 1, 1)": arima_30,
                "XGBoost": xgb_p30,
                "Centralized Standard LSTM": clstm_p30,
                "Centralized Attention-LSTM": catt_p30,
                "Global FedAvg (R=8)": fed_p30,
                "Personalized FedAvg (Ours)": pers_p30,
            },
            "60min": {
                "y": y60_test,
                "ARIMA(2, 1, 1)": arima_60,
                "XGBoost": xgb_p60,
                "Centralized Standard LSTM": clstm_p60,
                "Centralized Attention-LSTM": catt_p60,
                "Global FedAvg (R=8)": fed_p60,
                "Personalized FedAvg (Ours)": pers_p60,
            }
        }

        for hkey in ["30min", "60min"]:
            y_curr = preds_map[hkey]["y"]
            for m in model_names:
                p_curr = preds_map[hkey][m]
                m_dict = compute_metrics(y_curr, p_curr, capacity=cap)
                horizons[hkey]["records"][m]["all_y"].extend(y_curr)
                horizons[hkey]["records"][m]["all_p"].extend(p_curr)
                horizons[hkey]["records"][m]["lot_maes"].append(m_dict["MAE"])
                horizons[hkey]["records"][m]["lot_spaces"].append(m_dict.get("MAE_spaces", 0.0))

        test_slice_start += c_len

    # =========================================================================
    # STEP 5: CALCULATE AND EXPORT BENCHMARK TABLES DIRECTLY FROM VARIABLES
    # =========================================================================
    print("\n[5/6] Compiling and exporting verified benchmark tables...")

    table_exports = {}
    for hkey, out_csv in [("30min", "results/benchmark_30min_y30.csv"),
                          ("60min", "results/benchmark_60min_y60.csv")]:
        rows = []
        for m in model_names:
            all_y_arr = np.array(horizons[hkey]["records"][m]["all_y"])
            all_p_arr = np.array(horizons[hkey]["records"][m]["all_p"])
            lot_maes = horizons[hkey]["records"][m]["lot_maes"]
            lot_spaces = horizons[hkey]["records"][m]["lot_spaces"]

            # Compute Pooled Metrics across all 3,293 instances
            pooled_m = compute_metrics(all_y_arr, all_p_arr)

            rows.append({
                "Model": m,
                "Pooled MAE (Micro, Ratio)": pooled_m["MAE"],
                "Pooled RMSE (Ratio)": pooled_m["RMSE"],
                "Macro Mean MAE (Ratio)": round(float(np.mean(lot_maes)), 4),
                "Between-Lot Std (sigma)": round(float(np.std(lot_maes)), 4),
                "Mean Space Error (bays)": round(float(np.mean(lot_spaces)), 1)
            })

        df_out = pd.DataFrame(rows)
        df_out.to_csv(out_csv, index=False)
        table_exports[hkey] = df_out
        print(f"\n==================== {hkey.upper()} HORIZON BENCHMARK (N={len(all_y_arr)}) ====================")
        print(df_out.to_string(index=False))
        print(f"Saved directly to: {out_csv}")

    # Also update reconciled_benchmark_table.csv (for Fig 1 backwards-compatibility)
    table_exports["30min"].rename(columns={
        "Pooled MAE (Micro, Ratio)": "Pooled MAE (Micro)",
        "Pooled RMSE (Ratio)": "Pooled RMSE",
        "Macro Mean MAE (Ratio)": "Per-Lot Mean MAE (Macro)",
        "Between-Lot Std (sigma)": "Between-Lot Std (sigma)"
    }).to_csv("results/reconciled_benchmark_table.csv", index=False)

    print("\n[6/6] All tables successfully generated and exported directly from code execution!")


if __name__ == "__main__":
    main()
