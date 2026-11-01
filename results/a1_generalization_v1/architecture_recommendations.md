# IFSI — Architecture Recommendations & Next Steps: Post-A1 Investigation V1

**Project Root:** `D:\Project\IFSI-for-phishing-email-detection`  
**Status:** Proposal / Recommendations Only (Zero Implementation Conducted)  
**Governance Constraint:** Implementation strictly halted awaiting formal human review and approval.

---

## Executive Overview

Based on the empirical findings from the **A0 vs. A1 Generalization Benchmark** ($N = 500$, 1,000 predictions) and the subsequent **Root Cause Forensic Investigation**, this document provides concrete, engineering-grounded recommendations for four specific architectural dimensions:

```mermaid
flowchart TD
    A["Post-A1 Architectural Enhancements"] --> B["1. Multilingual Sanitizer Robustness"]
    A --> C["2. Sophisticated Phishing (Domain Telemetry)"]
    A --> D["3. False-Positive Suppression (Context Continuity)"]
    A --> E["4. Latency Optimization (Compact Telemetry)"]

    B --> V1["Validation: Multi-lingual Injection Suite"]
    C --> V2["Validation: BEC & VDR Challenge Corpus"]
    D --> V3["Validation: Difficult Compliance Benchmark"]
    E --> V4["Validation: Latency Micro-profiler"]
```

---

## 1. Recommendation 1: Multilingual Injection Sanitization

### 1.1 Root Cause
In `src/core/sanitizer.py`, `_find_normalized_span_indices` tokenizes candidate injection spans using `span.split()`. In non-whitespace-delimited languages (Chinese, Japanese, Korean), words are logographic and unspaced. When an LLM extracts an injection span but strips a newline delimiter (e.g. between an instruction header `【系统最高指令】` and the body `忽略规则`), `span.split()` treats the joined ideographs as a single token. Consequently, regex whitespace bridging (`\s+`) is never inserted, causing substring matching to fail. Additionally, secondary fallback heuristics (`HEURISTIC_PATTERNS`) contain only English regex patterns.

### 1.2 Proposed Technical Change
1. **Character-Level CJK Boundary Tokenization:** In `_find_normalized_span_indices`, detect if the candidate span contains CJK ideographs (Unicode ranges `\u4e00-\u9fff`). If present, split tokens at character boundaries or logograph-punctuation junctions so that flexible whitespace matching (`\s*` or `\s+`) can bridge newlines between logographs:
   ```python
   # Proposed enhancement (concept only):
   if any('\u4e00' <= char <= '\u9fff' for char in span):
       pattern = r"\s*".join(re.escape(c) for c in span if not c.isspace())
   ```
2. **Multilingual Secondary Heuristics:** Augment `HEURISTIC_PATTERNS` to include standard CJK adversarial framing patterns:
   - `r"【(?:系统|管理|AI).*?指令】.*?(?:\n\n|\Z)"`
   - `r"(?i)忽略(?:之前)?(?:所有)?安全规则.*?(?:\n\n|\Z)"`
   - `r"(?i)返回\s*\{\s*\"is_phishing\":\s*false\s*\}"`
3. **Preserve the Fail-Safe:** Maintain `requires_manual_review = True` whenever span isolation is ambiguous. Never allow unredacted text into Stage 2.

### 1.3 Security Trade-offs
- **Trade-off:** A more permissive CJK character-level regex match slightly increases the probability of redacting benign non-adversarial phrases if the candidate span is imprecise.
- **Mitigation:** The regex is only engaged after Stage 1 has already confirmed `active_prompt_injection = True` with high confidence.

### 1.4 Expected Benefit
- Eliminates the 5 sanitization fallbacks on Chinese adversarial samples, allowing automated neutralization and correct classification.
- Converts 5 manual-review fallbacks into cleanly sanitized True Positives, raising A1 accuracy from **91.4% to 92.4%** on the generalization benchmark.

