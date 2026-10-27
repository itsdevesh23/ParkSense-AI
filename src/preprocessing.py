"""
src/preprocessing.py
Phase 1: Automated Data Cleaning, Imputation, Normalization, and Partitioning
for Federated Multi-Lot Smart Parking Forecasting.

Testbed: Birmingham Parking Dataset (UCI Machine Learning Repository, 30 Lots).
Target: Availability Ratio y_t = (Capacity - Occupancy) / Capacity in [0, 1].
Split: Chronological 70% Train / 15% Validation / 15% Test (Zero lookahead).
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


def clean_raw_data(csv_path: str = "data/dataset.csv") -> pd.DataFrame:
    """
    Loads raw CSV and cleans sensor anomalies:
    - Parses timestamps
    - Clips occupancy between 0 and Capacity
    - Computes availability ratio y_t
    """
    df = pd.read_csv(csv_path)
    df["LastUpdated"] = pd.to_datetime(df["LastUpdated"])
    df = df.sort_values(["SystemCodeNumber", "LastUpdated"]).reset_index(drop=True)

    # Sensor anomaly handling:
    # 1. Negative occupancy readings (e.g., NIA North had -8)
    df["Occupancy"] = df["Occupancy"].clip(lower=0)
    # 2. Overcounting exceeding nominal capacity
    df["Occupancy"] = np.minimum(df["Occupancy"], df["Capacity"])

    # Continuous target variable: Availability Ratio in [0, 1]
    df["AvailabilityRatio"] = (df["Capacity"] - df["Occupancy"]) / df["Capacity"]
    df["AvailabilityRatio"] = df["AvailabilityRatio"].clip(lower=0.0, upper=1.0)

    return df


def resample_and_impute_sessions(
    lot_df: pd.DataFrame, freq: str = "30min"
) -> pd.DataFrame:
    """
    Resamples daily operating sessions (07:30 to 16:30) to a uniform 30-min grid.
    Forward-fills / linearly interpolates missing points within operating sessions.
    Avoids interpolating across nightly shutdown gaps.
    """
    lot_df = lot_df.copy()
    lot_df["Date"] = lot_df["LastUpdated"].dt.date
    processed_days = []

    for date, day_group in lot_df.groupby("Date"):
        day_group = day_group.set_index("LastUpdated").sort_index()

        # Deduplicate timestamps if any
        day_group = day_group[~day_group.index.duplicated(keep="first")]

        # Determine daily session boundary
        start_time = pd.Timestamp(f"{date} 08:00:00")
        end_time = pd.Timestamp(f"{date} 16:30:00")

        # Create uniform 30-min index for the business hours
        full_idx = pd.date_range(start=start_time, end=end_time, freq=freq)
        reindexed = day_group.reindex(day_group.index.union(full_idx))

        # Interpolate availability ratio within the operating session
        reindexed["AvailabilityRatio"] = (
            reindexed["AvailabilityRatio"].interpolate(method="time").ffill().bfill()
        )
        reindexed["Capacity"] = reindexed["Capacity"].ffill().bfill()
        reindexed["Occupancy"] = (
            reindexed["Capacity"] * (1.0 - reindexed["AvailabilityRatio"])
        ).round()
        reindexed["SystemCodeNumber"] = day_group["SystemCodeNumber"].iloc[0]

        # Filter strictly to the regular business hours grid
        resampled_session = reindexed.loc[full_idx].reset_index()
        resampled_session = resampled_session.rename(columns={"index": "Timestamp"})
        processed_days.append(resampled_session)

    if not processed_days:
        return pd.DataFrame()

    full_resampled = pd.concat(processed_days, ignore_index=True)
    full_resampled = full_resampled.sort_values("Timestamp").reset_index(drop=True)
    return full_resampled


def generate_sliding_windows(
    session_df: pd.DataFrame,
    seq_len: int = 6,  # 6 time steps = 3 hours lookback
    horizon: int = 2,  # 1 step (30 min) and 2 steps (60 min)
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Constructs sequence input windows X and multi-horizon prediction targets:
    - X: shape (N, seq_len, num_features)
    - y_30: shape (N,) (30-min ahead availability ratio)
    - y_60: shape (N,) (60-min ahead availability ratio)

    Features:
    0: AvailabilityRatio
    1: Sine hour of day
    2: Cosine hour of day
    3: Day of week / 7.0
    """
    session_df = session_df.copy()
    session_df["Hour"] = session_df["Timestamp"].dt.hour + session_df["Timestamp"].dt.minute / 60.0
    session_df["SinHour"] = np.sin(2 * np.pi * session_df["Hour"] / 24.0)
    session_df["CosHour"] = np.cos(2 * np.pi * session_df["Hour"] / 24.0)
    session_df["DayOfWeek"] = session_df["Timestamp"].dt.dayofweek / 7.0

    feature_cols = ["AvailabilityRatio", "SinHour", "CosHour", "DayOfWeek"]
    feature_matrix = session_df[feature_cols].values
    target_series = session_df["AvailabilityRatio"].values

    X_list, y_30_list, y_60_list = [], [], []

    # Construct sequences within continuous dates
    session_df["Date"] = session_df["Timestamp"].dt.date
    dates = session_df["Date"].values

    for i in range(len(session_df) - seq_len - horizon + 1):
        # Guarantee window does not cross across different days
        window_dates = dates[i : i + seq_len + horizon]
        if len(set(window_dates)) == 1:
            X_list.append(feature_matrix[i : i + seq_len])
            y_30_list.append(target_series[i + seq_len])       # 1-step ahead (+30 min)
            y_60_list.append(target_series[i + seq_len + 1])   # 2-step ahead (+60 min)

    if not X_list:
        return np.empty((0, seq_len, 4)), np.empty((0,)), np.empty((0,))

    return np.array(X_list, dtype=np.float32), np.array(y_30_list, dtype=np.float32), np.array(y_60_list, dtype=np.float32)


