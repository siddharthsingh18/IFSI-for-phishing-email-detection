# Phase 6 False Positive Root Cause Forensic Investigation

**Project:** IFSI Phishing Email Detection  
**Experiment:** Phase 7 — Domain Evidence Precision Refinement  
**Date:** November 2026  
**Status:** Completed Forensic Audit  

---

## 1. Executive Summary

In Phase 6, Config B (Domain Evidence Enabled) achieved 100% phishing recall (90/90 attacks) but produced **3 False Positives out of 110 legitimate emails** (False Positive Rate: 2.73%).

Each of these three failures was forensically reconstructed from raw headers, body text, Domain Analyzer V2 telemetry, and Stage 2 model reasoning.

The investigation proves that all three false positives stem from **overly rigid, incomplete domain relationship heuristics** rather than fundamental LLM reasoning failures:
1. **`gen-ord-010`:** Failure to recognize authentic enterprise secondary domains (`amazon-business.com`).
2. **`p6-leg-007`:** False identity mismatch triggered when an internal corporate employee (`@enterprise-corp.com`) legitimately references an internal vendor application ("SAP Concur") in the subject line.
3. **`p6-leg-015`:** Failure to map multi-domain SaaS architectures where transactional notices originate from one domain (`workday.com`) while tenant application portals reside on another (`myworkday.com`).

---

## 2. Granular Per-Sample Forensic Reconstruction

### Case 1: `gen-ord-010` — Legitimate Amazon Business Order Notification
- **Sample ID:** `gen-ord-010`
- **Source Corpus:** `data/evaluation/phase5_regression_160.jsonl`
- **Category / Subcategory:** `ordinary_legitimate` / `office_supplies`
- **Ground Truth:** `is_phishing: false`
- **Phase 6 Config B Verdict:** `is_phishing: true` (False Positive) $\to$ Action: `block` (Confidence: 0.95)

#### Full Email Artifact:
```email
From: auto-confirm@amazon-business.com
Subject: Your Amazon Business order #114-8829102 has shipped

Hello,

Your order of 4x Ergotron Dual-Monitor Arms has shipped via UPS Ground (Tracking: 1Z992810928192).

Estimated Delivery: Tomorrow by 5:00 PM.
Delivery Address: Suite 400, Receiving Dock, 100 Tech Blvd.

Thank you for shopping with Amazon Business.
```

#### Complete Processing Path:
1. **Header & Body Parsing:**
   - Display Name: `None`
   - Sender Address: `auto-confirm@amazon-business.com`
   - Sender Domain: `amazon-business.com`
   - Reply-To: `None`
   - Extracted Links: None
2. **Domain Analyzer V2 Execution:**
   - Heuristic checked `AUTHORIZED_BRAND_DOMAINS["amazon"]`, which was configured as:
     `{"amazon.com", "aws.amazon.com"}`.
   - The domain `amazon-business.com` embedded the brand substring `"amazon"` with a hyphenated suffix `"-business"`.
   - Because `amazon-business.com` was not explicitly listed in the dictionary, V2 triggered two severe alerts:
     - `Synthetic Brand Lookalike: Sender domain 'amazon-business.com' embeds brand name 'amazon' with hyphenated or extra words; does not match authorized domain(s) (amazon.com, aws.amazon.com).`
     - `Identity Mismatch: Header/Subject references 'Amazon' but sender domain is 'amazon-business.com'.`
3. **Stage 2 LLM Prompt & Verdict:**
   - The LLM received explicit instructions that synthetic brand lookalikes indicate phishing.
   - Seeing the telemetry declaring `amazon-business.com` an unauthorized synthetic lookalike, Stage 2 returned `is_phishing: true`.
4. **Root Cause:**
   - Amazon officially owns and uses `amazon-business.com` worldwide for enterprise corporate accounts.
   - Treating any hyphenated domain embedding a brand name as malicious without an auditable secondary domain registry caused the false positive.

---

### Case 2: `p6-leg-007` — Internal Corporate SAP Concur Expense Notice
- **Sample ID:** `p6-leg-007`
- **Source Corpus:** `data/evaluation/phase6_domain_challenge.jsonl`
- **Category / Subcategory:** `difficult_legitimate` / `legitimate_concur_subdomain`
- **Ground Truth:** `is_phishing: false`
- **Phase 6 Config B Verdict:** `is_phishing: true` (False Positive) $\to$ Action: `block` (Confidence: 0.95)

#### Full Email Artifact:
```email
From: concur-travel@enterprise-corp.com
Subject: SAP Concur: Expense Report #ER-4491 Approved for Payment

Attention Employee,

Your travel and lodging expense report for the London Technical Summit has been approved by your department director.

Reimbursement will be deposited to your primary direct deposit account in 3-5 business days.

Review payment advice: https://concur.internal.enterprise-corp.com/reimbursement/ER-4491

Corporate Finance Operations
```

