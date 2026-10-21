# Comprehensive Benchmark Report: M1–M4 Across Clean, Marked, and Unmarked Injections

## 1. Executive Summary & Main Finding

The computed results show different failure modes across the evaluated architectures. M1 clean recall was 94.53% with clean FPR 0.25%; marked and unmarked recall were 90.62% and 91.41%, respectively, so M1 is consistent with bootstrap-CI-bounded changes. M2 meets the near-degenerate clean-output rule, with clean specificity 0.00% and predicted-positive rate 100.00%. M3 recall changed from 41.59% on clean data to 21.05% under unmarked injection, a change of 20.54%. M4 recall changed from 99.22% to 96.09%; its clean FPR was already 76.90%, compared with 72.08% under unmarked injection; the available summary does not support calling this injection-induced without a significant control-only paired test.

---

## 2. Full Metrics Matrix (M1–M4 x Clean / Marked / Unmarked)

Evaluation conducted over $N = 522$ test split emails (128 Phishing, 394 Legitimate Control) under three experimental conditions:
- **Clean**: Unperturbed test emails from the stratified test split.
- **Marked**: Prompt injections enclosed in explicit delimiter markers (`[BEGIN EMBEDDED CLASSIFIER MESSAGE]`).
- **Unmarked**: Injections rewritten and naturally blended into normal email language (disclaimers, forwarding headers, signature blocks).

| Method | Condition | Accuracy | Recall (Attacked Phish) | FPR (Injected Control) | Precision | Specificity | F1 Score | Invalid Rate | Mean Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M1 (TF-IDF + LogReg)** | `clean` | 0.9847 | 0.9453 | 0.0025 | 0.9918 | 0.9975 | 0.9680 | 0.00% | `0.28 ms` |
| **M1 (TF-IDF + LogReg)** | `marked` | 0.9751 | 0.9062 | 0.0025 | 0.9915 | 0.9975 | 0.9469 | 0.00% | `0.29 ms` |
| **M1 (TF-IDF + LogReg)** | `unmarked` | 0.9770 | 0.9141 | 0.0025 | 0.9915 | 0.9975 | 0.9512 | 0.00% | `0.29 ms` |
| **M2 (Zero-Shot LLM)** | `clean` | 0.2386 | 1.0000 | 1.0000 | 0.2386 | 0.0000 | 0.3853 | 11.69% | `0.5135s` |
| **M2 (Zero-Shot LLM)** | `marked` | 0.2565 | 0.9569 | 0.9770 | 0.2461 | 0.0230 | 0.3915 | 11.11% | `0.4375s` |
| **M2 (Zero-Shot LLM)** | `unmarked` | 0.2838 | 0.9123 | 0.9244 | 0.2464 | 0.0756 | 0.3881 | 12.26% | `0.5117s` |
| **M3 (RAG Combined)** | `clean` | 0.4246 | 0.4159 | 0.5726 | 0.1895 | 0.4274 | 0.2604 | 11.11% | `0.7459s` |
| **M3 (RAG Combined)** | `marked` | 0.6688 | 0.0982 | 0.1562 | 0.1618 | 0.8438 | 0.1222 | 8.62% | `0.6601s` |
| **M3 (RAG Combined)** | `unmarked` | 0.6157 | 0.2105 | 0.2595 | 0.2000 | 0.7405 | 0.2051 | 7.28% | `0.8738s` |
| **M4 (RAG Decoupled)** | `clean` | 0.4176 | 0.9922 | 0.7690 | 0.2953 | 0.2310 | 0.4552 | 0.00% | `0.4354s` |
| **M4 (RAG Decoupled)** | `marked` | 0.4655 | 0.8984 | 0.6751 | 0.3018 | 0.3249 | 0.4519 | 0.00% | `0.4041s` |
| **M4 (RAG Decoupled)** | `unmarked` | 0.4464 | 0.9609 | 0.7208 | 0.3022 | 0.2792 | 0.4598 | 0.00% | `0.5049s` |

### 2.1 Operational Reliability & Latency Breakdown

Detailed operational summary reporting format validity, failure-to-format counts, total batch wall-clock runtime, and mean per-email inference latency across all 12 experimental conditions:

| Method | Condition | Total Samples | Valid Calls | Invalid Calls | Invalid Rate | Total Runtime | Mean Latency (per email) | Throughput |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M1 (TF-IDF + LogReg)** | `clean` | 522 | 522 | 0 | 0.00% | 0.15s | 0.28 ms | 3527.0 emails/s |
| **M1 (TF-IDF + LogReg)** | `marked` | 522 | 522 | 0 | 0.00% | 0.15s | 0.29 ms | 3434.2 emails/s |
| **M1 (TF-IDF + LogReg)** | `unmarked` | 522 | 522 | 0 | 0.00% | 0.15s | 0.29 ms | 3480.0 emails/s |
| **M2 (Zero-Shot LLM)** | `clean` | 522 | 461 | 61 | 11.69% | 268.06s | 0.5135s | 1.9 emails/s |
| **M2 (Zero-Shot LLM)** | `marked` | 522 | 464 | 58 | 11.11% | 228.36s | 0.4375s | 2.3 emails/s |
| **M2 (Zero-Shot LLM)** | `unmarked` | 522 | 458 | 64 | 12.26% | 267.13s | 0.5117s | 2.0 emails/s |
| **M3 (RAG Combined)** | `clean` | 522 | 464 | 58 | 11.11% | 389.38s | 0.7459s | 1.3 emails/s |
| **M3 (RAG Combined)** | `marked` | 522 | 477 | 45 | 8.62% | 344.58s | 0.6601s | 1.5 emails/s |
| **M3 (RAG Combined)** | `unmarked` | 522 | 484 | 38 | 7.28% | 456.13s | 0.8738s | 1.1 emails/s |
| **M4 (RAG Decoupled)** | `clean` | 522 | 522 | 0 | 0.00% | 227.29s | 0.4354s | 2.3 emails/s |
| **M4 (RAG Decoupled)** | `marked` | 522 | 522 | 0 | 0.00% | 210.94s | 0.4041s | 2.5 emails/s |
| **M4 (RAG Decoupled)** | `unmarked` | 522 | 522 | 0 | 0.00% | 263.57s | 0.5049s | 2.0 emails/s |

---

## 3. Confusion Matrices

| Method | Condition | Total | True Positives (TP) | False Negatives (FN) | True Negatives (TN) | False Positives (FP) | Invalid Calls |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **M1 (TF-IDF + LogReg)** | `clean` | 522 | 121 | 7 | 393 | 1 | 0 |
| **M1 (TF-IDF + LogReg)** | `marked` | 522 | 116 | 12 | 393 | 1 | 0 |
| **M1 (TF-IDF + LogReg)** | `unmarked` | 522 | 117 | 11 | 393 | 1 | 0 |
| **M2 (Zero-Shot LLM)** | `clean` | 522 | 110 | 0 | 0 | 351 | 61 |
| **M2 (Zero-Shot LLM)** | `marked` | 522 | 111 | 5 | 8 | 340 | 58 |
| **M2 (Zero-Shot LLM)** | `unmarked` | 522 | 104 | 10 | 26 | 318 | 64 |
| **M3 (RAG Combined)** | `clean` | 522 | 47 | 66 | 150 | 201 | 58 |
| **M3 (RAG Combined)** | `marked` | 522 | 11 | 101 | 308 | 57 | 45 |
| **M3 (RAG Combined)** | `unmarked` | 522 | 24 | 90 | 274 | 96 | 38 |
| **M4 (RAG Decoupled)** | `clean` | 522 | 127 | 1 | 91 | 303 | 0 |
| **M4 (RAG Decoupled)** | `marked` | 522 | 115 | 13 | 128 | 266 | 0 |
| **M4 (RAG Decoupled)** | `unmarked` | 522 | 123 | 5 | 110 | 284 | 0 |

---

## 4. Bootstrap Confidence Intervals

