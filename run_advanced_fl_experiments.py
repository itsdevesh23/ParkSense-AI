"""
run_advanced_fl_experiments.py
Runs the critical missing experiments:
1. IID-Shuffled FedAvg Control (shuffles training samples uniformly across clients)
2. FedProx (with proximal regularization mu = 0.01)
3. FedPer (federated shared base representation + private local output heads)
4. Multi-seed evaluation (seeds 42, 101, 2024) reporting mean +/- std
"""

import os
import sys
import copy
import glob
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.models import AttentionLSTM

# Device
device = torch.device("cpu")

# Load client data
client_files = sorted(glob.glob("data/processed/client_*.npz"))
clients_data = []
all_X_tr, all_y_tr = [], []
all_X_te, all_y_te = [], []
caps = []

for f in client_files:
    d = np.load(f)
    cap = float(d["capacity"])
    caps.append(cap)
    c_info = {
        "id": os.path.basename(f).replace(".npz", ""),
        "cap": cap,
        "X_tr": d["X_train"],
        "y_tr": d["y30_train"],
        "X_te": d["X_test"],
        "y_te": d["y30_test"],
    }
    clients_data.append(c_info)
    all_X_tr.append(d["X_train"])
    all_y_tr.append(d["y30_train"])
    all_X_te.append(d["X_test"])
    all_y_te.append(d["y30_test"])

concat_X_tr = np.concatenate(all_X_tr, axis=0)
concat_y_tr = np.concatenate(all_y_tr, axis=0)
n_total = len(concat_X_tr)

def aggregate_weights(weights_list, sample_counts):
    total = sum(sample_counts)
    avg_state = copy.deepcopy(weights_list[0])
    for k in avg_state.keys():
        avg_state[k] = torch.zeros_like(avg_state[k], dtype=torch.float32)
        for w, cnt in zip(weights_list, sample_counts):
            avg_state[k] += w[k].float() * (cnt / total)
    return avg_state

def evaluate_global(state_dict, clients):
    model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    model.load_state_dict(state_dict)
    model.eval()
    
    y_true_all, y_pred_all = [], []
    lot_maes = []
    with torch.no_grad():
        for c in clients:
            preds = model(torch.tensor(c["X_te"])).numpy()
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
results_record = []

# ==================== 1. IID-SHUFFLED FEDAVG CONTROL ====================
print("--- 1. IID-SHUFFLED FEDAVG CONTROL ---", flush=True)
for seed in seeds:
    np.random.seed(seed)
    torch.manual_seed(seed)
    perm = np.random.permutation(n_total)
    
    chunk_size = n_total // 30
    iid_clients = []
    for idx in range(30):
        start = idx * chunk_size
        end = (idx + 1) * chunk_size if idx < 29 else n_total
        iid_clients.append({
            "X_tr": concat_X_tr[perm[start:end]],
            "y_tr": concat_y_tr[perm[start:end]],
            "X_te": clients_data[idx]["X_te"],
            "y_te": clients_data[idx]["y_te"]
        })
        
    init_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    g_state = copy.deepcopy(init_model.state_dict())
    
    for r in range(8):
        local_w = []
        for c in iid_clients:
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            m.load_state_dict(g_state)
            m.train()
            loader = DataLoader(TensorDataset(torch.tensor(c["X_tr"]), torch.tensor(c["y_tr"])),
                                batch_size=32, shuffle=True)
            opt = torch.optim.Adam(m.parameters(), lr=0.001, weight_decay=1e-5)
            crit = nn.MSELoss()
            for ep in range(2):
                for bx, by in loader:
                    opt.zero_grad()
                    loss = crit(m(bx), by)
                    loss.backward()
                    opt.step()
            local_w.append(copy.deepcopy(m.state_dict()))
        g_state = aggregate_weights(local_w, [len(c["X_tr"]) for c in iid_clients])
        
    p_mae, p_rmse, m_mae, sig = evaluate_global(g_state, clients_data)
    results_record.append({"Model": "IID-Shuffled FedAvg Control", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig})
    print(f"  IID FedAvg Seed {seed}: Pooled MAE = {p_mae:.4f}, Macro MAE = {m_mae:.4f}, Sigma = {sig:.4f}", flush=True)

