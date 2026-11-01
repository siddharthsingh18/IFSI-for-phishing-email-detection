# Forensic Analysis of Previous Domain Telemetry Failures

**Project:** IFSI Phishing Email Detection  
**Experiment:** Phase 6 — Domain Evidence Integration Study  
**Date:** November 2026  
**Status:** Completed Analysis  

---

## 1. Executive Summary

In the M4 Ablation V1 benchmark (250 evaluated samples across 9 configurations), Configuration A1 (Legacy Domain Analysis **Disabled**) achieved **92.80% overall accuracy** and **96.00% phishing recall**. In contrast, Configuration A2 (Legacy Domain Analysis **Enabled**, identical in all other components) fell to **89.20% overall accuracy** and **88.80% phishing recall**.

Most alarmingly:
- **Sophisticated Phishing detection collapsed from 92.00% (46/50) in A1 to 78.00% (39/50) in A2 (-14.00% absolute drop).**
- **Conventional Phishing detection dropped from 100.00% (50/50) in A1 to 94.00% (47/50) in A2 (-6.00% absolute drop).**
- Overall False Negatives surged from **5 in A1 to 14 in A2 (+180% surge in missed phishing attacks)**.

This forensic investigation analyzes the source code of `src/core/domain_analyzer.py`, the Stage 2 prompt interaction in `src/core/prompts.py`, and the 13 specific phishing samples where the legacy domain telemetry actively tricked the Stage 2 LLM into classifying confirmed phishing attacks as legitimate corporate correspondence.

---

## 2. Empirical Performance Comparison: A1 vs. A2

Both configurations received the exact same 250 evaluation samples (Live Benchmark V2: 150; Held-Out Benchmark V1: 100) under identical hardware, seed, model (`qwen3.5:4b`), temperature (0.0), token limits (512), and top-3 RAG retrieval. The only variable was whether `domain_analyzer.analyze_domains(...)` was executed and appended to the Stage 2 prompt.

| Metric | Config A1 (Domain OFF) | Config A2 (Domain ON) | Delta (A2 - A1) |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **92.80%** (232/250) | 89.20% (223/250) | **-3.60%** |
| **Phishing Precision** | **90.23%** | 89.52% | -0.71% |
| **Phishing Recall** | **96.00%** (120/125) | 88.80% (111/125) | **-7.20%** |
| **Phishing F1** | **0.9302** | 0.8916 | **-0.0386** |
| **False Positive Rate (FPR)** | 10.40% (13/125) | 10.40% (13/125) | 0.00% |
| **False Negative Rate (FNR)** | **4.00%** (5/125) | **11.20%** (14/125) | **+7.20%** |
| **Total False Negatives** | **5** | **14** | **+9 missed attacks** |

### Category-Specific Breakdown

| Evaluation Category | Total Samples | A1 Correct (Domain OFF) | A2 Correct (Domain ON) | Delta |
| :--- | :---: | :---: | :---: | :---: |
| **Ordinary Genuine** | 50 | 49 (98.0%) | 49 (98.0%) | 0.0% |
| **Difficult Genuine** | 50 | 41 (82.0%) | 41 (82.0%) | 0.0% |
| **Conventional Phishing** | 50 | 50 (100.0%) | 47 (94.0%) | **-6.0%** |
| **Sophisticated Phishing** | 50 | 46 (92.0%) | 39 (78.0%) | **-14.0%** |
| **Prompt Injection** | 50 | 46 (92.0%) | 47 (94.0%) | +2.0% |

---

## 3. Discrepancy Case Analysis: The 13 Regressions

In 13 samples, A1 correctly detected phishing via email body/header cues, but A2 flipped to False Negative upon reading the domain telemetry block:

### Selected Representative Examples

#### Case 1: `v2-sop-10` — Fraudulent Wire Payment / Banking Change
- **Sender:** `billing-support@apex-industrial-contractors.com`
- **Subject:** *Important: Revised Wiring Instructions for Upcoming Milestone Payment*
- **A1 Verdict:** Phishing (Correct). Detected financial urgency and unauthorized wire alteration.
- **A2 Verdict:** Legitimate (False Negative).
- **A2 LLM Reasoning:**
  > *"The sender domain (apex-industrial-contractors.com) matches the link destination domain exactly, indicating no brand impersonation or lookalike attack. The email content describes a legitimate administrative action regarding a banking change and vendor compliance update (Form W-9), which is consistent with standard corporate communication patterns."*

#### Case 2: `v2-sop-06` — Executive Impersonation Memo
- **Sender:** `mark.vance.coo@exec-internal-memo.net`
- **Subject:** *From the Desk of the COO: Organizational Realignment & Q1 Targets*
- **A1 Verdict:** Phishing (Correct). Detected executive authority spoofing.
- **A2 Verdict:** Legitimate (False Negative).
- **A2 LLM Reasoning:**
  > *"The sender domain 'exec-internal-memo.net' aligns with the link destination, indicating a consistent internal infrastructure rather than a deceptive lookalike. The email content describes standard administrative tasks (operational realignment, budget adjustments) typical of legitimate corporate communications."*

