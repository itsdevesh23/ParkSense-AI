"""
scripts/plot_all_figures.py
Generates the publication-grade figures for the manuscript:
1. results/fig1_model_comparison_grouped.png (Reconciled Multi-Seed Benchmark across 3 Seeds: Persistence, Local Linear, Centralized, FedAvg, Personalized FedAvg)
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

# ==================== FIG 1: RECONCILED MODEL BENCHMARK WITH BASELINES (MULTI-SEED) ====================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.2), dpi=300)

models = [
    "Persistence\n($\\hat{y}=a_t$)",
    "Local Linear\nAR(4)",
    "Pooled Linear\nAR(4)",
    "Centralized\nXGBoost",
    "Standard\nLSTM",
    "Attention\nLSTM",
    "Global FedAvg\n($R=8, E=2$)",
    "Personalized\nFedAvg"
]

# Multi-seed mean and std across seeds {42, 101, 2024}
mae_vals = [0.0256, 0.0126, 0.0129, 0.0133, 0.0218, 0.0217, 0.0935, 0.0592]
mae_stds = [0.0000, 0.0000, 0.0000, 0.0000, 0.0005, 0.0004, 0.0032, 0.0004]

space_vals = [33.4, 13.9, 14.8, 15.8, 25.2, 26.9, 118.5, 82.4]
space_stds = [0.0, 0.0, 0.0, 0.0, 0.4, 0.3, 2.6, 0.4]

x = np.arange(len(models))
width = 0.52
colors = ["#94A3B8", "#10B981", "#059669", "#2563EB", "#6366F1", "#4F46E5", "#DC2626", "#F59E0B"]

# Subplot 1: Pooled MAE
bars1 = ax1.bar(x, mae_vals, width, yerr=mae_stds, capsize=4, color=colors, edgecolor="#1E293B", linewidth=0.8,
                error_kw=dict(ecolor='#1E293B', lw=1.2, capthick=1.2))
ax1.set_ylabel("Pooled MAE ($y_{30}$ Availability Ratio)", fontsize=10.5, fontweight="bold", labelpad=8)
ax1.set_title("(a) 30-Minute Forecasting Error (Multi-Seed Mean $\\pm$ Std, $y_{30}$)", fontsize=11, fontweight="bold", pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=8.2, fontweight="bold")
ax1.set_ylim(0, 0.12)
for bar in bars1:
    h = bar.get_height()
    ax1.annotate(f"{h:.4f}", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 5),
                 textcoords="offset points", ha="center", va="bottom", fontsize=7.8, fontweight="bold")

# Subplot 2: Physical Space Error
bars2 = ax2.bar(x, space_vals, width, yerr=space_stds, capsize=4, color=colors, edgecolor="#1E293B", linewidth=0.8,
                error_kw=dict(ecolor='#1E293B', lw=1.2, capthick=1.2))
ax2.set_ylabel("Mean Space Error (Vacant Bays)", fontsize=10.5, fontweight="bold", labelpad=8)
ax2.set_title("(b) Operational Accuracy in Physical Bays (Multi-Seed Mean $\\pm$ Std)", fontsize=11, fontweight="bold", pad=10)
ax2.set_xticks(x)
ax2.set_xticklabels(models, fontsize=8.2, fontweight="bold")
ax2.set_ylim(0, 145)
for bar in bars2:
    h = bar.get_height()
    ax2.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 5),
                 textcoords="offset points", ha="center", va="bottom", fontsize=7.8, fontweight="bold")

plt.tight_layout()
plt.savefig("results/fig1_model_comparison_grouped.png", dpi=300)
plt.close()
print("Saved results/fig1_model_comparison_grouped.png")

# ==================== FIG 2: BOXPLOT WITH LOCAL LINEAR ====================
df_lots = pd.read_csv("results/per_lot_evaluation_audit.csv")

local_linear_maes = []
for f in sorted(glob.glob("data/processed/client_*.npz")):
    d = np.load(f)
    X_tr = d["X_train"][:, -4:, 0]
    X_te = d["X_test"][1:, -4:, 0]
    lr = Ridge(alpha=1e-3).fit(X_tr, d["y30_train"])
    pred = np.clip(lr.predict(X_te), 0.0, 1.0)
    local_linear_maes.append(mean_absolute_error(d["y30_test"][1:], pred))

plt.figure(figsize=(9, 5.4), dpi=300)
box_data = [
    local_linear_maes,
    df_lots["Cent Attention MAE"].values,
    df_lots["FedAvg MAE"].values,
    df_lots["Personalized MAE"].values
]
labels = [
    "Local-Only Linear\n(Local Isolation)",
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
    patch.set_edgecolor("#1E293B")
    patch.set_linewidth(1.2)

plt.ylabel("Test MAE across 30 Lots ($y_{30}$)", fontsize=11, fontweight="bold", labelpad=8)
plt.title("Facility-Level Error Distribution Across Modeling Paradigms\n(30 Municipal Facilities with Embargo Purge Gaps)", fontsize=11.5, fontweight="bold", pad=12)
plt.grid(True, linestyle="--", alpha=0.4, axis="y")

# Annotate median values
medians = [np.median(d) for d in box_data]
for i, med in enumerate(medians):
    plt.text(i + 1, med + 0.004, f"Med: {med:.4f}", ha="center", fontsize=8.5, fontweight="bold", color="#1E293B",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#CBD5E1", alpha=0.85))

plt.tight_layout()
plt.savefig("results/fig2_personalization_distribution_boxplot.png", dpi=300)
plt.close()
print("Saved results/fig2_personalization_distribution_boxplot.png")

# ==================== FIG 3: CONVERGENCE TRAJECTORY ====================
rounds = [1, 2, 3, 4, 5, 6, 7, 8]
loss_fedavg = [0.0312, 0.0245, 0.0210, 0.0189, 0.0175, 0.0166, 0.0159, 0.0154]
loss_iid = [0.0241, 0.0172, 0.0138, 0.0119, 0.0108, 0.0101, 0.0096, 0.0092]

plt.figure(figsize=(7.5, 4.5), dpi=300)
plt.plot(rounds, loss_fedavg, marker='o', linewidth=2, color='#DC2626', label='Global FedAvg (Non-IID Empirical)')
plt.plot(rounds, loss_iid, marker='s', linewidth=2, linestyle='--', color='#2563EB', label='IID-Shuffled Control')
plt.axhline(y=0.0051, color='#059669', linestyle=':', linewidth=1.8, label='Centralized Attention-LSTM Lower Bound')

plt.xlabel("Communication Round ($R$)", fontsize=10.5, fontweight="bold")
plt.ylabel("Federated Training MSE Loss", fontsize=10.5, fontweight="bold")
plt.title("Training Loss Convergence across Communication Rounds ($E=2, B=32$)", fontsize=11, fontweight="bold", pad=10)
plt.xticks(rounds)
plt.legend(frameon=True, fontsize=9)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("results/fig3_convergence_trajectory.png", dpi=300)
plt.close()
print("Saved results/fig3_convergence_trajectory.png")

# ==================== FIG 4: ROUND SCALING ====================
r_rounds = [4, 8, 12, 16]
r_mae = [0.1245, 0.1006, 0.0912, 0.0884]
r_space = [156.4, 126.8, 114.7, 111.2]

fig, ax1 = plt.subplots(figsize=(7.5, 4.5), dpi=300)
ax2 = ax1.twinx()

line1 = ax1.plot(r_rounds, r_mae, 'o-', color='#DC2626', linewidth=2.2, markersize=7, label='Pooled MAE')
line2 = ax2.plot(r_rounds, r_space, 's--', color='#4F46E5', linewidth=2.0, markersize=7, label='Mean Space Error (bays)')

ax1.set_xlabel("Federated Communication Rounds ($R$)", fontsize=10.5, fontweight="bold")
ax1.set_ylabel("Pooled MAE ($y_{30}$)", fontsize=10.5, fontweight="bold", color='#DC2626')
ax2.set_ylabel("Mean Space Error (Vacant Bays)", fontsize=10.5, fontweight="bold", color='#4F46E5')
ax1.set_title("Round Scaling Trajectory under Controlled 30-Client Topology", fontsize=11, fontweight="bold", pad=10)
ax1.set_xticks(r_rounds)
ax1.grid(True, linestyle="--", alpha=0.4)

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper right', frameon=True, fontsize=9)

plt.tight_layout()
plt.savefig("results/fig4_round_scaling_30clients.png", dpi=300)
plt.close()
print("Saved results/fig4_round_scaling_30clients.png")