# ==================== 2. FEDPROX (mu = 0.01) ====================
print("\n--- 2. FEDPROX (mu = 0.01) ---", flush=True)
for seed in seeds:
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    init_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    g_state = copy.deepcopy(init_model.state_dict())
    
    for r in range(8):
        local_w = []
        for c in clients_data:
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            m.load_state_dict(g_state)
            m.train()
            loader = DataLoader(TensorDataset(torch.tensor(c["X_tr"]), torch.tensor(c["y_tr"])),
                                batch_size=32, shuffle=True)
            opt = torch.optim.Adam(m.parameters(), lr=0.001, weight_decay=1e-5)
            crit = nn.MSELoss()
            
            # Global reference tensors
            g_tensors = {k: v.clone() for k, v in g_state.items()}
            
            for ep in range(2):
                for bx, by in loader:
                    opt.zero_grad()
                    loss = crit(m(bx), by)
                    
                    # Proximal penalty
                    prox = 0.0
                    for name, param in m.named_parameters():
                        prox += ((param - g_tensors[name]) ** 2).sum()
                    loss = loss + (0.01 / 2.0) * prox
                    
                    loss.backward()
                    opt.step()
            local_w.append(copy.deepcopy(m.state_dict()))
        g_state = aggregate_weights(local_w, [len(c["X_tr"]) for c in clients_data])
        
    p_mae, p_rmse, m_mae, sig = evaluate_global(g_state, clients_data)
    results_record.append({"Model": "FedProx (mu = 0.01)", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig})
    print(f"  FedProx Seed {seed}: Pooled MAE = {p_mae:.4f}, Macro MAE = {m_mae:.4f}, Sigma = {sig:.4f}", flush=True)

# ==================== 3. FEDPER (Shared Representation, Private Head) ====================
print("\n--- 3. FEDPER (Shared Base, Private Head) ---", flush=True)
for seed in seeds:
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    init_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    # Global state holds base parameters only
    g_base_state = {k: v for k, v in init_model.state_dict().items() if not k.startswith("fc.")}
    
    # Each client holds private local head
    client_heads = [copy.deepcopy(init_model.fc.state_dict()) for _ in range(30)]
    
    for r in range(8):
        local_base_w = []
        for i, c in enumerate(clients_data):
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            full_state = copy.deepcopy(g_base_state)
            for hk, hv in client_heads[i].items():
                full_state[f"fc.{hk}"] = hv
            m.load_state_dict(full_state)
            m.train()
            
            loader = DataLoader(TensorDataset(torch.tensor(c["X_tr"]), torch.tensor(c["y_tr"])),
                                batch_size=32, shuffle=True)
            opt = torch.optim.Adam(m.parameters(), lr=0.001, weight_decay=1e-5)
            crit = nn.MSELoss()
            for ep in range(2):
                for bx, by in loader:
                    opt.zero_grad()
                    loss = crit(m(bx), by)
                    loss.backward()
                    opt.step()
                    
            client_heads[i] = copy.deepcopy(m.fc.state_dict())
            base_w = {k: v for k, v in m.state_dict().items() if not k.startswith("fc.")}
            local_base_w.append(base_w)
            
        g_base_state = aggregate_weights(local_base_w, [len(c["X_tr"]) for c in clients_data])
        
    y_true_all, y_pred_all = [], []
    lot_maes = []
    with torch.no_grad():
        for i, c in enumerate(clients_data):
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            full_state = copy.deepcopy(g_base_state)
            for hk, hv in client_heads[i].items():
                full_state[f"fc.{hk}"] = hv
            m.load_state_dict(full_state)
            m.eval()
            preds = np.clip(m(torch.tensor(c["X_te"])).numpy(), 0.0, 1.0)
            y_true_all.extend(c["y_te"])
            y_pred_all.extend(preds)
            lot_maes.append(mean_absolute_error(c["y_te"], preds))
            
    p_mae = mean_absolute_error(y_true_all, y_pred_all)
    p_rmse = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
    m_mae = np.mean(lot_maes)
    sig = np.std(lot_maes)
    results_record.append({"Model": "FedPer (Arivazhagan et al.)", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig})
    print(f"  FedPer Seed {seed}: Pooled MAE = {p_mae:.4f}, Macro MAE = {m_mae:.4f}, Sigma = {sig:.4f}", flush=True)

