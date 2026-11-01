# Dataset Integrity & Provenance Audit: Phase 6 Domain Challenge

**Dataset File:** `data/evaluation/phase6_domain_challenge.jsonl`  
**Dataset SHA-256:** `02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7`  
**Audit Date:** November 2026  
**Auditor:** Automated Forensic Auditor  
**Integrity Status:** PASSED (Zero Contamination, Verified Balance)  

---

## 1. Volume & Class Distribution

| Metric | Target Specification | Actual Measured | Verification Status |
| :--- | :---: | :---: | :---: |
| **Total Evaluation Samples** | 40 | 40 | PASS |
| **Sophisticated Phishing** | 20 | 20 | PASS |
| **Difficult Legitimate** | 20 | 20 | PASS |
| **Class Balance Ratio** | 50.0% / 50.0% | 50.0% / 50.0% | PASS |
| **Unique Sample IDs** | 40 | 40 | PASS |

---

## 2. Contamination & Cross-Dataset Overlap Audit

To guarantee that the Phase 6 Domain Challenge provides an unbiased, leak-free evaluation, all 40 candidate records were checked against historical evaluation corpora and the clean production FAISS index.

| Reference Corpus | Candidate Samples | ID Collisions | Exact Text Collisions | Contamination Status |
| :--- | :---: | :---: | :---: | :---: |
| **Phase 5 Regression Suite (160)** | 160 | 0 | 0 | CLEAN (Zero Leakage) |
| **A1 Generalization Benchmark (500)** | 500 | 0 | 0 | CLEAN (Zero Leakage) |
| **Clean FAISS Index Metadata (1,321)** | 1,321 | 0 | 0 | CLEAN (Zero Leakage) |

---

## 3. Challenge Taxonomy & Domain Pretexts

### 3.1 Sophisticated Phishing Samples (20)
- **Executive VDR & Governance Pretexting (4):** `corporate-strategy-vdr.com`, `exec-talent-advisory.com`, `workplace-culture-audit.org`, `corporate-mail-gateway.net`.
- **HR & Benefits Portal Lookalikes (3):** `enterprise-benefits-portal.net`, `adp-payroll-portal.org`, `concur-travel-expense.net`.
- **Enterprise Brand Impersonation (6):** `docusign-envelope-review.com`, `zoom-meeting-secure.com`, `microsoft-account-verify.net`, `okta-verify-gateway.com`, `quickbooks-vendorpay.net`, `salesforce-pipeline-auth.com`.
- **Logistics, Cloud & Legal Service Lookalikes (5):** `federal-court-notices.org`, `corporate-servicedesk-portal.com`, `dhl-express-customs.org`, `cloud-enterprise-billing.net`, `amextravel-corporate.com`.
- **Header & Routing Deception (2):** `enterprise-cloud-consulting.com` (Reply-To mismatch to external inbox), `reputable-partner-consulting.com` (cross-domain link to external auth gateway).

### 3.2 Difficult Legitimate Samples (20)
- **Multi-Tenant Enterprise SaaS Platforms (7):** `docusign.net`, `greenhouse.io`, `zoom.us`, `salesforce.com`, `github.com`, `concursolutions.com`, `slack.com`.
- **Internal Subdomains & Single Sign-On (5):** `learning.internal.enterprise-corp.com`, `concur.internal.enterprise-corp.com`, `enterprise-corp.okta.com`, `enterprise-corp.zendesk.com`, `enterprise-corp.atlassian.net`.
- **Authorized Corporate Vendors & Hyphenated Domains (5):** `service-now.com`, `lw-legalpartners.com`, `gourmet-corporate-catering.com`, `enterprise-investor-relations.com`, `myworkday.com`.
- **Standard Enterprise Notifications (3):** AWS official invoice (`amazon.com`), internal corporate facilities desk (`enterprise-corp.com`), internal quality audit governance notice (`enterprise-corp.com`).

---

## 4. Integrity Verdict

The dataset satisfies all experimental requirements:
- Strictly balanced (20 phish / 20 legit).
- Verified zero contamination with the clean FAISS retrieval index.
- Verified zero contamination with prior evaluation benchmarks.
- Richly represents the exact domain lookalike vectors that modern corporate email defenses encounter.
