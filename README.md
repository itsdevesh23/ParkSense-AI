# ParkSense AI: Federated Multi-Lot Smart Parking Forecasting

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dataset: UCI Birmingham](https://img.shields.io/badge/DOI-10.24432%2FC51K5Z-green.svg)](https://doi.org/10.24432/C51K5Z)

Official implementation and empirical benchmark code for the research paper:  
**"When Does Federation Help Multi-Lot Smart Parking Forecasting? An Empirical Benchmark on the Birmingham IoT Stream"**  
*Devesh Munagala and Abhinav* — *Department of Computer Science and Engineering, Vellore Institute of Technology, India.*

---

## 📌 Overview

**ParkSense AI** evaluates the practical trade-offs between centralized deep learning, decentralized local analytics, and federated learning paradigms for multi-lot municipal smart parking forecasting.

Using 35,717 sensor observations from 30 municipal parking facilities in Birmingham, UK (UCI Machine Learning Repository, DOI: [10.24432/C51K5Z](https://doi.org/10.24432/C51K5Z)), we construct a rigorous chronological benchmark across 3,263 unified test sequence windows (with embargo purge gaps at partition boundaries), forecasting availability ratios at both **30-minute (`y_30`)** and **60-minute (`y_60`)** lookahead horizons.

### 🔑 Key Findings

1. **Dominance of Local Linear Baselines:** A 5-parameter local-only linear AR(4) model per facility (4 lag weights + intercept) achieves a 30-minute MAE of **0.0126** ($\sim 13.9$ bays), outperforming centralized Attention-LSTM (**0.0217**; $26.9$ bays) and standard FedAvg (**0.1006**; $126.8$ bays) while requiring **zero communication** and maintaining complete data containment without cross-facility telemetry pooling.
2. **Compute Starvation vs. Non-IID Drift:** Under standard federated budgets ($R=8$ rounds, $E=2$ epochs), each client executes barely 256 gradient updates ($\sim 1.78\%$ of centralized compute, which executes 14,370 Adam gradient steps). An IID-shuffled control experiment indicates that non-IID spatial drift accounts for 35.8% of the initial gap under communication-constrained budgets (R=8), while the remaining 64.2% residual deficit reflects optimization under-training; under matched compute parity (R=15, ~14,790 gradient steps), non-IID heterogeneity accounts for 73.9% of the deficit as compute starvation is mitigated under strict round budgets.
3. **Personalization Gap Recovery:** Post-aggregation local fine-tuning (**Personalized FedAvg**) cuts FedAvg error by **36.7%** (MAE: $0.0592 \pm 0.0004$), recovering **47.8%** of the performance gap toward centralized models in multi-seed evaluations (and **50.6%** in the primary single-seed benchmark, MAE: 0.0607).
4. **Refuting the Bandwidth Myth:** Federated neural modeling transmits **110.35 MB** (105.24 MiB across 8 rounds) across 30 clients—**74.6× larger** than streaming raw telemetry (1.48 MB / 1.41 MiB). FL is justified by institutional data sovereignty and multi-stakeholder commercial confidentiality, not edge uplink bandwidth savings.

---

## 📊 Benchmark Results

### Primary Multi-Horizon Benchmark (Seed 42, 3,263 Purged Test Windows)

*Exported directly from verified code execution (`results/benchmark_30min_y30.csv`, `results/benchmark_60min_y60.csv`, and `results/reconciled_benchmark_table.csv`).*

| Horizon | Forecasting Model | Pooled MAE (Micro) | Pooled RMSE | Macro MAE | Between-Lot Std ($\sigma$) | Space Error (Bays) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **30-Min Ahead (`y_30`)** | **Local Linear AR(4) (Local isolation)** | **0.0126** | **0.0179** | **0.0125** | **0.0049** | **13.9** |
| | Pooled Linear AR(4) (Centralized) | 0.0129 | 0.0189 | 0.0130 | 0.0049 | 14.7 |
| | Centralized XGBoost | 0.0145 | 0.0201 | 0.0152 | 0.0057 | 17.5 |
| | Centralized Attention-LSTM | 0.0217 | 0.0285 | 0.0230 | 0.0109 | 26.9 |
| | Centralized Standard LSTM | 0.0218 | 0.0300 | 0.0232 | 0.0129 | 25.2 |
| | Persistence (Naive) | 0.0256 | 0.0386 | 0.0249 | 0.0134 | 33.4 |
| | **Personalized FedAvg (Local Adaptation)** | **0.0607** | **0.0818** | **0.0627** | **0.0279** | **73.2** |
| | Global FedAvg ($R=8, B=32$) | 0.1006 | 0.1309 | 0.1030 | 0.0534 | 126.8 |
| **60-Min Ahead (`y_60`)** | Centralized XGBoost | **0.0245** | **0.0343** | **0.0264** | **0.0112** | **30.1** |
| | **Local Linear AR(4) (Local isolation)** | 0.0248 | 0.0350 | 0.0243 | 0.0094 | 28.4 |
| | Pooled Linear AR(4) (Centralized) | 0.0259 | 0.0375 | 0.0266 | 0.0095 | 30.4 |
| | Centralized Standard LSTM | 0.0291 | 0.0402 | 0.0305 | 0.0117 | 35.5 |
| | Centralized Attention-LSTM | 0.0304 | 0.0415 | 0.0316 | 0.0118 | 37.2 |
| | Persistence (Naive) | 0.0492 | 0.0715 | 0.0477 | 0.0250 | 64.2 |
| | **Personalized FedAvg (Local Adaptation)** | **0.0732** | **0.0962** | **0.0750** | **0.0263** | **92.3** |
| | Global FedAvg ($R=8, B=32$) | 0.1078 | 0.1416 | 0.1106 | 0.0552 | 137.1 |

### Multi-Seed Federated Learning Evaluation (Seeds: 42, 101, 2024)

*Exported directly from `results/advanced_fl_experiments.csv` across 3 random seeds on the 30 parking facilities.*

| Federated Paradigm / Algorithm | Pooled MAE (Micro) | Pooled RMSE | Macro Mean MAE | Between-Lot Std ($\sigma$) |
| :--- | :---: | :---: | :---: | :---: |
| Global FedAvg ($R=8, E=2, B=32$) | $0.0935 \pm 0.0032$ | $0.1230 \pm 0.0030$ | $0.0963 \pm 0.0029$ | $0.0498 \pm 0.0013$ |
| IID-Shuffled FedAvg Control | $0.0678 \pm 0.0019$ | $0.0956 \pm 0.0023$ | $0.0711 \pm 0.0019$ | $0.0361 \pm 0.0012$ |
| FedProx ($\mu = 0.01$) | $0.1305 \pm 0.0162$ | $0.1607 \pm 0.0157$ | $0.1333 \pm 0.0169$ | $0.0573 \pm 0.0040$ |
| FedPer (Shared Base, Private Head) | $0.0775 \pm 0.0012$ | $0.1056 \pm 0.0007$ | $0.0798 \pm 0.0009$ | $0.0379 \pm 0.0007$ |
| **Personalized FedAvg (Fine-Tuning)** | **$0.0592 \pm 0.0004$** | **$0.0786 \pm 0.0001$** | **$0.0612 \pm 0.0001$** | **$0.0243 \pm 0.0014$** |

### Compute-Parity Federated Benchmark ($R = 15$, ~14,790 Gradient Updates Matching Centralized 30 Epochs)

*Exported directly from `results/compute_parity_experiments.csv` across 3 random seeds {42, 101, 2024}.*

| Regime & Protocol | Federated Algorithm | Pooled MAE (Micro) | Pooled RMSE | Macro Mean MAE | Between-Lot Std ($\sigma$) | Mean Space Error (Bays) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Matched Compute Parity** ($R=15$) | Compute-Parity Global FedAvg ($R=15$) | $0.0858 \pm 0.0015$ | $0.1139 \pm 0.0011$ | $0.0889 \pm 0.0016$ | $0.0465 \pm 0.0007$ | $109.5 \pm 1.8$ |
| | Compute-Parity IID-Shuffled FedAvg | $0.0384 \pm 0.0010$ | $0.0541 \pm 0.0018$ | $0.0405 \pm 0.0010$ | $0.0198 \pm 0.0008$ | $47.5 \pm 1.0$ |
| | **Compute-Parity Personalized FedAvg** | **$0.0548 \pm 0.0012$** | **$0.0741 \pm 0.0022$** | **$0.0565 \pm 0.0015$** | **$0.0222 \pm 0.0022$** | **$67.5 \pm 1.6$** |

---

## 🏗 Implemented Model Architecture

The implemented `AttentionLSTM` backbone in `src/models.py` consists of:
- **Input Dimension:** 4 features ($a_t$, $\sin(2\pi h_t / 24)$, $\cos(2\pi h_t / 24)$, $d_t / 7.0$).
- **Recurrent Backbone:** 2-layer LSTM ($H = 64$), producing hidden sequence $h_1, \dots, h_L$ ($51,200$ parameters).
- **Temporal Attention:** Feedforward alignment network scoring each hidden state $h_t$:
  $$e_t = w_a^T \tanh(W_a h_t + b_a) + b_s, \quad \alpha_t = \frac{\exp(e_t)}{\sum_{\tau=1}^L \exp(e_\tau)}, \quad c = \sum_{t=1}^L \alpha_t h_t$$
  where $W_a \in \mathbb{R}^{32 \times 64}$, $b_a \in \mathbb{R}^{32}$, $w_a \in \mathbb{R}^{32}$, $b_s \in \mathbb{R}$ ($2,113$ parameters).
- **Output MLP Head:** Concatenates context with final hidden state $[c; h_L] \in \mathbb{R}^{128}$ projected via dense layer ($128 \rightarrow 32$), ReLU, Dropout ($p = 0.2$), linear ($32 \rightarrow 1$), and Sigmoid ($4,161$ parameters).
- **Total Trainable Parameters:** Exactly **57,474 float32 weights** ($229,896\text{ bytes} = 224.51\text{ KiB}$).

---

## 📁 Repository Structure

```text
ParkSense-AI/
├── backend/                  # FastAPI inference backend & simulated IoT telemetry stream
│   ├── app/
│   │   ├── main.py           # Application entrypoint & CORS config
│   │   ├── api/routes.py     # API endpoints: /forecast, /stream, /lots, /metrics
│   │   └── core/             # Model loading & stream generator
│   └── requirements.txt      # Backend Python dependencies
├── data/                     # Birmingham parking dataset and regularized series
│   ├── dataset.csv           # Raw UCI Birmingham parking data (35,717 rows, 30 lots)
│   └── processed/            # Chronologically partitioned train/val/test matrices (with purge gap)
├── frontend/                 # Interactive full-stack web dashboard (React + TypeScript)
│   ├── src/
│   │   ├── components/       # Metric cards, forecast charts, lot cards, map views
│   │   ├── pages/            # Role-based views: Driver, Operator, Admin
│   │   └── App.tsx           # Dashboard routing and state management
│   ├── package.json
│   └── vite.config.ts
├── models/                   # Saved PyTorch model weights (.pt)
│   ├── centralized_att_lstm_30.pt
│   ├── centralized_att_lstm_60.pt
│   ├── centralized_lstm_30.pt
│   ├── centralized_lstm_60.pt
│   ├── fedavg_att_lstm_30min.pt
│   ├── fedavg_att_lstm_60min.pt
│   └── personalized/         # Per-facility adapted checkpoints
├── results/                  # Benchmark CSVs, multi-seed evaluation logs & publication figures
│   ├── benchmark_30min_y30.csv
│   ├── benchmark_60min_y60.csv
│   ├── reconciled_benchmark_table.csv
│   ├── advanced_fl_experiments.csv
│   ├── fig_architecture.png
│   ├── fig1_model_comparison_grouped.png
│   ├── fig2_personalization_distribution_boxplot.png
│   ├── fig3_convergence_trajectory.png
│   └── fig4_round_scaling_30clients.png
├── scripts/                  # Standalone benchmark execution & verification scripts
│   ├── reconcile_full_benchmark.py
│   └── plot_all_figures.py
├── src/                      # Core modeling library
│   ├── models.py             # Attention-LSTM (4-feat), Standard LSTM, MLP architectures
│   ├── federated_trainer.py  # FedAvg, FedProx, FedPer, and personalization routines
│   └── preprocessing.py      # Day bounding, session regularization & sequence windowing (with purge gap)
├── build_journal_manuscript.py  # Automated manuscript builder script
├── Journal_Manuscript_Final_Submission.docx # Complete submission-ready manuscript
└── README.md
```

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/itsdevesh23/ParkSense-AI.git
cd ParkSense-AI
```

### 2. Python Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install numpy pandas scikit-learn statsmodels xgboost matplotlib seaborn fastapi uvicorn python-docx
```

### 3. Reproduce Empirical Benchmarks
```bash
# Run Phase 1 Preprocessing (creates train/val/test with embargo purge gaps)
python -c "from src.preprocessing import run_phase1_pipeline; run_phase1_pipeline()"

# Run Master Reconciled Benchmark across all models (N=3,263)
python scripts/reconcile_full_benchmark.py

# Regenerate all publication figures
python scripts/plot_all_figures.py
```

### 4. Launch the ParkSense AI Web Dashboard
To launch both the FastAPI backend and React frontend simultaneously:
```bash
# Run the automated launch script (Windows)
.\run_parksense.bat

# Or run services individually:
# Backend:
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend:
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser to view the interactive dashboard.

---

## 📜 Citation

If you use ParkSense AI or reference our empirical benchmark in your research, please cite:

```bibtex
@article{munagala2026parksense,
  title={When Does Federation Help Multi-Lot Smart Parking Forecasting? An Empirical Benchmark on the Birmingham IoT Stream},
  author={Munagala, Devesh and Abhinav},
  journal={arXiv preprint},
  year={2026},
  publisher={Vellore Institute of Technology},
  url={https://github.com/itsdevesh23/ParkSense-AI}
}
```

---

## 📄 License

This repository is distributed under the [MIT License](LICENSE).
