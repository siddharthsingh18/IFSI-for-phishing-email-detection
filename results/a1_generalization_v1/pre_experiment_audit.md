# Phase 1 Pre-Experiment Audit: A1 Generalization Validation V1

**Date:** November 1, 2026  
**Auditor:** Independent Research Validation Agent  
**Project:** `D:\Project\IFSI-for-phishing-email-detection`  
**Milestone:** A1 Generalization Validation V1  
**Objective:** Independent empirical validation of A1 architecture generalization against A0 baseline on unseen emails  

---

## 1. Architectural Specifications & Frozen Configurations

### 1.1 Architecture A0: Production M4 Baseline
- **Role:** Production reference baseline
- **Implementation Source:** `src/core/inference.py` (`classify_email_m4`) and `src/experiments/m4_ablation_v1/ablation_engine.py` (Config `A0`)
- **Stage 1 Injection Detector:** Baseline binary detector (`baseline_v1`)
  - Prompt: `BASELINE_STAGE1_PROMPT` (`SYSTEM_INJECTION_DETECTOR` from `src/phishbench/evaluate_decoupled_rag.py`)
  - Output schema: `{"has_prompt_injection": true|false}`
- **Stage 1.5 Sanitization:** **DISABLED** (`sanitization_enabled=False`)
  - Raw unredacted email body is passed directly to Stage 2
- **Domain Telemetry:** **DISABLED** (`domain_analysis_enabled=False`)
- **RAG Retrieval Mode:** Standard vector proximity retrieval (`rag_mode="standard"`)
  - Retrieval size: $k=3$ nearest neighbors
  - Index: `results/rag_index_clean/index.faiss` (1,321 vectors)
  - Embedding Model: `sentence-transformers/all-MiniLM-L6-v2`
- **Stage 2 Phishing Classifier:** Baseline prompt (`stage2_prompt_mode="baseline"`)
  - Prompt: `STAGE2_BASELINE` (`SYSTEM_IS_PHISHING_ONLY` from `src/phishbench/evaluate_decoupled_rag.py`)
  - Output schema: `{"is_phishing": true|false}`

### 1.2 Architecture A1: Frozen Experimental Candidate
- **Role:** Generalization test candidate (highest performing model in M4 Ablation V1)
- **Implementation Source:** `src/experiments/m4_ablation_v1/ablation_engine.py` (Config `A1`)
- **Stage 1 Injection Detector:** Fine-grained active vs. quoted classifier (`experimental_v2`)
  - Prompt: `EXPERIMENTAL_STAGE1_PROMPT` (`SYSTEM_INJECTION_DETECTOR_V2` from `src/core/inference_m4_v2.py`)
  - Output schema: `{"active_prompt_injection": bool, "quoted_prompt_injection": bool, "injection_span": str, "reasoning": str}`
- **Stage 1.5 Sanitization:** **ENABLED** (`sanitization_enabled=True`)
  - Implementation: `src/core/sanitizer.py` (`sanitize_stage2_input`)
  - Mechanism: Replaces active prompt injection spans with `[UNTRUSTED_INSTRUCTION_REDACTED]`
- **Domain Telemetry:** **STRICTLY DISABLED** (`domain_analysis_enabled=False`)
  - Verified: No sender parsing, no SPF/DKIM simulation, no lookalike domain block
- **RAG Retrieval Mode:** Standard vector proximity retrieval (`rag_mode="standard"`)
  - Retrieval size: $k=3$ nearest neighbors
  - Balanced RAG: **STRICTLY DISABLED** (no 2+2 symmetric retrieval)
  - Index: `results/rag_index_clean/index.faiss` (identical clean index)
  - Embedding Model: `sentence-transformers/all-MiniLM-L6-v2`
- **Stage 2 Phishing Classifier:** Sanitization-aware prompt (`stage2_prompt_mode="sanitization_only"`)
  - Prompt: `STAGE2_WITH_SANITIZATION_ONLY` (from `src/experiments/m4_ablation_v1/prompts.py`)
  - Directives: Explicitly explains `[UNTRUSTED_INSTRUCTION_REDACTED]` placeholder; instructs LLM to disregard untrusted body instructions; contains ZERO domain scrutiny directives

---

## 2. Model & Inference Runtime Parameters

Both A0 and A1 will be evaluated under strictly identical local LLM execution parameters:

| Parameter | Setting | Verification Source |
|:---|:---|:---|
| **Inference Engine** | Local Ollama API (`http://127.0.0.1:11434`) | `src/core/inference.py` |
| **Model Name** | `qwen3.5:4b` | `src/core/model_config.py` (`DEFAULT_LIVE_MODEL`) |
| **Model ID** | `d8b0f5e9760c` (Size: 3.3 GB) | Local Ollama registry |
| **Temperature** | `0.0` (Deterministic greedy decoding) | `AblationConfig.temperature` |
| **Max Predict Tokens** | `512` tokens (`num_predict=512`) | `AblationConfig.num_predict` |
| **Timeout** | `60.0` seconds | `AblationConfig.timeout` |
| **Execution Mode** | Sequential (one sample at a time, avoiding GPU contention) | Evaluation runner protocol |

---

## 3. Cryptographic Hashes of Relevant Implementations & Dependencies

All source code, prompts, vector stores, and prior benchmark datasets were hashed prior to dataset construction:

| File / Component Path | SHA-256 Digest | Status |
|:---|:---:|:---:|
| `src/core/inference.py` | `aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506` | **FROZEN / UNMODIFIED** |
| `src/core/inference_m4_v2.py` | `fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37` | **FROZEN / UNMODIFIED** |
| `src/core/models.py` | `0a138b78ed84babbd3bdfeced6b3d8fa573ce5b18d171831e9e4bfd391fe66ab` | **FROZEN / UNMODIFIED** |
| `src/core/model_config.py` | `437ea2f042ae54bb73aae7d83142432c2c20eb084b9c00135762dee71a6cbeaf` | **FROZEN / UNMODIFIED** |
| `src/core/sanitizer.py` | `28c52002dd5adfa69d7a341b36921709237ba366d086e05c64276a2cc1175b3c` | **FROZEN / UNMODIFIED** |
| `src/core/domain_analyzer.py` | `67b7ac265d4740ceab3d629a29222955658a5fe4046444aebb9b3d04fea3ba56` | **FROZEN / UNMODIFIED** |
| `src/core/balanced_retriever.py` | `a6e2de41b66247cec20e44aec74e4c7967e4d62efae9642e2a8b5a81ee1d7646` | **FROZEN / UNMODIFIED** |
| `src/experiments/m4_ablation_v1/ablation_engine.py` | `0b31ca7743e24f2524cf6db229cecf419ebe368fe872e8d9016b2f40faebf82e` | **FROZEN / UNMODIFIED** |
| `src/experiments/m4_ablation_v1/prompts.py` | `31611448b3f3bbb9b9bc2ed6fe1fd3efe1f8c193b7e1e6af777d5482845c274d` | **FROZEN / UNMODIFIED** |
| `src/phishbench/evaluate_decoupled_rag.py` | `dcec64af35796ac59616f4dd61ee290c2cac60bb74d51875bead9cfe63a896c0` | **FROZEN / UNMODIFIED** |
| `results/rag_index_clean/index.faiss` | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` | **CLEAN / UNMODIFIED (1,321 vectors)** |
| `results/rag_index_clean/metadata.json` | `4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece` | **CLEAN / UNMODIFIED** |
| `data/evaluation/live_benchmark_v2.jsonl` | `1c762180451b90c8ad4e0500b5881526a69db3c6a69bffd09e3b7ed2ba0463e9` | **HISTORICAL BENCHMARK (150 samples)** |
| `data/evaluation/heldout_benchmark_v1.jsonl` | `42722ce81deffda02c788777af6aef2ce4b550fbba3ff1115f57a3a9c943f0c9` | **HISTORICAL BENCHMARK (100 samples)** |
| `results/m4_ablation_v1/predictions.jsonl` | `9bfa6a12b2a647ff952bb8fc6f2358897ad1e5317ad1dcabf3b5ddbb409d94fc` | **ABLATION V1 TRUTH (2,250 records)** |

---

## 4. Architectural Invariance Verification

1. **Isolation of A1:**
   - A1 explicitly sets `domain_analysis_enabled = False`. No structured domain blocks or WHOIS/SPF indicators will be parsed or passed to the Stage 2 prompt.
   - A1 explicitly sets `rag_mode = "standard"`. Exemplar retrieval will strictly query the top-3 nearest vector neighbors using `get_rag_retriever()`.
   - A1 explicitly sets `sanitization_enabled = True`. Candidate injection spans extracted by Stage 1 will be replaced with `[UNTRUSTED_INSTRUCTION_REDACTED]`.
2. **Evaluation Equivalence:**
   - Both A0 and A1 will receive identically formatted inputs: `{"sample_id", "subject", "sender", "body"}`.
   - Both A0 and A1 query the exact same clean vector database (`results/rag_index_clean/index.faiss`).
   - Neither architecture will be retrained, fine-tuned, or modified during this milestone.

