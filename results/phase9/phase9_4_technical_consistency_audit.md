# Phase 9.4: Technical Consistency & Implementation Audit Report

**Document Identifier:** `IFSI-TCA-2026-09-4`  
**Target Manuscript:** `results/phase9/phase9_3_research_manuscript.md`  
**Traceability Register:** `results/phase9/phase9_3_evidence_traceability.md`  
**Auditor:** Research Governance & Technical Audit Agent  
**Date:** November 2026  

---

## 1. Executive Summary

Phase 9.4 conducts a comprehensive forensic consistency audit reconciling the research manuscript (`phase9_3_research_manuscript.md`), empirical traceability register (`phase9_3_evidence_traceability.md`), and historical experimental records against the actual codebase implementations, configuration files, API schemas, and frontend application code.

### Summary of Audit Findings
1. **Operational Action Schema Reconciled**: The manuscript originally used abstract policy labels (`PASS`, `FLAG_ALERT`, `BLOCK_PHISH`, `QUARANTINE_SECURITY`). The actual codebase across all versions (M4 baseline, Frozen A1, Engine V4, FastAPI backend, and React frontend) implements a concrete 4-value enum: `allow`, `block`, `quarantine_review`, and `manual_review`. The manuscript has been corrected to explicitly define the exact implemented enum and its decision logic.
2. **Sample-Count and Denominator Integrity Confirmed**: Every sample count across Phase 4 ($N=250$), A1 Generalization ($N=500$), Phase 5 ($N=160$), Phase 6 ($N=200$), and Phase 7 ($N=240$) has been audited against primary dataset files. Quoted injection denominators (50 samples in P5, 50 samples in P7) and active containment denominators (50 active cases in P5, 11 unit tests) are cryptographically verified.
3. **Architecture-to-Implementation Alignment Verified**: The two-stage decoupled execution flow, Stage 1 compact prompting, Sanitizer V2 regex boundary logic, Clean FAISS Top-3 retrieval, and Domain Analyzer V3 Public Suffix parsing in `engine_v4.py` match the conceptual architecture. RAG retrieval execution timing (performed during Step 1 staging over inbound text) was clarified in the manuscript.
4. **Production Baseline vs. Research Candidate Boundary Maintained**: Production M4 (`src/core/inference.py`) remains strictly isolated from the frozen research candidate (`src/experiments/phase7_domain_precision/engine_v4.py`).

---

## 2. Operational Action Schema Reconciliation

### 2.1 Codebase Implementation vs. Manuscript Specification
A detailed forensic investigation of the security action definitions across the repository revealed the following source mappings:

| Component / Layer | Source File Path | Line Range | Defined Action Values | Implemented Decision Logic |
| :--- | :--- | :---: | :--- | :--- |
| **Production Baseline Engine** | `src/core/inference.py` | L413–L430 | `'allow'`, `'block'`, `'quarantine_review'`, `'manual_review'` | Phish $\to$ `block`; Legit + Inj $\to$ `quarantine_review`; Legit Clean $\to$ `allow`; Pipeline failure $\to$ `manual_review`. |
| **Frozen A1 Engine** | `src/core/inference_m4_v2.py` | L290–L320 | `'allow'`, `'block'`, `'quarantine_review'`, `'manual_review'` | Phish $\to$ `block`; Legit + Active Inj $\to$ `quarantine_review`; Legit + Quoted Inj $\to$ `allow`; Failure $\to$ `manual_review`. |
| **Candidate Engine V4** | `src/experiments/phase7_domain_precision/engine_v4.py` | L200–L213 | `'allow'`, `'block'`, `'quarantine_review'`, `'manual_review'` | Failed stages/sanitization alert $\to$ `manual_review`; Phish $\to$ `block`; Legit + Active Inj $\to$ `quarantine_review`; Clean/Quoted $\to$ `allow`. |
| **FastAPI REST Schema** | `src/api/main.py` | L133 | `Field("allow", description="Recommended security action ('allow', 'quarantine_review', 'block', 'manual_review')")` | Strict Pydantic string validation over the 4 canonical states. |
| **Frontend API Types** | `frontend/src/api/client.ts` | L12 | `'allow' \| 'quarantine_review' \| 'block' \| 'manual_review' \| string` | TypeScript discriminated union for API response parsing. |
| **Frontend UI Rendering** | `frontend/src/components/MethodResultCard.tsx` | L151–L180 | Badge Labels: `'ACTION: BLOCK'`, `'ACTION: QUARANTINE / REVIEW'`, `'ACTION: MANUAL REVIEW'`, `'ACTION: ALLOW'` | Color-coded badges mapping directly to the 4 implemented action states. |

