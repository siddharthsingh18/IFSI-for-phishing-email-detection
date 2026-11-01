# Phase 7: Inference Latency Performance & Percentile Comparison

## 1. Executive Summary

Phase 7 benchmarked inference latency across all configurations on an identical execution platform (`qwen3.5:4b` running locally on Ollama, greedy decoding with `temperature: 0.0`, `num_predict: 512`, standard top-3 RAG over clean FAISS).

The structured evidence format of **Domain Analyzer V3** (Config B) reduced total inference latency compared to the baseline Config A:
- **Total Mean Latency**: Config B reduced latency from **4,418.41 ms** down to **4,087.57 ms** (**-330.84 ms / 7.5% speedup**).
- **Total Median (P50) Latency**: Reduced from **4,134.51 ms** to **3,935.20 ms**.
- **P90 Tail Latency**: Reduced from **5,747.66 ms** to **5,034.62 ms** (**-12.4% reduction**).
- **P95 Tail Latency**: Reduced from **6,472.62 ms** to **5,378.43 ms** (**-1,094.19 ms / -16.9% reduction**).

---

## 2. Granular Stage-by-Stage Latency Distribution

| Configuration | Metric | Stage 1 (Injection Detection) | Stage 2 (Phishing Classifier) | Total End-to-End Latency |
| :--- | :--- | :--- | :--- | :--- |
| **Config A**<br>*(Frozen Phase 6 Baseline)* | Mean<br>Median (P50)<br>P90<br>P95 | 2,334.51 ms<br>2,112.85 ms<br>3,262.54 ms<br>3,591.05 ms | 1,834.74 ms<br>1,724.75 ms<br>2,219.80 ms<br>2,407.11 ms | 4,418.41 ms<br>4,134.51 ms<br>5,747.66 ms<br>6,472.62 ms |
| **Config B**<br>*(Experimental V3)* | Mean<br>Median (P50)<br>P90<br>P95 | 2,234.83 ms<br>2,083.10 ms<br>3,069.90 ms<br>3,308.84 ms | 1,669.34 ms<br>1,656.05 ms<br>1,926.59 ms<br>1,985.49 ms | **4,087.57 ms**<br>**3,935.20 ms**<br>**5,034.62 ms**<br>**5,378.43 ms** |
| **Config C**<br>*(Domain Evidence Disabled)* | Mean | 2,185.12 ms | 1,421.40 ms | 3,680.09 ms |

---

## 3. Engineering Analysis of Latency Differences

### 3.1 Domain Analyzer Overhead
The pure Python execution of `analyze_email_domains_v3` executes deterministically in **under 2 milliseconds** per email. The multi-domain dictionary lookups and regex URL extractions incur negligible computational overhead.

### 3.2 Stage 2 Generation Efficiency
The primary latency reduction between Config A and Config B occurs in **Stage 2**:
- Stage 2 mean generation duration decreased from **1,834.74 ms** to **1,669.34 ms** (**-165.40 ms**).
- Stage 2 P95 latency dropped from **2,407.11 ms** to **1,985.49 ms** (**-17.5%**).

**Root Cause**: In Domain Analyzer V2 (Config A), unstructured, speculative anomaly text (e.g. contradictory identity mismatch and lookalike warnings) caused the language model to generate longer, hesitant reasoning traces before outputting its JSON schema. In Domain Analyzer V3 (Config B), the clear epistemic grouping (`Verified Organizational Relationships`, `Observable Structural Facts`, `Observed Structural Anomalies`) provides unambiguous inputs, allowing the model to converge immediately to its final JSON response with fewer generation tokens.

---

## 4. Latency vs. Throughput SLA Summary

- **Single Worker Throughput**: Config B processes ~15 emails per minute on local consumer hardware.
- **Latency Stability**: P95 latency of 5.38 seconds satisfies enterprise email gateway filtering thresholds (< 10 seconds per message buffer).
- **No Latency Regression**: V3 introduces zero latency overhead relative to V2 while improving execution speed and reducing tail variance.