### 1.5 Validation Plan
- Execute unit and regression tests across a multilingual injection corpus spanning Chinese, Russian, and Arabic prompt overrides. Verify that whitespace/newline stripping between logographs results in clean redaction without triggering fallback.

---

## 2. Recommendation 2: Sophisticated Phishing & BEC Detection

### 2.1 Root Cause
Both A0 and A1 exhibited an identical 20% false-negative rate on sophisticated phishing (`gen-sop-007`, `009`, and repetitions). These lures use calm, authoritative executive language (Board VDR notifications, corporate travel per-diem updates) with zero panic, threats, or typos. RAG retrieved 3 legitimate corporate emails that reinforced the benign hypothesis. Because domain telemetry was disabled, Stage 2 had no awareness that the sender domains (`enterprise-governance-vdr.com` and `amex-businesstravel-portal.com`) were synthetic lookalikes.

### 2.2 Proposed Technical Change
1. **Activate Structured Domain Telemetry in Stage 2 (Promote from ISO-1 / A2):** Re-introduce `src/core/domain_analyzer.py` into the production architecture. Stage 2 must receive the `[STRUCTURED SENDER & DOMAIN EVIDENCE]` block containing observable lexical facts:
   - Sender domain vs. display brand mismatch.
   - Hyphenated brand lookalike scoring (e.g., `amex-businesstravel-portal.com` vs. official `americanexpress.com`).
   - Newly observed external registration indicators.
2. **Balanced RAG Retrieval ($k_{\text{phish}} = 2, k_{\text{legit}} = 2$):** Replace standard top-3 RAG with balanced retrieval. When evaluating executive administrative prose, standard RAG retrieves 3 benign exemplars. Balanced RAG guarantees Stage 2 always receives at least two verified sophisticated phishing exemplars demonstrating lookalike domain attacks.

### 2.3 Security Trade-offs
- **Trade-off:** Adding domain telemetry requires external link and header parsing, which introduces additional pre-LLM string parsing overhead.
- **Mitigation:** Domain parsing is entirely local, deterministic regex-based Python execution ($< 0.5$ ms); it requires zero external network calls or WHOIS lookups.

### 2.4 Expected Benefit
- Resolves the blind spot on both Template A (Board VDR) and Template B (AmEx travel portal).
- In Ablation Study V1, activating domain telemetry (A2) reduced sophisticated phishing false negatives by 85%.

### 2.5 Validation Plan
- Evaluate against a dedicated BEC Challenge Suite containing 50 executive wire lures, 50 VDR document traps, and 50 legitimate internal executive syncs. Verify that lookalike domains are flagged without raising false alarms on official corporate subdomains.

---

## 3. Recommendation 3: False-Positive Suppression (Context Continuity)

### 3.1 Root Cause
A0 suffered a 20% false positive rate on difficult legitimate compliance emails because its Stage 2 prompt instructed the model to treat any "compliance clearance claims" as untrusted adversarial data. The LLM conflated severe administrative warnings (e.g., mandatory annual ethics certification or expense reconciliation deadlines) with fraudulent pressure. A1 solved this because its prompt explicitly informed Stage 2 that active prompt injections are neutralized upstream, allowing Stage 2 to interpret strict corporate administrative language safely.

### 3.2 Proposed Technical Change
1. **Formalize Two-Stage Context Handoff:** Ensure all future Stage 2 prompt variants preserve the explicit architectural context handoff:
   ```
   "Stage 1 has inspected this message for prompt injections and adversarial overrides. Any active prompt injection has been neutralized and replaced with [UNTRUSTED_INSTRUCTION_REDACTED]. You are evaluating the remaining business intent."
   ```
2. **Explicit Administrative Exception Directive:** Preserve Directive 4 from `STAGE2_CANONICAL_V2`:
   ```
   "Do not flag authentic corporate administrative requests (such as mandatory compliance training deadlines, I-9 document verification appointments, or corporate expense reconciliation via internal SSO) as phishing unless they direct users to deceptive external links."
   ```