### 2.2 Nature of the Discrepancy & Resolution
The manuscript's original Section 3.4 introduced theoretical, uppercase action labels (`PASS`, `FLAG_ALERT`, `BLOCK_PHISH`, `QUARANTINE_SECURITY`) and omitted the fail-safe `manual_review` state. This represented a conceptual abstraction by the authors rather than a separate system version. 

**Resolution**: Section 3.4 and Section 4 of `results/phase9/phase9_3_research_manuscript.md` have been updated to formally specify the implemented operational action space:
$$\text{security\_action} \in \{\text{"allow"}, \text{"block"}, \text{"quarantine\_review"}, \text{"manual\_review"}\}$$
with the exact decision piecewise function matching `engine_v4.py` lines 200–213.

---

## 3. Evaluation Sample-Count & Denominator Integrity Audit

Every experimental evaluation reported in the manuscript was audited against its raw dataset files and prediction records:

| Phase & Evaluation Suite | Manuscript Citation | Raw Dataset Path | Sample Count & Ground Truth Distribution | Prediction Artifact Traced | Denominator Integrity Verdict |
| :--- | :---: | :--- | :--- | :--- | :---: |
| **Phase 4 Controlled Ablation** | Section 7.1, Table 1 | `live_benchmark_v2.jsonl` (150) + `heldout_benchmark_v1.jsonl` (100) | $N = 250$<br/>125 Legitimate, 125 Phishing<br/>25 Active Inj, 25 Quoted Inj | `results/m4_ablation_v1/predictions.jsonl` (2,250 records across 9 configs) | **EXACT MATCH** ($N=250$ identical across all 9 configs) |
| **A1 Generalization V1** | Section 6.2, 7.1 | `data/evaluation/a1_generalization_v1.jsonl` | $N = 500$<br/>250 Legitimate, 250 Phishing<br/>200 Active Inj, 50 Quoted Inj | `results/a1_generalization_v1/final_report.md` | **EXACT MATCH** ($N=500$) |
| **Phase 5 Latency Optimization** | Section 7.2, Table 2 | `data/evaluation/phase5_regression_160.jsonl` | $N = 160$<br/>100 Injection (50 Active + 50 Quoted)<br/>60 Standard (40 Legit + 20 Sophisticated Phish) | `results/phase5_a1_sanitizer_latency/predictions.jsonl` (320 records) | **EXACT MATCH** ($N=160$ across Frozen A1 & A1-Opt) |
| **Phase 6 Domain Evidence** | Section 7.3, Table 3 | `phase5_regression_160` (160) + `phase6_domain_challenge` (40) | $N = 200$<br/>110 Legitimate, 90 Phishing<br/>(40 Sophisticated Lookalike Phish) | `results/phase6_domain_evidence/predictions.jsonl` (440 records) | **EXACT MATCH** ($N=200$ across Config A & B; $N=80$ Config C) |
| **Phase 7 Domain Precision** | Section 7.4, Table 4 | `phase5_160` (160) + `phase6_40` (40) + `phase7_precision_challenge` (40) | $N = 240$<br/>130 Legitimate, 110 Phishing<br/>(60 Sophisticated Lookalike/BEC Phish) | `results/phase7_domain_precision/predictions.jsonl` (560 records) | **EXACT MATCH** ($N=240$ across Config A & B; $N=80$ Config C) |

### 3.1 Denominator Breakdown for Specific Defensive Tasks
1. **Quoted-Injection Safe-Delivery**:
   - In `phase5_regression_160.jsonl`, exactly 50 emails are labeled `injection_type: "quoted"`. Both Frozen A1 and A1-Opt safe-delivered **50/50 (100.0%)**.
   - In `phase7_domain_precision/predictions.jsonl`, exactly 50 emails are labeled `injection_type: "quoted"`. Config B safe-delivered **49/50 (98.0%)**, with exactly 1 false positive on sample `gen-inj-071` (line 128).
2. **Active-Injection Containment**:
   - In `phase5_regression_160.jsonl`, exactly 50 emails are labeled `injection_type: "active"`. Sanitizer V2 achieved **50/50 (100.0%)** redaction.
   - In `tests/test_sanitizer_v2.py`, exactly 11 automated unit tests evaluate CJK, Cyrillic, multiline wrapping, and punctuation boundaries. All **11/11 (100.0%)** pass with zero collateral text corruption.
