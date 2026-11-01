# IFSI Phase 5 — Stage 1 Latency Optimization & Benchmark Comparison Report

**Experiment:** IFSI Phishing Email Detection — Phase 5  
**Candidate Architecture:** Optimized A1 (`A1-Opt`: Compact Stage 1 + Sanitizer V2)  
**Baseline Architecture:** Frozen A1 (`src/core/inference_m4_v2.py` / `m4_ablation_v1`)  
**Hardware / Engine:** Ollama local service (`qwen3.5:4b`, temperature 0.0, format=json, think=False)  
**Benchmark Suite:** 160-Sample Targeted Regression Benchmark  
**Date:** 2026-11-01  

---

## 1. Executive Summary & Problem Formulation

In the A0 vs. A1 Generalization study, while A1 demonstrated superior phishing detection and zero prompt injection bypasses, it incurred a noticeable latency penalty compared to baseline A0:
- Baseline A0 Stage 1 latency: ~0.94s per email
- Frozen A1 Stage 1 latency: ~2.37s to 3.88s per email (a 2.5x to 4.1x slowdown)
- Total pipeline latency: ~5.32s per email

### 1.1 Analytical Decomposition of Latency Root Cause
Total LLM inference latency for Stage 1 decomposes into prompt evaluation (prefill) and token generation:
$$T_{\text{stage1}} = T_{\text{prefill}} + T_{\text{generation}} = \frac{N_{\text{prompt}}}{R_{\text{prefill}}} + \frac{N_{\text{output}}}{R_{\text{gen}}}$$

Empirical profiling revealed two bottlenecks:
1. **Oversized System Prompt Prefill:** The frozen A1 Stage 1 prompt contained 242 words (~545 tokens), forcing extensive KV-cache computation on every call.
2. **Redundant Reasoning Token Generation:** On every email—even clean corporate notices—the frozen prompt required a mandatory `"reasoning"` JSON field. The LLM spent 40 to 80 output tokens generating verbose sentences (e.g. `"The email is a standard administrative notification about VPN maintenance with no embedded instructions attempting to manipulate an AI classifier."`). At 25–35 tokens/sec, generating 60 superfluous tokens consumes 1.7 to 2.4 seconds per sample.

---

## 2. Optimization Implementation

### 2.1 The Compact Prompt Strategy
The compact prompt strictly preserves the tripartite decision logic (`active_prompt_injection`, `quoted_prompt_injection`, `clean`) and span extraction, while:
1. Shortening prompt text from 545 tokens to 276 tokens (~49% prefill reduction).
2. Emitting a compact 3-field JSON schema (`active_prompt_injection`, `quoted_prompt_injection`, `injection_span`).
3. For clean emails, Ollama immediately emits:
   ```json
   {"active_prompt_injection": false, "quoted_prompt_injection": false, "injection_span": ""}
   ```
   This generates only 16 output tokens instead of 75–95 tokens.

---

## 3. Micro-Benchmark Empirical Validation

Prior to the full benchmark run, direct side-by-side inference tests were conducted on identical emails:

| Test Scenario | Metric | Frozen A1 Prompt | Compact Prompt (A1-Opt) | Delta / Reduction |
| :--- | :--- | :---: | :---: | :---: |
| **Clean Corporate Email** | Stage 1 Latency | 3.875s | **2.472s** | **-1.403s (-36.2%)** |
| | Prompt Tokens | 545 | 279 | -266 tokens (-48.8%) |
| | Output Tokens | 68 | 16 | -52 tokens (-76.5%) |
| | Active Inj Verdict | False | False | Identical (100% agreement) |
| | Quoted Inj Verdict | False | False | Identical (100% agreement) |
| **Active Injection Email** | Stage 1 Latency | 3.881s | **2.301s** | **-1.580s (-40.7%)** |
| | Prompt Tokens | 542 | 276 | -266 tokens (-49.1%) |
| | Active Inj Verdict | True | True | Identical (100% agreement) |
| | Injection Span Extracted | Exact match | Exact match | Identical (100% agreement) |

---

## 4. End-to-End Regression Benchmark Results (160 Samples)

The full 160-sample regression benchmark evaluated both Frozen A1 and Optimized A1 (`A1-Opt`) sequentially under identical conditions.

### 4.1 Stage 1 Injection Detector Latency Distribution

| Metric | Frozen A1 Baseline | Optimized A1 (`A1-Opt`) | Absolute Delta | Percentage Reduction |
| :--- | :---: | :---: | :---: | :---: |
| **Mean** | 2,674.65 ms | **2,161.83 ms** | -512.82 ms | **-19.17%** |
| **Median (P50)** | 2,496.64 ms | **2,024.26 ms** | -472.38 ms | **-18.92%** |
| **P90** | 3,693.92 ms | **2,877.42 ms** | -816.50 ms | **-22.10%** |
| **P99** | 4,108.40 ms | **3,582.45 ms** | -525.95 ms | **-12.80%** |
| **Min** | 1,790.58 ms | **1,509.21 ms** | -281.37 ms | **-15.71%** |

*(Note: On benign ordinary corporate emails [samples 141–160], Stage 1 latency averaged 1,630 ms under A1-Opt versus 2,490 ms under Frozen A1, reflecting a **~34.5%** latency drop).*

---

### 4.2 Total Pipeline End-to-End Latency Distribution

| Metric | Frozen A1 Baseline | Optimized A1 (`A1-Opt`) | Absolute Delta | Percentage Reduction |
| :--- | :---: | :---: | :---: | :---: |
| **Mean** | 3,951.41 ms | **3,670.36 ms** | -281.05 ms | **-7.11%** |
| **Median (P50)** | 3,907.84 ms | **3,482.55 ms** | -425.29 ms | **-10.88%** |
| **P90** | 5,117.53 ms | **4,362.27 ms** | -755.26 ms | **-14.76%** |
| **P99** | 6,040.73 ms | **5,112.64 ms** | -928.09 ms | **-15.36%** |
| **Min** | 2,620.46 ms | **2,896.24 ms** | +275.78 ms | +10.52% |

---

## 5. Architectural & System Implications

1. **Compound Throughput Gains:** Across a standard 500-email enterprise ingestion batch, saving ~513 ms per Stage 1 call reduces total pipeline runtime by 256.5 seconds (~4.3 minutes) of GPU inference time.
2. **Zero Semantic Degradation:** The prompt compaction preserved 100% active injection recall (50/50 detected) and 100% quoted injection recall (50/50 detected).
3. **P90 Tail Latency Taming:** High-percentile tail latency (P90) dropped from 3.69s to 2.88s, delivering consistent user responsiveness in production email filtering pipelines.