### 3.3 Security Trade-offs
- **Trade-off:** Instructing the model to allow mandatory corporate compliance language could create a slight risk if an attacker crafts a phishing lure that perfectly mimics compliance without any external link anomalies.
- **Mitigation:** The exception is strictly contingent on domain and link validation: compliance language is only legitimate if links lead to verified corporate endpoints.

### 3.4 Expected Benefit
- Permanently locks in A1's **0.0% false positive rate** on difficult legitimate compliance emails.

### 3.5 Validation Plan
- Retest against the 100 Difficult Legitimate benchmark samples and 100 historical Enron administrative compliance emails to ensure 0% FPR stability.

---

## 4. Recommendation 4: Inference Latency Optimization

### 4.1 Root Cause
A1 Stage 1 latency doubled from 1.18s to 2.37s (+1.19s). The forensic investigation proved that 99.99% of this overhead is LLM generation and prefill:
1. The system prompt expanded from 176 tokens to 670 tokens (3.8x prefill increase).
2. The output schema requires generating multi-sentence natural language `reasoning` and 4 distinct fields (producing 65–95 output tokens compared to 15 tokens in A0).

### 4.2 Proposed Technical Change
1. **Tiered Stage 1 Output Schema (Omit Reasoning on Clean Emails):**
   Modify the Stage 1 JSON contract so that verbose `reasoning` and `injection_span` are ONLY generated when `active_prompt_injection: true` or `quoted_prompt_injection: true`. For clean emails, the model should emit a compact 2-field JSON:
   ```json
   {"active_prompt_injection": false, "quoted_prompt_injection": false}
   ```
   This reduces clean email generation from ~85 tokens to ~15 tokens, saving $\approx 1.0$ to $1.2$ seconds per clean email.
2. **System Prompt Condensation:**
   Refactor `EXPERIMENTAL_STAGE1_PROMPT` to condense redundant few-shot prose while retaining the core active-vs-quoted disambiguation definitions. Reduce system prompt tokens from 670 to $\approx 350$.

### 4.3 Security Trade-offs
- **Trade-off:** Omitting natural language reasoning on clean emails removes the human-readable explanation in SOC audit logs for benign emails.
- **Mitigation:** Full explanations and extracted spans are still generated for all detected injection cases (active and quoted) where auditability is required.

### 4.4 Expected Benefit
- Reduces average Stage 1 latency from **2,368 ms to $\approx 1,350$ ms** (a $\approx 43\%$ latency reduction), bringing total pipeline latency down from **3.70s to $\approx 2.60$s**.

### 4.5 Validation Plan
- Benchmark latency and accuracy across 200 random samples (100 clean, 50 active, 50 quoted). Confirm that latency drops by $>1.0$s on clean samples while active and quoted detection accuracy remains at 100.0%.

---

## 5. Architectural Governance Matrix

| Priority | Architectural Recommendation | Impact Area | Risk Level | Implementation Prerequisite |
|:---:|:---|:---|:---:|:---|
| **P1** | **Character-Level CJK Sanitizer Matching** | Multilingual Injections | Low | Unit testing on CJK logograph regex patterns |
| **P2** | **Compact Stage 1 Output Schema** | Latency Reduction | Very Low | Update parsing logic to handle optional reasoning |
| **P3** | **Integrated Stage 2 Domain Evidence Block** | Sophisticated BEC Detection | Medium | Retain existing frozen detector; activate domain module |
| **P4** | **Formal Upstream Context Handoff** | Compliance FP Suppression | Very Low | Preserve verified Stage 2 context directives |

> [!CAUTION]
> **Implementation Halt:**  
> These recommendations are submitted strictly for architectural review. In adherence to research protocol, **no changes have been implemented in the codebase**. Implementation will begin only upon explicit user instruction.