#### Case 3: `v2-sop-02` — Executive Bonus Census Credential Harvesting
- **Sender:** `robert.vance.chro@executive-talent-board.com`
- **Subject:** *Confidential Request: Executive Bonus & Deferred Compensation Census*
- **A1 Verdict:** Phishing (Correct).
- **A2 Verdict:** Legitimate (False Negative).
- **A2 LLM Reasoning:**
  > *"Sender domain 'executive-talent-board.com' matches the verified organizational domain and exhibits standard corporate naming patterns without deceptive hyphenation or suspicious TLDs. No external URLs were detected in the email content, eliminating the risk of redirecting to phishing sites."*

#### Case 4: `heldout-sop-14` — Corporate Travel Itinerary Spoofing
- **Sender:** `travel-operations@amextravel-corporate.com`
- **Subject:** *American Express Global Business Travel: Flight Itinerary Schedule Change*
- **A1 Verdict:** Phishing (Correct).
- **A2 Verdict:** Legitimate (False Negative).
- **A2 LLM Reasoning:**
  > *"Sender domain 'amextravel-corporate.com' aligns with the link destination and represents a legitimate corporate administrative entity. The email content describes a standard business travel itinerary modification notification consistent with legitimate corporate communications."*

---

## 4. Root Causes in `src/core/domain_analyzer.py`

Inspection of `src/core/domain_analyzer.py` reveals four fatal design flaws:

### Flaw 1: False Reassurance on Negative Heuristics (Lines 209–210)
```python
if not indicators:
    lines.append("- Observable Domain Signals: Clean / Standard corporate naming patterns.")
```
**Mechanism:** The legacy analyzer had a hardcoded list of 35 brand names (`microsoft`, `google`, `paypal`, `workday`, etc.). If an attacker used a domain like `executive-talent-board.com` or `apex-industrial-contractors.com`, none of the 35 brand strings matched. Because `indicators` remained empty, line 210 injected the explicit assertion:
`- Observable Domain Signals: Clean / Standard corporate naming patterns.`
The LLM interpreted this statement as an authoritative, verified cryptographic or threat-intel confirmation that the domain was clean corporate infrastructure.

### Flaw 2: The "Link Alignment" Fallacy (Lines 185–187)
```python
if sender_domain and link_domain == sender_domain:
    lines.append("- Link Alignment: Sender domain matches destination link.")
```
**Mechanism:** Sophisticated spear-phishers routinely purchase their own domain (e.g., `exec-internal-memo.net`) and host their harvesting page on the exact same domain. The legacy analyzer celebrated this as positive evidence of safety, declaring that the sender domain matched the destination link. The LLM then reasoned: *"The sender domain matches the link destination, so this is not an attack."*

### Flaw 3: Binary Brand Impersonation vs. Universal Domain Blindness
The legacy analyzer used a naive substring search:
```python
KNOWN_BRANDS = ["paypal", "microsoft", "apple", "google", "amazon", "chase", "wellsfargo", "bankofamerica", ...]
```
While this caught 4 crude brand attacks (e.g., `corporate-workday-portal.com`, `corporate-concur-portal.org`), it completely missed targeted lookalikes outside the 35 brands and actively whitewashed them with the "Clean" label.

### Flaw 4: Hyper-Aggressive Directive Prompting and Risk Escalation
When an indicator was triggered, the legacy analyzer emitted:
`[CRITICAL RISK - BRAND IMPERSONATION]` or `[HIGH RISK - DECEPTIVE LOOKALIKE DOMAIN]`
In `src/core/prompts.py` (`SYSTEM_IS_PHISHING_ONLY_V2`), the LLM was instructed:
> *"If domain analysis flags [CRITICAL RISK] or [HIGH RISK], classify as is_phishing: true unless overwhelming counter-evidence exists."*
This made the system hyper-sensitive to false positives on legitimate multi-tenant SaaS domains (e.g., Zendesk ticketing, Greenhouse recruitment, DocuSign envelope notifications), while failing catastrophically whenever an attacker bypassed the heuristic.

---

## 5. Architectural Requirements for Phase 6 Domain Evidence

To eliminate these vulnerabilities, Phase 6 must adhere to the following strict architectural principles:

1. **Strictly Neutral Observable Structural Telemetry:**  
   The domain analyzer must extract and report **purely factual observables** (sender address, sender domain, display name, reply-to address, reply-to domain, extracted URL hostnames, URL-to-sender alignment).
2. **Zero Evaluative Hallucinations ("Clean / Standard"):**  
   If no anomalous patterns are observed, state neutrally: *"No structural anomalies or brand keyword collisions observed in available headers"*. Never assert that a domain is "Clean", "Verified", or "Standard corporate infrastructure". Absence of an indicator is not evidence of safety.
3. **Zero Synthetic Severity Flags:**  
   Remove `[CRITICAL RISK]`, `[HIGH RISK]`, or numerical risk scores. The Stage 2 model must synthesize structural domain facts alongside email body semantics, urgency indicators, and RAG exemplars.
4. **Distinguish Infrastructure / SaaS from Impersonation:**  
   Recognize common multi-tenant SaaS patterns (DocuSign, Zoom, Salesforce, ServiceNow) neutrally without penalizing legitimate cross-domain transactional links.
5. **Display Name vs. Sender Domain Alignment:**  
   Explicitly check whether the header Display Name claims an identity (e.g. "Workday HR") that diverges from the actual sender domain (e.g. `random-mail.com`), providing objective evidence of identity spoofing.