def chronological_split(
    X: np.ndarray, y_30: np.ndarray, y_60: np.ndarray,
    train_frac: float = 0.70,
    val_frac: float = 0.15
) -> Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Partitions sequentially: 70% Train, 15% Validation, 15% Test.
    Strict chronological ordering eliminates future-leakage risk.
    """
    n = len(X)
    train_end = int(n * train_frac)
    val_end = int(n * (train_frac + val_frac))

    return {
        "train": (X[:train_end], y_30[:train_end], y_60[:train_end]),
        "val": (X[train_end:val_end], y_30[train_end:val_end], y_60[train_end:val_end]),
        "test": (X[val_end:], y_30[val_end:], y_60[val_end:])
    }


def run_phase1_pipeline(
    csv_path: str = "data/dataset.csv",
    output_dir: str = "data/processed",
    seq_len: int = 6,
    min_samples_per_client: int = 50
) -> Dict:
    """
    Executes end-to-end Phase 1 data pipeline:
    1. Clean raw CSV anomalies
    2. Resample and impute sessions for all 30 parking clients
    3. Generate sliding windows and cyclical features
    4. Apply strict chronological 70/15/15 split per client
    5. Save client-level and global aggregated datasets
    """
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 60)
    print("PHASE 1: DATA PREPROCESSING & PARTITIONING PIPELINE")
    print("=" * 60)

    print("Step 1: Cleaning raw dataset...")
    df = clean_raw_data(csv_path)
    print(f"Loaded {len(df):,} records across {df['SystemCodeNumber'].nunique()} parking facilities.")

    client_metadata = {}
    valid_clients = []

    global_X_train, global_y30_train, global_y60_train = [], [], []
    global_X_val, global_y30_val, global_y60_val = [], [], []
    global_X_test, global_y30_test, global_y60_test = [], [], []

    lots = sorted(df["SystemCodeNumber"].unique())

    print("\nStep 2: Processing individual client streams...")
    for idx, lot_id in enumerate(lots):
        lot_df = df[df["SystemCodeNumber"] == lot_id]
        capacity = int(lot_df["Capacity"].iloc[0])

        # Resample onto uniform 30-minute daytime grid
        resampled = resample_and_impute_sessions(lot_df, freq="30min")
        if len(resampled) == 0:
            print(f"  [Client {idx:02d} | {lot_id}] Skipped (no valid sessions)")
            continue

        # Create lookback sequence windows
        X, y_30, y_60 = generate_sliding_windows(resampled, seq_len=seq_len)

        if len(X) < min_samples_per_client:
            print(f"  [Client {idx:02d} | {lot_id}] Skipped (only {len(X)} windows, below threshold)")
            continue

        # Chronological 70/15/15 partition
        splits = chronological_split(X, y_30, y_60)
        valid_clients.append(lot_id)

        # Save individual client partitions
        client_file = os.path.join(output_dir, f"client_{idx:02d}_{lot_id}.npz")
        np.savez_compressed(
            client_file,
            X_train=splits["train"][0], y30_train=splits["train"][1], y60_train=splits["train"][2],
            X_val=splits["val"][0], y30_val=splits["val"][1], y60_val=splits["val"][2],
            X_test=splits["test"][0], y30_test=splits["test"][1], y60_test=splits["test"][2],
            capacity=capacity
        )

        client_metadata[lot_id] = {
            "client_index": idx,
            "lot_id": lot_id,
            "capacity": capacity,
            "raw_records": len(lot_df),
            "resampled_steps": len(resampled),
            "total_windows": len(X),
            "train_samples": len(splits["train"][0]),
            "val_samples": len(splits["val"][0]),
            "test_samples": len(splits["test"][0]),
            "file": client_file
        }

        # Accumulate for centralized global training
        global_X_train.append(splits["train"][0])
        global_y30_train.append(splits["train"][1])
        global_y60_train.append(splits["train"][2])

        global_X_val.append(splits["val"][0])
        global_y30_val.append(splits["val"][1])
        global_y60_val.append(splits["val"][2])

        global_X_test.append(splits["test"][0])
        global_y30_test.append(splits["test"][1])
        global_y60_test.append(splits["test"][2])

        print(f"  [Client {idx:02d} | {lot_id:15s}] Cap: {capacity:4d} | Windows: {len(X):4d} "
              f"(Train: {len(splits['train'][0])}, Val: {len(splits['val'][0])}, Test: {len(splits['test'][0])})")

    # Save centralized global pooled dataset for baseline benchmarking
    global_file = os.path.join(output_dir, "global_dataset.npz")
    np.savez_compressed(
        global_file,
        X_train=np.concatenate(global_X_train, axis=0),
        y30_train=np.concatenate(global_y30_train, axis=0),
        y60_train=np.concatenate(global_y60_train, axis=0),
        X_val=np.concatenate(global_X_val, axis=0),
        y30_val=np.concatenate(global_y30_val, axis=0),
        y60_val=np.concatenate(global_y60_val, axis=0),
        X_test=np.concatenate(global_X_test, axis=0),
        y30_test=np.concatenate(global_y30_test, axis=0),
        y60_test=np.concatenate(global_y60_test, axis=0)
    )

    # Save summary metadata JSON
    meta_summary = {
        "dataset_name": "Birmingham Parking Dataset (UCI)",
        "num_valid_clients": len(valid_clients),
        "total_clients_in_raw": len(lots),
        "seq_len": seq_len,
        "input_features": ["AvailabilityRatio", "SinHour", "CosHour", "DayOfWeek"],
        "target_horizons": ["+30min (1-step)", "+60min (2-step)"],
        "split_ratios": {"train": 0.70, "val": 0.15, "test": 0.15},
        "total_global_train_samples": int(sum(c["train_samples"] for c in client_metadata.values())),
        "total_global_val_samples": int(sum(c["val_samples"] for c in client_metadata.values())),
        "total_global_test_samples": int(sum(c["test_samples"] for c in client_metadata.values())),
        "clients": client_metadata
    }

    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(meta_summary, f, indent=2)

    print("\n" + "=" * 60)
    print("PHASE 1 COMPLETE!")
    print(f"Active Federated Clients: {len(valid_clients)}")
    print(f"Total Centralized Samples: Train={meta_summary['total_global_train_samples']:,}, "
          f"Val={meta_summary['total_global_val_samples']:,}, Test={meta_summary['total_global_test_samples']:,}")
    print(f"Saved preprocessed artifacts to: {output_dir}")
    print("=" * 60)

    return meta_summary


if __name__ == "__main__":
    run_phase1_pipeline()