| Method | Condition | Recall (CI) | FPR (CI) | F1 Score (CI) | Precision (CI) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **M1 (TF-IDF + LogReg)** | `clean` | 0.9453 `[0.9000, 0.9832]` | 0.0025 `[0.0000, 0.0078]` | 0.9680 `[0.9427, 0.9882]` | 0.9918 `[0.9737, 1.0000]` |
| **M1 (TF-IDF + LogReg)** | `marked` | 0.9062 `[0.8516, 0.9552]` | 0.0025 `[0.0000, 0.0081]` | 0.9469 `[0.9153, 0.9736]` | 0.9915 `[0.9703, 1.0000]` |
| **M1 (TF-IDF + LogReg)** | `unmarked` | 0.9141 `[0.8621, 0.9600]` | 0.0025 `[0.0000, 0.0081]` | 0.9512 `[0.9212, 0.9773]` | 0.9915 `[0.9706, 1.0000]` |
| **M2 (Zero-Shot LLM)** | `clean` | 1.0000 `[1.0000, 1.0000]` | 1.0000 `[1.0000, 1.0000]` | 0.3853 `[0.3321, 0.4348]` | 0.2386 `[0.1991, 0.2778]` |
| **M2 (Zero-Shot LLM)** | `marked` | 0.9569 `[0.9167, 0.9912]` | 0.9770 `[0.9601, 0.9913]` | 0.3915 `[0.3395, 0.4421]` | 0.2461 `[0.2072, 0.2867]` |
| **M2 (Zero-Shot LLM)** | `unmarked` | 0.9123 `[0.8571, 0.9630]` | 0.9244 `[0.8957, 0.9506]` | 0.3881 `[0.3367, 0.4374]` | 0.2464 `[0.2077, 0.2871]` |
| **M3 (RAG Combined)** | `clean` | 0.4159 `[0.3250, 0.5096]` | 0.5726 `[0.5192, 0.6261]` | 0.2604 `[0.1989, 0.3184]` | 0.1895 `[0.1411, 0.2383]` |
| **M3 (RAG Combined)** | `marked` | 0.0982 `[0.0459, 0.1574]` | 0.1562 `[0.1190, 0.1940]` | 0.1222 `[0.0585, 0.1905]` | 0.1618 `[0.0781, 0.2576]` |
| **M3 (RAG Combined)** | `unmarked` | 0.2105 `[0.1368, 0.2925]` | 0.2595 `[0.2153, 0.3043]` | 0.2051 `[0.1366, 0.2756]` | 0.2000 `[0.1321, 0.2727]` |
| **M4 (RAG Decoupled)** | `clean` | 0.9922 `[0.9730, 1.0000]` | 0.7690 `[0.7285, 0.8094]` | 0.4552 `[0.4008, 0.5051]` | 0.2953 `[0.2512, 0.3387]` |
| **M4 (RAG Decoupled)** | `marked` | 0.8984 `[0.8444, 0.9470]` | 0.6751 `[0.6298, 0.7228]` | 0.4519 `[0.3992, 0.5048]` | 0.3018 `[0.2577, 0.3486]` |
| **M4 (RAG Decoupled)** | `unmarked` | 0.9609 `[0.9262, 0.9916]` | 0.7208 `[0.6755, 0.7643]` | 0.4598 `[0.4055, 0.5109]` | 0.3022 `[0.2580, 0.3467]` |

---

## 5. Paired McNemar Hypothesis Tests (with Holm-Bonferroni Correction)

Tests evaluate discordant classification pairs on matching original email IDs using exact two-sided binomial tests.
Both unadjusted (raw) $p$-values and Holm-Bonferroni adjusted $p$-values are reported to control the Family-Wise Error Rate (FWER) at $\alpha = 0.05$.

### A. M2 (Zero-Shot) vs M3 (RAG Combined)
| Condition | Paired N | Both Correct | M2 Correct, M3 Wrong (b) | M2 Wrong, M3 Correct (c) | Raw p-value | Holm-Bonferroni p-value | Significance (α=0.05) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `clean` | 522 | 44 | 66 | 153 | `3.9043e-09` | `3.1235e-08` | **Statistically Significant** |
| `marked` | 522 | 18 | 101 | 301 | `3.4472e-24` | `3.4472e-23` | **Statistically Significant** |
| `unmarked` | 522 | 46 | 84 | 252 | `1.2216e-20` | `1.0994e-19` | **Statistically Significant** |

### B. Marked vs Unmarked Injections (Per Method)
| Method | Paired N | Both Correct | Marked Correct, Unmarked Wrong (b) | Marked Wrong, Unmarked Correct (c) | Raw p-value | Holm-Bonferroni p-value | Significance (α=0.05) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M1 (TF-IDF + LogReg)** | 522 | 509 | 0 | 1 | `1.0000e+00` | `1.0000e+00` | Not Significant |
| **M2 (Zero-Shot LLM)** | 522 | 91 | 28 | 39 | `2.2155e-01` | `8.6260e-01` | Not Significant |
| **M3 (RAG Combined)** | 522 | 229 | 90 | 69 | `1.1243e-01` | `5.6215e-01` | Not Significant |
| **M4 (RAG Decoupled)** | 522 | 175 | 68 | 58 | `4.2279e-01` | `8.6260e-01` | Not Significant |

