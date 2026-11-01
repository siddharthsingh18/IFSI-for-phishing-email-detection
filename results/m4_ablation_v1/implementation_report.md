# Implementation Report: M4 Ablation Study (Phase 2)

**Experiment:** IFSI Phishing Email Detection — M4 Modular Component Ablation Study  
**Version:** V1  
**Status:** Implementation Complete & Validated  
**Date:** 2026-10-31  
**Target Codebase Location:** `src/experiments/m4_ablation_v1/`  

---

## 1. Executive Summary

Phase 2 of the M4 Ablation Study establishes a rigorous, modular, configuration-driven experimental engine under `src/experiments/m4_ablation_v1/`. The framework enables controlled empirical isolation of each enhancement introduced in M4 Experimental V2 relative to the M4 Production Baseline, specifically:

1. **Active vs. Quoted Prompt-Injection Classifier** (Stage 1).
2. **Untrusted Instruction Redaction & Sanitization** (Stage 1.5).
3. **Structured Sender & Domain Telemetry Analysis** (Feature enrichment).
4. **Balanced Class Retrieval** (2 Phish + 2 Legit exemplars vs. Top-3 nearest neighbors).
5. **Decoupled Injection Classifier vs. Sanitizer** (ISO-4 isolation).

The implementation strictly honors all safety constraints: production M4 (`src/core/inference.py`), canonical experimental M4 (`src/core/inference_m4_v2.py`), historical benchmark datasets (`results/live_benchmark_v1/`, `results/live_benchmark_v2/`, `results/m4_experiment_v1/`), and the clean FAISS index (`results/rag_index_clean/`) remain completely read-only and unmodified.

---

## 2. Architecture & Modular Package Layout

The ablation framework is housed in an isolated package structure:

```
src/experiments/
└── m4_ablation_v1/
    ├── __init__.py               # Exports CONFIGURATIONS, AblationConfig, classify_email_ablation
    ├── prompts.py                # Isolated Stage 1 & Stage 2 prompt templates with zero cross-leakage
    └── ablation_engine.py        # Core configuration dataclass and modular execution pipeline
```

### 2.1 Component Dependency Graph

```
                                      [Email Input (Subject, Sender, Body)]
                                                        │
                         ┌──────────────────────────────┴──────────────────────────────┐
                         ▼                                                             ▼
             [Stage 1: Injection Detector]                             [Feature Extraction: Domain Analyzer]
        ┌────────────────────────────────┐                             ┌──────────────────────────────────┐
        │  baseline_v1  │ experimental_v2 │                             │  domain_analysis_enabled: True   │
        │  (Binary)     │ (Active/Quoted)│                             │  - Sender vs link mismatch       │
        └───────┬────────────────┬───────┘                             │  - Punycode / IP detection       │
                │                │                                     │  domain_analysis_enabled: False  │
                ▼                ▼                                     │  - Block completely omitted      │
         [has_injection]  [active, quoted, span]                       └────────────────┬─────────────────┘
                │                │                                                      │
                └────────┬───────┘                                                      │
                         ▼                                                              │
            [Stage 1.5: Sanitizer]                                                      │
        ┌────────────────────────────────┐                                              │
        │  sanitization_enabled: True    │                                              │
        │  - Redacts detected spans to   │                                              │
        │    [UNTRUSTED_INSTRUCTION_...] │                                              │
        │  sanitization_enabled: False   │                                              │
        │  - Passes original raw text    │                                              │
        └────────────────┬───────────────┘                                              │
                         ▼                                                              │
               [Sanitized / Raw Body]                                                   │
                         │                                                              │
                         ├──────────────────────────────────────────────┐               │
                         ▼                                              ▼               │
             [RAG Retrieval Engine]                                     │               │
        ┌────────────────────────────────┐                              │               │
        │  rag_mode: "standard"          │                              │               │
        │  - Top-3 nearest neighbors     │                              │               │
        │  rag_mode: "balanced"          │                              │               │
        │  - 2 Phish + 2 Legit exemplars │                              │               │
        └────────────────┬───────────────┘                              │               │
                         ▼                                              ▼               ▼
                 [Reference Block]                             [Assembled Stage 2 Prompt]
                         └──────────────────────────────────────────────┬───────────────┘
                                                                        ▼
                                                       [Stage 2: Phishing Classifier]
                                                       ┌──────────────────────────────┐
                                                       │ Strict JSON Response:        │
                                                       │ - is_phishing (bool)         │
                                                       │ - confidence (float)         │
                                                       │ - reasoning (str)            │
                                                       └──────────────┬───────────────┘
                                                                      ▼
                                                       [Deterministic Security Router]
                                                       ┌──────────────────────────────┐
                                                       │ - block                      │
                                                       │ - quarantine_review          │
                                                       │ - allow                      │
                                                       └──────────────────────────────┘
```

---

## 3. Detailed Component Isolation Mechanisms

### 3.1 Stage 1: Injection Detector Selection
- **`baseline_v1`**: Uses `BASELINE_STAGE1_PROMPT` (the binary injection prompt from production M4). Output returns `has_prompt_injection` (bool).
- **`experimental_v2`**: Uses `EXPERIMENTAL_STAGE1_PROMPT` (the active-vs-quoted prompt from experimental M4). Distinguishes malicious execution instructions (`active_prompt_injection=True`) from passive references/SOC quotes (`quoted_prompt_injection=True`) and extracts the targeted instruction span (`injection_span`).

### 3.2 Stage 1.5: Sanitization Isolation & Methodological Decoupling
In the canonical experimental pipeline, injection detection and span sanitization were invoked sequentially. To measure whether performance gains stem from *detecting* injection or *redacting* text, sanitization is governed by an explicit boolean flag `sanitization_enabled`:
- When `True` and active injection is detected: `sanitize_stage2_input` replaces the detected malicious span with `[UNTRUSTED_INSTRUCTION_REDACTED: Malicious prompt injection attempt removed by security pre-filter]`.
- When `False`: The raw, unredacted email text is forwarded directly to Stage 2, preserving any adversarial instructions intact.

