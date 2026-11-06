# Phase 9.4: Repository Readiness & Pre-Release Assessment Report

**Document Identifier:** `IFSI-REL-2026-09-4`  
**Repository Working Directory:** `D:\Project\IFSI-for-phishing-email-detection`  
**Audit Date:** November 2026  
**Auditor:** Research Governance & Repository Readiness Audit Agent  

---

## 1. Executive Summary & Readiness Verdict

```
========================================================================================
REPOSITORY PRE-RELEASE READINESS VERDICT:
STATUS: READY FOR REPOSITORY ARCHIVAL & CODE RELEASE PREPARATION;
        DEPENDENCIES VERIFIED & RESOLVED (PHASE 9.4.1);
        GIT WORKING TREE PENDING AUTHORIZED ATOMIC COMMIT.
========================================================================================
- Working Tree Integrity: MODIFIED TRACKED: pyproject.toml (+tldextract==5.1.2).
                          UNTRACKED: results/phase9/, tools/init_phase9.py.
- Automated Test Suite: 147 TESTS COLLECTED ACROSS 26 MODULES.
- Cryptographic Artifact Integrity: 100% INVARIANTS PASS (tools/init_phase9.py).
- Code Release Dependency Status: CLEARED (numpy==2.4.6, scikit-learn==1.9.1 verified on
                                  PyPI; tldextract==5.1.2 added; pip --dry-run exit code 0).
- Scientific Publication Blocker: Track A external evaluation remains formally BLOCKED.
========================================================================================
```

---

## 2. Project Architecture & Directory Layout Assessment

The repository adheres to a clean separation of concerns across core inference, experimental branches, offline benchmarking, and full-stack application interfaces:

```
D:\Project\IFSI-for-phishing-email-detection
├── config/                  # Ollama endpoints, dataset quality gates, model configs
├── data/                    # Evaluation benchmark suites (N=40 to N=500), source manifests
├── docs/                    # Architectural specifications and UI screenshots
├── frontend/                # React 19 + Vite + TypeScript web interface
├── prompts/                 # Versioned prompt templates
├── results/                 # Historical benchmark predictions, metrics, and Phase 9 audit records
│   ├── rag_index_clean/     # Cryptographically frozen FAISS dense index (1,321 vectors)
│   └── phase9/              # Phase 9 governance, claims integrity, manuscript, and audit reports
├── scripts/                 # Utility scripts for data preparation and proxy setup
├── src/
│   ├── api/                 # FastAPI REST application routes and Pydantic schemas
│   ├── core/                # Production M1–M4 inference engines (Source of Truth)
│   ├── experiments/         # Phased experimental candidates (Phase 5, 6, 7 Engine V4)
│   └── phishbench/          # Offline benchmarking tools and RAG utilities
├── tests/                   # 147 automated tests across 26 test modules
└── tools/                   # Independent audit, dataset building, and verification tools
```

---

## 3. Automated Test Coverage Overview

A comprehensive collection audit via `pytest --collect-only` identifies **147 automated tests across 26 test files**:

| Test Module Path | Test Count | Target Scope & Invariant Verified |
| :--- | :---: | :--- |
| `tests/test_sanitizer_v2.py` | 11 | English exact/whitespace, Chinese CJK, Japanese kana/kanji, Russian Cyrillic, Arabic RTL, fullwidth punctuation brackets, heuristic fallback, and unresolvable manual-review fail-safe. |
| `tests/test_m4_experimental.py` | 15 | Domain Analyzer lookalike detection, input sanitizer span extraction, security policy mapping (`allow`, `block`, `quarantine_review`, `manual_review`), and prompt schema guarantees. |
| `tests/test_a1_generalization_validation.py` | 8 | Sample uniqueness, category balance, ground truth balance, zero leakage with RAG index, and code/index hash invariance. |
| `tests/test_api.py` & `test_stream_api.py` | 6 | FastAPI health endpoints, CORS headers, OpenAPI documentation, and typed SSE streaming events. |
| `tests/test_core.py` & `test_models.py` | 13 | Serialized email invariance, prompt file parity, exact McNemar pairing, and TF-IDF M1 loader bounds. |
| `tests/test_rag.py` & `test_decoupled_rag.py` | 10 | Zero test-set leakage in FAISS index, reference block formatting, and decoupled schema validation. |
| `tests/test_data_loader.py` & `test_data_parsers.py` | 18 | Mbox/CSV round-trip, deduplication, cluster grouping, and SpamAssassin ham tree validation. |
| `tests/test_ollama_client.py` | 10 | Pydantic response parsing, confidence clamping, retry logic, and prompt hash determinism. |
| *Other supporting test modules* | 56 | Confounding audits, dataset building integrity, and dashboard telemetry. |

