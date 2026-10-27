# TECHNICAL RECONCILIATION & AUDIT MEMORANDUM (FROZEN FOR REVIEW 2)
**Project Title:** Federated Multi-Lot Smart Parking Forecasting Using Attention-Based LSTM on IoT Streams  
**Team Identity:** Team 4: Devesh Munagala (23BCT0149) & Abhinav (23BCT0142)  
**Evaluation Stage:** Review 2 Technical Audit & Multi-Horizon Benchmark Validation  
**Date:** October 13, 2026  

---

## 1. Executive Summary

This memorandum formally records the finalized, reproducible benchmarking results across all 30 municipal parking facilities in the Birmingham testbed. All six forecasting models have been executed across the **exact same 3,293 chronological test observations** ($N = 3,293$) across both the 30-minute (`y30`) and 60-minute (`y60`) forecast horizons.

All reported metrics are exported directly from code execution variables (`scripts/reconcile_full_benchmark.py`) into version-controlled CSV files:
* [benchmark_30min_y30.csv](file:///c:/Users/deves/OneDrive/Documents/Design%20of%20smart%20cities/results/benchmark_30min_y30.csv)
* [benchmark_60min_y60.csv](file:///c:/Users/deves/OneDrive/Documents/Design%20of%20smart%20cities/results/benchmark_60min_y60.csv)

---

## 2. Experimental Rigor & Methodological Safeguards

### 2.1 Full-Sample Evaluation Parity Across All Six Models
* **Test Dataset Identity:** Bit-for-bit array equality between the concatenated client test partitions and the global test partition was verified:
  $$\max |\mathbf{X}_{\text{concat}} - \mathbf{X}_{\text{global}}| = \mathbf{0.0 \times 10^0}, \quad \max |\mathbf{y}_{\text{concat}} - \mathbf{y}_{\text{global}}| = \mathbf{0.0 \times 10^0}$$
* Every model was evaluated over the exact same 3,293 test instances in identical chronological order.

### 2.2 Strict ARIMA Convergence Safeguard
In `scripts/reconcile_full_benchmark.py`, the ARIMA(2, 1, 1) evaluator explicitly checks for optimization convergence and warnings using `ConvergenceWarning` from `statsmodels.tools.sm_exceptions`:

```python
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    result = ARIMA(series, order=(2, 1, 1)).fit()

converged = getattr(result, "mle_retvals", {}).get("converged", True)
convergence_warning = any(issubclass(w.category, ConvergenceWarning) for w in caught)

if not converged or convergence_warning:
    return last_value, last_value
```

* **Effect of Convergence Fallback:** Whenever an individual 6-point sliding window issues a `ConvergenceWarning` or fails to invert, the model gracefully falls back to the persistent last known value ($y_t$), and forecasts are strictly bounded to $[0, 1]$.
* **Benchmarking Against Pure Naive Persistence ($\hat{y}_{t+h} = y_t$):**
  * **30-Min Horizon (`y30`):** Naive Persistence MAE = **$0.0257$** vs. ARIMA MAE = **$0.0213$** (a **$17.1\%$ improvement** over persistence).
  * **60-Min Horizon (`y60`):** Naive Persistence MAE = **$0.0494$** vs. ARIMA MAE = **$0.0424$** (a **$14.2\%$ improvement** over persistence).

### 2.3 Reconciling FedAvg Configurations (8 Communication Rounds)
* **Configuration 1 (Primary Benchmark):** `batch_size = 32`, standard pipeline initialization $\rightarrow$ Pooled MAE = **$0.1007$**, Macro MAE = **$0.1029$**.
* **Configuration 2 (Round Scaling Study):** `batch_size = 64`, explicit seeds (`seed = 42`) $\rightarrow$ Pooled MAE at Round 8 = **$0.1144$**, Macro MAE = **$0.1170$**.
* The difference reflects different local update volumes per round ($\approx 18$ updates/client/round at batch size 32 versus $\approx 10$ at batch size 64 for a representative 280-sample client), and is documented as distinct experimental configurations. Configuration 1 is frozen as the primary Global FedAvg baseline.

### 2.4 Resampled Intraday Grid (18 Timestamps per Day)
* Daily operating hours span $08:00$ to $16:30$ at 30-min intervals, generating exactly **18 discrete timestamps per day**.
* Constraining sliding sequences strictly within individual calendar days yields **11 valid sliding windows per day for $T_{\text{in}} = 6$** versus **5 valid windows for $T_{\text{in}} = 12$** (a **$+120\%$ sample yield increase**).
* The 6-step lookback spans **2.5 hours of elapsed time** ($t-5$ to $t$) and covers a **nominal 3-hour history window** of six 30-minute observation bins.

---

## 3. Frozen Multi-Horizon Benchmark Tables (Full Test Set $N = 3,293$)

> **Unit Definition:**  
> All MAE, RMSE, and $\sigma$ values represent errors in the capacity-normalized availability ratio ($y_t \in [0, 1]$). Physical operational errors are reported explicitly in vacant parking bays.

### Table 1: Model Comparison — 30-Minute-Ahead Forecasting (`y30`)
*Exported directly to [benchmark_30min_y30.csv](file:///c:/Users/deves/OneDrive/Documents/Design%20of%20smart%20cities/results/benchmark_30min_y30.csv).*

| Model Tier | Model Architecture | Pooled MAE (Micro, Ratio) | Pooled RMSE (Ratio) | Macro Mean MAE (Ratio) | Between-Lot Std ($\sigma$) | Mean Space Error (Bays) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Tier 1: Statistical** | ARIMA(2, 1, 1) | 0.0213 | 0.0320 | 0.0210 | 0.0096 | 26.4 |
| **Tier 2: ML Baseline** | XGBoost Regressor | **0.0145** | **0.0202** | **0.0154** | **0.0063** | **17.6** |
| **Tier 3: Deep Centralized** | Centralized Standard LSTM | 0.0218 | 0.0300 | 0.0232 | 0.0129 | 25.2 |
| **Tier 3: Deep Centralized** | Centralized Attention-LSTM | 0.0217 | 0.0285 | 0.0231 | 0.0108 | 27.0 |
| **Tier 4: Distributed FL** | Global FedAvg ($R=8$) | 0.1007 | 0.1313 | 0.1029 | 0.0531 | 127.1 |
| **Tier 4: Distributed FL** | **Personalized FedAvg (Ours)** | **0.0607** | **0.0818** | **0.0627** | **0.0276** | **73.1** |

*30-Minute Personalization Gains:*
* **Pooled MAE Reduction:** $\frac{0.1007 - 0.0607}{0.1007} = \mathbf{39.7\%}$
* **Macro Mean MAE Reduction:** $\frac{0.1029 - 0.0627}{0.1029} = \mathbf{39.1\%}$
* **Between-Lot Error Variability Reduction ($\sigma$):** $\frac{0.0531 - 0.0276}{0.0531} = \mathbf{48.0\%}$
* **Physical Space Error Reduction:** $\frac{127.1 - 73.1}{127.1} = \mathbf{42.5\%}$ (saving an average of $54.0$ bays per forecast)

---

### Table 2: Model Comparison — 60-Minute-Ahead Forecasting (`y60`)
*Exported directly to [benchmark_60min_y60.csv](file:///c:/Users/deves/OneDrive/Documents/Design%20of%20smart%20cities/results/benchmark_60min_y60.csv).*

| Model Tier | Model Architecture | Pooled MAE (Micro, Ratio) | Pooled RMSE (Ratio) | Macro Mean MAE (Ratio) | Between-Lot Std ($\sigma$) | Mean Space Error (Bays) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Tier 1: Statistical** | ARIMA(2, 1, 1) | 0.0424 | 0.0613 | 0.0416 | 0.0186 | 53.5 |
| **Tier 2: ML Baseline** | XGBoost Regressor | **0.0245** | **0.0343** | **0.0262** | **0.0106** | **30.0** |
| **Tier 3: Deep Centralized** | Centralized Standard LSTM | 0.0291 | 0.0402 | 0.0308 | 0.0124 | 35.6 |
| **Tier 3: Deep Centralized** | Centralized Attention-LSTM | 0.0304 | 0.0415 | 0.0318 | 0.0122 | 37.2 |
| **Tier 4: Distributed FL** | Global FedAvg ($R=8$) | 0.1079 | 0.1418 | 0.1105 | 0.0549 | 137.5 |
| **Tier 4: Distributed FL** | **Personalized FedAvg (Ours)** | **0.0717** | **0.0943** | **0.0747** | **0.0277** | **90.0** |

*60-Minute Personalization Gains:*
* **Pooled MAE Reduction:** $\frac{0.1079 - 0.0717}{0.1079} = \mathbf{33.5\%}$
* **Macro Mean MAE Reduction:** $\frac{0.1105 - 0.0747}{0.1105} = \mathbf{32.4\%}$
* **Between-Lot Error Variability Reduction ($\sigma$):** $\frac{0.0549 - 0.0277}{0.0549} = \mathbf{49.5\%}$
* **Physical Space Error Reduction:** $\frac{137.5 - 90.0}{137.5} = \mathbf{34.5\%}$ (saving an average of $47.5$ bays per forecast)

---

## 4. Evidence-Based Research Findings

1. **Centralized Baseline Superiority:**  
   XGBoost Regressor achieves the strongest centralized results at both horizons ($0.0145$ at 30m; $0.0245$ at 60m), outperforming centralized deep neural networks.
2. **Consistent Personalization Benefit Across Horizons:**  
   Personalized fine-tuning reduces error relative to standard FedAvg across both horizons ($39.7\%$ pooled MAE reduction at 30m; $33.5\%$ reduction at 60m) while cutting between-lot error variability ($\sigma$) by approximately half ($48.0\%$ at 30m; $49.5\%$ at 60m).
3. **Diminishing Returns from Communication Rounds:**  
   The 30-client round-scaling study ($0.2062 \rightarrow 0.1144 \rightarrow 0.1006 \rightarrow 0.0978$) demonstrates diminishing returns as communication rounds increase under heterogeneous client data.
4. **Accuracy Gap Under Simulated Federated Learning:**  
   Even with personalization, federated models ($0.0607$ at 30m; $0.0717$ at 60m) exhibit an accuracy gap compared with centralized benchmarks ($0.0145$–$0.0218$ at 30m; $0.0245$–$0.0304$ at 60m). This is documented as an empirical accuracy gap under the current simulated federated setup, rather than claiming a quantified privacy–accuracy trade-off.
5. **Data Locality Scope:**  
   The architecture maintains raw-data locality on simulated edge nodes during training, providing practical architectural data containment rather than a formal mathematical differential privacy guarantee.

---

## 5. Official Faculty Presentation Script (Review 2 Guide Update)

> *"Madam, we have developed a six-model benchmarking pipeline for parking availability forecasting across 30 parking facilities using the Birmingham dataset. We are evaluating 30-minute and 60-minute prediction horizons across the exact same 3,293 test observations.*
>
> *In the current results, XGBoost provides the strongest centralized benchmark, with pooled MAE values of 0.0145 at 30 minutes and 0.0245 at 60 minutes.*
>
> *Personalized FedAvg improves upon standard FedAvg, reducing pooled MAE by 39.7% at 30 minutes (0.1007 to 0.0607) and 33.5% at 60 minutes (0.1079 to 0.0717) compared with standard FedAvg, while cutting cross-lot error variability across facilities by approximately half.*
>
> *We have also conducted a communication-round scaling study, analyzed prediction errors across parking facilities, verified ARIMA convergence safeguards with persistence fallbacks, and documented the remaining accuracy gap between centralized and federated learning under non-IID conditions. We are now freezing these benchmark files and synchronizing the final report and presentation slides."*
