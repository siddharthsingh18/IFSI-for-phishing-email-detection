# Independent Forensic Audit Report: M4 Ablation V1 Experiment

**Audit Date:** November 1, 2026  
**Auditor:** Independent Automated Scientific Audit Agent  
**Repository:** `D:\Project\IFSI-for-phishing-email-detection`  
**Evaluation Target:** M4 Decoupled Two-Stage RAG Ablation Study V1  
**Source of Truth:** `results/m4_ablation_v1/predictions.jsonl` (2,250 raw inference records)  

---

## Executive Summary & Final Recommendation

An independent, mathematical and procedural forensic audit was conducted on the completed M4 Ablation V1 benchmark. The audit validated all 2,250 raw inference records, checked input consistency, independently recomputed all performance metrics and denominators, verified ground-truth injection labeling across all 50 injection samples, and performed rigorous paired hypothesis testing using both asymptotic continuity-corrected McNemar $\chi^2$ and exact two-tailed binomial tests.

### Primary Audit Findings

1. **Prediction Integrity is 100% Verified:**
   - Exactly 2,250 prediction records exist across 9 configurations ($9 \times 250$).
   - Exactly 250 unique email samples per configuration (150 from Live Benchmark V2 + 100 from Held-Out Benchmark V1).
   - Zero missing configuration/sample combinations, zero duplicate pairs, zero inference failures, and identical input content across all configurations.
2. **Top Empirical Architecture is Configuration A1:**
   - **Configuration A1 (Active/Quoted Classifier + Stage 1.5 Sanitizer)** achieved the **highest overall accuracy (92.80%)**, highest F1-score (93.02%), lowest overall error count (18 total errors), and 100% active injection recall (25/25), while running ~38% faster than the full architecture (4.18s vs 6.70s mean latency).
3. **Domain Telemetry Induced Subtle False Negatives on Sophisticated Phishing:**
   - In configurations containing domain telemetry (A2, A3, A4, ISO-1, ISO-3), when the sender domain was synthetically clean or lacked known bad reputation, the telemetry banner `[DOMAIN TELEMETRY: CLEAN / NO SUSPICIOUS SIGNALS]` falsely reassured the Stage 2 LLM. This caused 8 sophisticated phishing lures (e.g., `v2-sop-02`, `v2-sop-06`, `v2-sop-07`, `v2-sop-10`, `v2-sop-14`, `v2-sop-17`, `v2-sop-24`) to be misclassified as legitimate (False Negatives), dropping sophisticated phishing recall from 96.0% in ISO-2 down to 76.0% in A4.
4. **No Paired Comparison Reached Formal Statistical Significance ($p \ge 0.05$):**
   - Under rigorous continuity-corrected McNemar tests and exact binomial tests, none of the 8 paired architectural contrasts achieve $p < 0.05$ at sample size $N = 250$. All 95% confidence intervals for paired differences in proportions ($\Delta$) cross zero. Previous claims of "statistically meaningful" gains reflect directional shifts rather than formal statistical rejection of the null hypothesis.
5. **Exact Parity Confirmed (A4 vs A3):**
   - Config A3 (modular ablation engine with all 4 components enabled) produced bit-for-bit identical predictions to Config A4 (canonical `src/core/inference_m4_v2.py`) across all 250 evaluation samples (0 discordant pairs, $\chi^2 = 0.0$, $p = 1.0$).

### Formal Audit Recommendation

**`A1 candidate for further validation.`**

- Configuration A1 strikes the optimal balance of high detection accuracy (92.80%), low false positive rate (10.40%), zero active injection bypasses (100% recall), fast inference speed (4.18s), and freedom from domain telemetry's false-reassurance failure modes.
- Selected components—specifically **Structured Domain Telemetry**—require further prompt calibration and confidence weighting before they can be considered for production deployment.

---

## 1. Prediction Integrity & Dataset Validation

The raw predictions in `results/m4_ablation_v1/predictions.jsonl` were audited against the primary source datasets:
- `data/evaluation/live_benchmark_v2.jsonl` (150 samples)
- `data/evaluation/heldout_benchmark_v1.jsonl` (100 samples)