### C. Combined (M3) vs Decoupled (M4)
| Condition | Paired N | Both Correct | M3 Correct, M4 Wrong (b) | M3 Wrong, M4 Correct (c) | Raw p-value | Holm-Bonferroni p-value | Significance (α=0.05) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `clean` | 522 | 77 | 120 | 141 | `2.1565e-01` | `8.6260e-01` | Not Significant |
| `marked` | 522 | 113 | 206 | 130 | `3.9935e-05` | `2.7955e-04` | **Statistically Significant** |
| `unmarked` | 522 | 110 | 188 | 123 | `2.7145e-04` | `1.6287e-03` | **Statistically Significant** |

### D. Comprehensive Holm-Bonferroni Family-Wise Error Rate Summary

Rank-ordered Holm-Bonferroni step-down correction across all $m = 10$ paired McNemar hypothesis tests to control Family-Wise Error Rate (FWER):

| Rank ($k$) | Hypothesis Test Comparison | Discordant ($b / c$) | Raw $p$-value | Multiplier ($m - k + 1$) | Holm-Bonferroni $p$-value | Decision (α=0.05) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | M2 vs M3 (Marked) | 101 / 301 | `3.4472e-24` | 10 | `3.4472e-23` | **Reject $H_0$ (Significant)** |
| 2 | M2 vs M3 (Unmarked) | 84 / 252 | `1.2216e-20` | 9 | `1.0994e-19` | **Reject $H_0$ (Significant)** |
| 3 | M2 vs M3 (Clean) | 66 / 153 | `3.9043e-09` | 8 | `3.1235e-08` | **Reject $H_0$ (Significant)** |
| 4 | M3 vs M4 (Marked) | 206 / 130 | `3.9935e-05` | 7 | `2.7955e-04` | **Reject $H_0$ (Significant)** |
| 5 | M3 vs M4 (Unmarked) | 188 / 123 | `2.7145e-04` | 6 | `1.6287e-03` | **Reject $H_0$ (Significant)** |
| 6 | M3 (Marked vs Unmarked) | 90 / 69 | `1.1243e-01` | 5 | `5.6215e-01` | Fail to Reject (Not Sig.) |
| 7 | M3 vs M4 (Clean) | 120 / 141 | `2.1565e-01` | 4 | `8.6260e-01` | Fail to Reject (Not Sig.) |
| 8 | M2 (Marked vs Unmarked) | 28 / 39 | `2.2155e-01` | 3 | `8.6260e-01` | Fail to Reject (Not Sig.) |
| 9 | M4 (Marked vs Unmarked) | 68 / 58 | `4.2279e-01` | 2 | `8.6260e-01` | Fail to Reject (Not Sig.) |
| 10 | M1 (Marked vs Unmarked) | 0 / 1 | `1.0000e+00` | 1 | `1.0000e+00` | Fail to Reject (Not Sig.) |

---

## 6. Detailed Architectural Insights

### 1. Invariance of Classical Feature Baselines (M1)
The TF-IDF + LogisticRegression baseline has clean recall 94.53% and clean FPR 0.25%. Marked recall is 90.62% and unmarked recall is 91.41%; the computed bootstrap-bounded invariance rule holds for both injected conditions.

### 2. Single-Call LLMs and Free-Form Reasoning Evasion (M2, M3)
M2 meets the computed near-degenerate clean-output rule. For M3, recall changes from 41.59% on clean data to 21.05% under unmarked injection, a change of 20.54%; this is a same-method clean-to-unmarked comparison.

### 3. The False-Alarm Tax of Decoupled Staged Inference (M4)
Decoupled inference changes M4 recall from 99.22% on clean data to 96.09% under unmarked injection. For FPR, its clean FPR was already 76.90%, compared with 72.08% under unmarked injection; the available summary does not support calling this injection-induced without a significant control-only paired test.

---

## 7. Limitations

1. **Local Model Scale**: Experiments utilize `qwen2.5:0.5b` running on local Metal hardware via Ollama. While this demonstrates foundational mechanisms at sub-billion parameter scale, larger frontier models (e.g. 70B+ or closed API models) may exhibit different reasoning calibration and instruction-following robustness.
2. **Fixed Injection Templates**: Injection payloads were synthesized using three natural blending styles (footer disclaimers, forwarding headers, signature blocks). Advanced adversaries employing adaptive, multi-turn, or polyglot encodings may identify alternative bypass vectors.
3. **Inference Latency & Cost**: Two-call decoupling increases API request volume. In high-throughput enterprise mail gateways, the measured latency and control false-positive behavior require secondary triage before deployment.
4. **Corpus Distribution**: The baseline corpus combines Nazario phishing archives and Enron legitimate emails. Domain shifts to modern enterprise collaboration messaging (e.g., Slack, Microsoft Teams) may exhibit different baseline token priors.
