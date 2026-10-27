"""
src/plot_results.py
Generates publication-quality benchmark visualization charts:
1. results/benchmark_comparison_barchart.png (6-Model MAE across 30m & 60m)
2. results/personalization_variance_comparison.png (FedAvg vs Personalized FedAvg)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)

df = pd.read_csv("results/benchmark_comparison.csv")

# Set style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

models = [
    "ARIMA(2,1,1)",
    "XGBoost",
    "Centralized LSTM",
    "Centralized Att-LSTM",
    "FedAvg Att-LSTM",
    "Personalized FedAvg"
]

mae_30 = df["30m MAE"].values
mae_60 = df["60m MAE"].values

x = np.arange(len(models))
width = 0.35

rects1 = ax.bar(x - width/2, mae_30, width, label="30-min Horizon (+1 Step)", color="#1F4E79", edgecolor="black", alpha=0.9)
rects2 = ax.bar(x + width/2, mae_60, width, label="60-min Horizon (+2 Steps)", color="#2E75B6", edgecolor="black", alpha=0.9)

ax.set_ylabel("Mean Absolute Error (Availability Ratio $y_t$)", fontsize=11, fontweight="bold")
ax.set_title("6-Model Benchmark Comparison on Birmingham Smart Parking Testbed", fontsize=13, fontweight="bold", pad=15)
ax.set_xticks(x)
ax.set_xticklabels(models, rotation=18, ha="right", fontsize=9.5, fontweight="bold")
ax.legend(frameon=True, facecolor="white", edgecolor="none", fontsize=10)
ax.set_ylim(0, max(max(mae_30), max(mae_60)) * 1.25)

for rect in rects1:
    h = rect.get_height()
    ax.annotate(f"{h:.4f}", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

for rect in rects2:
    h = rect.get_height()
    ax.annotate(f"{h:.4f}", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

plt.tight_layout()
out_chart = "results/benchmark_comparison_barchart.png"
plt.savefig(out_chart)
plt.close()
print(f"Saved benchmark bar chart to: {out_chart}")
