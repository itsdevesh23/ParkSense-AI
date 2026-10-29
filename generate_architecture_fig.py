import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up figure
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis('off')

# Background color
fig.patch.set_facecolor('#ffffff')

# Colors
c_cloud = '#1E3A8A'    # Deep Blue
c_client = '#0F766E'   # Teal
c_server = '#4338CA'   # Indigo
c_box_bg = '#F8FAFC'   # Slate 50
c_border = '#CBD5E1'   # Slate 300
c_accent = '#D97706'   # Amber

# Main Container Box: Federated Coordinator (Cloud / Central Server)
rect_server = patches.FancyBboxPatch((3.5, 4.4), 5.0, 2.2, boxstyle="round,pad=0.2",
                                     edgecolor=c_server, facecolor='#EEF2FF', linewidth=1.5)
ax.add_patch(rect_server)
ax.text(6.0, 6.2, "CENTRAL FEDERATED COORDINATOR (PARAMETER SERVER)", 
        fontsize=10.5, fontweight='bold', color=c_server, ha='center')

# Parameter Aggregation Box inside Server
rect_agg = patches.FancyBboxPatch((3.9, 4.7), 4.2, 1.2, boxstyle="round,pad=0.1",
                                  edgecolor=c_border, facecolor='#FFFFFF', linewidth=1.2)
ax.add_patch(rect_agg)
ax.text(6.0, 5.55, "Synchronous FedAvg Aggregation Algorithm", fontsize=9.5, fontweight='bold', color='#1E293B', ha='center')
ax.text(6.0, 5.15, r"$w_{r+1} = \sum_{k=1}^{K} \frac{n_k}{n} w_{r+1}^{(k)}$", fontsize=11, color='#1E293B', ha='center')
ax.text(6.0, 4.85, "Zero Raw Data Transmission • Aggregates Model Weights Only", fontsize=8, fontstyle='italic', color='#64748B', ha='center')

# Clients Box: 3 Representational Clients out of 30
client_data = [
    {"name": "Client 1 (BHMEURBRD02)", "x": 0.5, "cap": "Cap: 220 bays (Min)", "samples": "~1,190 readings"},
    {"name": "Client k (Bull Ring)", "x": 4.5, "cap": "Cap: 3,053 bays (Major)", "samples": "~1,190 readings"},
    {"name": "Client 30 (Others-CCCPS133)", "x": 8.5, "cap": "Cap: 4,675 bays (Max)", "samples": "~1,190 readings"}
]

for c in client_data:
    cx = c["x"]
    # Outer Client Container
    rect_c = patches.FancyBboxPatch((cx, 0.4), 3.0, 3.2, boxstyle="round,pad=0.15",
                                    edgecolor=c_client, facecolor='#F0FDF4', linewidth=1.4)
    ax.add_patch(rect_c)
    ax.text(cx + 1.5, 3.35, f"LOCAL PARKING LOT EDGE NODE\n{c['name']}", fontsize=8.5, fontweight='bold', color=c_client, ha='center')
    ax.text(cx + 1.5, 2.95, f"{c['cap']} • {c['samples']}", fontsize=7.5, color='#475569', ha='center')
    
    # IoT Stream Box
    rect_iot = patches.FancyBboxPatch((cx + 0.2, 2.15), 2.6, 0.65, boxstyle="round,pad=0.08",
                                      edgecolor='#86EFAC', facecolor='#FFFFFF', linewidth=1.0)
    ax.add_patch(rect_iot)
    ax.text(cx + 1.3, 2.55, "IoT Occupancy Sensor Stream", fontsize=7.8, fontweight='bold', color='#065F46', ha='center')
    ax.text(cx + 1.3, 2.3, r"$a_t = \frac{C - O_t}{C} \in [0, 1]$ (30m Interval)", fontsize=7.5, color='#047857', ha='center')
    
    # Local Attention-LSTM Model Box
    rect_model = patches.FancyBboxPatch((cx + 0.2, 1.25), 2.6, 0.75, boxstyle="round,pad=0.08",
                                        edgecolor='#6EE7B7', facecolor='#FFFFFF', linewidth=1.0)
    ax.add_patch(rect_model)
    ax.text(cx + 1.3, 1.72, "Temporal Attention-LSTM", fontsize=8, fontweight='bold', color='#065F46', ha='center')
    ax.text(cx + 1.3, 1.50, "2-Layer LSTM (h=64) + Temporal Attention", fontsize=7.2, color='#334155', ha='center')
    ax.text(cx + 1.3, 1.33, r"Lookback $L=6$ steps (3.0 hours)", fontsize=7.2, color='#64748B', ha='center')
    
    # Personalization fine-tuning box
    rect_pers = patches.FancyBboxPatch((cx + 0.2, 0.55), 2.6, 0.55, boxstyle="round,pad=0.08",
                                       edgecolor='#FBBF24', facecolor='#FFFBEB', linewidth=1.0)
    ax.add_patch(rect_pers)
    ax.text(cx + 1.3, 0.88, "Edge Personalization Layer", fontsize=7.5, fontweight='bold', color='#92400E', ha='center')
    ax.text(cx + 1.3, 0.67, "Local Fine-Tuning (3 epochs, lr=0.0003)", fontsize=7.0, color='#B45309', ha='center')

# Connecting Arrows between Server and Clients
# Client 1
ax.annotate("", xy=(2.0, 3.75), xytext=(4.3, 4.4),
            arrowprops=dict(arrowstyle="<->", color=c_server, lw=1.6, ls='--', shrinkA=3, shrinkB=3))
ax.text(2.6, 4.2, "Weights Exchange\n(No Raw Data)", fontsize=7.5, color=c_server, fontweight='bold', ha='center')

# Client k (Center)
ax.annotate("", xy=(6.0, 3.75), xytext=(6.0, 4.4),
            arrowprops=dict(arrowstyle="<->", color=c_server, lw=1.6, ls='--', shrinkA=3, shrinkB=3))
ax.text(6.4, 4.05, "Global Weights\nLocal Gradients", fontsize=7.5, color=c_server, fontweight='bold', ha='left')

# Client 30
ax.annotate("", xy=(10.0, 3.75), xytext=(7.7, 4.4),
            arrowprops=dict(arrowstyle="<->", color=c_server, lw=1.6, ls='--', shrinkA=3, shrinkB=3))
ax.text(9.4, 4.2, "Weights Exchange\n(No Raw Data)", fontsize=7.5, color=c_server, fontweight='bold', ha='center')

plt.tight_layout()
plt.savefig("results/fig_architecture.png", dpi=300, bbox_inches='tight')
print("Architecture figure generated: results/fig_architecture.png")
