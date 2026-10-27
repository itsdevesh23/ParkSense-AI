"""
run_fast_advanced_fl.py
High-speed vectorized execution of missing FL experiments across 3 seeds (42, 101, 2024):
1. IID-Shuffled FedAvg Control
2. FedProx (mu = 0.01)
3. FedPer (Shared base representation + Private local output head)
4. Standard FedAvg & Personalized FedAvg
Pre-allocates PyTorch tensors for sub-minute execution.
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
    X_te_t = torch.tensor(d["X_test"], dtype=torch.float32)
    y_te_np = d["y30_test"]
    
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
    with torch.no_grad():
        for c in client_list:
            preds = model(c["X_te"]).numpy()
            preds = np.clip(preds, 0.0, 1.0)
            y_true_all.extend(c["y_te"])
            y_pred_all.extend(preds)
            lot_maes.append(mean_absolute_error(c["y_te"], preds))
            
    p_mae = mean_absolute_error(y_true_all, y_pred_all)
    p_rmse = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
    m_mae = np.mean(lot_maes)
    sig = np.std(lot_maes)
    return p_mae, p_rmse, m_mae, sig

seeds = [42, 101, 2024]
results = []
t0 = time.time()

# ==================== 1. IID-SHUFFLED FEDAVG CONTROL ====================
print("--- 1. IID-SHUFFLED FEDAVG CONTROL ---", flush=True)
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
    for r in range(8):
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
        
    p_mae, p_rmse, m_mae, sig = evaluate_global(g_state, clients)
    results.append({"Model": "IID-Shuffled FedAvg Control", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig})
    print(f"  IID FedAvg Seed {seed}: MAE={p_mae:.4f}, Macro={m_mae:.4f}, Sigma={sig:.4f}", flush=True)

# ==================== 2. FEDPROX (mu = 0.01) ====================
print("\n--- 2. FEDPROX (mu = 0.01) ---", flush=True)
for seed in seeds:
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    init_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    g_state = copy.deepcopy(init_model.state_dict())
    crit = nn.MSELoss()
    
    for r in range(8):
        local_w = []
        # Pre-extract parameter list for fast proximal calc
        g_params = [v.clone() for k, v in g_state.items()]
        
        for c in clients:
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            m.load_state_dict(g_state)
            m.train()
            opt = torch.optim.Adam(m.parameters(), lr=0.001, weight_decay=1e-5)
            
            for ep in range(2):
                for bx, by in c["loader"]:
                    opt.zero_grad()
                    loss = crit(m(bx), by)
                    
                    # Fast proximal penalty
                    prox = sum(((p - gp) ** 2).sum() for p, gp in zip(m.parameters(), g_params[:len(list(m.parameters()))]))
                    loss = loss + (0.01 / 2.0) * prox
                    loss.backward()
                    opt.step()
            local_w.append(copy.deepcopy(m.state_dict()))
        g_state = aggregate_weights(local_w, [len(c["X_tr"]) for c in clients])
        
    p_mae, p_rmse, m_mae, sig = evaluate_global(g_state, clients)
    results.append({"Model": "FedProx (mu = 0.01)", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig})
    print(f"  FedProx Seed {seed}: MAE={p_mae:.4f}, Macro={m_mae:.4f}, Sigma={sig:.4f}", flush=True)

# ==================== 3. FEDPER (Shared Base, Private Head) ====================
print("\n--- 3. FEDPER (Shared Base, Private Head) ---", flush=True)
for seed in seeds:
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    init_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    g_base_state = {k: v for k, v in init_model.state_dict().items() if not k.startswith("fc.")}
    client_heads = [copy.deepcopy(init_model.fc.state_dict()) for _ in range(30)]
    crit = nn.MSELoss()
    
    for r in range(8):
        local_base_w = []
        for i, c in enumerate(clients):
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            full_state = copy.deepcopy(g_base_state)
            for hk, hv in client_heads[i].items():
                full_state[f"fc.{hk}"] = hv
            m.load_state_dict(full_state)
            m.train()
            opt = torch.optim.Adam(m.parameters(), lr=0.001, weight_decay=1e-5)
            
            for ep in range(2):
                for bx, by in c["loader"]:
                    opt.zero_grad()
                    loss = crit(m(bx), by)
                    loss.backward()
                    opt.step()
                    
            client_heads[i] = copy.deepcopy(m.fc.state_dict())
            base_w = {k: v for k, v in m.state_dict().items() if not k.startswith("fc.")}
            local_base_w.append(base_w)
            
        g_base_state = aggregate_weights(local_base_w, [len(c["X_tr"]) for c in clients])
        
    # Evaluate FedPer
    y_true_all, y_pred_all = [], []
    lot_maes = []
    with torch.no_grad():
        for i, c in enumerate(clients):
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            full_state = copy.deepcopy(g_base_state)
            for hk, hv in client_heads[i].items():
                full_state[f"fc.{hk}"] = hv
            m.load_state_dict(full_state)
            m.eval()
            preds = np.clip(m(c["X_te"]).numpy(), 0.0, 1.0)
            y_true_all.extend(c["y_te"])
            y_pred_all.extend(preds)
            lot_maes.append(mean_absolute_error(c["y_te"], preds))
            
    p_mae = mean_absolute_error(y_true_all, y_pred_all)
    p_rmse = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
    m_mae = np.mean(lot_maes)
    sig = np.std(lot_maes)
    results.append({"Model": "FedPer (Shared Base, Private Head)", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig})
    print(f"  FedPer Seed {seed}: MAE={p_mae:.4f}, Macro={m_mae:.4f}, Sigma={sig:.4f}", flush=True)

# ==================== 4. FEDAVG & PERSONALIZED FEDAVG ====================
print("\n--- 4. STANDARD FEDAVG & PERSONALIZED FEDAVG ---", flush=True)
for seed in seeds:
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    init_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    g_state = copy.deepcopy(init_model.state_dict())
    crit = nn.MSELoss()
    
    for r in range(8):
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
        
    p_mae, p_rmse, m_mae, sig = evaluate_global(g_state, clients)
    results.append({"Model": "Global FedAvg (R=8)", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig})
    
    # Personalization fine-tuning
    y_true_all, y_pred_all = [], []
    lot_maes = []
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
            lot_maes.append(mean_absolute_error(c["y_te"], preds))
            
    p_mae_p = mean_absolute_error(y_true_all, y_pred_all)
    p_rmse_p = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
    m_mae_p = np.mean(lot_maes)
    sig_p = np.std(lot_maes)
    results.append({"Model": "Personalized FedAvg (Ours)", "Seed": seed, "Pooled MAE": p_mae_p, "Pooled RMSE": p_rmse_p, "Macro MAE": m_mae_p, "Sigma": sig_p})
    print(f"  Seed {seed}: FedAvg MAE={p_mae:.4f} -> Personalized MAE={p_mae_p:.4f} (Sigma={sig_p:.4f})", flush=True)

df_res = pd.DataFrame(results)
df_res.to_csv("results/advanced_fl_experiments.csv", index=False)
print(f"\nExecution finished in {time.time() - t0:.1f}s!", flush=True)

summary = df_res.groupby("Model").agg({
    "Pooled MAE": ["mean", "std"],
    "Macro MAE": ["mean", "std"],
    "Sigma": ["mean", "std"]
})
print("\n=== SUMMARY ACROSS 3 SEEDS ===", flush=True)
print(summary, flush=True)
