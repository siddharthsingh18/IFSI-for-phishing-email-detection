# Phase 6 Implementation & Benchmark Execution Report

**Project:** IFSI Phishing Email Detection  
**Experiment:** Phase 6 — Domain Evidence Integration Study  
**Date:** November 2026  
**Status:** Completed & Independently Verified  

---

## 1. Executive Summary

Phase 6 investigated whether carefully designed structured domain telemetry could resolve the persistent sophisticated phishing blind spot identified in Phase 5 without degrading active prompt-injection defense, quoted injection handling, or inference latency.

A fully isolated experimental package was implemented under `src/experiments/phase6_domain_evidence/` and evaluated across 200 distinct email samples (160 from the Phase 5 regression suite and 40 from the new Phase 6 domain challenge benchmark).

The experiment produced **440 total prediction records** recorded in `results/phase6_domain_evidence/predictions.jsonl`.

### Key Findings
1. **Blind Spot Resolved:** On the 20 sophisticated phishing samples from the regression suite where Frozen A1 and A1-Opt scored **0.0% recall (0/20)**, Config B (Domain Evidence Enabled) achieved **100.0% recall (20/20)**.
2. **Perfect Phishing Recall Across Full Suite:** Config B achieved **100.0% recall (90/90)** across all phishing attacks in the 200-sample corpus (compared to 70.0% in Config A), representing a **+30.00% absolute increase in recall**.
3. **High Overall Accuracy:** Config B attained **98.50% overall accuracy** (197/200), improving by **+12.00%** over Config A (86.50%). On the 160 regression samples, accuracy reached **99.38%** (159/160).
4. **Security Containment Maintained:** 100% active prompt injections were contained (50/50 quarantined or blocked), and 100% quoted injections were preserved without false alarms (50/50 allowed).
5. **Boundary Conditions Identified:** The domain evidence module produced 3 false positives out of 110 legitimate emails (FPR: 2.73%) due to enterprise third-party domain aliases (`myworkday.com`, `amazon-business.com`) and internal corporate discussions mentioning third-party vendor names (`concur-travel@enterprise-corp.com`).

---

## 2. Component Implementation Architecture

All new code was strictly quarantined under `src/experiments/phase6_domain_evidence/`:

- `domain_analyzer_v2.py`: Deterministically extracts sender display names, sender domains, reply-to routing, extracted destination URLs, registered domains, and checks for synthetic lookalikes, chained administrative keywords, and cross-domain links. Emits neutral, factual structural evidence without subjective risk scores or false reassurances.
- `prompts_v3.py`: Houses `STAGE1_COMPACT_PROMPT` (Phase 5 fast injection detector), `STAGE2_FROZEN_PROMPT` (used by Config A and Config C), and `STAGE2_WITH_DOMAIN_EVIDENCE_PROMPT` (used by Config B).
- `engine_v3.py`: Modular two-stage inference engine implementing Config A, Config B, and Config C with standardized parameter controls (`qwen3.5:4b`, temp=0.0, max_tokens=512, top-3 standard RAG).
- `tools/build_phase6_domain_challenge.py`: Generated 40 focused domain challenge samples with verified zero overlap against the clean FAISS index or previous benchmarks.
- `tools/run_phase6_benchmark.py`: Sequential benchmark runner with per-sample checkpointing.
- `tools/compute_phase6_metrics.py`: Independent metrics calculator reading directly from raw `predictions.jsonl`.

---

## 3. Cryptographic Invariance of Protected Files

Before and after execution, cryptographic SHA-256 hashes of all protected files were audited:

| Component | Path | SHA-256 Hash | Integrity Status |
| :--- | :--- | :--- | :---: |
| **Production Baseline** | `src/core/inference.py` | `aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506` | UNCHANGED |
| **Frozen A1 Candidate** | `src/core/inference_m4_v2.py` | `fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37` | UNCHANGED |
| **Clean FAISS Index** | `results/rag_index_clean/index.faiss` | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` | UNCHANGED |
| **Phase 5 Regression Suite** | `data/evaluation/phase5_regression_160.jsonl` | `5c84a56a6db9049444458f33ce9bc54fc4813589bdf013bf377e8da928236111` | UNCHANGED |
| **Phase 6 Domain Challenge** | `data/evaluation/phase6_domain_challenge.jsonl` | `02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7` | VERIFIED |

---

## 4. Benchmark Execution Summary

- Total Sequential Predictions: **280 runs** (40 Config A, 200 Config B, 40 Config C) + **160 synced Config A baseline records**.
- Total Records in `predictions.jsonl`: **440 records**.
- Total Inference Runtime: **1,225.88 seconds (20.43 minutes)**.
- Inference Failure Count: **0 failures** (100% valid JSON responses across all stages).