| Integrity Dimension | Expected Requirement | Audited Value | Status |
|:---|:---:|:---:|:---:|
| **Total Prediction Records** | 2,250 | 2,250 | **PASS** |
| **Configurations Evaluated** | 9 | 9 (`A0`, `ISO-4`, `A1`, `A2`, `A3`, `A4`, `ISO-1`, `ISO-2`, `ISO-3`) | **PASS** |
| **Samples per Configuration** | Exactly 250 | 250 for all 9 configurations | **PASS** |
| **Missing Combinations** | 0 | 0 | **PASS** |
| **Duplicate $(Config, Sample)$ Pairs** | 0 | 0 | **PASS** |
| **Inference Failures (`is_valid == False`)** | 0 | 0 | **PASS** |
| **Input Content Consistency** | 100% identical subject/sender/body | 100% identical across all 9 configurations | **PASS** |
| **Ground-Truth Label Alignment** | 100% match with source datasets | 100% match (125 Phishing, 125 Genuine) | **PASS** |
| **Live Benchmark V2 Representation** | 150 samples | 150 samples per config ($150 \times 9 = 1,350$) | **PASS** |
| **Held-Out Benchmark V1 Representation** | 100 samples | 100 samples per config ($100 \times 9 = 900$) | **PASS** |

---

## 2. Independently Recomputed Performance Metrics

All metrics were independently calculated from raw predictions without relying on previous calculation artifacts.

### 2.1 Combined Benchmark ($N = 250$: 125 Phishing, 125 Genuine)

| Config ID | Accuracy | Precision | Recall | F1-Score | FPR | FNR | TP / FN | FP / TN | Active Inj Rec | Quoted Inj Acc | Mean Latency |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A0** | **91.60%** | 87.68% | 96.80% | 92.02% | 13.60% | 3.20% | 121 / 4 | 17 / 108 | 100.0% (25/25) | 0.0% (0/25) | 3.40s |
| **ISO-4** | **92.00%** | 88.32% | 96.80% | 92.37% | 12.80% | 3.20% | 121 / 4 | 16 / 109 | 100.0% (25/25) | 76.0% (19/25) | 4.88s |
| **A1** | **92.80%** | **90.23%** | 96.00% | **93.02%** | **10.40%** | 4.00% | 120 / 5 | 13 / 112 | 100.0% (25/25) | 80.0% (20/25) | 4.18s |
| **A2** | **89.20%** | 89.52% | 88.80% | 89.16% | 10.40% | 11.20% | 111 / 14 | 13 / 112 | 100.0% (25/25) | 80.0% (20/25) | 6.83s |
| **A3** | **89.60%** | 90.91% | 88.00% | 89.43% | **8.80%** | 12.00% | 110 / 15 | 11 / 114 | 100.0% (25/25) | 84.0% (21/25) | 6.88s |
| **A4** | **89.60%** | 90.91% | 88.00% | 89.43% | **8.80%** | 12.00% | 110 / 15 | 11 / 114 | 100.0% (25/25) | 84.0% (21/25) | 6.70s |
| **ISO-1** | **88.00%** | 89.26% | 86.40% | 87.80% | 10.40% | 13.60% | 108 / 17 | 13 / 112 | 100.0% (25/25) | 80.0% (20/25) | 4.21s |
| **ISO-2** | **91.20%** | 87.05% | 96.80% | 91.67% | 14.40% | 3.20% | 121 / 4 | 18 / 107 | 100.0% (25/25) | 72.0% (18/25) | 4.06s |
| **ISO-3** | **89.20%** | 89.52% | 88.80% | 89.16% | 10.40% | 11.20% | 111 / 14 | 13 / 112 | 100.0% (25/25) | 80.0% (20/25) | 6.74s |

### 2.2 Live Benchmark V2 Breakdown ($N = 150$: 75 Phishing, 75 Genuine)