### 3.3 Feature Enrichment: Structured Domain Telemetry Isolation
- When `domain_analysis_enabled=True`: `analyze_email_domains` computes RFC 5322 header checks, body URL extraction, domain mismatch analysis, and IP/punycode flags. This is formatted as `[STRUCTURED SENDER & DOMAIN EVIDENCE]` and injected into Stage 2.
- When `domain_analysis_enabled=False`: Domain analysis is completely bypassed. No telemetry block is created, and Stage 2 prompt templates contain no references to domain evidence.

### 3.4 Retrieval Mode: Standard vs. Balanced RAG
Both modes query the exact same underlying FAISS index (`results/rag_index_clean/index.faiss`, 1,321 vectors, SHA256 verified) without index mutation:
- **`rag_mode="standard"`**: Invokes `retriever.retrieve(sanitized_text, top_k=3)` using cosine similarity, formatting exemplars with `format_reference_block()`.
- **`rag_mode="balanced"`**: Invokes `retrieve_balanced(sanitized_text, k_phish=2, k_legit=2)` guaranteeing class symmetry (2 phishing, 2 legitimate), formatting exemplars with `format_balanced_reference_block()`.

### 3.5 Stage 2 Prompt Adaptation (Preventing Confounding References)
A critical methodological vulnerability in ablation studies is prompt-leakage: if a prompt commands the LLM to *"analyze the domain evidence block above"* while domain analysis is disabled, the model experiences unnatural confusion, polluting the ablation.

To eliminate this confound, `prompts.py` defines tailored Stage 2 system prompts:
1. **`STAGE2_BASELINE`**: Pure baseline prompt without domain or sanitization instructions. Used by **A0** and **ISO-4**.
2. **`STAGE2_WITH_SANITIZATION_ONLY`**: Instructs the model on redacted instruction markers, but contains zero domain directives. Used by **A1** and **ISO-2**.
3. **`STAGE2_WITH_DOMAIN_ONLY`**: Instructs the model on domain evidence analysis, but contains zero sanitization directives. Used by **ISO-1**.
4. **`STAGE2_WITH_SANITIZATION_AND_DOMAIN`**: Incorporates both sanitization and domain directives, tailored for standard RAG. Used by **A2** and **ISO-3**.
5. **`STAGE2_CANONICAL_V2`**: Full canonical prompt incorporating sanitization, domain analysis, and balanced exemplar analysis. Used by **A3** and **A4**.

---

## 4. Configuration Declarations

The engine exposes 9 configurations registered in `CONFIGURATIONS`:

| Config ID | Component Focus | Injection Detector | Sanitizer | Domain Analysis | RAG Mode | Stage 2 Prompt Mode |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **A0** | Production M4 Baseline | `baseline_v1` | Disabled | Disabled | `standard` (k=3) | `baseline` |
| **ISO-4** | Isolated Injection Classifier | `experimental_v2` | Disabled | Disabled | `standard` (k=3) | `baseline` |
| **A1** | + Sanitization Engine | `experimental_v2` | **Enabled** | Disabled | `standard` (k=3) | `sanitization_only` |
| **A2** | + Domain Analysis Telemetry | `experimental_v2` | **Enabled** | **Enabled** | `standard` (k=3) | `sanitization_and_domain` |
| **A3** | + Balanced RAG Retrieval | `experimental_v2` | **Enabled** | **Enabled** | **`balanced`** (2+2) | `canonical_v2` |
| **A4** | Canonical Full Experimental | `experimental_v2` | **Enabled** | **Enabled** | **`balanced`** (2+2) | `canonical_v2` |
| **ISO-1** | Without Sanitization | `experimental_v2` | Disabled | **Enabled** | **`balanced`** (2+2) | `domain_only` |
| **ISO-2** | Without Domain Analysis | `experimental_v2` | **Enabled** | Disabled | **`balanced`** (2+2) | `sanitization_only` |
| **ISO-3** | Without Balanced RAG | `experimental_v2` | **Enabled** | **Enabled** | `standard` (k=3) | `sanitization_and_domain` |

---

## 5. Security Action Policy Enforcement

Every configuration evaluates security routing via a single deterministic policy:
1. `is_phishing == True` $\rightarrow$ **`block`** (highest priority).
2. `is_phishing == False` AND `active_prompt_injection == True` (or `has_prompt_injection == True` in baseline) $\rightarrow$ **`quarantine_review`**.
3. `is_phishing == False` AND `quoted_prompt_injection == True` (no active injection) $\rightarrow$ **`allow`** (with security audit note).
4. `is_phishing == False` AND no injection detected $\rightarrow$ **`allow`**.

---

## 6. Latency & Telemetry Instrumentation

Each ablation inference captures granular execution metrics:
- **`stage1_latency_ms`**: Precise wall-clock duration of Stage 1 injection inference.
- **`stage2_latency_ms`**: Precise wall-clock duration of Stage 2 phishing inference.
- **`total_latency_ms`**: Sum of Stage 1 and Stage 2 model latencies.
- **`wall_clock_ms`**: Total end-to-end execution time including RAG search, domain telemetry, and text formatting.
- **`retrieved_exemplar_ids`**: List of IDs for all exemplars provided to Stage 2.
- **`is_sanitized`**: Boolean flag confirming whether redaction occurred.
- **`domain_evidence_present`**: Boolean flag confirming whether domain evidence was injected.

This fine-grained tracking guarantees rigorous latency-accuracy trade-off evaluations across all components.

