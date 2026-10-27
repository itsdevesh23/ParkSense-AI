"""
scripts/plot_all_figures.py
Generates the publication-grade figures for the manuscript:
1. results/fig1_model_comparison_grouped.png (Reconciled Benchmark with Baselines: Persistence, Local Linear, Centralized, FedAvg, Personalized FedAvg)
2. results/fig2_personalization_distribution_boxplot.png (Between-Lot Distribution across 30 Facilities: Local Linear, Centralized, FedAvg, Personalized FedAvg)
3. results/fig3_convergence_trajectory.png (FedAvg Training Loss across Communication Rounds)
4. results/fig4_round_scaling_30clients.png (Controlled 30-client round scaling plateau proof)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

os.makedirs("results", exist_ok=True)
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

# ==================== FIG 1: RECONCILED MODEL BENCHMARK WITH BASELINES ====================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2), dpi=300)

models = [
    "Persistence\n($\\hat{y}=a_t$)",
    "Local Linear\nAR(4)",
    "Pooled Linear\nAR(4)",
    "Centralized\nXGBoost",
    "Centralized\nAttn-LSTM",
    "Global FedAvg\n($R=8, E=2$)",
    "Personalized\nFedAvg"
]

mae_vals = [0.0257, 0.0126, 0.0129, 0.0145, 0.0217, 0.1007, 0.0607]
space_vals = [35.2, 14.5, 15.1, 17.6, 27.0, 127.1, 73.1]
x = np.arange(len(models))
width = 0.55
colors = ["#94A3B8", "#10B981", "#059669", "#2563EB", "#4F46E5", "#DC2626", "#F59E0B"]

# Subplot 1: Pooled MAE
bars1 = ax1.bar(x, mae_vals, width, color=colors, edgecolor="#1E293B", linewidth=0.8)
ax1.set_ylabel("Pooled MAE ($y_{30}$ Availability Ratio)", fontsize=10.5, fontweight="bold", labelpad=8)
ax1.set_title("(a) 30-Minute Forecasting Error (Micro-Average, $y_{30}$)", fontsize=11, fontweight="bold", pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=8.5, fontweight="bold")
ax1.set_ylim(0, 0.12)
for bar in bars1:
    h = bar.get_height()
    ax1.annotate(f"{h:.4f}", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

# Subplot 2: Physical Space Error
bars2 = ax2.bar(x, space_vals, width, color=colors, edgecolor="#1E293B", linewidth=0.8)
ax2.set_ylabel("Mean Space Error (Vacant Bays)", fontsize=10.5, fontweight="bold", labelpad=8)
ax2.set_title("(b) Operational Accuracy in Physical Bays (30-Minute)", fontsize=11, fontweight="bold", pad=10)
ax2.set_xticks(x)
ax2.set_xticklabels(models, fontsize=8.5, fontweight="bold")
ax2.set_ylim(0, 150)
for bar in bars2:
    h = bar.get_height()
    ax2.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

plt.tight_layout()
plt.savefig("results/fig1_model_comparison_grouped.png", dpi=300)
plt.close()

# ==================== FIG 2: BOXPLOT WITH LOCAL LINEAR ====================
df_lots = pd.read_csv("results/per_lot_evaluation_audit.csv")

local_linear_maes = []
for f in sorted(glob.glob("data/processed/client_*.npz")):
    d = np.load(f)
    X_tr = d["X_train"][:, -4:, 0]
    X_te = d["X_test"][:, -4:, 0]
    lr = Ridge(alpha=1e-3).fit(X_tr, d["y30_train"])
    pred = np.clip(lr.predict(X_te), 0.0, 1.0)
    local_linear_maes.append(mean_absolute_error(d["y30_test"], pred))

plt.figure(figsize=(9, 5.4), dpi=300)
box_data = [
    local_linear_maes,
    df_lots["Cent Attention MAE"].values,
    df_lots["FedAvg MAE"].values,
    df_lots["Personalized MAE"].values
]
labels = [
    "Local-Only Linear\n(Fully Private)",
    "Centralized\nAttention-LSTM",
    "Global FedAvg\n($R=8$)",
    "Personalized FedAvg\n(Local Adaptation)"
]

bp = plt.boxplot(box_data, tick_labels=labels, patch_artist=True, widths=0.45,
                 medianprops=dict(color="#B91C1C", linewidth=2.2),
                 flierprops=dict(marker='o', color='#1E293B', alpha=0.7, markersize=5))

box_colors = ["#D1FAE5", "#DBEAFE", "#FEE2E2", "#FEF3C7"]
for patch, color in zip(bp['boxes'], box_colors):
    patch.set_facecolor(color)
    patch.set_edgecolor("#334155")
    patch.set_linewidth(1.0)

# Annotate the extreme outliers explicitly
# FedAvg max outlier: 0.2599 at BHMBRCBRG01
plt.annotate("Outlier: 0.2599\n(BHMBRCBRG01)", xy=(3, 0.2599), xytext=(3.25, 0.24),
             arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.2), fontsize=8, fontweight="bold", color="#991B1B")

# Personalized max outlier for BHMBRCBRG01: 0.1240, NIA North: 0.1268
plt.annotate("Reduced: 0.1240\n(52.3% drop)", xy=(4, 0.1240), xytext=(4.22, 0.15),
             arrowprops=dict(arrowstyle="->", color="#D97706", lw=1.2), fontsize=8, fontweight="bold", color="#B45309")

plt.ylabel("Test MAE across 30 Individual Parking Facilities", fontsize=10.5, fontweight="bold", labelpad=8)
plt.title("Inter-Lot Error Distribution & Variance Reduction across 30 Facilities", fontsize=11.5, fontweight="bold", pad=12)
plt.tight_layout()
plt.savefig("results/fig2_personalization_distribution_boxplot.png", dpi=300)
plt.close()

# ==================== FIG 3: CONVERGENCE TRAJECTORY ====================
rounds_loss = [
    (1, 0.0894), (2, 0.0541), (3, 0.0382), (4, 0.0275),
    (5, 0.0211), (6, 0.0169), (7, 0.0142), (8, 0.0128)
]
r_x, r_y = zip(*rounds_loss)

plt.figure(figsize=(7.5, 4.5), dpi=300)
plt.plot(r_x, r_y, marker='o', linewidth=2.2, color='#1E3A8A', label="Federated Global Train MSE")
plt.axhline(y=0.0042, color='#059669', linestyle='--', linewidth=1.8, label="Centralized Baseline MSE (30 Epochs)")
plt.xlabel("Communication Round ($r$)", fontsize=10.5, fontweight="bold", labelpad=8)
plt.ylabel("Global Aggregation Loss (MSE)", fontsize=10.5, fontweight="bold", labelpad=8)
plt.title("Global Federated Aggregation Convergence Curve (Rounds 1–8)", fontsize=11, fontweight="bold", pad=10)
plt.xticks(range(1, 9))
plt.legend(frameon=True, fontsize=9.5)
plt.tight_layout()
plt.savefig("results/fig3_convergence_trajectory.png", dpi=300)
plt.close()

# ==================== FIG 4: 30-CLIENT ROUND SCALING ====================
df_rounds = pd.read_csv("results/round_scaling_30clients.csv")
plt.figure(figsize=(8, 4.8), dpi=300)
plt.plot(df_rounds["Rounds"], df_rounds["Pooled Test MAE"], marker='o', linewidth=2.5, color='#1E3A8A', label="Pooled Test MAE ($B=64$)")
plt.plot(df_rounds["Rounds"], df_rounds["Macro Mean MAE"], marker='s', linewidth=2.2, color='#2563EB', linestyle='--', label="Macro Mean MAE ($B=64$)")

plt.axhline(y=0.0607, color='#059669', linestyle=':', linewidth=2, label="Personalized FedAvg ($R=8, B=32$: 0.0607)")
plt.annotate("Diminishing returns region\n(R=12-16: MAE ~0.098-0.100)", xy=(14, 0.099), xytext=(8.5, 0.145),
             arrowprops=dict(arrowstyle="->", color="#1E293B", lw=1.5), fontsize=8.5, fontweight="bold")

plt.xlabel("Communication Rounds Across All 30 Clients", fontsize=10.5, fontweight="bold", labelpad=8)
plt.ylabel("Test MAE ($y_{30}$ Availability Ratio)", fontsize=10.5, fontweight="bold", labelpad=8)
plt.title("Controlled Round Scaling on 30 Clients: Convergence & Diminishing Returns", fontsize=11, fontweight="bold", pad=12)
plt.xticks(df_rounds["Rounds"])
plt.legend(frameon=True, fontsize=9.5)
plt.tight_layout()
plt.savefig("results/fig4_round_scaling_30clients.png", dpi=300)
plt.close()

print("Regenerated all publication figures with reconciled baselines successfully!")
