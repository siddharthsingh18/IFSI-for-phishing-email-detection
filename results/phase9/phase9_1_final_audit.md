# Phase 9.1: Final Research Candidate Freeze & Reproducibility Audit Report

## 1. Executive Summary

Phase 9.1 concludes the architectural investigation cycle of the IFSI Phishing Email Detection Research Program following Phase 8.1C. This audit establishes an immutable cryptographic freeze of the recommended research candidate, verifies all 12 protected baseline invariants, registers complete experimental provenance across Phases 4 through 7, and validates that the host environment is 100% reproducible with zero missing dependencies.

In accordance with strict research governance and freeze rules:
- **Zero code implementations, datasets, predictions, or RAG indexes were modified.**
- **Zero model inferences or retraining runs were conducted.**
- **Zero git commits or pushes were executed.**
- **The recommended research candidate is frozen strictly for independent evaluation; production promotion remains unauthorized.**

---

## 2. Selected Research Candidate

| Attribute | Specification |
| :--- | :--- |
| **Selected Architecture** | **Phase 7 Config B (Candidate Snapshot)** |
| **Execution Engine** | [`src/experiments/phase7_domain_precision/engine_v4.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/experiments/phase7_domain_precision/engine_v4.py) (`b3c6e9b86d664fc911c82f80e81bff7686cbd2032352fd9326b5e0c40f689b01`) |
| **Domain Telemetry Subsystem**| [`src/experiments/phase7_domain_precision/domain_analyzer_v3.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/experiments/phase7_domain_precision/domain_analyzer_v3.py) (`7abde00e3795c7e02504d60ad1f631e101eeefb7b9566c70b73bc02b25f32525`) |
| **Sanitizer Subsystem** | [`src/experiments/phase5_a1_optimization/sanitizer_v2.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/experiments/phase5_a1_optimization/sanitizer_v2.py) (`b51f938ca3a3b4e2b9f4212d4178b58cd47c3f8b4a48a0ba9a0539be4759aa55`) |
| **Stage 1 Prompt** | `STAGE1_COMPACT_PROMPT` in `prompts_v2.py` (String SHA-256: `9b65a597d47cf60eb4a5321e1cd1d867a8925ffa485cf565a844281d7911a1c6`) |
| **Stage 2 Prompt** | `STAGE2_WITH_DOMAIN_EVIDENCE_PROMPT` in `prompts_v3.py` (String SHA-256: `ac23b52d01d8dc9bde352f947e6468118987e4eeb9f817376977a9884a6493bf`) |
| **RAG Retrieval Strategy** | Standard Top-3 Nearest Neighbors over `results/rag_index_clean/index.faiss` |
| **Primary Model & Host** | `qwen3.5:4b` running on local Ollama service (`v0.40.13`) at `http://127.0.0.1:11434` |
| **Deterministic Parameters** | `temperature: 0.0`, `num_predict: 512`, `format: "json"`, `think: false`, `timeout: 60.0s` |
| **Benchmark Empirical Record**| **Accuracy: 99.58%** (239/240), **Phishing Recall: 100.0%** (110/110), **Active Inj Containment: 100.0%** (50/50), **FPR: 0.77%** (1/130), **Mean Latency: 4.09s** |
| **Promotion Readiness** | **NOT PRODUCTION READY**. Candidate is frozen strictly for large-scale external evaluation. |

---

## 3. Protected Baseline Invariance Audit

All 12 protected baseline components were verified against their authorized reference digests. Every component matches with zero discrepancies:

| # | Protected Baseline Component | Target File Path | Reference Expected Hash | Verified Actual Hash | Status |
| :-: | :--- | :--- | :--- | :--- | :-: |
| 1 | Production Baseline M4 | `src/core/inference.py` | `aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506` | `aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506` | **MATCH** |
| 2 | Frozen A1 Implementation | `src/core/inference_m4_v2.py` | `fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37` | `fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37` | **MATCH** |
| 3 | Clean FAISS Vector Index | `results/rag_index_clean/index.faiss` | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` | **MATCH** |
| 4 | Clean FAISS Metadata | `results/rag_index_clean/metadata.json` | `4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece` | `4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece` | **MATCH** |
| 5 | Phase 5 Sanitizer V2 | `src/experiments/phase5_a1_optimization/sanitizer_v2.py` | `b51f938ca3a3b4e2b9f4212d4178b58cd47c3f8b4a48a0ba9a0539be4759aa55` | `b51f938ca3a3b4e2b9f4212d4178b58cd47c3f8b4a48a0ba9a0539be4759aa55` | **MATCH** |
| 6 | Phase 6 Domain Analyzer V2 | `src/experiments/phase6_domain_evidence/domain_analyzer_v2.py` | `e27aefb062350e758840aedd4ecb5eb29e43ae19b61f228a3c864aa3df59fc44` | `e27aefb062350e758840aedd4ecb5eb29e43ae19b61f228a3c864aa3df59fc44` | **MATCH** |
| 7 | Phase 6 Engine V3 | `src/experiments/phase6_domain_evidence/engine_v3.py` | `dbe5150dc7365b6a560b09f9056129fc24d50e0ebfa13c53719c6336263ae8a8` | `dbe5150dc7365b6a560b09f9056129fc24d50e0ebfa13c53719c6336263ae8a8` | **MATCH** |
| 8 | Phase 7 Domain Analyzer V3 | `src/experiments/phase7_domain_precision/domain_analyzer_v3.py` | `7abde00e3795c7e02504d60ad1f631e101eeefb7b9566c70b73bc02b25f32525` | `7abde00e3795c7e02504d60ad1f631e101eeefb7b9566c70b73bc02b25f32525` | **MATCH** |
| 9 | Phase 7 Engine V4 | `src/experiments/phase7_domain_precision/engine_v4.py` | `b3c6e9b86d664fc911c82f80e81bff7686cbd2032352fd9326b5e0c40f689b01` | `b3c6e9b86d664fc911c82f80e81bff7686cbd2032352fd9326b5e0c40f689b01` | **MATCH** |
| 10 | Phase 5 Regression 160 | `data/evaluation/phase5_regression_160.jsonl` | `325bf42f244120667aa00051ed0e2086b02645958c138699cd3bd32d615fc606` | `325bf42f244120667aa00051ed0e2086b02645958c138699cd3bd32d615fc606` | **MATCH** |
| 11 | Phase 6 Domain Challenge 80 | `data/evaluation/phase6_domain_challenge.jsonl` | `02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7` | `02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7` | **MATCH** |
| 12 | Phase 7 Precision Challenge 80 | `data/evaluation/phase7_precision_challenge.jsonl` | `a6ea7aa12d5bc997939d9cd8c721b728fc6fc22cc2a6aab0ef38912f7fb71c1c` | `a6ea7aa12d5bc997939d9cd8c721b728fc6fc22cc2a6aab0ef38912f7fb71c1c` | **MATCH** |

---

## 4. Evaluation Datasets & Index Hashes

| Dataset Identifier | File Path | Record Count ($N$) | File Size | SHA-256 Digest |
| :--- | :--- | :---: | :---: | :--- |
| **Phase 4 Live Benchmark V2** | `data/evaluation/live_benchmark_v2.jsonl` | 150 | 127,778 B | `1c762180451b90c8ad4e0500b5881526a69db3c6a69bffd09e3b7ed2ba0463e9` |
| **Phase 4 Held-Out Benchmark V1** | `data/evaluation/heldout_benchmark_v1.jsonl` | 100 | 73,096 B | `42722ce81deffda02c788777af6aef2ce4b550fbba3ff1115f57a3a9c943f0c9` |
| **A1 Generalization Validation V1** | `data/evaluation/a1_generalization_v1.jsonl` | 500 | 693,874 B | `ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336` |
| **Phase 5 Regression 160** | `data/evaluation/phase5_regression_160.jsonl` | 160 | 232,240 B | `325bf42f244120667aa00051ed0e2086b02645958c138699cd3bd32d615fc606` |
| **Phase 6 Domain Challenge** | `data/evaluation/phase6_domain_challenge.jsonl` | 40 | 38,611 B | `02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7` |
| **Phase 7 Precision Challenge** | `data/evaluation/phase7_precision_challenge.jsonl` | 40 | 37,525 B | `a6ea7aa12d5bc997939d9cd8c721b728fc6fc22cc2a6aab0ef38912f7fb71c1c` |
| **Clean FAISS Vector Index** | `results/rag_index_clean/index.faiss` | 1,321 vecs | 2,029,101 B | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` |
| **Clean FAISS Metadata** | `results/rag_index_clean/metadata.json` | 1,321 meta | 1,221,623 B | `4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece` |

---

## 5. Prediction & Metrics Artifact Inventory

| Experiment Artifact | File Path | Line Count | File Size | SHA-256 Digest |
| :--- | :--- | :---: | :---: | :--- |
| **Phase 4 Predictions** | `results/m4_ablation_v1/predictions.jsonl` | 2,250 | 3,585,973 B | `4a0cb0afdda10d22420d39a2b9fff754287f9a054a9c32485a517a70a003b449` |
| **Phase 4 Metrics** | `results/m4_ablation_v1/metrics.json` | — | 83,153 B | `1936a70641460248d1901bef4306abe9742148a934b42c02aef798b9c97a88b8` |
| **Phase 4 Verified Metrics** | `results/m4_ablation_v1/independently_verified_metrics.json` | — | 69,260 B | `9dbf7689f97a784046e9981451ecc70a7c699df93f240133eb58aeb39a7735d3` |
| **A1 Generalization Predictions** | `results/a1_generalization_v1/predictions.jsonl` | 1,000 | 1,568,619 B | `7b1645eeae682bfbdaffb28dce7930ec71b2ccbf3cc519417ed99c4b9459589e` |
| **A1 Generalization Metrics** | `results/a1_generalization_v1/metrics.json` | — | 24,170 B | `d7e7d4c840fb098ce480f386b42f2e66e8ce3fe7d037623929511da2e89d8931` |
| **Phase 5 Predictions** | `results/phase5_a1_sanitizer_latency/predictions.jsonl` | 320 | 633,045 B | `cf569e133a1aa3a39f8ed2b725ef5e34ce8c140be630b6b2851115d7db15847d` |
| **Phase 5 Regression Metrics** | `results/phase5_a1_sanitizer_latency/regression_metrics.json` | — | 3,895 B | `40302cfc01fa36983f6c62fa475cf33b963801f3ce1963de0d7e181c160cfc86` |
| **Phase 5 Independent Metrics**| `results/phase5_a1_sanitizer_latency/independent_metrics.json` | — | 6,151 B | `1678fb135d51a1380e5ad8aeae04f2f66a9bede02d5dbedfa76bbd1163ba81dd` |
| **Phase 6 Predictions** | `results/phase6_domain_evidence/predictions.jsonl` | 440 | 871,067 B | `242df69af3883d1fdac6afe4910cf9a277a1693ed700e501b0832ba92e1b246b` |
| **Phase 6 Independent Metrics**| `results/phase6_domain_evidence/independent_metrics.json` | — | 7,967 B | `9842cec270ceedbeb44dbdb207e7d6e7a6da0896cf7ea68cca386673cbd2f718` |
| **Phase 7 Predictions** | `results/phase7_domain_precision/predictions.jsonl` | 560 | 841,967 B | `2e2efbcacc597afcccd060043618ad33cfc6372d42b23b477c749c804daea724` |
| **Phase 7 Independent Metrics**| `results/phase7_domain_precision/independent_metrics.json` | — | 11,950 B | `1d576aaeb18922b2af4eaaacfac78a57691c8228a355f1801d6b3e0f678fe45d` |
| **Phase 7 Final Audit Summary**| `results/phase7_final_audit/audit_summary.json` | — | 3,377 B | `e9b24cf2e5b88d32412cb898e1dbb2cb9641afe2a61cdb87b5a724e0276fd7e9` |

---

## 6. Host Environment & Dependency Verification Audit

- **Python Runtime**: `Python 3.13.9` (64-bit AMD64) on Windows 11 Enterprise (Build 26200).
- **Inference Service**: Ollama daemon active at `http://127.0.0.1:11434` (`version 0.40.13`).
- **Installed Primary Models**: `qwen3.5:4b`, `qwen2.5:0.5b`, `gemma3:4b` confirmed pulled and accessible locally.
- **Critical Libraries**:
  - `faiss-cpu == 1.15.1` (Verified functional)
  - `sentence-transformers == 6.1.0` (Verified functional)
  - `torch == 2.14.1+cpu` (Verified functional)
  - `httpx == 0.28.1` (Verified functional)
  - `pydantic == 2.14.1` (Verified functional)
  - `fastapi == 0.141.1` (Verified functional)
  - `scikit-learn == 1.7.2` (Verified functional)
  - `numpy == 2.3.5` (Verified functional)
  - `tqdm == 4.67.1` (Verified functional)
- **Dependency Status**: **ZERO MISSING OR UNVERIFIABLE DEPENDENCIES**.

---

## 7. Deliverables & Artifacts Generated in Phase 9.1

All deliverables for Phase 9.1 were written under `results/phase9/`:

1. [final_candidate_inventory.md](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase9/final_candidate_inventory.md) — Comprehensive technical inventory of all candidate architectures, role distinctions, and technical lineage.
2. [reproducibility_manifest.md](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase9/reproducibility_manifest.md) — Cryptographic manifest of source codes, models, parameters, prompts, sanitizer, domain analyzer, and runtime dependencies.
3. [experiment_provenance_matrix.md](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase9/experiment_provenance_matrix.md) — Cross-phase mapping linking datasets, configurations, predictions, and metrics across Phases 4–7.
4. [candidate_selection_decision.md](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase9/candidate_selection_decision.md) — Multi-criteria decision matrix justifying selection of Phase 7 Config B as the frozen research candidate.
5. [phase9_1_final_audit.md](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase9/phase9_1_final_audit.md) — Master audit report and governance sign-off.

---

## 8. Mandatory Pre-Flight Verification Checklist Before Phase 9.2

Before executing Phase 9.2 (Large-Scale Independent Evaluation Execution):

- [x] Phase 7 Config B frozen and cryptographically identified (`Engine V4` + `Domain Analyzer V3`).
- [x] All 12 baseline hashes verified and intact.
- [x] All 5 historical evaluation prediction logs intact and hash-verified.
- [x] No modifications to production M4 or frozen A1.
- [x] Clean FAISS index untouched (1,321 vectors).
- [x] Zero uncommitted git changes to code or baseline data.
- [x] Host environment dependencies fully verified.
- [x] Research candidate acknowledged as **frozen research candidate, not production-promoted**.