| Config ID | Accuracy | Precision | Recall | F1-Score | FPR | FNR | TP / FN | FP / TN | Active Inj Rec | Quoted Inj Acc | Mean Latency |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A0** | **91.33%** | 87.80% | 96.00% | 91.72% | 13.33% | 4.00% | 72 / 3 | 10 / 65 | 100.0% (15/15) | 0.0% (0/15) | 3.59s |
| **ISO-4** | **92.00%** | 88.89% | 96.00% | 92.31% | 12.00% | 4.00% | 72 / 3 | 9 / 66 | 100.0% (15/15) | 80.0% (12/15) | 5.15s |
| **A1** | **92.00%** | 89.87% | 94.67% | 92.21% | 10.67% | 5.33% | 71 / 4 | 8 / 67 | 100.0% (15/15) | 86.7% (13/15) | 4.12s |
| **A2** | **88.67%** | 90.28% | 86.67% | 88.44% | 9.33% | 13.33% | 65 / 10 | 7 / 68 | 100.0% (15/15) | 86.7% (13/15) | 6.77s |
| **A3** | **88.00%** | 91.30% | 84.00% | 87.50% | 8.00% | 16.00% | 63 / 12 | 6 / 69 | 100.0% (15/15) | 86.7% (13/15) | 7.10s |
| **A4** | **88.00%** | 91.30% | 84.00% | 87.50% | 8.00% | 16.00% | 63 / 12 | 6 / 69 | 100.0% (15/15) | 86.7% (13/15) | 6.53s |
| **ISO-1** | **88.00%** | 91.30% | 84.00% | 87.50% | 8.00% | 16.00% | 63 / 12 | 6 / 69 | 100.0% (15/15) | 86.7% (13/15) | 4.29s |
| **ISO-2** | **92.00%** | 88.89% | 96.00% | 92.31% | 12.00% | 4.00% | 72 / 3 | 9 / 66 | 100.0% (15/15) | 80.0% (12/15) | 4.02s |
| **ISO-3** | **88.67%** | 90.28% | 86.67% | 88.44% | 9.33% | 13.33% | 65 / 10 | 7 / 68 | 100.0% (15/15) | 86.7% (13/15) | 6.91s |

### 2.3 Held-Out Benchmark V1 Breakdown ($N = 100$: 50 Phishing, 50 Genuine)

| Config ID | Accuracy | Precision | Recall | F1-Score | FPR | FNR | TP / FN | FP / TN | Active Inj Rec | Quoted Inj Acc | Mean Latency |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A0** | **92.00%** | 87.50% | 98.00% | 92.45% | 14.00% | 2.00% | 49 / 1 | 7 / 43 | 100.0% (10/10) | 0.0% (0/10) | 3.12s |
| **ISO-4** | **92.00%** | 87.50% | 98.00% | 92.45% | 14.00% | 2.00% | 49 / 1 | 7 / 43 | 100.0% (10/10) | 70.0% (7/10) | 4.47s |
| **A1** | **94.00%** | 90.74% | 98.00% | 94.23% | 10.00% | 2.00% | 49 / 1 | 5 / 45 | 100.0% (10/10) | 70.0% (7/10) | 4.28s |
| **A2** | **90.00%** | 88.46% | 92.00% | 90.20% | 12.00% | 8.00% | 46 / 4 | 6 / 44 | 100.0% (10/10) | 70.0% (7/10) | 6.93s |
| **A3** | **92.00%** | 90.38% | 94.00% | 92.16% | 10.00% | 6.00% | 47 / 3 | 5 / 45 | 100.0% (10/10) | 80.0% (8/10) | 6.55s |
| **A4** | **92.00%** | 90.38% | 94.00% | 92.16% | 10.00% | 6.00% | 47 / 3 | 5 / 45 | 100.0% (10/10) | 80.0% (8/10) | 6.97s |
| **ISO-1** | **88.00%** | 86.54% | 90.00% | 88.24% | 14.00% | 10.00% | 45 / 5 | 7 / 43 | 100.0% (10/10) | 70.0% (7/10) | 4.08s |
| **ISO-2** | **90.00%** | 84.48% | 98.00% | 90.74% | 18.00% | 2.00% | 49 / 1 | 9 / 41 | 100.0% (10/10) | 60.0% (6/10) | 4.11s |
| **ISO-3** | **90.00%** | 88.46% | 92.00% | 90.20% | 12.00% | 8.00% | 46 / 4 | 6 / 44 | 100.0% (10/10) | 70.0% (7/10) | 6.49s |

