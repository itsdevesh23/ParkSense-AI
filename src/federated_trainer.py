"""
src/federated_trainer.py
Phase 4 & 5: Federated Learning Simulation & Client Personalization
1. Federated Attention-LSTM (FedAvg) across 30 municipal parking clients.
2. Personalized Federated Attention-LSTM (p-FedAvg) with localized fine-tuning.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import copy
import glob
import json
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from typing import Dict, List, Tuple
from src.models import AttentionLSTM, compute_metrics


class FederatedClient:
    """
    Simulated Edge Parking Client.
    Holds private historical data partitions and trains locally without sharing raw streams.
    """
    def __init__(self, client_id: str, npz_path: str, target_key: str = "y30"):
        self.client_id = client_id
        data = np.load(npz_path)
        self.capacity = int(data["capacity"])
        self.X_train = data["X_train"]
        self.y_train = data[f"{target_key}_train"]
        self.X_val = data["X_val"]
        self.y_val = data[f"{target_key}_val"]
        self.X_test = data["X_test"]
        self.y_test = data[f"{target_key}_test"]
        self.num_samples = len(self.X_train)

    def train_local(
        self,
        global_state: dict,
        epochs: int = 2,
        lr: float = 0.001,
        batch_size: int = 32
    ) -> Tuple[dict, float]:
        """
        Loads global state, runs local SGD/Adam epochs, and returns updated state.
        """
        model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
        model.load_state_dict(global_state)
        model.train()

        train_loader = DataLoader(
            TensorDataset(torch.tensor(self.X_train), torch.tensor(self.y_train)),
            batch_size=batch_size,
            shuffle=True
        )

        optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
        criterion = nn.MSELoss()

        total_loss = 0.0
        for epoch in range(epochs):
            for bx, by in train_loader:
                optimizer.zero_grad()
                pred = model(bx)
                loss = criterion(pred, by)
                loss.backward()
                optimizer.step()
                total_loss += loss.item() * len(bx)

        avg_loss = total_loss / (epochs * len(self.X_train)) if len(self.X_train) > 0 else 0.0
        return copy.deepcopy(model.state_dict()), avg_loss

    def fine_tune_personalized(
        self,
        global_state: dict,
        epochs: int = 3,
        lr: float = 0.0003,
        batch_size: int = 32
    ) -> nn.Module:
        """
        Fine-tunes global weights on the client's local historical patterns.
        """
        model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
        model.load_state_dict(global_state)
        model.train()

        train_loader = DataLoader(
            TensorDataset(torch.tensor(self.X_train), torch.tensor(self.y_train)),
            batch_size=batch_size,
            shuffle=True
        )

        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        criterion = nn.MSELoss()

        for epoch in range(epochs):
            for bx, by in train_loader:
                optimizer.zero_grad()
                pred = model(bx)
                loss = criterion(pred, by)
                loss.backward()
                optimizer.step()

        return model

    def evaluate_model(self, model: nn.Module) -> dict:
        model.eval()
        with torch.no_grad():
            preds = model(torch.tensor(self.X_test)).numpy()
            preds = np.clip(preds, 0.0, 1.0)
        return compute_metrics(self.y_test, preds, capacity=self.capacity)


def federated_averaging(weights_list: List[dict], sample_counts: List[int]) -> dict:
    """
    Executes standard FedAvg parameter aggregation:
    w_global = sum_k (n_k / N) * w_k
    """
    total_samples = sum(sample_counts)
    avg_weights = copy.deepcopy(weights_list[0])

    for key in avg_weights.keys():
        avg_weights[key] = torch.zeros_like(avg_weights[key], dtype=torch.float32)
        for w, count in zip(weights_list, sample_counts):
            weight_factor = count / total_samples
            avg_weights[key] += w[key].float() * weight_factor

    return avg_weights


def run_federated_simulation(
    data_dir: str = "data/processed",
    models_dir: str = "models",
    target_step: str = "30min",
    rounds: int = 10,
    local_epochs: int = 2,
    personalize_epochs: int = 3
) -> dict:
    """
    Orchestrates FedAvg across 30 parking clients followed by local personalization.
    """
    os.makedirs(models_dir, exist_ok=True)
    target_key = "y30" if target_step == "30min" else "y60"

    client_files = sorted(glob.glob(os.path.join(data_dir, "client_*.npz")))
    clients = []
    for f in client_files:
        cid = os.path.basename(f).replace(".npz", "")
        clients.append(FederatedClient(cid, f, target_key=target_key))

    print(f"\nInitialized {len(clients)} federated parking clients for horizon [{target_step}].")

    # Initialize Global Server Model
    global_model = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    global_state = copy.deepcopy(global_model.state_dict())

    print("\n--- Starting FedAvg Communication Rounds ---")
    for r in range(1, rounds + 1):
        local_weights = []
        sample_counts = []
        round_losses = []

        for client in clients:
            updated_state, loss = client.train_local(
                global_state, epochs=local_epochs, lr=0.001
            )
            local_weights.append(updated_state)
            sample_counts.append(client.num_samples)
            round_losses.append(loss)

        # Server FedAvg Aggregation
        global_state = federated_averaging(local_weights, sample_counts)
        avg_round_loss = np.mean(round_losses)

        if r % 2 == 0 or r == rounds:
            print(f"  Round {r:02d}/{rounds:02d} | Aggregated Across {len(clients)} Clients | Mean Client MSE: {avg_round_loss:.5f}")

    global_model.load_state_dict(global_state)
    torch.save(global_state, os.path.join(models_dir, f"fedavg_att_lstm_{target_step}.pt"))

    # Evaluate Global FedAvg Model across all client test sets
    global_fed_metrics = []
    for client in clients:
        m = client.evaluate_model(global_model)
        global_fed_metrics.append(m)

    fed_mae = np.mean([m["MAE"] for m in global_fed_metrics])
    fed_rmse = np.mean([m["RMSE"] for m in global_fed_metrics])
    fed_mape = np.mean([m["MAPE_eps"] for m in global_fed_metrics])
    fed_spaces = np.mean([m.get("MAE_spaces", 0.0) for m in global_fed_metrics])
    fed_std = np.std([m["MAE"] for m in global_fed_metrics])

    print(f"\n[FedAvg Global Model ({target_step})]: MAE={fed_mae:.4f} | RMSE={fed_rmse:.4f} | MAPE={fed_mape:.2f}% | MAE_spaces={fed_spaces:.1f} bays | Inter-Lot Std={fed_std:.4f}")

    # Phase 5: Client Personalization (Local Fine-Tuning)
    print("\n--- Executing Phase 5: Client Local Fine-Tuning (Personalization) ---")
    pers_metrics = []
    for client in clients:
        p_model = client.fine_tune_personalized(
            global_state, epochs=personalize_epochs, lr=0.0003
        )
        m_p = client.evaluate_model(p_model)
        pers_metrics.append(m_p)

    pers_mae = np.mean([m["MAE"] for m in pers_metrics])
    pers_rmse = np.mean([m["RMSE"] for m in pers_metrics])
    pers_mape = np.mean([m["MAPE_eps"] for m in pers_metrics])
    pers_spaces = np.mean([m.get("MAE_spaces", 0.0) for m in pers_metrics])
    pers_std = np.std([m["MAE"] for m in pers_metrics])

    print(f"[Personalized FedAvg ({target_step})]: MAE={pers_mae:.4f} | RMSE={pers_rmse:.4f} | MAPE={pers_mape:.2f}% | MAE_spaces={pers_spaces:.1f} bays | Inter-Lot Std={pers_std:.4f}")

    return {
        "FedAvg": {
            "MAE": round(float(fed_mae), 4),
            "RMSE": round(float(fed_rmse), 4),
            "MAPE_eps": round(float(fed_mape), 2),
            "MAE_spaces": round(float(fed_spaces), 1),
            "std_lots": round(float(fed_std), 4)
        },
        "Personalized_FedAvg": {
            "MAE": round(float(pers_mae), 4),
            "RMSE": round(float(pers_rmse), 4),
            "MAPE_eps": round(float(pers_mape), 2),
            "MAE_spaces": round(float(pers_spaces), 1),
            "std_lots": round(float(pers_std), 4)
        }
    }


if __name__ == "__main__":
    run_federated_simulation(rounds=6, target_step="30min")
