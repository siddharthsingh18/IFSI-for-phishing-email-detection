# IFSI Phase 5 — Promotion Readiness Review

**Review Target:** Optimized A1 Architecture (`A1-Opt`: Compact Stage 1 + Sanitizer V2)  
**Evaluation Scope:** 160-Sample Targeted Regression Suite (`results/phase5_a1_sanitizer_latency/`)  
**Auditor:** Independent Antigravity Forensic Auditor  
**Date:** 2026-11-01  

---

## 1. Formal Readiness Decision

### **DECISION: 1. Suitable for another controlled experiment.**

> [!IMPORTANT]
> **Production Promotion Restriction:**
> In accordance with strict evaluation protocols, **A1-Opt MUST NOT be promoted to production** based solely on this targeted 160-sample regression benchmark.
> While A1-Opt successfully resolved the multilingual sanitization breakdown and achieved meaningful Stage 1 latency reductions, full-scale production readiness requires validating these improvements across broader, independent real-world datasets and integrating domain analysis to address sophisticated phishing attacks.

---

## 2. Decision Justification & Supporting Evidence

### 2.1 Criteria Satisfied for Continuation:
1. **Definitive Fix for Multilingual Sanitization:**
   - Frozen A1 failed on all 5 Chinese active prompt injection challenge emails (`gen-inj-008`, `018`, `028`, `038`, `048`) due to whitespace tokenization limitations on unspaced CJK logographs, falling back to `manual_review` and scoring as false negatives.
   - Sanitizer V2 achieved **5/5 (100.0%) clean sanitizations**, zero manual review fallbacks, and 5/5 blocked attacks.
   - Across all 50 active injection samples in the benchmark, sanitization success improved from **90.0% $\rightarrow$ 100.0%**.
2. **Empirical Latency Reduction:**
   - Stage 1 latency was reduced by **-512.82 ms (-19.17% mean)** and **-472.38 ms (-18.92% median P50)** across the 160 samples.
   - On clean corporate emails, latency dropped by **~34.5%** (~1.63s vs. ~2.49s) by eliminating verbose reasoning generation.
   - P90 tail latency improved from **3.69s $\rightarrow$ 2.88s (-22.10%)**.
3. **Preservation of Injection Disambiguation:**
   - Quoted injection recall remained at **100.0%** (50/50 detected) with **100.0% safe delivery** (50/50 allowed, zero false blocks).
   - Active injection containment remained at **100.0%** (zero active prompt injection attempts reached the user inbox).
4. **Preservation of Legitimate Email Integrity:**
   - Difficult legitimate emails achieved **0.0% false positives** (20/20 allowed).
   - Ordinary legitimate emails achieved **0.0% false positives** (20/20 allowed).
5. **Architectural & Cryptographic Invariance:**
   - Production M4 (`src/core/inference.py`), Frozen A1 (`src/core/inference_m4_v2.py`), and the clean FAISS index (`results/rag_index_clean/index.faiss`) were 100% hash-preserved.

---

## 3. Unresolved Deficiencies & Production Disqualifiers

While A1-Opt is structurally sound, two primary factors preclude immediate production promotion:

1. **Sophisticated Phishing Blind Spot (0% Recall):**
   - Both Frozen A1 and Optimized A1 missed all 20 sophisticated phishing samples (`gen-sop-007` to `gen-sop-099`).
   - Because A1 deliberately isolates sanitization without structured sender and link domain analysis, it cannot detect threats whose deceptive signals reside entirely in lookalike domains.
   - A production email security system cannot be deployed with an unmitigated 0% detection rate on low-urgency lookalike domain attacks.
2. **Targeted Sample Scope (160 Samples):**
   - The Phase 5 regression dataset was targeted specifically at the known failure clusters and control groups (160 samples).
   - Generalization across hundreds or thousands of uncurated real-world emails must be evaluated before production release.

---

## 4. Next Experimental Recommendations

Before any production changes are proposed, the research roadmap should proceed through the following controlled steps:

1. **Full-Scale A1-Opt Generalization Benchmark:**
   - Evaluate A1-Opt against the full 500-sample benchmark (`data/evaluation/a1_generalization_v1.jsonl`) to establish statistical confidence across all 500 samples.
2. **Architecture Integration (A4-Opt / Unified M4):**
   - Combine the validated components from M4 Ablation:
     - Component 1: Compact Stage 1 Prompt (from Phase 5).
     - Component 1.5: Sanitizer V2 (from Phase 5).
     - Component 2: Structured Sender & Domain Telemetry (from A2/A4) to resolve the 20 sophisticated phishing misses.
     - Component 3: Balanced RAG Retrieval (from A3/A4).
3. **Edge Case Sanitizer Unit Testing:**
   - Expand unit tests to cover zero-width characters, bidirectional Unicode formatting, and multiple disjoint injection spans.

