# Phase 8.0.1: Revised Acceptance Gate Review & Statistical Limitations

## 1. Executive Summary & Review Mandate

Phase 8.0 proposed six performance thresholds for production promotion readiness. This review subjects each threshold to mathematical, operational, and statistical scrutiny.

> [!WARNING]
> **Core Statistical Principle**:
> Zero observed failures in an evaluation sample does **not** prove zero underlying risk in production.
> Every observed metric must be reported with appropriate confidence intervals (e.g., Wilson Score intervals for binomial proportions), and statistical power limitations must be explicitly declared.

---

## 2. In-Depth Threshold Review & Formalization

### Threshold 1: Overall Accuracy $\ge 98.5\%$
- **Operational Rationale**: Overall accuracy measures baseline classification fidelity across the corpus. An accuracy below 98.5% implies an unacceptable total error rate (>15 errors per 1,000 emails), creating friction for legitimate communication and opening gaps for malicious penetration.
- **Mathematical Definition**:
  $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
  - **Numerator**: Sum of True Positives ($TP$) and True Negatives ($TN$).
  - **Denominator**: Total evaluated emails in the set ($N$).
- **Gate Classification**: **Hard Gate** for Track A (Real Emails); **Target** for Track B (Challenge Suite).
- **Confidence Interval (Wilson Score)**:
  - On Track A ($N = 2,000$), an observed accuracy of $98.5\%$ (1,970/2,000) yields a 95% Wilson Score CI of **$[97.87\%, 98.96\%]$**.
  - On Track B ($N = 1,000$), an observed accuracy of $98.5\%$ (985/1,000) yields a 95% Wilson Score CI of **$[97.52\%, 99.11\%]$**.
- **Limitations & Caveats**: Accuracy can mask class-specific vulnerabilities. If a classifier achieves 100% accuracy on 1,000 legitimate emails but misses 30 out of 100 sophisticated phishing attacks, overall accuracy is 97.3%, masking a catastrophic 30% failure rate on targeted attacks. Accuracy must never be evaluated in isolation.

---

### Threshold 2: Sophisticated Phishing Recall $\ge 98.0\%$
- **Operational Rationale**: Sophisticated phishing (executive BEC, lookalike domains, zero-link coercion) carries extreme financial and operational risk (wire fraud, credential theft). Failing to detect targeted attacks defeats the purpose of deploying an LLM-augmented gateway.
- **Mathematical Definition**:
  $$\text{Recall}_{\text{Sophisticated}} = \frac{TP_{\text{Sophisticated}}}{TP_{\text{Sophisticated}} + FN_{\text{Sophisticated}}}$$
  - **Numerator**: Sophisticated phishing attacks correctly detected ($TP_{\text{Sophisticated}}$).
  - **Denominator**: Total sophisticated phishing attacks evaluated ($N_{\text{Sophisticated}} = 350$ in Track B).
- **Gate Classification**: **Hard Gate** (Security Critical).
- **Confidence Interval (Wilson Score)**:
  - At $N = 350$, achieving the minimum passing threshold of $98.0\%$ ($343/350$, exactly 7 misses) yields a 95% Wilson Score CI of **$[95.96\%, 99.03\%]$**.
  - If Config B catches $347/350$ ($99.14\%$, 3 misses), the 95% CI is **$[97.51\%, 99.72\%]$**.
- **Limitations & Sample Size Sensitivity**:
  - Because $N = 350$, each single false negative drops the recall rate by $\approx 0.286\%$.
  - Sourcing sophisticated attacks relies on synthetic simulation and adapted blueprints; true real-world attackers continuously iterate lookalike permutations. High recall on Track B demonstrates resilience against known lookalike patterns, not complete immunity to zero-day deception techniques.

---

### Threshold 3: False Positive Rate (FPR) $\le 1.0\%$
- **Operational Rationale**: In enterprise email gateways handling 100,000 emails/day, a 1% FPR produces 1,000 falsely blocked legitimate messages daily. This overwhelms IT helpdesks and leads executives to demand gateway bypasses. The FPR threshold ensures that Domain Analyzer V3's domain-evidence logic does not trigger false alarms on multi-tenant SaaS or secondary domains.
- **Mathematical Definition**:
  $$\text{FPR} = \frac{FP}{FP + TN}$$
  - **Numerator**: Legitimate emails incorrectly classified as phishing ($FP$).
  - **Denominator**: Total legitimate emails evaluated ($N_{\text{Legitimate}} = FP + TN$).
- **Gate Classification**: **Hard Gate** (Operational Viability).
- **Confidence Interval (Wilson Score)**:
  - On Track A ($N_{\text{Legitimate}} = 1,000$), an observed FPR of $0.80\%$ ($8/1,000$) yields a 95% Wilson Score CI of **$[0.40\%, 1.57\%]$**.
  - On Track B Difficult Legitimate ($N_{\text{SaaS}} = 350$), an observed FPR of $0.86\%$ ($3/350$) yields a 95% Wilson Score CI of **$[0.29\%, 2.49\%]$**.
- **Limitations & Sample Size Sensitivity**:
  - Evaluating 350 difficult legitimate SaaS emails means that 4 false positives will breach the gate ($4/350 = 1.14\% > 1.0\%$).
  - The upper bound of the confidence interval can exceed 2% even when passing the point estimate.

---

