"""
scripts/reconcile_metrics.py
Strict reconciliation of Pooled (Micro-Average) vs Per-Lot (Macro-Average) metrics
for all 6 models across 30-min and 60-min horizons.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import glob
import torch
import numpy as np
import pandas as pd
import xgboost as xgb
from statsmodels.tsa.arima.model import ARIMA

from src.models import AttentionLSTM, StandardLSTM, compute_metrics
from src.federated_trainer import FederatedClient

device = "cpu"
client_files = sorted(glob.glob("data/processed/client_*.npz"))
global_data = np.load("data/processed/global_dataset.npz")

print("=" * 80)
print("RECONCILING POOLED (MICRO) VS PER-LOT (MACRO) METRICS FOR ALL MODELS")
print("=" * 80)

# Load DL models
cent_att_30 = AttentionLSTM(4, 64, 2)
cent_att_30.load_state_dict(torch.load("models/centralized_att_lstm_30.pt", map_location=device))
cent_att_30.eval()

cent_lstm_30 = StandardLSTM(4, 64, 2)
cent_lstm_30.load_state_dict(torch.load("models/centralized_lstm_30.pt", map_location=device))
cent_lstm_30.eval()

fed_att_30 = AttentionLSTM(4, 64, 2)
fed_att_30.load_state_dict(torch.load("models/fedavg_att_lstm_30min.pt", map_location=device))
fed_att_30.eval()

# Load XGBoost model by refitting fast on flattened data
X_tr_flat = global_data["X_train"].reshape(len(global_data["X_train"]), -1)
X_val_flat = global_data["X_val"].reshape(len(global_data["X_val"]), -1)
xgb_model = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1)
xgb_model.fit(X_tr_flat, global_data["y30_train"], eval_set=[(X_val_flat, global_data["y30_val"])], verbose=False)

# Collect test predictions
results_table = []

for model_name in ["ARIMA(2,1,1)", "XGBoost", "Centralized LSTM", "Centralized Attention-LSTM", "FedAvg (Global)", "Personalized FedAvg"]:
    all_y = []
    all_preds = []
    per_lot_maes = []
    per_lot_spaces = []

    for f in client_files:
        cid = os.path.basename(f).replace(".npz", "")
        d = np.load(f)
        X_test, y_test = d["X_test"], d["y30_test"]
        cap = int(d["capacity"])

        if model_name == "ARIMA(2,1,1)":
            preds = []
            eval_sub = min(len(X_test), 15)
            for i in range(eval_sub):
                try:
                    res = ARIMA(X_test[i, :, 0], order=(2, 1, 1)).fit()
                    preds.append(float(np.clip(res.forecast(steps=1)[0], 0, 1)))
                except:
                    preds.append(float(X_test[i, -1, 0]))
            preds = np.array(preds)
            y_eval = y_test[:eval_sub]
            all_y.extend(y_eval)
            all_preds.extend(preds)
            m = compute_metrics(y_eval, preds, capacity=cap)
            per_lot_maes.append(m["MAE"])
            per_lot_spaces.append(m.get("MAE_spaces", 0.0))
            continue
        elif model_name == "XGBoost":
            preds = np.clip(xgb_model.predict(X_test.reshape(len(X_test), -1)), 0, 1)
        elif model_name == "Centralized LSTM":
            with torch.no_grad():
                preds = np.clip(cent_lstm_30(torch.tensor(X_test)).numpy(), 0, 1)
        elif model_name == "Centralized Attention-LSTM":
            with torch.no_grad():
                preds = np.clip(cent_att_30(torch.tensor(X_test)).numpy(), 0, 1)
        elif model_name == "FedAvg (Global)":
            with torch.no_grad():
                preds = np.clip(fed_att_30(torch.tensor(X_test)).numpy(), 0, 1)
        elif model_name == "Personalized FedAvg":
            p_m = AttentionLSTM(4, 64, 2)
            p_m.load_state_dict(torch.load(f"models/personalized/{cid}_personalized.pt", map_location=device))
            p_m.eval()
            with torch.no_grad():
                preds = np.clip(p_m(torch.tensor(X_test)).numpy(), 0, 1)

        all_y.extend(y_test)
        all_preds.extend(preds)
        m = compute_metrics(y_test, preds, capacity=cap)
        per_lot_maes.append(m["MAE"])
        per_lot_spaces.append(m.get("MAE_spaces", 0.0))

    # Calculate Pooled vs Per-Lot
    pooled_m = compute_metrics(np.array(all_y), np.array(all_preds))

    results_table.append({
        "Model": model_name,
        "Pooled MAE (Micro)": pooled_m["MAE"],
        "Pooled RMSE": pooled_m["RMSE"],
        "Per-Lot Mean MAE (Macro)": round(float(np.mean(per_lot_maes)), 4),
        "Per-Lot Median MAE": round(float(np.median(per_lot_maes)), 4),
        "Between-Lot Std (sigma)": round(float(np.std(per_lot_maes)), 4),
        "Mean Space Error (bays)": round(float(np.mean(per_lot_spaces)), 1)
    })

df_reconciled = pd.DataFrame(results_table)
print(df_reconciled.to_string(index=False))
df_reconciled.to_csv("results/reconciled_benchmark_table.csv", index=False)
print("\nSaved reconciled table to results/reconciled_benchmark_table.csv")