# ==================== 4. FEDAVG & PERSONALIZED FEDAVG MULTI-SEED ====================
print("\n--- 4. STANDARD FEDAVG & PERSONALIZED FEDAVG MULTI-SEED ---", flush=True)
for seed in seeds:
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    init_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    g_state = copy.deepcopy(init_model.state_dict())
    
    for r in range(8):
        local_w = []
        for c in clients_data:
            m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
            m.load_state_dict(g_state)
            m.train()
            loader = DataLoader(TensorDataset(torch.tensor(c["X_tr"]), torch.tensor(c["y_tr"])),
                                batch_size=32, shuffle=True)
            opt = torch.optim.Adam(m.parameters(), lr=0.001, weight_decay=1e-5)
            crit = nn.MSELoss()
            for ep in range(2):
                for bx, by in loader:
                    opt.zero_grad()
                    loss = crit(m(bx), by)
                    loss.backward()
                    opt.step()
            local_w.append(copy.deepcopy(m.state_dict()))
        g_state = aggregate_weights(local_w, [len(c["X_tr"]) for c in clients_data])
        
    p_mae, p_rmse, m_mae, sig = evaluate_global(g_state, clients_data)
    results_record.append({"Model": "Global FedAvg (R=8)", "Seed": seed, "Pooled MAE": p_mae, "Pooled RMSE": p_rmse, "Macro MAE": m_mae, "Sigma": sig})
    
    # Personalization fine-tuning
    y_true_all, y_pred_all = [], []
    lot_maes = []
    for c in clients_data:
        m = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
        m.load_state_dict(g_state)
        m.train()
        loader = DataLoader(TensorDataset(torch.tensor(c["X_tr"]), torch.tensor(c["y_tr"])),
                            batch_size=32, shuffle=True)
        opt = torch.optim.Adam(m.parameters(), lr=0.0003)
        crit = nn.MSELoss()
        for ep in range(3):
            for bx, by in loader:
                opt.zero_grad()
                loss = crit(m(bx), by)
                loss.backward()
                opt.step()
        m.eval()
        with torch.no_grad():
            preds = np.clip(m(torch.tensor(c["X_te"])).numpy(), 0.0, 1.0)
            y_true_all.extend(c["y_te"])
            y_pred_all.extend(preds)
            lot_maes.append(mean_absolute_error(c["y_te"], preds))
            
    p_mae_p = mean_absolute_error(y_true_all, y_pred_all)
    p_rmse_p = np.sqrt(mean_squared_error(y_true_all, y_pred_all))
    m_mae_p = np.mean(lot_maes)
    sig_p = np.std(lot_maes)
    results_record.append({"Model": "Personalized FedAvg (Ours)", "Seed": seed, "Pooled MAE": p_mae_p, "Pooled RMSE": p_rmse_p, "Macro MAE": m_mae_p, "Sigma": sig_p})
    print(f"  Seed {seed}: FedAvg MAE = {p_mae:.4f} -> Personalized MAE = {p_mae_p:.4f} (Sigma = {sig_p:.4f})", flush=True)

# Save results
df_res = pd.DataFrame(results_record)
df_res.to_csv("results/advanced_fl_experiments.csv", index=False)

summary = df_res.groupby("Model").agg({
    "Pooled MAE": ["mean", "std"],
    "Macro MAE": ["mean", "std"],
    "Sigma": ["mean", "std"]
})
print("\n=== ADVANCED FL EXPERIMENTAL SUMMARY (3 SEEDS) ===", flush=True)
print(summary, flush=True)