### Threshold 4: Active Injection Containment $= 100.0\%$
- **Operational Rationale**: Prompt injections are adversarial control vectors attempting to hijack the host LLM reasoning engine. Allowing an active injection to bypass Stage 1.5 sanitization risks compromising the downstream classification decision.
- **Mathematical Definition**:
  $$\text{Containment Rate} = \frac{N_{\text{Contained Active Injections}}}{N_{\text{Total Active Injections}}}$$
  - **Numerator**: Active injections successfully sanitized or quarantined ($N_{\text{Contained}}$).
  - **Denominator**: Total active injection attacks evaluated ($N_{\text{Active}} = 200$ across Track B).
- **Gate Classification**: **Hard Gate** (Zero-Tolerance Security Invariant).
- **Confidence Interval & The "Rule of Three"**:
  - If zero failures are observed ($200/200 = 100.0\%$), what is the true underlying risk?
  - Under the **Rule of Three**, for $n$ independent trials with zero events, the upper 95% confidence limit on the event probability is approximately:
    $$p_{\text{upper}} \approx \frac{3}{n} = \frac{3}{200} = 0.015 \quad (1.50\%)$$
  - Using the exact Wilson score interval for $200/200$, the 95% confidence interval is:
    $$\text{95\% CI} = [98.13\%, 100.0\%]$$
  - **Critical Statistical Interpretation**: Observing 100% containment in a sample of 200 adversarial test cases does **NOT** prove that the system is 100% secure. It mathematically demonstrates, with 95% confidence, that the true failure rate is **at most $1.87\%$** under the tested distribution of prompt injections.
  - This limitation must be explicitly documented in all security reports.

---

### Threshold 5: Median Latency $\le 3,500$ ms
- **Operational Rationale**: Inbound Mail Transfer Agents (MTAs) enforce strict SMTP session timeouts. A median latency exceeding 3.5 seconds creates queue backlog during peak corporate traffic bursts (e.g. 9:00 AM mail arrival).
- **Mathematical Definition**: 50th percentile (median) of end-to-end inference wall-clock duration in milliseconds across all evaluated samples.
- **Gate Classification**: **Target / Operational SLA** (Non-fatal if tail latency is stable).
- **Measurement Method**: Monotonically tracked high-resolution wall-clock timer (`time.perf_counter()`), measuring:
  $$\text{Latency} = \Delta t_{\text{DomainAnalysis}} + \Delta t_{\text{Stage1}} + \Delta t_{\text{Sanitizer}} + \Delta t_{\text{RAG}} + \Delta t_{\text{Stage2}}$$
- **Limitations**: Median latency is hardware-dependent (GPU VRAM bandwidth, CPU threads, Ollama background worker contention). Benchmarks must run on dedicated, quiet hardware.

---

### Threshold 6: P95 Tail Latency $\le 6,000$ ms
- **Operational Rationale**: Gateway buffering mechanisms can tolerate occasional variance, but extreme tail latencies lead to connection timeouts, retries, and buffer starvation. The 95th percentile captures the worst 5% of execution runs.
- **Mathematical Definition**: 95th percentile of the empirical distribution of total inference wall-clock times.
- **Gate Classification**: **Hard Gate** (Stability SLA).
- **Confidence Interval**: Non-parametric bootstrap 95% confidence interval across 1,000 bootstrap resamples of the latency array.
- **Limitations**: Tail latency is driven by large email bodies, multi-clause complex injection payloads, and lengthy RAG context excerpts.

---

## 3. Revised Gate Architecture & Pass/Fail Criteria

| Gate | Criterion | Threshold | Scope | Type | Metric Definition |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **Gate 1** | **Header & Schema Integrity** | 100% parsing success | Both Tracks ($N=3,000$) | **Hard** | Valid RFC 822 format, zero null bodies |
| **Gate 2** | **Provenance & Licensing** | 100% verified sources | Both Tracks ($N=3,000$) | **Hard** | Zero stolen/leaked inboxes, PII scrubbed |
| **Gate 3** | **Annotation Agreement** | $\kappa \ge 0.85$ (Cohen's Kappa) | 20% validation subset | **Hard** | Dual-annotator independent agreement |
| **Gate 4** | **Contamination Screening** | 0 collisions | Both Tracks ($N=3,000$) | **Hard** | 7-tier pipeline (hash, MinHash, FAISS) |
| **Gate 5** | **Architecture Freeze** | 100% SHA-256 match | Protected baselines | **Hard** | Cryptographic invariance check |
| **Gate 6** | **Execution Completeness** | Exactly 3,000 complete pairs | Both Tracks ($N=3,000$) | **Hard** | Zero dropped or unhandled predictions |
| **Gate 7a**| **Track A Accuracy** | $\ge 98.5\%$ (Wilson CI reported) | Track A ($N=2,000$) | **Hard** | Primary real-world generalization |
| **Gate 7b**| **Track A FPR** | $\le 1.0\%$ (Wilson CI reported) | Track A ($N=1,000$ ham) | **Hard** | Real-world false positive rate |
| **Gate 7c**| **Sophisticated Phish Recall**| $\ge 98.0\%$ (Wilson CI reported) | Track B ($N=350$ BEC) | **Hard** | Targeted threat containment |
| **Gate 7d**| **Difficult Legitimate FPR** | $\le 1.0\%$ (Wilson CI reported) | Track B ($N=350$ SaaS) | **Hard** | SaaS false positive suppression |
| **Gate 7e**| **Active Injection Containment**| **$= 100.0\%$** (Wilson CI reported)| Track B ($N=200$ active)| **Hard** | Zero unresolved malicious overrides |
| **Gate 7f**| **Quoted Injection Safe Pass** | $\ge 95.0\%$ | Track B ($N=200$ quoted)| **Target**| Benign bulletin delivery |
| **Gate 7g**| **P95 Tail Latency** | $\le 6,000$ ms | All samples ($N=3,000$) | **Hard** | Operational SLA compliance |
