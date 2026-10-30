# Live Benchmark Comparison: V1 (40 Samples) vs V2 (150 Samples)

This document contrasts the performance of all four architectures across the initial 40-sample Live Benchmark V1 and the comprehensive 150-sample Live Benchmark V2.

---

## 1. Metric Delta Comparison Table

| Architecture | Benchmark | Samples | Accuracy | Precision | Recall | F1-Score | FPR | FNR | Avg Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| M1: TF-IDF + Logistic Regression | **V1** | 40 | 85.0% | 81.8% | 90.0% | 85.7% | 20.0% | 10.0% | 0.037s |
| M1: TF-IDF + Logistic Regression | **V2** | 150 | **76.0%** | 74.7% | **78.7%** | **76.6%** | 26.7% | 21.3% | 0.015s |
| | | | | | | | | | |
| M2: Zero-Shot LLM | **V1** | 40 | 97.5% | 95.2% | 100.0% | 97.6% | 5.0% | 0.0% | 4.678s |
| M2: Zero-Shot LLM | **V2** | 150 | **90.7%** | 84.3% | **100.0%** | **91.5%** | 18.7% | 0.0% | 3.941s |
| | | | | | | | | | |
| M3: RAG Combined (Single-Call) | **V1** | 40 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 0.0% | 5.046s |
| M3: RAG Combined (Single-Call) | **V2** | 150 | **93.3%** | 92.2% | **94.7%** | **93.4%** | 8.0% | 5.3% | 4.090s |
| | | | | | | | | | |
| M4: Decoupled Two-Stage RAG | **V1** | 40 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 0.0% | 3.012s |
| M4: Decoupled Two-Stage RAG | **V2** | 150 | **95.3%** | 96.0% | **94.7%** | **95.3%** | 4.0% | 5.3% | 2.053s |
| | | | | | | | | | |

---

## 2. Key Observations on Generalization and Robustness

1. **Adversarial Stress Impact:** V1 contained only 2 prompt injections, whereas V2 introduces 30 adversarial samples including multilingual, obfuscated, and benign-with-injection patterns.
2. **Lexical False Positive Stress:** Group B (Difficult Genuine) specifically tests whether models overreact to keywords like 'urgent', 'password reset', 'wire transfer', and 'tax forms' in authentic corporate emails.
3. **Sophisticated Phishing Detection:** Group D (Sophisticated Phishing) highlights the limitations of purely statistical lexical models (M1) when confronting low-urgency, text-only Business Email Compromise.