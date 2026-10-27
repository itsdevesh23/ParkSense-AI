"""
src/models.py
Deep Learning Model Architectures for Smart Parking Availability Forecasting:
1. Standard LSTM (Centralized)
2. Attention-LSTM (Centralized & Federated Backbone)
   - Multi-Head Temporal Self-Attention over sequence hidden states
   - Evaluates on 30-min (1-step) and 60-min (2-step) availability horizons.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Tuple


class StandardLSTM(nn.Module):
    """
    Standard 2-layer LSTM sequence model.
    Takes input (Batch, Seq_Len, Features) and predicts availability ratio in [0, 1].
    """
    def __init__(self, input_dim: int = 4, hidden_dim: int = 64, num_layers: int = 2, dropout: float = 0.2):
        super(StandardLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid()  # Bounded availability ratio in [0, 1]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, (hn, cn) = self.lstm(x)
        # Use final time step hidden representation
        last_hidden = out[:, -1, :]
        pred = self.fc(last_hidden)
        return pred.squeeze(-1)


class TemporalAttention(nn.Module):
    """
    Temporal Self-Attention mechanism over LSTM hidden states.
    Computes dynamic attention weights alpha_t over the historical sequence.
    """
    def __init__(self, hidden_dim: int):
        super(TemporalAttention, self).__init__()
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, lstm_outputs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # lstm_outputs: (B, T, H)
        scores = self.attention(lstm_outputs)  # (B, T, 1)
        weights = F.softmax(scores, dim=1)     # (B, T, 1)
        context = torch.sum(weights * lstm_outputs, dim=1)  # (B, H)
        return context, weights.squeeze(-1)


class AttentionLSTM(nn.Module):
    """
    Attention-Based LSTM Architecture.
    Combines recurrent sequence encoding with temporal attention to focus
    on critical rapid-transition intervals.
    """
    def __init__(self, input_dim: int = 4, hidden_dim: int = 64, num_layers: int = 2, dropout: float = 0.2):
        super(AttentionLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.attention = TemporalAttention(hidden_dim)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),  # Concatenation of attention context + last hidden state
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid()  # Enforces availability ratio [0, 1]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (Batch, Seq_Len, Features)
        out, (hn, cn) = self.lstm(x)
        context, weights = self.attention(out)
        last_hidden = out[:, -1, :]
        combined = torch.cat([context, last_hidden], dim=1)
        pred = self.fc(combined)
        return pred.squeeze(-1)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, capacity: int = None, epsilon: float = 0.01) -> Dict[str, float]:
    """
    Evaluates standardized forecasting metrics:
    - MAE: Mean Absolute Error on ratio [0, 1]
    - RMSE: Root Mean Squared Error on ratio [0, 1]
    - MAPE_eps: Epsilon-smoothed Mean Absolute Percentage Error (handles 0 occupancy safely)
    - MAE_spaces: Physical parking bay error = MAE * Capacity
    """
    y_true = np.asarray(y_true, dtype=np.float32)
    y_pred = np.asarray(y_pred, dtype=np.float32)

    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mape = float(np.mean(np.abs(y_true - y_pred) / (y_true + epsilon)) * 100.0)

    res = {
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "MAPE_eps": round(mape, 2)
    }

    if capacity is not None and capacity > 0:
        res["MAE_spaces"] = round(mae * capacity, 1)

    return res