#### Complete Processing Path:
1. **Header & Body Parsing:**
   - Sender Address: `concur-travel@enterprise-corp.com`
   - Sender Domain: `enterprise-corp.com` (Verified internal corporate domain)
   - Extracted Link: `https://concur.internal.enterprise-corp.com/reimbursement/ER-4491` (Host: `concur.internal.enterprise-corp.com`)
2. **Domain Analyzer V2 Execution:**
   - Link destination analysis correctly identified internal alignment:
     `Domain Alignment: Destination link hosts are internal subdomains or exact matches of sender domain 'enterprise-corp.com'.`
   - BUT the subject line check scanned for brand names: `subject = "SAP Concur: Expense Report..."`.
   - V2 matched brand `"concur"`, looked up authorized domains (`{"concur.com", "concursolutions.com"}`), saw that the sender domain was `enterprise-corp.com`, and emitted:
     `Identity Mismatch: Header/Subject references 'Concur' but sender domain is 'enterprise-corp.com' (authorized domains: concur.com, concursolutions.com).`
3. **Stage 2 LLM Prompt & Verdict:**
   - The Stage 2 model saw conflicting evidence: "Identity Mismatch" vs. "Domain Alignment".
   - The prompt instructed: *"Deceptive synthetic domains that chain administrative keywords or embed recognized brand names... indicate phishing."*
   - The model prioritized the "Identity Mismatch" alert and classified the email as phishing (`block`).
4. **Root Cause:**
   - The sender is an internal corporate employee/service operating under the company's verified primary domain (`@enterprise-corp.com`).
   - Mentioning a corporate software vendor (Concur, Workday, Slack, Zoom, DocuSign) in an internal email is completely standard business operations.
   - Emitting an "Identity Mismatch" alert for emails originating from an organization's own internal domain was a major algorithmic flaw.

---

### Case 3: `p6-leg-015` — Workday HCM Official Payslip Notification
- **Sample ID:** `p6-leg-015`
- **Source Corpus:** `data/evaluation/phase6_domain_challenge.jsonl`
- **Category / Subcategory:** `difficult_legitimate` / `legitimate_workday_official_domain`
- **Ground Truth:** `is_phishing: false`
- **Phase 6 Config B Verdict:** `is_phishing: true` (False Positive) $\to$ Action: `block` (Confidence: 0.95)

#### Full Email Artifact:
```email
From: Workday Notifications <notifications@workday.com>
Subject: Workday: Your Monthly Payslip is Ready for Review

Your payslip for the pay period ending October 31, 2026 is now available in Workday.

View payslip and tax withholding details:
https://www.myworkday.com/enterprise-corp/login.htmld

Workday Human Capital Management
```

#### Complete Processing Path:
1. **Header & Body Parsing:**
   - Display Name: `Workday Notifications`
   - Sender Address: `notifications@workday.com`
   - Sender Domain: `workday.com`
   - Extracted Link: `https://www.myworkday.com/enterprise-corp/login.htmld` (Host: `www.myworkday.com`, Registered Domain: `myworkday.com`)
2. **Domain Analyzer V2 Execution:**
   - The analyzer checked `AUTHORIZED_BRAND_DOMAINS["workday"]`, which was configured only as `{"workday.com"}`.
   - When inspecting the destination link host `www.myworkday.com`, the registered domain was `myworkday.com` (different from `workday.com`).
   - V2 detected the brand name `"workday"` in `myworkday.com`, saw it was not in `{"workday.com"}`, and emitted:
     - `Deceptive Link Destination: Link host 'www.myworkday.com' embeds brand name 'workday' in an unofficial domain (authorized: workday.com).`
     - `External Destination: All extracted destination links (myworkday.com) point outside sender domain 'workday.com' to unverified third-party hosts.`
3. **Stage 2 LLM Prompt & Verdict:**
   - The LLM was told by the telemetry that the link destination was a "Deceptive Link Destination" embedding the brand name in an unofficial domain.
   - The LLM classified the email as phishing (`block`).
4. **Root Cause:**
   - Workday architecturally separates its corporate/transactional domain (`workday.com`) from its customer tenant application portals (`myworkday.com`).
   - The analyzer lacked multi-domain SaaS awareness for customer-facing tenant domains.

---

## 3. Mandatory Engineering Remedies for Domain Analyzer V3

1. **Enterprise Secondary Domain Whitelisting:** Explicitly register verified secondary domains used by major providers (e.g., `amazon-business.com` for Amazon B2B).
2. **Multi-Domain Tenant Mapping:** Map recognized multi-tenant SaaS providers to both their notification origins and tenant web application portals (e.g. `workday.com` $\to$ `myworkday.com`, `concur.com` $\to$ `concursolutions.com`).
3. **Internal Sender Contextual Exemption:** If an email originates from an internal enterprise domain (e.g. `@enterprise-corp.com`) or points to an internal corporate subdomain (`*.internal.enterprise-corp.com`), brand mention heuristics in the subject or body must NOT emit an "Identity Mismatch". Internal employees legitimately reference corporate software tools every day.

