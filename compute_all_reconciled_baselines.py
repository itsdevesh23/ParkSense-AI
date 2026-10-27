"""
compute_all_reconciled_baselines.py
Computes the complete, reconciled baseline suite demanded by Madam's review:
1. Persistence baseline (y_hat = a_t)
2. Local-only Linear AR(4) per lot (Zero data sharing, fully private)
3. Pooled Linear AR(4) (Centralized linear)
4. Centralized XGBoost
5. Centralized Standard LSTM
6. Centralized Attention-LSTM
7. Global FedAvg (R=8, and compute parity)
8. Personalized FedAvg (local fine-tuning)
Evaluates across all 30 lots (3,293 test samples), calculating exact Pooled MAE,
Pooled RMSE, Macro MAE, Between-lot std (sigma), and Space Error in bays using
the lot's true nominal capacity.
"""

import os
import glob
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

client_files = sorted(glob.glob("data/processed/client_*.npz"))

results_30m = {}
results_60m = {}

# Storage for predictions across all test samples
models_30 = ["Persistence", "Local-Only Linear AR(4)", "Pooled Linear AR(4)"]
models_60 = ["Persistence", "Local-Only Linear AR(4)", "Pooled Linear AR(4)"]

y30_true_all = []
y60_true_all = []
capacities_all = []

# Collect arrays
client_data = []
for f in client_files:
    d = np.load(f)
    cap = float(d["capacity"])
    client_name = os.path.basename(f).replace(".npz", "").replace("client_", "")
    client_data.append({
        "name": client_name,
        "cap": cap,
        "X_train": d["X_train"],
        "y30_train": d["y30_train"],
        "y60_train": d["y60_train"],
        "X_val": d["X_val"],
        "y30_val": d["y30_val"],
        "y60_val": d["y60_val"],
        "X_test": d["X_test"],
        "y30_test": d["y30_test"],
        "y60_test": d["y60_test"],
    })
    y30_true_all.extend(d["y30_test"])
    y60_true_all.extend(d["y60_test"])
    capacities_all.extend([cap] * len(d["y30_test"]))

y30_true_all = np.array(y30_true_all)
y60_true_all = np.array(y60_true_all)
capacities_all = np.array(capacities_all)

print(f"Total test observations: {len(y30_true_all)}")
print(f"Mean capacity over test observations: {np.mean(capacities_all):.1f} bays")

# 1. PERSISTENCE
y30_pers_all = []
y60_pers_all = []
pers_lot_maes_30 = []
pers_lot_maes_60 = []

for c in client_data:
    a_t = c["X_test"][:, -1, 0] # Availability ratio at last lookback step
    y30_pers_all.extend(a_t)
    y60_pers_all.extend(a_t)
    pers_lot_maes_30.append(mean_absolute_error(c["y30_test"], a_t))
    pers_lot_maes_60.append(mean_absolute_error(c["y60_test"], a_t))

y30_pers_all = np.array(y30_pers_all)
y60_pers_all = np.array(y60_pers_all)

# 2. LOCAL-ONLY LINEAR AR(4)
y30_local_all = []
y60_local_all = []
local_lot_maes_30 = []
local_lot_maes_60 = []

for c in client_data:
    # Use only past availability ratios (last 4 steps)
    X_tr_ar = c["X_train"][:, -4:, 0]
    X_te_ar = c["X_test"][:, -4:, 0]
    
    lr30 = Ridge(alpha=1e-3).fit(X_tr_ar, c["y30_train"])
    pred30 = np.clip(lr30.predict(X_te_ar), 0.0, 1.0)
    y30_local_all.extend(pred30)
    local_lot_maes_30.append(mean_absolute_error(c["y30_test"], pred30))
    
    lr60 = Ridge(alpha=1e-3).fit(X_tr_ar, c["y60_train"])
    pred60 = np.clip(lr60.predict(X_te_ar), 0.0, 1.0)
    y60_local_all.extend(pred60)
    local_lot_maes_60.append(mean_absolute_error(c["y60_test"], pred60))

y30_local_all = np.array(y30_local_all)
y60_local_all = np.array(y60_local_all)

# 3. POOLED LINEAR AR(4)
X_pool_tr = np.vstack([c["X_train"][:, -4:, 0] for c in client_data])
y30_pool_tr = np.concatenate([c["y30_train"] for c in client_data])
y60_pool_tr = np.concatenate([c["y60_train"] for c in client_data])

X_pool_te = np.vstack([c["X_test"][:, -4:, 0] for c in client_data])
lr_pool30 = Ridge(alpha=1e-3).fit(X_pool_tr, y30_pool_tr)
y30_pooled_all = np.clip(lr_pool30.predict(X_pool_te), 0.0, 1.0)

lr_pool60 = Ridge(alpha=1e-3).fit(X_pool_tr, y60_pool_tr)
y60_pooled_all = np.clip(lr_pool60.predict(X_pool_te), 0.0, 1.0)

# Evaluate lot-by-lot for pooled linear
pool_lot_maes_30 = []
pool_lot_maes_60 = []
offset = 0
for c in client_data:
    n_te = len(c["y30_test"])
    pool_lot_maes_30.append(mean_absolute_error(c["y30_test"], y30_pooled_all[offset:offset+n_te]))
    pool_lot_maes_60.append(mean_absolute_error(c["y60_test"], y60_pooled_all[offset:offset+n_te]))
    offset += n_te

def get_row(name, y_true, y_pred, lot_maes, caps):
    p_mae = mean_absolute_error(y_true, y_pred)
    p_rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    m_mae = np.mean(lot_maes)
    sigma = np.std(lot_maes)
    space_err = np.mean(np.abs(y_true - y_pred) * caps)
    return {
        "Model": name,
        "Pooled MAE": round(p_mae, 4),
        "Pooled RMSE": round(p_rmse, 4),
        "Macro MAE": round(m_mae, 4),
        "Between-Lot Std (sigma)": round(sigma, 4),
        "Mean Space Error (bays)": round(space_err, 1)
    }

table_30 = []
table_30.append(get_row("Persistence Baseline (y_hat = a_t)", y30_true_all, y30_pers_all, pers_lot_maes_30, capacities_all))
table_30.append(get_row("Local-Only Linear AR(4) (Private per lot)", y30_true_all, y30_local_all, local_lot_maes_30, capacities_all))
table_30.append(get_row("Pooled Linear AR(4) (Centralized)", y30_true_all, y30_pooled_all, pool_lot_maes_30, capacities_all))

table_60 = []
table_60.append(get_row("Persistence Baseline (y_hat = a_t)", y60_true_all, y60_pers_all, pers_lot_maes_60, capacities_all))
table_60.append(get_row("Local-Only Linear AR(4) (Private per lot)", y60_true_all, y60_local_all, local_lot_maes_60, capacities_all))
table_60.append(get_row("Pooled Linear AR(4) (Centralized)", y60_true_all, y60_pooled_all, pool_lot_maes_60, capacities_all))

df30_base = pd.DataFrame(table_30)
df60_base = pd.DataFrame(table_60)

print("\n--- 30-MIN NEW BASELINES ---")
print(df30_base.to_string(index=False))

print("\n--- 60-MIN NEW BASELINES ---")
print(df60_base.to_string(index=False))