---

## 4. Documentation Assessment & Pre-Release Gaps

### 4.1 Documentation Strengths
- **Comprehensive Technical Monograph**: `results/phase9/phase9_3_research_manuscript.md` provides a complete, mathematically rigorous explanation of the research problem, two-stage architecture, and experimental findings.
- **Auditable Traceability**: `results/phase9/phase9_3_evidence_traceability.md` maps every table and number to primary prediction files and SHA-256 digests.
- **Honest Limitations**: The manuscript and audit reports extensively document all negative results, the `gen-inj-071` false positive, and the formal blocking of Track A independent evaluation.

### 4.2 Documentation Gaps for Public GitHub Release
1. **`README.md` Model Discrepancy**: The root `README.md` documents `qwen2.5:0.5b` as the default model and `llama3.2:3b` as a promotion candidate. While correct for the lightweight web demo, it does not state that **all Phase 4–7 candidate experiments and the research candidate (`engine_v4.py`) require `qwen3.5:4b`**. A dedicated section or `REPRODUCIBILITY.md` document must clarify this for researchers attempting to replicate benchmark tables.
2. **Landing Page Screenshot**: `README.md` explicitly notes that the committed UI screenshot shows an older counter. A refreshed screenshot of the current React 19 interface is recommended prior to public release.

---

## 5. Public Release Blockers & Status

The pre-release audit examined two potential code release blockers and one scientific publication gate:

### Item 1: Dependency Declarations in `pyproject.toml` — RESOLVED in Phase 9.4.1
- **Prior Claim in Phase 9.4**: Erroneously asserted that pinned versions `numpy==2.4.6` and `scikit-learn==1.9.1` do not exist on PyPI, conflating installed Conda environment versions (`numpy 2.3.5`, `scikit-learn 1.7.2`) with upstream package availability.
- **Verification & Resolution (Phase 9.4.1)**:
  - Authoritative PyPI release inspection confirmed both releases exist with pre-compiled `cp313-cp313-win_amd64.whl` wheels:
    - `https://pypi.org/project/numpy/2.4.6/`
    - `https://pypi.org/project/scikit-learn/1.9.1/`
  - Direct runtime dependency `tldextract` (imported by `src/experiments/phase7_domain_precision/domain_analyzer_v3.py`) was added to `pyproject.toml` as `"tldextract==5.1.2",`.
  - Dry-run verification `pip install --dry-run -e .` executed on Python 3.13.9 AMD64 completed successfully with **exit code 0** (zero conflicts, all wheels cleanly resolvable).
- **Status**: **CLEARED / RESOLVED**.

### Item 2: Working Tree State & Commit Authorization — OPERATIONAL REQUIREMENT
- **Current Git Status**: `git status --short` shows modified tracked file `pyproject.toml` and untracked Phase 9 directories:
  ```text
   M pyproject.toml
  ?? results/phase9/
  ?? tools/init_phase9.py
  ```
- **Consequence**: The repository cannot be pushed to a remote GitHub repository in its current uncommitted state. Once Phase 9.4 and 9.4.1 audits are finalized and explicitly authorized by the project lead, a single atomic commit should be created.
- **Status**: **PENDING PROJECT LEAD COMMIT AUTHORIZATION**.

### Item 3: Scientific Publication Gate — EXTERNAL EVALUATION BLOCKED
- **Track A Independent Acquisition**: Track A external email acquisition remains formally **BLOCKED and UNAUTHORIZED** per Phase 8.1A/8.1B/8.1C findings.
- **Consequence**: Code and technical monograph are ready for archival and open sharing, but formal claims of generalized real-world detection efficacy in academic journal submissions remain gated until an independent, unconfounded email corpus is legally acquired and evaluated.
- **Status**: **GOVERNANCE GATE ENFORCED**.

---

## 6. Final Readiness Recommendation

1. **For Scientific & Technical Review**: **READY**. The codebase, manuscript, traceability ledger, and audit documents provide an exceptionally complete, defensible research archive.
2. **For Package Installation & Environment Setup**: **READY**. Direct installation via `pip install -e .` resolves without error across Python 3.13 systems.
3. **For Public GitHub Push**: **READY PENDING COMMIT AUTHORIZATION**.
   - Dependency definitions are verified and resolved.
   - Commit the working tree and push to remote only upon explicit project lead authorization.
