"""
run_compute_parity_experiments.py
Evaluates FedAvg, IID-Shuffled FedAvg, and Personalized FedAvg at COMPUTE PARITY:
R = 15 rounds, E = 2 local epochs, B = 32.
Total gradient steps across the federation = 15 * 2 * 493 = 14,790 updates (~14,370 centralized steps).
Each client executes 30 local epochs (identical to centralized 30 epochs).
Evaluates across seeds 42, 101, 2024 on the 30 Birmingham lots with embargo purge gaps.
"""

import os
import copy
import glob
import time
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.models import AttentionLSTM

torch.set_num_threads(4)

# Load client data and pre-convert to torch tensors
client_files = sorted(glob.glob("data/processed/client_*.npz"))
clients = []
concat_X_tr_list, concat_y_tr_list = [], []

for f in client_files:
    d = np.load(f)
    cap = float(d["capacity"])
    X_tr_t = torch.tensor(d["X_train"], dtype=torch.float32)
    y_tr_t = torch.tensor(d["y30_train"], dtype=torch.float32)
    # Embargo purge gap: test slice
    X_te_t = torch.tensor(d["X_test"][1:], dtype=torch.float32)
    y_te_np = d["y30_test"][1:]
    
    clients.append({
        "id": os.path.basename(f).replace(".npz", ""),
        "cap": cap,
        "X_tr": X_tr_t,
        "y_tr": y_tr_t,
        "X_te": X_te_t,
        "y_te": y_te_np,
        "loader": DataLoader(TensorDataset(X_tr_t, y_tr_t), batch_size=32, shuffle=True)
    })
    concat_X_tr_list.append(d["X_train"])
    concat_y_tr_list.append(d["y30_train"])

concat_X_tr = torch.tensor(np.concatenate(concat_X_tr_list, axis=0), dtype=torch.float32)
concat_y_tr = torch.tensor(np.concatenate(concat_y_tr_list, axis=0), dtype=torch.float32)
n_total = len(concat_X_tr)

def aggregate_weights(weights_list, sample_counts):
    total = sum(sample_counts)
    avg_state = copy.deepcopy(weights_list[0])
    for k in avg_state.keys():
        avg_state[k] = torch.zeros_like(avg_state[k], dtype=torch.float32)
        for w, cnt in zip(weights_list, sample_counts):
            avg_state[k] += w[k].float() * (cnt / total)
    return avg_state

def evaluate_global(state_dict, client_list):
    model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    model.load_state_dict(state_dict)
    model.eval()
    
    y_true_all, y_pred_all = [], []
    lot_maes = []
    lot_spaces = []
    with torch.no_grad():
        for c in client_list:
            preds = model(c["X_te"]).numpy()
            preds = np.clip(preds, 0.0, 1.0)
            y_true_all.extend(c["y_te"])
            y_pred_all.extend(preds)
            lot_mae = mean_absolute_error(c["y_te"], preds)
            lot_maes.append(lot_mae)
            lot_spaces.append(lot_mae * c["cap"])
            
    p_mae = mean_absolute_error(y_true_all, y_pred_all)
    p_rmse = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
    m_mae = np.mean(lot_maes)
    sig = np.std(lot_maes)
    space_err = np.mean(lot_spaces)
    return p_mae, p_rmse, m_mae, sig, space_err

seeds = [42, 101, 2024]
results = []
t0 = time.time()