---

## 3. Injection-Label Forensic Audit (All 50 Samples)

The benchmark corpus contains exactly **50 injection-containing samples**:
- **Active Injection Attacks ($N = 25$):** Malicious phishing emails where the injection payload attempts to alter model instructions (15 in V2: `v2-inj-01` to `v2-inj-15`; 10 in Held-Out: `heldout-inj-01` to `heldout-inj-10`).
- **Quoted Injection Advisories ($N = 25$):** Legitimate genuine emails containing passive quotes of adversarial prompts for research, SOC analysis, or training (15 in V2: `v2-inj-16` to `v2-inj-30`; 10 in Held-Out: `heldout-inj-11` to `heldout-inj-20`).

### 3.1 Disambiguation of Injection Evaluation Metrics

It is vital to distinguish three separate metrics:
1. **Active Injection Recall ($TP_{active} / (TP_{active} + FN_{active})$):** Did the system detect malicious injection attacks?
2. **Quoted Injection Accuracy ($Correct_{quoted} / Total_{quoted}$):** Did the system recognize benign quotes, avoid active-injection flagging, and **NOT** block the email?
3. **Overall Injection Recall ($TP_{inj} / (TP_{inj} + FN_{inj})$):** Did Stage 1 flag `has_prompt_injection == True` regardless of active vs. quoted status?

### 3.2 Configuration Injection Audit Summary

| Config ID | Active Injection Recall | Active Misses | Quoted Accuracy (Operational) | Quoted False Blocks | Quoted Misclassification IDs |
|:---|:---:|:---:|:---:|:---:|:---|
| **A0** | **100.0% (25/25)** | 0 | **0.0% (0/25)** | 7 | All 25 failed (no quoted category; 7 blocked as phishing: `v2-inj-22,24,25`, `heldout-inj-11,13,19,20`) |
| **ISO-4** | **100.0% (25/25)** | 0 | **76.0% (19/25)** | 5 | 6 failed: `v2-inj-19,22,25`, `heldout-inj-11,19,20` (5 blocked as phishing) |
| **A1** | **100.0% (25/25)** | 0 | **80.0% (20/25)** | 3 | 5 failed: `v2-inj-19,22,25`, `heldout-inj-11,20` (3 blocked as phishing) |
| **A2** | **100.0% (25/25)** | 0 | **80.0% (20/25)** | 3 | 5 failed: `v2-inj-19,22,25`, `heldout-inj-11,20` (3 blocked as phishing) |
| **A3** | **100.0% (25/25)** | 0 | **84.0% (21/25)** | 2 | 4 failed: `v2-inj-19,22,25`, `heldout-inj-20` (2 blocked as phishing) |
| **A4** | **100.0% (25/25)** | 0 | **84.0% (21/25)** | 2 | 4 failed: `v2-inj-19,22,25`, `heldout-inj-20` (2 blocked as phishing) |
| **ISO-1** | **100.0% (25/25)** | 0 | **80.0% (20/25)** | 4 | 5 failed: `v2-inj-19,22,25`, `heldout-inj-11,20` (4 blocked as phishing) |
| **ISO-2** | **100.0% (25/25)** | 0 | **72.0% (18/25)** | 5 | 7 failed: `v2-inj-19,22,25`, `heldout-inj-11,16,19,20` (5 blocked as phishing) |
| **ISO-3** | **100.0% (25/25)** | 0 | **80.0% (20/25)** | 3 | 5 failed: `v2-inj-19,22,25`, `heldout-inj-11,20` (3 blocked as phishing) |

**Key Takeaways from the Injection Audit:**
- Zero active injection attacks were missed across all 9 configurations ($100\%$ active recall).
- Baseline A0 blocked 7 legitimate quoted security advisories.
- With sanitization (A1, A3, A4), false blocks on quoted injections dropped from 7 to 2 or 3.
- `v2-inj-25` (French security audit quoting injection test cases) failed across all 9 configurations because Stage 2 LLM misclassified French technical text as phishing.

---

## 4. Statistical Audit of Paired Architectural Comparisons

