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

Using 35,717 sensor observations from 30 municipal parking facilities in Birmingham, UK (UCI Machine Learning Repository, DOI: [10.24432/C51K5Z](https://doi.org/10.24432/C51K5Z)), we construct a rigorous chronological benchmark across 3,293 unified test windows, forecasting availability ratios at both **30-minute (`y_30`)** and **60-minute (`y_60`)** lookahead horizons.

### 🔑 Key Findings

1. **Dominance of Local Linear Baselines:** A 4-parameter local-only linear AR model per facility achieves a 30-minute MAE of **0.0126** ($\sim 14.5$ bays), outperforming centralized Attention-LSTM (**0.0217**; $27.0$ bays) and standard FedAvg (**0.1007**; $130.6$ bays) while requiring **zero communication** and providing complete data privacy.
2. **Compute Starvation vs. Non-IID Drift:** Under standard federated budgets ($R=8$ rounds, $E=2$ epochs), each client executes barely 256 gradient updates ($\sim 1.78\%$ of centralized compute). An IID-shuffled control experiment proves that compute starvation accounts for **64.2%** of FedAvg's performance deficit, while non-IID drift contributes 35.8%.
3. **Personalization Gap Recovery:** Post-aggregation local fine-tuning (**Personalized FedAvg**) cuts FedAvg error by **36.7%** (MAE: $0.0592 \pm 0.0004$), recovering **47.8%** of the performance gap toward centralized models in multi-seed evaluations (and **50.6%** in the primary single-seed benchmark).
4. **Refuting the Bandwidth Myth:** Federated neural modeling transmits **110.35 MB** (105.24 MiB across 8 rounds) across 30 clients—**74.6× larger** than streaming raw telemetry (1.48 MB / 1.41 MiB). FL is justified by institutional data sovereignty and GDPR compliance, not edge uplink bandwidth savings.

---

## 📊 Benchmark Results

### Primary Multi-Horizon Benchmark (Seed 42, 3,293 Test Windows)

| Horizon | Forecasting Model | Pooled MAE (Micro) | Pooled RMSE | Macro MAE | Space Error (Macro Bays) | Space Error (Micro Bays) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **30-Min Ahead (`y_30`)** | Local Linear AR(4) | **0.0126** | **0.0270** | **0.0132** | **14.5** | **17.6** |
| | Centralized XGBoost | 0.0145 | 0.0276 | 0.0149 | 17.5 | 20.3 |
| | Centralized Attention-LSTM | 0.0217 | 0.0384 | 0.0215 | 27.0 | 30.3 |
| | Centralized Standard LSTM | 0.0218 | 0.0385 | 0.0216 | 27.2 | 30.5 |
| | Persistence (Naive) | 0.0257 | 0.0468 | 0.0274 | 33.3 | 35.9 |
| | Pooled Global Linear | 0.0483 | 0.0699 | 0.0519 | 63.6 | 67.5 |
| | **Personalized FedAvg** | **0.0607** | **0.0886** | **0.0577** | **73.1** | **75.0** |
| | Global FedAvg | 0.1007 | 0.1343 | 0.0991 | 127.1 | 130.6 |
| **60-Min Ahead (`y_60`)** | Centralized XGBoost | **0.0245** | **0.0427** | **0.0250** | **29.7** | **34.2** |
| | Local Linear AR(4) | 0.0261 | 0.0480 | 0.0273 | 30.6 | 36.4 |
| | Centralized Standard LSTM | 0.0291 | 0.0483 | 0.0289 | 36.5 | 40.7 |
| | Centralized Attention-LSTM | 0.0304 | 0.0494 | 0.0300 | 37.8 | 42.4 |
| | Persistence (Naive) | 0.0494 | 0.0818 | 0.0527 | 64.3 | 69.0 |
| | Pooled Global Linear | 0.0571 | 0.0817 | 0.0617 | 75.9 | 79.8 |
| | **Personalized FedAvg** | **0.0717** | **0.1017** | **0.0683** | **86.4** | **88.6** |
| | Global FedAvg | 0.1079 | 0.1417 | 0.1070 | 137.4 | 140.7 |

### Multi-Seed Federated Learning Evaluation (Seeds: 42, 101, 2024)

| Federated Paradigm / Algorithm | Pooled MAE (Micro) | Pooled RMSE | Macro Mean MAE | Space Error (Macro Bays) |
| :--- | :---: | :---: | :---: | :---: |
| Centralized Attention-LSTM Benchmark | $0.0217 \pm 0.0001$ | $0.0384 \pm 0.0001$ | $0.0215 \pm 0.0001$ | $27.0 \pm 0.1$ |
| IID-Shuffled Federated Control | $0.0678 \pm 0.0019$ | $0.0963 \pm 0.0022$ | $0.0649 \pm 0.0019$ | $82.4 \pm 2.4$ |
| FedProx ($\mu = 0.01$) | $0.1305 \pm 0.0162$ | $0.1656 \pm 0.0167$ | $0.1293 \pm 0.0160$ | $166.4 \pm 20.6$ |
| Global FedAvg ($R = 8, E = 2$) | $0.0935 \pm 0.0020$ | $0.1264 \pm 0.0022$ | $0.0924 \pm 0.0020$ | $118.5 \pm 2.6$ |
| FedPer (Local MLP Head) | $0.0775 \pm 0.0012$ | $0.1082 \pm 0.0014$ | $0.0754 \pm 0.0012$ | $96.5 \pm 1.5$ |
| **Personalized FedAvg (Fine-Tuning)** | **$0.0592 \pm 0.0004$** | **$0.0864 \pm 0.0005$** | **$0.0563 \pm 0.0004$** | **$82.4 \pm 0.4$** |

---

## 🏗 Repository Structure

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
│   └── processed/            # Chronologically partitioned train/val/test matrices
├── frontend/                 # Interactive full-stack web dashboard (React + TypeScript)
│   ├── src/
│   │   ├── components/       # Metric cards, forecast charts, lot cards, map views
│   │   ├── pages/            # Role-based views: Driver, Operator, Admin
│   │   └── App.tsx           # Dashboard routing and state management
│   ├── package.json
│   └── vite.config.ts
├── models/                   # Saved PyTorch model weights (.pt)
│   ├── centralized_attention_lstm.pt
│   ├── global_fedavg.pt
│   └── personalized_fedavg/  # Per-facility adapted checkpoints
├── results/                  # Benchmark CSVs, multi-seed evaluation logs & figures
│   ├── benchmark_y30_primary.csv
│   ├── benchmark_y60_primary.csv
│   ├── federated_multiseed_comparison.csv
│   ├── fig_architecture.png
│   ├── fig_benchmark_comparison.png
│   └── fig_lot_performance_distribution.png
├── scripts/                  # Standalone benchmark execution & verification scripts
│   ├── reconcile_full_benchmark.py
│   ├── run_advanced_fl_experiments.py
│   └── plot_all_figures.py
├── src/                      # Core modeling library
│   ├── models.py             # Attention-LSTM, Standard LSTM, MLP architectures
│   ├── federated.py          # FedAvg, FedProx, FedPer, and personalization routines
│   ├── baselines.py          # Local linear, pooled linear, persistence, ARIMA
│   └── preprocessing.py      # Day bounding, session regularization & sequence windowing
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
# Run full 8-model benchmark across 30 and 60-minute horizons
python scripts/reconcile_full_benchmark.py

# Run advanced federated learning experiments (IID Control, FedProx, FedPer, Multi-seed)
python run_advanced_fl_experiments.py

# Generate all manuscript figures
python scripts/plot_all_figures.py
```

### 4. Launch the ParkSense AI Web Dashboard
To launch both the FastAPI backend and React frontend simultaneously:
```bash
# Run the automated launch script (Windows)
.\run_parksense.bat

# Or run services individually:
# Backend:
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

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
