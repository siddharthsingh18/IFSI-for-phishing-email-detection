# Phase 6: False Positive & Edge Case Analysis

**Project:** IFSI Phishing Email Detection  
**Experiment:** Phase 6 — Domain Evidence Integration Study  
**Date:** November 2026  
**Status:** Completed Analysis  

---

## 1. Executive Summary

A critical requirement of Phase 6 was to verify whether the introduction of structured domain evidence would cause false positives on legitimate emails (a major flaw of the legacy analyzer in M4 ablation).

Across **110 total legitimate emails** evaluated across the two suites (50 quoted injection discussions, 40 difficult legitimate emails, and 20 ordinary legitimate emails):
- **Config A (Baseline):** 0 False Positives (**0.0% FPR**, 110/110 true negatives).
- **Config B (Domain Evidence):** 3 False Positives (**2.73% FPR**, 107/110 true negatives).

While a 2.73% False Positive Rate is substantially superior to the legacy analyzer's 10.40% FPR, forensic dissection of the 3 false positive samples reveals precise heuristic edge cases that must be refined in future iterations.

---

## 2. Dissection of the Three False Positives

### Case 1: `gen-ord-010` — Legitimate Amazon Business Order Confirmation
- **Dataset:** `phase5_regression_160` (Ordinary Genuine)
- **Sender Address:** `auto-confirm@amazon-business.com`
- **Subject:** *Your Amazon Business order #114-8829102 has shipped*
- **Ground Truth:** Legitimate corporate procurement receipt.
- **Config B Verdict:** Phishing (False Positive).

#### Forensic Telemetry Emitted:
```
[STRUCTURED SENDER & DOMAIN EVIDENCE]
- Sender Address: auto-confirm@amazon-business.com
- Sender Domain: amazon-business.com
- Observable Structural Facts:
  * Synthetic Brand Lookalike: Sender domain 'amazon-business.com' embeds brand name 'amazon' with hyphenated or extra words; does not match authorized domain(s) (amazon.com, aws.amazon.com).
  * Identity Mismatch: Header/Subject references 'Amazon' but sender domain is 'amazon-business.com' (authorized domains: amazon.com, aws.amazon.com).
```

#### Root Cause:
Amazon officially registers and operates `amazon-business.com` as a secondary domain dedicated to B2B enterprise procurement accounts. The domain analyzer's `AUTHORIZED_BRAND_DOMAINS` dictionary only contained `amazon.com` and `aws.amazon.com`. Consequently, the heuristic deterministically flagged `amazon-business.com` as an unauthorized hyphenated lookalike, causing the Stage 2 model to flag it.

---

### Case 2: `p6-leg-007` — Internal Corporate Concur Expense Notification
- **Dataset:** `phase6_domain_challenge` (Difficult Legitimate)
- **Sender Address:** `concur-travel@enterprise-corp.com`
- **Subject:** *SAP Concur: Expense Report #ER-4491 Approved for Payment*
- **Destination Link:** `https://concur.internal.enterprise-corp.com/reimbursement/ER-4491`
- **Ground Truth:** Legitimate internal finance approval.
- **Config B Verdict:** Phishing (False Positive).

#### Forensic Telemetry Emitted:
```
[STRUCTURED SENDER & DOMAIN EVIDENCE]
- Sender Address: concur-travel@enterprise-corp.com
- Sender Domain: enterprise-corp.com
- Extracted Destination Links:
  * https://concur.internal.enterprise-corp.com/reimbursement/ER-4491 (Host: concur.internal.enterprise-corp.com)
- Observable Structural Facts:
  * Identity Mismatch: Header/Subject references 'Concur' but sender domain is 'enterprise-corp.com' (authorized domains: concur.com, concursolutions.com).
  * Domain Alignment: Destination link hosts are internal subdomains or exact matches of sender domain 'enterprise-corp.com'.
```

#### Root Cause:
This represents an **Internal Corporate Tool Reference**. The email was sent by the company's internal travel & expense team (`concur-travel@enterprise-corp.com`) using their verified corporate domain, directing the user to their internal corporate portal (`concur.internal.enterprise-corp.com`). However, because the Subject line mentioned "SAP Concur", the analyzer flagged an "Identity Mismatch", asserting that the email claimed to be Concur but originated from `enterprise-corp.com`. The LLM prioritized this alert over the internal link alignment.

---

### Case 3: `p6-leg-015` — Workday Official Payslip Notification
- **Dataset:** `phase6_domain_challenge` (Difficult Legitimate)
- **Sender Address:** `Workday Notifications <notifications@workday.com>`
- **Subject:** *Workday: Your Monthly Payslip is Ready for Review*
- **Destination Link:** `https://www.myworkday.com/enterprise-corp/login.htmld`
- **Ground Truth:** Legitimate SaaS HR payslip notification.
- **Config B Verdict:** Phishing (False Positive).

#### Forensic Telemetry Emitted:
```
[STRUCTURED SENDER & DOMAIN EVIDENCE]
- Sender Address: notifications@workday.com
- Sender Domain: workday.com
- Extracted Destination Links:
  * https://www.myworkday.com/enterprise-corp/login.htmld (Host: www.myworkday.com)
- Observable Structural Facts:
  * Deceptive Link Destination: Link host 'www.myworkday.com' embeds brand name 'workday' in an unofficial domain (authorized: workday.com).
  * External Destination: All extracted destination links (myworkday.com) point outside sender domain 'workday.com' to unverified third-party hosts.
```

#### Root Cause:
Workday hosts tenant login portals on `myworkday.com` while sending outbound transactional notifications from `workday.com`. The analyzer only registered `workday.com` as authorized. When it saw a link to `myworkday.com`, it flagged it as a "Deceptive Link Destination" embedding the brand name. The Stage 2 model obediently classified it as phishing.

---

## 3. Key Design Lessons for Phase 7

1. **Enterprise Secondary & Application Domains:**  
   Major enterprise SaaS platforms routinely use distinct second-level domains for customer tenants and portals (e.g. `myworkday.com`, `concursolutions.com`, `amazon-business.com`). The authorized domain registry must encompass verified multi-tenant infrastructure.
2. **Context-Aware Identity Mismatch:**  
   An email originating from the company's verified primary domain (`@enterprise-corp.com`) referencing an enterprise vendor (e.g., Concur, Workday, Zoom, Slack) in the subject line is standard corporate communication. The `Identity Mismatch` rule should only trigger when an **external third-party domain** claims to represent a recognized brand.
3. **Synthesis Over Hard Overrides:**  
   When internal subdomain alignment is confirmed (`concur.internal.enterprise-corp.com`), the analyzer should explicitly suppress brand collision flags for that internal application.