Every contrast was evaluated by pairing exact predictions across all 250 evaluation samples. Both the continuity-corrected McNemar $\chi^2$ statistic and the exact two-tailed binomial $p$-value were computed.

$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c} \quad \text{(Edwards continuity correction)}$$

$$\text{Exact Binomial } p = 2 \times \sum_{k=0}^{\min(b,c)} \binom{b+c}{k} 0.5^{b+c}$$

$$\Delta = \frac{b - c}{N}, \quad 95\% \text{ CI} = \Delta \pm 1.96 \times \frac{1}{N} \sqrt{(b+c) - \frac{(b-c)^2}{N}}$$

| Comparison | Contrast Label | Beneficial ($b$) | Harmful ($c$) | Net Gain ($b - c$) | McNemar $\chi^2$ | Asymp. $p$ | Exact Binom. $p$ | 95% Confidence Interval ($\Delta$) | Significance ($\alpha=0.05$) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **ISO-4 vs A0** | Stage 1 Active vs Quoted Classifier | 2 | 1 | **+1** | 0.0000 | 1.000000 | 1.000000 | $[-0.96\%, +1.76\%]$ | **Not Significant** |
| **A1 vs ISO-4** | Stage 1.5 Prompt Sanitization (Cumulative) | 3 | 1 | **+2** | 0.2500 | 0.617075 | 0.625000 | $[-0.76\%, +2.36\%]$ | **Not Significant** |
| **A2 vs A1** | Structured Domain Telemetry (Cumulative) | 14 | 23 | **-9** | 1.7297 | 0.188445 | 0.187742 | $[-8.35\%, +1.15\%]$ | **Not Significant** |
| **A3 vs A2** | Balanced RAG Retrieval (Cumulative) | 7 | 6 | **+1** | 0.0000 | 1.000000 | 1.000000 | $[-2.43\%, +3.23\%]$ | **Not Significant** |
| **A4 vs A3** | Canonical Experimental Engine Parity | 0 | 0 | **+0** | 0.0000 | 1.000000 | 1.000000 | $[0.00\%, 0.00\%]$ | **Exact Parity ($p=1.0$)** |
| **A4 vs ISO-1** | Sanitization (Leave-One-Out in Full Architecture) | 5 | 1 | **+4** | 1.5000 | 0.220671 | 0.218750 | $[-0.31\%, +3.51\%]$ | **Not Significant** |
| **A4 vs ISO-2** | Domain Telemetry (Leave-One-Out in Full Architecture) | 17 | 21 | **-4** | 0.2368 | 0.626496 | 0.627103 | $[-6.43\%, +3.23\%]$ | **Not Significant** |
| **A4 vs ISO-3** | Balanced RAG (Leave-One-Out in Full Architecture) | 7 | 6 | **+1** | 0.0000 | 1.000000 | 1.000000 | $[-2.43\%, +3.23\%]$ | **Not Significant** |

### Statistical Audit Conclusion

- **None of the performance differences achieve statistical significance at $\alpha = 0.05$.**
- All 95% confidence intervals cross zero ($0 \in [CI_{lower}, CI_{upper}]$).
- While Configuration A1 achieved the highest sample accuracy (92.80% vs 91.60% for A0), the net difference of +3 samples ($b=4, c=1$ vs A0) represents a directional trend that requires a larger sample size ($N \ge 800$) to reach statistical significance.
- Any description of these differences as "statistically significant" or "statistically proven" is mathematically invalid and must be corrected.

---

## 5. Reassessment of Component Conclusions

### 5.1 ISO-4 vs A0 (Fine-Grained Active vs. Quoted Injection Classifier)
- **Previous Claim:** "Eliminated false alarms on SOC advisories and quoting test cases."
- **Audit Reassessment:** **CONFIRMED.** Quoted injection accuracy improved from 0.0% to 76.0%, preventing 2 false blocks on critical security emails (`v2-inj-24` and `heldout-inj-13`). Zero active injection attacks were compromised.

