"""
eval_xgboost_multiseed.py
Evaluates XGBoost across seeds 42, 101, 2024.
"""

import glob
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

client_files = sorted(glob.glob("data/processed/client_*.npz"))
X_tr_list, y30_tr_list = [], []
X_te_list, y30_te_list = [], []
caps = []

for f in client_files:
    d = np.load(f)
    caps.append(float(d["capacity"]))
    # Flatten lookback features (6 steps x 4 features = 24 features)
    X_tr_list.append(d["X_train"].reshape(len(d["X_train"]), -1))
    y30_tr_list.append(d["y30_train"])
    X_te_list.append(d["X_test"].reshape(len(d["X_test"]), -1))
    y30_te_list.append(d["y30_test"])

X_tr = np.vstack(X_tr_list)
y_tr = np.concatenate(y30_tr_list)
X_te = np.vstack(X_te_list)
y_te = np.concatenate(y30_te_list)

xgb_results = []
for s in [42, 101, 2024]:
    model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.05, random_state=s, n_jobs=-1)
    model.fit(X_tr, y_tr)
    preds = np.clip(model.predict(X_te), 0.0, 1.0)
    p_mae = mean_absolute_error(y_te, preds)
    p_rmse = np.sqrt(mean_squared_error(y_te, preds))
    
    # Lot maes
    offset = 0
    lot_maes = []
    for x_c, y_c in zip(X_te_list, y30_te_list):
        n = len(y_c)
        lot_maes.append(mean_absolute_error(y_c, preds[offset:offset+n]))
        offset += n
    m_mae = np.mean(lot_maes)
    sig = np.std(lot_maes)
    xgb_results.append((p_mae, p_rmse, m_mae, sig))
    print(f"XGBoost Seed {s}: Pooled MAE = {p_mae:.4f}, Macro = {m_mae:.4f}, Sigma = {sig:.4f}")

maes = [r[0] for r in xgb_results]
print(f"XGBoost (3 Seeds): Mean MAE = {np.mean(maes):.4f} +/- {np.std(maes):.4f}")
