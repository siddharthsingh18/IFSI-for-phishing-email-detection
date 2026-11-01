# IFSI Phase 5 — Forensic Integrity & Invariance Audit Report

**Experiment:** IFSI Phishing Email Detection — Phase 5  
**Auditor:** Independent Antigravity Forensic Auditor  
**Date:** 2026-11-01  

---

## 1. Objective & Scope

This forensic audit verifies that Phase 5 (Sanitizer Reliability & Stage 1 Latency Optimization) strictly adhered to all mandatory protection constraints:
1. **Production Code Immutability:** Production M4 (`src/core/inference.py`) must remain untouched.
2. **Frozen Architecture Immutability:** Frozen A1 (`src/core/inference_m4_v2.py`) must remain untouched.
3. **Historical Benchmark Immutability:** Historical datasets, predictions, and reports in `results/a1_generalization_v1/` and `results/m4_ablation_v1/` must remain unchanged.
4. **Clean FAISS Index Immutability:** The clean FAISS index (`results/rag_index_clean/index.faiss`) must remain untouched; no evaluation samples may be added to any index.
5. **Stage 2 Invariance:** Stage 2 prompt (`STAGE2_WITH_SANITIZATION_ONLY`), directives, and standard RAG retrieval mode must remain identical between Frozen A1 and Optimized A1.
6. **Isolated Development:** All experimental implementations must reside strictly within `src/experiments/phase5_a1_optimization/` and `results/phase5_a1_sanitizer_latency/`.

---

## 2. SHA-256 Hash Verification of Protected Files

The following cryptographic hashes were computed before and verified after the experimental work:

| Protected File Path | Baseline SHA-256 Hash | Post-Run SHA-256 Hash | Status |
| :--- | :--- | :--- | :---: |
| `src/core/inference.py` | `aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506` | `aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506` | **INVARIANT** |
| `src/core/inference_m4_v2.py` | `fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37` | `fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37` | **INVARIANT** |
| `results/rag_index_clean/index.faiss` | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` | **INVARIANT** |
| `data/evaluation/a1_generalization_v1.jsonl` | `ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336` | `ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336` | **INVARIANT** |
| `results/a1_generalization_v1/predictions.jsonl` | `7b1645eeae682bfbdaffb28dce7930ec71b2ccbf3cc519417ed99c4b9459589e` | `7b1645eeae682bfbdaffb28dce7930ec71b2ccbf3cc519417ed99c4b9459589e` | **INVARIANT** |
| `results/m4_ablation_v1/predictions.jsonl` | `4a0cb0afdda10d22420d39a2b9fff754287f9a054a9c32485a517a70a003b449` | `4a0cb0afdda10d22420d39a2b9fff754287f9a054a9c32485a517a70a003b449` | **INVARIANT** |

---

## 3. Dataset & FAISS Vector Store Isolation

1. **Clean FAISS Index:** The index contains exactly 1,321 vectors, identical to its initial build state. Zero evaluation samples were vectorized or ingested into the index.
2. **Regression Benchmark Dataset:** The 160-sample regression subset was constructed deterministically from `data/evaluation/a1_generalization_v1.jsonl` and stored in a new file `data/evaluation/phase5_regression_160.jsonl`. The original benchmark file was opened exclusively in read-only mode (`"r"`).

---

## 4. Execution Controls

- **LLM Engine:** Ollama running `qwen3.5:4b` locally via `http://127.0.0.1:11434`.
- **Inference Parameters:** `temperature = 0.0`, `num_predict = 512`, `format = json`, `think = False`.
- **Evaluation Order:** Both configurations were evaluated sequentially to prevent GPU memory spikes or thread contention.
- **Fail-Safe Integrity:** The fail-safe trigger in Sanitizer V2 was verified: unresolved spans are never marked safe and are strictly routed to `security_action = "manual_review"`.