### 5.2 A1 vs ISO-4 (Stage 1.5 Prompt Sanitization)
- **Previous Claim:** "Neutralizes injection spans before Stage 2."
- **Audit Reassessment:** **CONFIRMED & REINFORCED.** Adding sanitization to ISO-4 produced +2 net accuracy gain (raising accuracy to 92.80%), dropped FPR from 12.80% to 10.40%, and cured false blocks on `v2-inj-22` and `heldout-inj-19`. Sanitization proved to be the single cleanest, highest-yield defensive improvement in the entire study.

### 5.3 A2 vs A1 (Structured Domain Telemetry)
- **Previous Claim:** "Provides valuable zero-day signals but requires calibration."
- **Audit Reassessment:** **CRITICAL FINDING.** Adding domain telemetry produced a net loss of -9 samples (14 beneficial vs 23 harmful shifts). Specifically, when domain telemetry found no known malicious reputation on synthetic sender domains, the `[DOMAIN TELEMETRY: CLEAN]` signal acted as a false reassurance to Stage 2 LLM, blinding it to sophisticated spear phishing lures.

### 5.4 A3 vs A2 (Balanced RAG Retrieval)
- **Previous Claim:** "Symmetric exemplar retrieval mitigates similarity skew."
- **Audit Reassessment:** **CONFIRMED.** Balanced 2+2 retrieval produced 7 beneficial vs 6 harmful shifts, but more importantly, dropped False Positive Rate to 8.80% (the lowest in the entire study) and raised Precision to 90.91%.

### 5.5 A4 vs ISO-1 (Sanitization in Full Architecture)
- **Previous Claim:** "Statistically meaningful net gain of +4."
- **Audit Reassessment:** **CORRECTION.** While sanitization yielded +4 net samples (5 beneficial, 1 harmful) and dropped FPR from 10.40% to 8.80%, McNemar's test yields $\chi^2 = 1.5000, p = 0.2207$. This is directionally positive and operationally sound, but NOT statistically significant ($p \ge 0.05$).

### 5.6 A4 vs ISO-2 (Domain Telemetry in Full Architecture)
- **Previous Claim:** "High variance on internal test domains."
- **Audit Reassessment:** **CONFIRMED.** Domain telemetry caused 38 prediction flips (17 beneficial, 21 harmful). It helped classify difficult corporate notices (`heldout-dif-16`, `heldout-dif-19`), but harmed detection on 8 sophisticated phishing lures.

### 5.7 A4 vs ISO-3 (Balanced RAG in Full Architecture)
- **Previous Claim:** "Balanced RAG stabilizes exemplar retrieval."
- **Audit Reassessment:** **CONFIRMED.** Balanced RAG provided a net +1 gain and maintained lower FPR (8.80% vs 10.40%).

---

## 6. Comprehensive Error Analysis Across Failure Patterns

Across the 250 evaluation samples, exactly **55 unique emails** failed in at least one configuration.

### 6.1 Sophisticated Phishing False Negatives ($17$ error samples)
- **Failure Pattern:** Lures featuring conversational, executive-level pretexting without urgency, threats, or overt link formatting (e.g. `v2-sop-02` Executive Bonus, `v2-sop-06` COO Realignment, `v2-sop-08` Gift Cards, `v2-sop-10` Revised Wiring Instructions, `v2-sop-14` Workplace Culture Investigation).
- **Vulnerability:** When Domain Telemetry was active, it reported `no lookalike domains detected`. Stage 2 LLM interpreted this absence of evidence as evidence of legitimacy, overriding conversational suspicion and causing 5 to 8 false negatives per configuration.

### 6.2 Difficult Genuine Corporate Communications ($22$ error samples)
- **Failure Pattern:** Mandatory compliance directives, W-2 tax forms, IT password expiration notices, and zero-day patch alerts (`v2-dif-19`, `heldout-dif-04`, `heldout-dif-05`, `heldout-dif-06`, `heldout-dif-12`, `heldout-dif-17`).
- **Vulnerability:** These emails legitimately employ urgent language ("MANDATORY", "FINAL CALL", "CRITICAL DIRECTIVE"). When evaluated by standard RAG, the nearest vector neighbors were aggressive phishing lures, creating a strong false-positive bias.