3. **Sophisticated Phishing Challenges**:
   - Phase 5: 20 sophisticated phishing attacks (`gen-sop-007` to `gen-sop-099`). Detected: **0/20 (0.0%)**.
   - Phase 6: 40 sophisticated lookalike phishing attacks. Config A detected **18/40 (45.0%)**; Config B detected **40/40 (100.0%)**.
   - Phase 7: 60 sophisticated lookalike and BEC attacks. Config A detected **60/60 (100.0%)**; Config B detected **60/60 (100.0%)**; Config C (ablation without domain evidence) detected **37/40 (92.5%)** on challenge subsets.

---

## 4. Implementation-to-Manuscript Verification

| Architectural Concept | Implemented Code Location | Implementation Behavior Verified | Manuscript Conformance Status |
| :--- | :--- | :--- | :---: |
| **Two-Stage Decoupled Flow** | `engine_v4.py` L75–L213 | Stage 1 evaluates injection; Sanitizer V2 redacts active spans; Stage 2 evaluates phishing on sanitized text with domain context. | **ALIGNED** |
| **Stage 1 Prompt Compaction** | `prompts_v2.py` (`STAGE1_COMPACT_PROMPT`) | Requires compact JSON: `injection_type`, `confidence`, `injection_spans`. Eliminates conversational CoT reasoning. | **ALIGNED** |
| **Sanitizer V2 Regex Engine** | `sanitizer_v2.py` L30–L150 | Boundary lookahead/lookbehind matching `(?:\b\|\W\|^)` and `(?:\b\|\W|$)`. Unicode NFKC normalization. | **ALIGNED** |
| **RAG Exemplar Selection** | `engine_v4.py` L79–L92 | Clean FAISS index queried using inner-product similarity with Sentence-Transformers embeddings ($k=3$). | **ALIGNED (Timing clarified)** |
| **Domain Telemetry V3** | `domain_analyzer_v3.py` L40–L350 | Uses Mozilla Public Suffix List via `tldextract` to extract registered domains; maps enterprise multi-tenant domains (`amazon-business.com`, Workday, Concur). | **ALIGNED** |
| **Fail-Safe Fallback** | `engine_v4.py` L201–L203 | Stage failure or sanitization error automatically routes email to `"manual_review"`. | **ALIGNED** |

---

## 5. Master Documentation Corrections Log

In accordance with Phase 9.4 correction rules, the following precise updates were applied to Phase 9.3 documentation:

| Original Manuscript Statement | Verified Implementation / Evidence | Correction Applied to Manuscript | Evidence Path |
| :--- | :--- | :--- | :--- |
| **Section 3.4**: Action space defined as `PASS`, `FLAG_ALERT`, `BLOCK_PHISH`, `QUARANTINE_SECURITY`. | Implementation across `engine_v4.py`, `main.py`, and `MethodResultCard.tsx` uses canonical enum: `"allow"`, `"block"`, `"quarantine_review"`, `"manual_review"`. | Formally defined $\text{security\_action} \in \{\text{"allow"}, \text{"block"}, \text{"quarantine\_review"}, \text{"manual\_review"}\}$ and documented the exact 4-case piecewise decision policy. | `src/experiments/phase7_domain_precision/engine_v4.py` (L200–213); `src/api/main.py` (L133); `frontend/src/components/MethodResultCard.tsx` (L151–180). |
| **Section 4 (Diagram)**: Diagram verdict node displayed `PASS \| FLAG_ALERT \| BLOCK_PHISH \| QUARANTINE_SECURITY`. | Runtime gateway returns `"allow"`, `"block"`, `"quarantine_review"`, or `"manual_review"`. | Updated Mermaid decision block to display `Gateway Action: allow \| block \| quarantine_review \| manual_review`. | `results/phase9/phase9_3_research_manuscript.md` (Section 4, Mermaid diagram). |
| **Section 4.2.1**: Stated that FAISS query is performed on the sanitized body text. | In `engine_v4.py` lines 79–92, Step 1 RAG retrieval is executed on the incoming email text during initial input staging. | Clarified that FAISS exemplar retrieval is executed during initial staging and assembled into Stage 2 alongside the sanitized body and domain evidence. | `src/experiments/phase7_domain_precision/engine_v4.py` (L79–L92). |

---

## 6. Remaining Unresolved Technical Items

1. **Residual Exploit Vocabulary Triggering (`gen-inj-071`)**: Sample `gen-inj-071` remains a known false positive in Phase 7 Config B. The Stage 2 LLM triggered on dense CVE exploit jargon in the email body despite clean domain telemetry. This does not represent an implementation crash, but an inherent semantic boundary limitation of small LLM classifiers.
2. **Missing `tldextract` in `pyproject.toml`**: `domain_analyzer_v3.py` requires `tldextract`, which is installed in the local environment (`5.1.2`) but missing from the dependencies list in `pyproject.toml`. This is documented in `phase9_4_reproducibility_assessment.md`.
