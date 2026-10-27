"""
src/run_all_experiments.py
Master Benchmark Suite for Federated Multi-Lot Smart Parking Forecasting:
Executes the full 6-Model Benchmark Suite across both 30-min and 60-min Horizons:
1. ARIMA(2, 1, 1)
2. XGBoost Regressor
3. Centralized Standard LSTM
4. Centralized Attention-LSTM (Tests H1)
5. Federated Attention-LSTM via FedAvg (Tests H2)
6. Personalized Federated Attention-LSTM via Local Fine-Tuning (Tests H3)

Saves results to:
- results/benchmark_summary.json
- results/benchmark_comparison.csv
"""

import os
import sys

# Ensure root directory is on Python search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pandas as pd
import numpy as np

from src.preprocessing import run_phase1_pipeline
from src.train_baselines import train_evaluate_xgboost, train_evaluate_arima
from src.train_centralized import run_centralized_experiments
from src.federated_trainer import run_federated_simulation


def main():
    print("=" * 75)
    print("FEDERATED MULTI-LOT SMART PARKING FORECASTING: 6-MODEL BENCHMARK SUITE")
    print("=" * 75)

    os.makedirs("results", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    # 1. Phase 1: Preprocessing & Client Creation
    if not os.path.exists("data/processed/global_dataset.npz"):
        print("\n>>> STEP 1: Running Phase 1 Data Preprocessing...")
        run_phase1_pipeline()
    else:
        print("\n>>> STEP 1: Processed data detected. Loading existing client streams.")

    benchmark_records = []

    # 2. Phase 2: Statistical Baselines
    print("\n>>> STEP 2: Running Phase 2 Statistical Baselines (ARIMA & XGBoost)...")
    arima_res = train_evaluate_arima(max_eval_samples=400)
    xgb_30 = train_evaluate_xgboost(target_step="30min")
    xgb_60 = train_evaluate_xgboost(target_step="60min")

    benchmark_records.append({
        "Model Tier": "Tier 1: Statistical",
        "Model": "ARIMA(2, 1, 1)",
        "Architecture / Paradigm": "Linear Autoregressive Baseline",
        "30m MAE": arima_res["metrics_30"]["MAE"],
        "30m RMSE": arima_res["metrics_30"]["RMSE"],
        "30m MAPE (%)": arima_res["metrics_30"]["MAPE_eps"],
        "60m MAE": arima_res["metrics_60"]["MAE"],
        "60m RMSE": arima_res["metrics_60"]["RMSE"],
        "60m MAPE (%)": arima_res["metrics_60"]["MAPE_eps"]
    })

    benchmark_records.append({
        "Model Tier": "Tier 2: Machine Learning",
        "Model": "XGBoost Regressor",
        "Architecture / Paradigm": "Gradient Boosted Trees (Centralized)",
        "30m MAE": xgb_30["metrics"]["MAE"],
        "30m RMSE": xgb_30["metrics"]["RMSE"],
        "30m MAPE (%)": xgb_30["metrics"]["MAPE_eps"],
        "60m MAE": xgb_60["metrics"]["MAE"],
        "60m RMSE": xgb_60["metrics"]["RMSE"],
        "60m MAPE (%)": xgb_60["metrics"]["MAPE_eps"]
    })

    # 3. Phase 3: Centralized Deep Learning
    print("\n>>> STEP 3: Running Phase 3 Centralized Deep Learning (LSTM & Attention-LSTM)...")
    dl_res = run_centralized_experiments(epochs=10, batch_size=64)

    benchmark_records.append({
        "Model Tier": "Tier 3: Deep Sequence",
        "Model": "Centralized Standard LSTM",
        "Architecture / Paradigm": "2-Layer Recurrent Neural Net (Centralized)",
        "30m MAE": dl_res["Standard_LSTM_30"]["MAE"],
        "30m RMSE": dl_res["Standard_LSTM_30"]["RMSE"],
        "30m MAPE (%)": dl_res["Standard_LSTM_30"]["MAPE_eps"],
        "60m MAE": dl_res["Standard_LSTM_60"]["MAE"],
        "60m RMSE": dl_res["Standard_LSTM_60"]["RMSE"],
        "60m MAPE (%)": dl_res["Standard_LSTM_60"]["MAPE_eps"]
    })

    benchmark_records.append({
        "Model Tier": "Tier 3: Deep Sequence",
        "Model": "Centralized Attention-LSTM",
        "Architecture / Paradigm": "Temporal Attention + LSTM (Centralized)",
        "30m MAE": dl_res["Attention_LSTM_30"]["MAE"],
        "30m RMSE": dl_res["Attention_LSTM_30"]["RMSE"],
        "30m MAPE (%)": dl_res["Attention_LSTM_30"]["MAPE_eps"],
        "60m MAE": dl_res["Attention_LSTM_60"]["MAE"],
        "60m RMSE": dl_res["Attention_LSTM_60"]["RMSE"],
        "60m MAPE (%)": dl_res["Attention_LSTM_60"]["MAPE_eps"]
    })

    # 4. Phase 4 & 5: Federated Learning and Personalization
    print("\n>>> STEP 4 & 5: Running Phase 4 (FedAvg) and Phase 5 (Personalization) Simulations...")
    fed_res_30 = run_federated_simulation(target_step="30min", rounds=8, local_epochs=2, personalize_epochs=3)
    fed_res_60 = run_federated_simulation(target_step="60min", rounds=8, local_epochs=2, personalize_epochs=3)

    benchmark_records.append({
        "Model Tier": "Tier 4: Federated Learning",
        "Model": "Federated Attention-LSTM",
        "Architecture / Paradigm": "FedAvg Distributed Aggregation (Decentralized)",
        "30m MAE": fed_res_30["FedAvg"]["MAE"],
        "30m RMSE": fed_res_30["FedAvg"]["RMSE"],
        "30m MAPE (%)": fed_res_30["FedAvg"]["MAPE_eps"],
        "60m MAE": fed_res_60["FedAvg"]["MAE"],
        "60m RMSE": fed_res_60["FedAvg"]["RMSE"],
        "60m MAPE (%)": fed_res_60["FedAvg"]["MAPE_eps"]
    })

    benchmark_records.append({
        "Model Tier": "Tier 4: Federated Learning",
        "Model": "Personalized Federated Attention-LSTM",
        "Architecture / Paradigm": "FedAvg + Local Fine-Tuning (Client-Personalized)",
        "30m MAE": fed_res_30["Personalized_FedAvg"]["MAE"],
        "30m RMSE": fed_res_30["Personalized_FedAvg"]["RMSE"],
        "30m MAPE (%)": fed_res_30["Personalized_FedAvg"]["MAPE_eps"],
        "60m MAE": fed_res_60["Personalized_FedAvg"]["MAE"],
        "60m RMSE": fed_res_60["Personalized_FedAvg"]["RMSE"],
        "60m MAPE (%)": fed_res_60["Personalized_FedAvg"]["MAPE_eps"]
    })

    # Export benchmark comparison table
    df_results = pd.DataFrame(benchmark_records)
    csv_path = "results/benchmark_comparison.csv"
    df_results.to_csv(csv_path, index=False)

    json_path = "results/benchmark_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_records, f, indent=2)

    print("\n" + "=" * 75)
    print("COMPLETE 6-MODEL BENCHMARK RESULTS ACROSS HORIZONS")
    print("=" * 75)
    print(df_results.to_string(index=False))
    print("\nSaved benchmark tables to:")
    print(f"  - {csv_path}")
    print(f"  - {json_path}")
    print("=" * 75)


if __name__ == "__main__":
    main()