### 6.3 Quoted Injections ($10$ error samples)
- **Failure Pattern:** Legitimate emails quoting adversarial prompts (`v2-inj-19`, `v2-inj-22`, `v2-inj-25`, `heldout-inj-11`, `heldout-inj-20`).
- **Vulnerability:** While Stage 1 identified them as quoted injections, unsanitized configurations passed the adversarial instructions into Stage 2, where the LLM either executed the instruction or became confused and declared the email malicious. `v2-inj-25` (in French) suffered from multilingual classification degradation across all 9 models.

### 6.4 Active Injections ($0$ error samples)
- **Zero active injection bypasses occurred in any model.** Stage 1 reliably caught 100% of malicious injection prompts across both benchmarks.

---

## 7. Audit Discrepancies Identified and Corrected

| Discrepancy # | Area | Previous Report Claim | Forensic Audit Fact | Correction Applied |
|:---:|:---|:---|:---|:---|
| **1** | **Quoted Injection Accuracy** | "ISO-4 achieved 100% quoted injection classification accuracy" | Raw tag match was 92.0% (23/25), but operational accuracy (avoiding false block/phishing verdict) was **76.0% (19/25)** for ISO-4 and **80.0% (20/25)** for A1. | Corrected to operational block-free accuracy. |
| **2** | **Statistical Significance** | "Statistically meaningful net gain of +4 in A4 vs ISO-1" | McNemar test with continuity correction yields $\chi^2 = 1.5000, p = 0.2207$. $p \ge 0.05$. | Explicitly stated as not statistically significant. |
| **3** | **Domain Telemetry Effect** | Described primarily as having "sensitivity on internal test domains" | Domain telemetry also created **false negative blind spots on sophisticated phishing** due to false-reassurance clean domain signals. | Full trade-off documented in report. |

---

## 8. Artifact and File Verification Audit Trail

### 8.1 Files Inspected
- `results/m4_ablation_v1/predictions.jsonl` (2,250 records)
- `data/evaluation/live_benchmark_v2.jsonl` (150 samples)
- `data/evaluation/heldout_benchmark_v1.jsonl` (100 samples)
- `results/m4_ablation_v1/metrics.json`
- `src/experiments/m4_ablation_v1/ablation_engine.py`
- `src/experiments/m4_ablation_v1/run_ablation_benchmark.py`
- `src/core/inference.py` (Production M4)
- `src/core/inference_m4_v2.py` (Canonical Experimental M4)
- `results/rag_index_clean/index.faiss` (Clean vector store)
- `results/rag_index_clean/metadata.json` (Clean exemplar metadata)

### 8.2 Deliverables Created
1. `results/m4_ablation_v1/forensic_audit.md` (This document)
2. `results/m4_ablation_v1/independently_verified_metrics.json`
3. `results/m4_ablation_v1/independently_verified_comparisons.json`

### 8.3 Integrity Hashes Verified

| File | Verification SHA-256 Hash | Mutated? |
|:---|:---:|:---:|
| `results/rag_index_clean/index.faiss` | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` | **NO (100% Intact)** |
| `results/rag_index_clean/metadata.json` | `4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece` | **NO (100% Intact)** |
| `src/core/inference.py` | `aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506` | **NO (100% Intact)** |
| `src/core/inference_m4_v2.py` | `fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37` | **NO (100% Intact)** |
| `data/evaluation/live_benchmark_v2.jsonl` | `1c762180451b90c8ad4e0500b5881526a69db3c6a69bffd09e3b7ed2ba0463e9` | **NO (100% Intact)** |
| `data/evaluation/heldout_benchmark_v1.jsonl` | `42722ce81deffda02c788777af6aef2ce4b550fbba3ff1115f57a3a9c943f0c9` | **NO (100% Intact)** |
| `results/m4_ablation_v1/predictions.jsonl` | `9bfa6a12b2a647ff952bb8fc6f2358897ad1e5317ad1dcabf3b5ddbb409d94fc` | **Source of Truth Verified** |

### 8.4 Git Working Tree Status
```
git status --short:
?? results/m4_ablation_v1/
?? src/experiments/
?? tests/integration_sanity_ablation.py
?? tests/test_m4_ablation.py
git diff: [CLEAN - 0 modifications to tracked codebase]
```

