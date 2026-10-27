"""
src/train_centralized.py
Phase 3: Centralized Deep Learning Models in PyTorch
1. Centralized Standard LSTM
2. Centralized Attention-LSTM
Trained across the pooled dataset for 30-min and 60-min horizons.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from src.models import StandardLSTM, AttentionLSTM, compute_metrics


def train_pytorch_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int = 15,
    lr: float = 0.001,
    device: str = "cpu"
) -> nn.Module:
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    criterion = nn.MSELoss()

    best_val_loss = float("inf")
    best_state = None

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(X_batch)

        train_loss /= len(train_loader.dataset)

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for X_val, y_val in val_loader:
                X_val, y_val = X_val.to(device), y_val.to(device)
                preds = model(X_val)
                loss = criterion(preds, y_val)
                val_loss += loss.item() * len(X_val)
        val_loss /= len(val_loader.dataset)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        if epoch % 5 == 0 or epoch == epochs:
            print(f"  Epoch {epoch:02d}/{epochs:02d} | Train MSE: {train_loss:.5f} | Val MSE: {val_loss:.5f}")

    if best_state is not None:
        model.load_state_dict(best_state)
    return model


def evaluate_pytorch_model(model: nn.Module, X_test: np.ndarray, y_test: np.ndarray, device: str = "cpu") -> dict:
    model.eval()
    model.to(device)
    with torch.no_grad():
        X_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
        preds = model(X_tensor).cpu().numpy()
        preds = np.clip(preds, 0.0, 1.0)
    return compute_metrics(y_test, preds)


def run_centralized_experiments(
    data_dir: str = "data/processed",
    models_dir: str = "models",
    epochs: int = 15,
    batch_size: int = 64
) -> dict:
    os.makedirs(models_dir, exist_ok=True)
    device = "cpu"
    print("=" * 60)
    print("PHASE 3: CENTRALIZED DEEP LEARNING EXPERIMENTS")
    print("=" * 60)

    data = np.load(os.path.join(data_dir, "global_dataset.npz"))
    X_train, X_val, X_test = data["X_train"], data["X_val"], data["X_test"]
    y30_train, y30_val, y30_test = data["y30_train"], data["y30_val"], data["y30_test"]
    y60_train, y60_val, y60_test = data["y60_train"], data["y60_val"], data["y60_test"]

    results = {}

    # 1. Standard LSTM (+30 min)
    print("\n--- Training Centralized Standard LSTM (+30 min Horizon) ---")
    train_loader = DataLoader(TensorDataset(torch.tensor(X_train), torch.tensor(y30_train)), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(torch.tensor(X_val), torch.tensor(y30_val)), batch_size=batch_size, shuffle=False)

    lstm_30 = StandardLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    lstm_30 = train_pytorch_model(lstm_30, train_loader, val_loader, epochs=epochs, device=device)
    torch.save(lstm_30.state_dict(), os.path.join(models_dir, "centralized_lstm_30.pt"))
    results["Standard_LSTM_30"] = evaluate_pytorch_model(lstm_30, X_test, y30_test)
    print(f"Results Standard LSTM (+30m): {results['Standard_LSTM_30']}")

    # 2. Attention-LSTM (+30 min)
    print("\n--- Training Centralized Attention-LSTM (+30 min Horizon) ---")
    att_30 = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    att_30 = train_pytorch_model(att_30, train_loader, val_loader, epochs=epochs, device=device)
    torch.save(att_30.state_dict(), os.path.join(models_dir, "centralized_att_lstm_30.pt"))
    results["Attention_LSTM_30"] = evaluate_pytorch_model(att_30, X_test, y30_test)
    print(f"Results Attention-LSTM (+30m): {results['Attention_LSTM_30']}")

    # 3. Standard LSTM (+60 min)
    print("\n--- Training Centralized Standard LSTM (+60 min Horizon) ---")
    train_loader_60 = DataLoader(TensorDataset(torch.tensor(X_train), torch.tensor(y60_train)), batch_size=batch_size, shuffle=True)
    val_loader_60 = DataLoader(TensorDataset(torch.tensor(X_val), torch.tensor(y60_val)), batch_size=batch_size, shuffle=False)

    lstm_60 = StandardLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    lstm_60 = train_pytorch_model(lstm_60, train_loader_60, val_loader_60, epochs=epochs, device=device)
    torch.save(lstm_60.state_dict(), os.path.join(models_dir, "centralized_lstm_60.pt"))
    results["Standard_LSTM_60"] = evaluate_pytorch_model(lstm_60, X_test, y60_test)
    print(f"Results Standard LSTM (+60m): {results['Standard_LSTM_60']}")

    # 4. Attention-LSTM (+60 min)
    print("\n--- Training Centralized Attention-LSTM (+60 min Horizon) ---")
    att_60 = AttentionLSTM(input_dim=4, hidden_dim=64, num_layers=2)
    att_60 = train_pytorch_model(att_60, train_loader_60, val_loader_60, epochs=epochs, device=device)
    torch.save(att_60.state_dict(), os.path.join(models_dir, "centralized_att_lstm_60.pt"))
    results["Attention_LSTM_60"] = evaluate_pytorch_model(att_60, X_test, y60_test)
    print(f"Results Attention-LSTM (+60m): {results['Attention_LSTM_60']}")

    return results


if __name__ == "__main__":
    run_centralized_experiments(epochs=12)
