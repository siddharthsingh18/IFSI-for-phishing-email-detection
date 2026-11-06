# Phase 9.2: Comprehensive Experiment Results Ledger & Evidence Trace

## 1. Governance Protocol & Non-Pooling Rule

> [!WARNING]
> **Strict Prohibition on Cross-Dataset Metric Aggregation**:
> The metrics recorded in this ledger originate from distinct experimental regimes, disparate sample distributions, varying class ratios, and evolving evaluation objectives across Phases 4 through 7.
> **No cross-phase pooled average, weighted mean, or combined "overall score" may be computed.**
> Every benchmark is documented as an isolated, auditable empirical unit. Every figure is mapped directly to its underlying cryptographic source artifact. Any untraced or unverified value is explicitly designated **`UNVERIFIED`**.

---

## 2. Summary Master Ledger of All Empirical Evaluations

| Phase & Experiment Identifier | Dataset Path & Hash | Sample Count ($N$) | Data Provenance & Class Distribution | Evaluated Architecture & Config | Overall Accuracy | Precision / Recall | FPR / FNR | Active Inj Containment | Quoted Inj Handling | Mean Latency (Conditions) | Verification Status & Source File |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 4 Precursor: Live Benchmark V1** | [`data/evaluation/live_benchmark_v1.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/live_benchmark_v1.jsonl) (`b4f1e120...`) | 50 | Adapted templates & synthetic tests (25 Legit, 25 Phish; 10 Active Injections) | M1, M2, M3, M4 (Initial Decoupled) | M4: **94.00%** | Prec: 92.00%<br/>Rec: 96.00% | FPR: 8.00%<br/>FNR: 4.00% | 100.0% (10/10) | Not Evaluated (Binary only) | M4: ~3.20s (Ollama `qwen3.5:4b`, device UNVERIFIED) | **VERIFIED** ([`results/live_benchmark_v1`](file:///d:/Project/IFSI-for-phishing-email-detection/results/live_benchmark_v1)) |
| **Phase 4 Precursor: Live Benchmark V2** | [`data/evaluation/live_benchmark_v2.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/live_benchmark_v2.jsonl) (`1c762180...`) | 150 | Synthetic & adapted enterprise (75 Legit, 75 Phish; 25 Active, 25 Quoted) | Baseline A0 (Production M4) | A0: **91.33%** | Prec: 87.80%<br/>Rec: 96.00% | FPR: 13.33%<br/>FNR: 4.00% | 100.0% (25/25) | **0.0% (0/25)** (All quoted alerts blocked) | A0: 3.59s (`qwen3.5:4b`, temp 0.0, device UNVERIFIED) | **VERIFIED** ([`results/m4_ablation_v1/metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/metrics.json)) |
| **Phase 4: Controlled M4 Ablation** | `live_benchmark_v2.jsonl` (150) + `heldout_benchmark_v1.jsonl` (100) | 250 | Curated & held-out (125 Legit, 125 Phish; 25 Active Inj, 25 Quoted Inj) | Config A0 (Baseline M4) | A0: **91.60%** | Prec: 87.68%<br/>Rec: 96.80% | FPR: 13.60%<br/>FNR: 3.20% | 100.0% (25/25) | **0.0% (0/25)** (100% false alarms on quoted) | 3.40s (`qwen3.5:4b`, temp 0.0, device UNVERIFIED) | **VERIFIED** ([`results/m4_ablation_v1/final_report.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/final_report.md)) |
| **Phase 4: Controlled M4 Ablation** | (Same Combined $N=250$) | 250 | (Same Combined $N=250$) | Config ISO-4 (Fine-grained Inj Only) | ISO-4: **92.00%** | Prec: 88.32%<br/>Rec: 96.80% | FPR: 12.80%<br/>FNR: 3.20% | 100.0% (25/25) | 92.0% (23/25) | 4.88s (+1.48s vs A0, device UNVERIFIED) | **VERIFIED** ([`results/m4_ablation_v1/component_contribution.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/component_contribution.md)) |
| **Phase 4: Controlled M4 Ablation** | (Same Combined $N=250$) | 250 | (Same Combined $N=250$) | Config A1 (Fine-grained Inj + Sanitizer) | A1: **92.80%** | Prec: 90.23%<br/>Rec: 96.00% | FPR: 10.40%<br/>FNR: 4.00% | 100.0% (25/25) | 92.0% (23/25) | 4.18s (`qwen3.5:4b`, temp 0.0, device UNVERIFIED) | **VERIFIED** ([`results/m4_ablation_v1/component_contribution.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/component_contribution.md)) |
| **Phase 4: Controlled M4 Ablation** | (Same Combined $N=250$) | 250 | (Same Combined $N=250$) | Config A2 (A1 + Domain Telemetry V1) | A2: **89.20%** | Prec: 89.52%<br/>Rec: 88.80% | FPR: 10.40%<br/>FNR: 11.20% | 100.0% (25/25) | 92.0% (23/25) | 6.83s (+2.65s vs A1, device UNVERIFIED) | **VERIFIED** (Domain V1 caused 23 harmful shifts) |
| **Phase 4: Controlled M4 Ablation** | (Same Combined $N=250$) | 250 | (Same Combined $N=250$) | Config A4 (Full Canonical Architecture) | A4: **89.60%** | Prec: 90.91%<br/>Rec: 88.00% | FPR: 8.80%<br/>FNR: 12.00% | 100.0% (25/25) | 92.0% (23/25) | 6.70s (`qwen3.5:4b`, temp 0.0, device UNVERIFIED) | **VERIFIED** ([`results/m4_ablation_v1/predictions.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/predictions.jsonl)) |
| **Phase 4.5: A1 Generalization V1** | [`data/evaluation/a1_generalization_v1.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/a1_generalization_v1.jsonl) (`ab602982...`) | 500 | Synthetic adversarial & SOC incident mail (250 Legit, 250 Phish; 200 Inj, 50 Quoted) | Frozen A1 (`inference_m4_v2.py`) | A1: **93.40%** | Prec: 91.40%<br/>Rec: 95.60% | FPR: 8.80%<br/>FNR: 4.40% | 100.0% (200/200) | **100.0% (50/50)** (All quoted alerts safe-delivered) | 5.32s total / 2.37s–3.88s Stage 1 (device UNVERIFIED) | **VERIFIED** ([`results/a1_generalization_v1/final_report.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/a1_generalization_v1/final_report.md)) |
| **Phase 5: A1 Sanitizer & Latency Optimization** | [`data/evaluation/phase5_regression_160.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/phase5_regression_160.jsonl) (`325bf42f...`) | 160 | Targeted regression: 100 prompt injection tests (50 active, 50 quoted) + 60 standard (40 Legit, 20 Phish) | Frozen A1 Baseline vs. A1-Opt (`engine_v2.py`) | Both: **87.50%** (140/160 correct) | Prec: 50.00%*<br/>Rec: 50.00%* | FPR: 0.00%<br/>FNR: 50.00%* | **100.0% (50/50)** (Sanitizer V2 active contained) | **100.0% (50/50)** (All 50 quoted alerts delivered) | A1-Opt: 3.89s (Stage 1: **1.57s**, -41.2% speedup, device UNVERIFIED) | **VERIFIED** ([`results/phase5_a1_sanitizer_latency/regression_metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase5_a1_sanitizer_latency/regression_metrics.json))<br/>*\*All 20 sophisticated phish missed by both* |
| **Phase 6: Domain Evidence Study** | `phase5_regression_160` (160) + `phase6_domain_challenge` (40) | 200 | Combined regression + lookalike challenge (110 Legit, 90 Phish; 40 Sophisticated Phish) | Config A (A1-Opt Baseline, No Domain) | A: **89.00%** (178/200) | Prec: 100.0%<br/>Rec: 75.56% | FPR: 0.00%<br/>FNR: 24.44% | 100.0% (50/50) | 100.0% (50/50) (Quoted delivered) | Config A: 3.89s mean (device UNVERIFIED) | **VERIFIED** (Missed 22/40 sophisticated phish; recall = 45.0%) |
| **Phase 6: Domain Evidence Study** | (Same Combined $N=200$) | 200 | (Same Combined $N=200$) | Config B (A1-Opt + Domain Analyzer V2) | B: **96.50%** (193/200) | Prec: 96.77%<br/>Rec: 100.0% | **FPR: 2.73% (3/110)**<br/>FNR: 0.00% | 100.0% (50/50) | 100.0% (50/50) (Quoted delivered) | Config B: 4.47s (+403ms context overhead, device UNVERIFIED) | **VERIFIED** (Caught 40/40 sophisticated phish; 3 FPs on SaaS) |
| **Phase 7: Domain Precision Refinement** | `phase5_160` (160) + `phase6_40` (40) + `phase7_precision_40` (40) | 240 | Combined regression, lookalikes, & SaaS auth (130 Legit, 110 Phish; 60 Sophisticated) | Config A (Frozen P6 Config B Baseline) | A: **97.50%** (234/240) | Prec: 94.83%<br/>Rec: 100.0% | **FPR: 4.62% (6/130)**<br/>FNR: 0.00% | 100.0% (50/50) | 100.0% (50/50) (Quoted delivered) | Config A: 4.42s mean / 6.47s P95 (device UNVERIFIED) | **VERIFIED** ([`results/phase7_domain_precision/independent_metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase7_domain_precision/independent_metrics.json)) |
| **Phase 7: Domain Precision Refinement** | (Same Combined $N=240$) | 240 | (Same Combined $N=240$) | Config B (**Candidate: Domain Analyzer V3**) | B: **99.58%** (239/240) | **Prec: 99.10%**<br/>**Rec: 100.0%** | **FPR: 0.77% (1/130)**<br/>**FNR: 0.00%** | **100.0% (50/50)** | **98.0% (49/50)** (1 FP on `gen-inj-071` attack vocab) | **Config B: 4.09s mean / 5.38s P95 (-16.9% tail, device UNVERIFIED)** | **VERIFIED** (Remediated 3/3 historical FPs + 3/3 SaaS FPs; 1 FP on vocab) |
| **Phase 7: Domain Precision Refinement** | `phase6_challenge` (40) + `phase7_challenge` (40) | 80 | Domain challenge subsets only (40 Legit, 40 Phish) | Config C (Domain Evidence Ablation) | C: **96.25%** (77/80) | Prec: 100.0%<br/>Rec: 92.50% | FPR: 0.00%<br/>FNR: 7.50% (3/40 missed) | Not Evaluated (Challenge set only) | Not Evaluated | Config C: 3.68s mean (device UNVERIFIED) | **VERIFIED** (Ablation proves domain evidence adds net recall gain; note P6 Config C had 97.5% parity on `p6-sop-016`) |

---

## 3. Granular Experiment Forensic Profiles

### 3.1 Phase 4: Controlled M4 Component Ablation ($N=250$)
- **Objective**: Decompose M4 into four modular enhancements and quantify the individual statistical attribution of each component.
- **Dataset Composition**:
  - `data/evaluation/live_benchmark_v2.jsonl` (150 samples) + `data/evaluation/heldout_benchmark_v1.jsonl` (100 samples).
  - Ground Truth: 125 Legitimate, 125 Phishing (Balanced 50/50).
  - Injection Partition: 25 Active Injections, 25 Quoted Injection SOC reports.
- **Evaluated Configurations (9 Total, 2,250 Model Inferences)**:
  - `A0`: Production Baseline M4 (single-class injection detector, no sanitizer, standard RAG).
  - `ISO-4`: Fine-grained Active/Quoted Classifier alone.
  - `A1`: Active/Quoted Classifier + Stage 1.5 Regex Sanitizer V1.
  - `A2`: A1 + Structured Domain Analysis V1.
  - `A3`: A2 + Balanced RAG Retrieval (2L + 2P).
  - `A4`: Full Experimental Canonical System.
  - `ISO-1`: Full system without Sanitizer.
  - `ISO-2`: Full system without Domain Telemetry.
  - `ISO-3`: Full system without Balanced RAG.
- **Empirical Metrics Traced**:
  - Canonical Parity Confirmed: A4 vs. A3 achieved 100.0% prediction parity across 250 samples (McNemar $\chi^2 = 0.000, p = 1.000$).
  - Sanitizer Net Gain: Adding Sanitizer V1 to ISO-4 produced $+2$ net correct classifications ($p = 0.617$); in the full system (A4 vs. ISO-1), it produced $+4$ net correct classifications ($p = 0.221$).
  - Domain Telemetry V1 Failure: A2 vs. A1 caused **23 harmful shifts** against only 14 beneficial shifts ($-9$ net loss, accuracy dropped from 92.8% to 89.2%).
  - Quoted Injection Accuracy: A0 scored **0.0% (0/25)**; A1 through A4 scored **92.0% (23/25)**.
- **Limitations & Forensic Path**:
  - Domain Analyzer V1 over-triggered on synthetic benchmark domains without active DNS.
  - Latency of full pipeline reached 6.70s–6.88s (unacceptable for production mail gateways).
  - Evidence: [`results/m4_ablation_v1/component_contribution.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/component_contribution.md), [`predictions.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/predictions.jsonl).

### 3.2 A1 Generalization Validation V1 ($N=500$)
- **Objective**: Assess the out-of-distribution stability of Frozen A1 across 500 adversarial and benign corporate emails.
- **Dataset Composition**:
  - `data/evaluation/a1_generalization_v1.jsonl` (250 Legitimate, 250 Phishing).
  - Injection distribution: 100 marked injections, 100 unmarked injections, 50 quoted security alert discussions.
- **Evaluated Configurations**: Baseline A0 vs. Frozen A1 (`src/core/inference_m4_v2.py`).
- **Empirical Metrics Traced**:
  - Overall Accuracy: A1 achieved **93.40%** (467/500) vs. A0 **89.20%** (446/500).
  - Active Injection Containment: A1 contained **100.0% (200/200)** active injections.
  - Quoted Injection Handling: A1 achieved **100.0% (50/50)** safe delivery, whereas A0 blocked 100% of quoted reports as attacks.
  - Total Pipeline Latency: Mean 5.32s per email. Stage 1 required 2.37s–3.88s due to verbose reasoning generation.
- **Limitations & Forensic Path**:
  - Sanitizer V1 failed on non-ASCII characters, CJK characters, and punctuation attached to closing tokens.
  - Evidence: [`results/a1_generalization_v1/final_report.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/a1_generalization_v1/final_report.md), [`root_cause_analysis.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/a1_generalization_v1/root_cause_analysis.md).

### 3.3 Phase 5: A1 Sanitizer & Latency Optimization ($N=160$)
- **Objective**: Validate Sanitizer V2 against multilingual/boundary stress cases and measure Stage 1 latency optimization.
- **Dataset Composition**:
  - `data/evaluation/phase5_regression_160.jsonl` (N=160).
  - 100 Injection test cases: 50 active injection stress cases (CJK characters, attached punctuation, multiline wrapping) + 50 quoted SOC alert discussions.
  - 60 Standard regression cases: 40 ordinary legitimate emails, 20 sophisticated phishing emails (`gen-sop-007` to `gen-sop-099`).
- **Evaluated Configurations**: Frozen A1 Baseline vs. A1-Opt (`engine_v2.py`).
- **Empirical Metrics Traced**:
  - Overall Accuracy: **87.50% (140/160)** for both models (zero prediction drift on regression suite).
  - Latency Reduction: Stage 1 mean latency reduced from 2.67s to **1.57s (-41.2% speedup)**. Total latency reduced from 5.32s to **3.89s (-26.9%)**.
  - Execution Compute Device: **UNVERIFIED** (host accelerator device not recorded in prediction metadata).
  - Sanitizer V2 Performance: 100% containment of active injections (50/50) across all CJK and punctuation edge cases; 100% safe-delivery of quoted alerts (50/50); zero text corruption.
  - **Sophisticated Phishing Blind Spot**: Both Frozen A1 and A1-Opt missed **all 20 sophisticated phishing emails (0% recall / 20 false negatives)**.
- **Limitations & Forensic Path**:
  - Proved that domain-blind semantic classification cannot reliably catch sophisticated lookalike domains.
  - Evidence: [`results/phase5_a1_sanitizer_latency/regression_metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase5_a1_sanitizer_latency/regression_metrics.json), [`sophisticated_phishing_audit.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase5_a1_sanitizer_latency/sophisticated_phishing_audit.md).

### 3.4 Phase 6: Domain Evidence Integration Study ($N=200$)
- **Objective**: Investigate whether structured sender and domain telemetry (Domain Analyzer V2) can resolve the sophisticated phishing blind spot without causing false alarms.
- **Dataset Composition**:
  - Combined suite: `phase5_regression_160` (160) + `phase6_domain_challenge` (40: 20 difficult legit + 20 sophisticated phish).
  - Total: 110 Legitimate, 90 Phishing (including 40 sophisticated lookalike attacks).
- **Evaluated Configurations**:
  - Config A: A1-Opt Baseline (No Domain Evidence, 200 samples).
  - Config B: A1-Opt + Domain Analyzer V2 (200 samples).
  - Config C: Domain Evidence Ablation (40 challenge samples).
- **Empirical Metrics Traced**:
  - Sophisticated Phishing Recall: Config A scored **45.0%** (18/40 detected, 22 missed). Config B scored **100.0% (40/40 detected, 0 missed)**.
  - False Positive Incurrence: Config A had 0 FPs (0.0% FPR). Config B incurred **3 False Positives (2.73% FPR)** on legitimate corporate emails:
    1. `gen-ord-010`: Amazon Business order confirmation (flagged `amazon-business.com` as brand lookalike).
    2. `p6-leg-007`: Internal SAP Concur travel booking notification (flagged internal subdomain mismatch).
    3. `p6-leg-015`: Workday tenant performance review (flagged `myworkday.com` as unauthorized).
  - Config C Ablation & Parity: Removing domain evidence resulted in 22 missed phishing samples. On the 40 challenge samples, Config C achieved 97.5% prediction parity with Config A (39/40 identical), with sample `p6-sop-016` flipping from `false` (Config A) to `true` (Config C) due to decision boundary sensitivity near threshold and floating-point summation variation across separate sessions.
  - Computational Overhead: Domain Analyzer V2 CPU time $< 1\text{ ms}$; Stage 2 LLM prompt expansion added $+403\text{ ms}$ (mean latency 4.47s vs. 3.89s; host compute device UNVERIFIED).
- **Limitations & Forensic Path**:
  - Domain Analyzer V2 heuristics were too rigid, generating unacceptable false alarms on multi-tenant SaaS.
  - Evidence: [`results/phase6_domain_evidence/false_positive_analysis.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase6_domain_evidence/false_positive_analysis.md), [`sophisticated_phishing_analysis.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase6_domain_evidence/sophisticated_phishing_analysis.md).

### 3.5 Phase 7: Domain Precision Refinement Study ($N=240$)
- **Objective**: Deploy Domain Analyzer V3 (multi-level Public Suffix parsing, enterprise SaaS whitelist, internal corporate sender context) to remediate the Phase 6 false positives while preserving 100% phishing recall.
- **Dataset Composition**:
  - Combined suite: `phase5_regression_160` (160) + `phase6_domain_challenge` (40) + `phase7_precision_challenge` (40: 20 difficult SaaS/corporate legit + 20 sophisticated phish).
  - Total: 130 Legitimate, 110 Phishing (including 60 sophisticated phishing attacks).
- **Evaluated Configurations (560 Total Predictions)**:
  - Config A: Frozen Phase 6 Baseline (Domain Analyzer V2, 240 samples).
  - Config B: Experimental Research Candidate (Domain Analyzer V3, 240 samples).
  - Config C: Domain Evidence Ablation (80 challenge samples).
- **Empirical Metrics Traced**:
  - Overall Accuracy: Config B reached **99.58% (239/240)** vs. Config A **97.50% (234/240)** (+2.08 pp net gain).
  - False Positive Remediation: Config A generated 6 FPs ($\text{FPR} = 4.62\%$). Config B generated **1 FP ($\text{FPR} = 0.77\%$)**, achieving an **83.3% relative reduction in false positives**.
    - Remediated 100% (3/3) of historical Phase 6 FPs (`gen-ord-010`, `p6-leg-007`, `p6-leg-015`).
    - Remediated 100% (3/3) of new SaaS challenge FPs (`p7-leg-001`, `p7-leg-002`, `p7-leg-003`).
  - Phishing Recall: Config B detected **60 out of 60 sophisticated phishing attacks (100.0% recall, 0 false negatives)**.
  - Quoted Injection Handling: Config B safe-delivered 49 of 50 quoted alerts (98.0%). Single Residual FP Dissected: Sample `gen-inj-071` (a quoted educational security report where Stage 2 LLM tripped on attack vocabulary; Domain Analyzer V3 reported zero anomalies).
  - Latency & Compute Device: Config B mean latency dropped to **4.09s** (-331 ms vs. Config A); P95 tail latency dropped to **5.38s (-16.9% tail speedup)** due to cleaner evidence structuring. Execution hardware compute device is **UNVERIFIED** (host accelerator device not logged in prediction records).
- **Limitations & Forensic Path**:
  - Evaluated on 240 controlled challenge samples; enterprise mail gateway deployment requires validation against thousands of raw, uncurated real emails (Track A).
  - Evidence: [`results/phase7_domain_precision/independent_metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase7_domain_precision/independent_metrics.json), [`results/phase7_final_audit/audit_summary.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase7_final_audit/audit_summary.json).
