# Phase 8.0.1: Real Email Corpus (Track A) vs. Controlled Challenge Corpus (Track B)

> [!IMPORTANT]
> **PHASE 8.1A GOVERNANCE UPDATE**:
> 1. **Track A Acquisition Hold**: Per [`phase8_1a_final_decision.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1a_final_decision.md), neither Enron nor Jose Nazario is currently cleared for acquisition due to unresolved licensing and historical data independence (including `369` active Enron vectors in `rag_index_clean` and `100%` historical consumption of `phishing3.mbox`).
> 2. **Track B1 vs. Track B2 Sub-Partition**: Per [`phase8_1a_track_b_clarifications.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1a_track_b_clarifications.md), Track B explicitly separates `synthetic_email_envelope` and `adapted_email_example` records (**Track B1**, `is_email: true`) from `standalone_non_email_document` research papers and vulnerability advisories (**Track B2**, `is_email: false`, `header_origin: "none"`). Standalone documents never receive fabricated email headers and remain strictly excluded from email classification metrics.

## 1. Architectural Mandate: Strict Track Separation

To ensure scientific defensibility and prevent methodological confusion, the IFSI Phase 8 evaluation is split into **two completely separate evaluation tracks**:

```
+──────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    PHASE 8 DUAL-TRACK ARCHITECTURE                               |
+──────────────────────────────────────────────────────────────────────────────────────────────────+
|                                                                                                  |
|   ┌────────────────────────────────────────┐            ┌────────────────────────────────────┐   |
|   | TRACK A: INDEPENDENT REAL EMAIL CORPUS |            | TRACK B: CONTROLLED CHALLENGE SUITE|   |
|   └───────────────────┬────────────────────┘            └─────────────────┬──────────────────┘   |
|                       │                                                   │                      |
|       Authentic RFC 822 Email Messages                     Synthetic / Adapted / Stress Tests    |
|       Real Enterprise & Phishing Traffic                   Targeted BEC, Lookalikes, Injections  |
|       Verified Public Provenance                           Adversarial Boundary Probing          |
|                       │                                                   │                      |
|                       ▼                                                   ▼                      |
|          [Track A Independent Run]                           [Track B Independent Run]           |
|                       │                                                   │                      |
|                       ▼                                                   ▼                      |
|          [Track A Standalone Report]                         [Track B Standalone Report]         |
|                                                                                                  |
+──────────────────────────────────────────────────────────────────────────────────────────────────+
```

> [!CAUTION]
> **Strict Reporting Invariant**:
> - **NEVER COMBINE** Track A and Track B predictions into a single pooled metric table.
> - **NEVER DESCRIBE** Track B synthetic challenge results as "real-world independent email generalization."
> - Both tracks must report separate confusion matrices, precision, recall, false positive rates, confidence intervals, and latency distributions.

---

## 2. Track A: Independently Sourced Email Corpus (Real Emails)

### 2.1 Scope & Definition
Track A consists **exclusively of authentic email messages** sourced from verified public research repositories. Every sample in Track A must:
1. Originate from an authentic, real-world email transmission.
2. Possess an intact RFC 822 / MIME transport envelope with authentic headers (`From:`, `Subject:`, `Date:`, `Message-ID:`).
3. Contain realistic body formatting, including organic signatures, disclaimers, conversational threads, or mass-market phishing lures.
4. Have zero synthetic adversarial modifications (no artificial prompt injection payloads injected into the body).

### 2.2 Historical vs. Contemporary Email Distinctions
Evaluation reports must explicitly acknowledge the historical provenance of Track A corpora:

| Characteristic | Historical Email Corpora (Track A) | Modern Operational Mailbox (Contemporary) | Impact on Evaluation & Interpretation |
| :--- | :--- | :--- | :--- |
| **Sourcing Period** | 1999–2002 (Enron), 2005–2019 (Nazario) | 2024–2026 | Historical corpora reflect early web and intranet communication styles. |
| **Cloud SaaS Infrastructure** | Absent (Pre-Workday, Pre-Okta, Pre-Slack) | Ubiquitous (Multi-tenant SaaS authentication) | Track A cannot evaluate modern corporate SaaS authentication false positives. |
| **Authentication Headers** | Absent / Primitive (Pre-DKIM, Pre-DMARC) | Standardized (SPF, DKIM, DMARC, ARC) | Domain Analyzer V3 must operate primarily on From header and body link evidence. |
| **Attack Sophistication** | Mass credential theft, generic banking lures | Targeted zero-link BEC, display spoofing | Track A tests generalizability against conventional volume threats. |

### 2.3 Sourcing & Target Allocation (Target $N = 2,000$)
Track A is balanced between authentic legitimate business communications and authentic historical phishing lures:

```
[TRACK A: REAL EMAIL CORPUS (N = 2,000)]
  ├── Real Legitimate Emails (N = 1,000; 50.0%)
  │     └── Enron Email Corpus (Curated Clean Subset)
  │           ├── Internal peer-to-peer correspondence (N = 400)
  │           ├── Operational scheduling and project updates (N = 300)
  │           └── External vendor and business correspondence (N = 300)
  └── Real Phishing Emails (N = 1,000; 50.0%)
        └── Jose Nazario Phishing Corpus
              ├── Financial & banking account suspensions (N = 400)
              ├── Mass cloud / webmail credential harvesters (N = 350)
              └── E-commerce, delivery, and transactional lures (N = 250)
```

---

## 3. Track B: Controlled Challenge Corpus (Stress-Test Suite)

### 3.1 Scope & Definition
Track B evaluates system resilience against modern, high-impact threat vectors and operational edge cases that **cannot be ethically or legally sourced from public real-world mailboxes**.

Track B incorporates:
1. **Difficult Legitimate SaaS Communications**: Synthetic or adapted notifications modeling modern multi-tenant enterprise tools (Okta, Workday, Microsoft 365, AWS, Concur) to evaluate false positive suppression in Domain Analyzer V3.
2. **Sophisticated Phishing Attacks**: Handcrafted or adapted threat scenarios based on FBI IC3 bulletins, CISA alerts, and red-team findings (display name spoofing, hyphenated lookalike domains, executive BEC, vendor banking updates).
3. **Prompt Injection Challenges**: OWASP Top 10 for LLMs payloads embedded into synthetic email envelopes to evaluate Stage 1.5 Sanitizer V2 containment and quoted injection handling.

### 3.2 Target Allocation (Target $N = 1,000$)

```
[TRACK B: CONTROLLED CHALLENGE CORPUS (N = 1,000)]
  ├── Difficult Legitimate Enterprise Challenges (N = 350; 35.0%)
  │     ├── Enterprise SaaS authentication (Workday, Okta, Azure AD) (N = 150)
  │     ├── Verified corporate secondary domains (Amazon Business, AWS) (N = 100)
  │     └── High-urgency internal IT & security maintenance bulletins (N = 100)
  ├── Sophisticated Phishing Attacks (N = 350; 35.0%)
  │     ├── Executive BEC / Zero-link payroll & wire fraud (N = 150)
  │     ├── Synthetic lookalike brand domains (N = 120)
  │     └── Display name spoofing & reply-to hijacking (N = 80)
  └── Dedicated Prompt Injection Suite (N = 300; 30.0%)
        ├── Active Malicious Prompt Injections (N = 150)
        │     ├── Direct instruction overrides (N = 30)
        │     ├── System prompt / XML escape tokens (N = 30)
        │     ├── Markdown exemplar exfiltration lures (N = 30)
        │     ├── Context poisoning & contradictory few-shot spans (N = 30)
        │     └── Multilingual CJK (Chinese, Japanese, Korean) injections (N = 30)
        └── Quoted Benign Security Advisories (N = 150)
              ├── SOC vulnerability advisories quoting injection strings (N = 75)
              ├── Security awareness employee training emails (N = 50)
              └── Bug bounty report discussion threads (N = 25)
```

---

## 4. Methodological Distinction and Reporting Protocols

| Metric / Attribute | Track A (Independent Real Emails) | Track B (Controlled Challenge Suite) |
| :--- | :--- | :--- |
| **Primary Evaluation Objective** | Generalization to authentic historical communications. | Robustness against targeted evasion, false positive traps, and prompt injections. |
| **Scientific Claim Supported** | *"Model generalizes to independently sourced real-world emails without overfitting."* | *"Model demonstrates robustness against synthetic adversarial evasion and SaaS false positive traps."* |
| **Forbidden Claim** | Do not claim performance reflects modern 2026 SaaS mailboxes without acknowledging era constraints. | Do not claim synthetic challenge results represent real-world statistical distribution or prevalence. |
| **Ground Truth Establishment** | Historical consensus and archive documentation. | Dual-annotator agreement on synthetic design criteria. |
| **Contamination Standard** | Strict 7-tier screening against training splits and FAISS index. | Strict semantic deduplication against historical Phase 5/6/7 challenge sets. |

### Separate Metric Reporting Format
All Phase 8 result publications must display dual tables:

```
TABLE 1: TRACK A (REAL-WORLD INDEPENDENT EVALUATION, N = 2,000)
  - Accuracy:         [Observed %] (95% CI: [Low%, High%])
  - Phishing Recall:  [Observed %] (95% CI: [Low%, High%])
  - False Pos. Rate:  [Observed %] (95% CI: [Low%, High%])
  - P95 Latency:      [Observed ms]

TABLE 2: TRACK B (CONTROLLED ADVERSARIAL CHALLENGE SUITE, N = 1,000)
  - Difficult Legitimate FPR:    [Observed %] (Target <= 1.0%)
  - Sophisticated Phish Recall:  [Observed %] (Target >= 98.0%)
  - Active Injection Containment: [Observed %] (Target = 100.0%)
  - Quoted Injection Pass Rate:   [Observed %] (Target >= 95.0%)
  - P95 Latency:                 [Observed ms]
```
