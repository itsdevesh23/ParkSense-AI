"""
src/train_baselines.py
Phase 2: Reference Statistical Baselines
1. ARIMA(2, 1, 1): Classical linear autoregressive benchmark.
2. XGBoost Regressor: Non-linear gradient boosted decision tree benchmark.
Evaluates on 30-min (1-step) and 60-min (2-step) availability horizons.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import numpy as np
import xgboost as xgb
from statsmodels.tsa.arima.model import ARIMA
from src.models import compute_metrics


def train_evaluate_xgboost(
    data_dir: str = "data/processed",
    target_step: str = "30min"  # '30min' or '60min'
) -> dict:
    """
    Fits an XGBoost regressor on flattened sequence windows + temporal features.
    """
    print(f"\n--- Training XGBoost Baseline ({target_step} Horizon) ---")
    global_data = np.load(os.path.join(data_dir, "global_dataset.npz"))

    # Flatten X from (N, Seq_Len, Features) to (N, Seq_Len * Features)
    X_train = global_data["X_train"].reshape(len(global_data["X_train"]), -1)
    X_val = global_data["X_val"].reshape(len(global_data["X_val"]), -1)
    X_test = global_data["X_test"].reshape(len(global_data["X_test"]), -1)

    y_train = global_data["y30_train"] if target_step == "30min" else global_data["y60_train"]
    y_val = global_data["y30_val"] if target_step == "30min" else global_data["y60_val"]
    y_test = global_data["y30_test"] if target_step == "30min" else global_data["y60_test"]

    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    preds = model.predict(X_test)
    preds = np.clip(preds, 0.0, 1.0)
    metrics = compute_metrics(y_test, preds)

    print(f"XGBoost [{target_step}] -> MAE: {metrics['MAE']:.4f} | RMSE: {metrics['RMSE']:.4f} | MAPE: {metrics['MAPE_eps']:.2f}%")
    return {"metrics": metrics, "predictions": preds, "model": model}


def train_evaluate_arima(
    data_dir: str = "data/processed",
    max_eval_samples: int = 500
) -> dict:
    """
    Fits an ARIMA(2, 1, 1) model on chronological availability sequences.
    Evaluated over a representative sample to maintain fast evaluation turnaround.
    """
    print("\n--- Fitting ARIMA(2, 1, 1) Statistical Baseline ---")
    global_data = np.load(os.path.join(data_dir, "global_dataset.npz"))

    # Extract historical univariate series from feature 0
    X_test = global_data["X_test"][:max_eval_samples]
    y_test_30 = global_data["y30_test"][:max_eval_samples]
    y_test_60 = global_data["y60_test"][:max_eval_samples]

    preds_30, preds_60 = [], []

    for i in range(len(X_test)):
        series = X_test[i, :, 0]
        try:
            # Fit fast local ARIMA
            res = ARIMA(series, order=(2, 1, 1)).fit()
            forecast = res.forecast(steps=2)
            preds_30.append(float(np.clip(forecast[0], 0.0, 1.0)))
            preds_60.append(float(np.clip(forecast[1], 0.0, 1.0)))
        except Exception:
            # Fallback to persistent naive last observation
            last_val = float(series[-1])
            preds_30.append(last_val)
            preds_60.append(last_val)

    m30 = compute_metrics(y_test_30, np.array(preds_30))
    m60 = compute_metrics(y_test_60, np.array(preds_60))

    print(f"ARIMA [+30min] -> MAE: {m30['MAE']:.4f} | RMSE: {m30['RMSE']:.4f} | MAPE: {m30['MAPE_eps']:.2f}%")
    print(f"ARIMA [+60min] -> MAE: {m60['MAE']:.4f} | RMSE: {m60['RMSE']:.4f} | MAPE: {m60['MAPE_eps']:.2f}%")

    return {"metrics_30": m30, "metrics_60": m60}


if __name__ == "__main__":
    xgb_30 = train_evaluate_xgboost(target_step="30min")
    xgb_60 = train_evaluate_xgboost(target_step="60min")
    arima_res = train_evaluate_arima()