# ==================== 1. COMPUTE PARITY: NON-IID FEDAVG (R=15) ====================
print("--- 1. COMPUTE PARITY: NON-IID FEDAVG (R=15, E=2, ~14,790 steps) ---", flush=True)
for seed in seeds:
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    init_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    g_state = copy.deepcopy(init_model.state_dict())
    crit = nn.MSELoss()
    
    for r in range(15):
        local_w = []
        for c in clients:
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            m.load_state_dict(g_state)
            m.train()
            opt = torch.optim.Adam(m.parameters(), lr=0.001, weight_decay=1e-5)
            for ep in range(2):
                for bx, by in c["loader"]:
                    opt.zero_grad()
                    loss = crit(m(bx), by)
                    loss.backward()
                    opt.step()
            local_w.append(copy.deepcopy(m.state_dict()))
        g_state = aggregate_weights(local_w, [len(c["X_tr"]) for c in clients])
        
    p_mae, p_rmse, m_mae, sig, sp = evaluate_global(g_state, clients)
    results.append({"Model": "Compute-Parity FedAvg (R=15, Non-IID)", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig, "Space Error": sp})
    print(f"  Non-IID FedAvg (R=15) Seed {seed}: MAE={p_mae:.4f}, RMSE={p_rmse:.4f}, Macro={m_mae:.4f}, Sigma={sig:.4f}, Space={sp:.1f} bays", flush=True)

    # Also evaluate personalized fine-tuning at R=15
    y_true_all, y_pred_all = [], []
    lot_maes = []
    lot_spaces = []
    for c in clients:
        m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
        m.load_state_dict(g_state)
        m.train()
        opt = torch.optim.Adam(m.parameters(), lr=0.0003)
        for ep in range(3):
            for bx, by in c["loader"]:
                opt.zero_grad()
                loss = crit(m(bx), by)
                loss.backward()
                opt.step()
        m.eval()
        with torch.no_grad():
            preds = np.clip(m(c["X_te"]).numpy(), 0.0, 1.0)
            y_true_all.extend(c["y_te"])
            y_pred_all.extend(preds)
            lot_mae = mean_absolute_error(c["y_te"], preds)
            lot_maes.append(lot_mae)
            lot_spaces.append(lot_mae * c["cap"])
            
    p_mae_p = mean_absolute_error(y_true_all, y_pred_all)
    p_rmse_p = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
    m_mae_p = np.mean(lot_maes)
    sig_p = np.std(lot_maes)
    sp_p = np.mean(lot_spaces)
    results.append({"Model": "Compute-Parity Personalized FedAvg (R=15)", "Seed": seed, "Pooled MAE": p_mae_p, "Pooled RMSE": p_rmse_p, "Macro MAE": m_mae_p, "Sigma": sig_p, "Space Error": sp_p})
    print(f"    Personalized (R=15) Seed {seed}: MAE={p_mae_p:.4f}, Space={sp_p:.1f} bays", flush=True)

# ==================== 2. COMPUTE PARITY: IID-SHUFFLED FEDAVG (R=15) ====================
print("\n--- 2. COMPUTE PARITY: IID-SHUFFLED FEDAVG (R=15, E=2, ~14,790 steps) ---", flush=True)
chunk_size = n_total // 30
for seed in seeds:
    torch.manual_seed(seed)
    np.random.seed(seed)
    perm = torch.randperm(n_total)
    
    iid_clients = []
    for idx in range(30):
        st = idx * chunk_size
        en = (idx + 1) * chunk_size if idx < 29 else n_total
        cx = concat_X_tr[perm[st:en]]
        cy = concat_y_tr[perm[st:en]]
        iid_clients.append({
            "loader": DataLoader(TensorDataset(cx, cy), batch_size=32, shuffle=True),
            "num_samples": len(cx)
        })
        
    init_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    g_state = copy.deepcopy(init_model.state_dict())
    crit = nn.MSELoss()
    
    for r in range(15):
        local_w = []
        for ic in iid_clients:
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            m.load_state_dict(g_state)
            m.train()
            opt = torch.optim.Adam(m.parameters(), lr=0.001, weight_decay=1e-5)
            for ep in range(2):
                for bx, by in ic["loader"]:
                    opt.zero_grad()
                    loss = crit(m(bx), by)
                    loss.backward()
                    opt.step()
            local_w.append(copy.deepcopy(m.state_dict()))
        g_state = aggregate_weights(local_w, [ic["num_samples"] for ic in iid_clients])
        
    p_mae, p_rmse, m_mae, sig, sp = evaluate_global(g_state, clients)
    results.append({"Model": "Compute-Parity IID-Shuffled FedAvg (R=15)", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig, "Space Error": sp})
    print(f"  IID FedAvg (R=15) Seed {seed}: MAE={p_mae:.4f}, RMSE={p_rmse:.4f}, Macro={m_mae:.4f}, Sigma={sig:.4f}, Space={sp:.1f} bays", flush=True)

df_res = pd.DataFrame(results)
df_res.to_csv("results/compute_parity_experiments.csv", index=False)
print(f"\nExecution finished in {time.time() - t0:.1f}s!", flush=True)

summary = df_res.groupby("Model").agg({
    "Pooled MAE": ["mean", "std"],
    "Pooled RMSE": ["mean", "std"],
    "Macro MAE": ["mean", "std"],
    "Sigma": ["mean", "std"],
    "Space Error": ["mean", "std"]
})
print("\n=== COMPUTE-PARITY SUMMARY ACROSS 3 SEEDS ===", flush=True)
print(summary, flush=True)
