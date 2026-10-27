"""
scripts/experiment_rounds_30clients.py
Controlled Communication Round Scaling Experiment on the FULL 30-Client Population:
Evaluates FedAvg convergence across 4, 8, 12, and 16 communication rounds
with identical data splits, local epochs (E=2), learning rate (0.001), and evaluation protocol.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import copy
import glob
import torch
import numpy as np
import pandas as pd

from src.models import AttentionLSTM, compute_metrics
from src.federated_trainer import FederatedClient, federated_averaging

torch.manual_seed(42)
np.random.seed(42)

client_files = sorted(glob.glob("data/processed/client_*.npz"))
clients = [FederatedClient(os.path.basename(f).replace(".npz", ""), f, target_key="y30") for f in client_files]

print("=" * 75)
print(f"CONTROLLED 30-CLIENT FEDAVG ROUND SCALING EXPERIMENT (K={len(clients)})")
print("=" * 75)

global_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
global_state = copy.deepcopy(global_model.state_dict())

total_rounds = 16
checkpoint_rounds = [4, 8, 12, 16]
round_history = []

for r in range(1, total_rounds + 1):
    local_weights = []
    sample_counts = []
    round_losses = []

    for client in clients:
        # Use batch_size=64 for faster CPU throughput
        updated_state, loss = client.train_local(global_state, epochs=2, lr=0.001, batch_size=64)
        local_weights.append(updated_state)
        sample_counts.append(client.num_samples)
        round_losses.append(loss)

    global_state = federated_averaging(local_weights, sample_counts)
    mean_train_loss = np.mean(round_losses)

    if r in checkpoint_rounds:
        global_model.load_state_dict(global_state)
        
        # Evaluate on all 30 client test sets
        lot_maes = []
        all_y, all_preds = [], []
        for client in clients:
            with torch.no_grad():
                preds = np.clip(global_model(torch.tensor(client.X_test)).numpy(), 0, 1)
            m = compute_metrics(client.y_test, preds)
            lot_maes.append(m["MAE"])
            all_y.extend(client.y_test)
            all_preds.extend(preds)

        pooled_mae = compute_metrics(np.array(all_y), np.array(all_preds))["MAE"]
        macro_mae = np.mean(lot_maes)
        std_mae = np.std(lot_maes)

        print(f"  Round {r:02d}/{total_rounds:02d} | Train MSE: {mean_train_loss:.5f} | "
              f"Pooled Test MAE: {pooled_mae:.4f} | Macro Mean MAE: {macro_mae:.4f} | Inter-Lot Std: {std_mae:.4f}")

        round_history.append({
            "Rounds": r,
            "Mean Train MSE": round(float(mean_train_loss), 5),
            "Pooled Test MAE": round(float(pooled_mae), 4),
            "Macro Mean MAE": round(float(macro_mae), 4),
            "Between-Lot Std": round(float(std_mae), 4)
        })

df_rounds = pd.DataFrame(round_history)
df_rounds.to_csv("results/round_scaling_30clients.csv", index=False)
print("\nSaved 30-client round scaling results to: results/round_scaling_30clients.csv")
