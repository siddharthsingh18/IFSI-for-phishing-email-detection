# Phase 8.0.1: Source Suitability Audit

## 1. Executive Summary & Purpose

This audit evaluates every candidate data source proposed in Phase 8.0 against strict scientific, legal, and operational standards. Sourcing email data for benchmark evaluation requires unambiguous distinction between:
1. **Actual Email Messages**: Genuine communications possessing authentic RFC 822/MIME envelopes, transport headers (`From:`, `To:`, `Subject:`, `Date:`, `Received:`, `Message-ID:`), and authentic body formatting.
2. **Non-Email Documents & Filings**: Regulatory filings, compliance documents, or financial reports that do not possess email envelopes or transport structures.
3. **Narrative Reports & Advisories**: Investigative bulletins, loss summaries, and case narratives describing cybercrimes without containing raw message transcripts.
4. **Isolated Test Payloads**: Synthetically constructed prompt injection strings or snippets lacking native email context.

> [!CRITICAL]
> **Core Finding**: Only **two** of the seven proposed candidate sources contain actual, verifiable email messages: the **Enron Email Corpus** and the **Jose Nazario Phishing Corpus**.
> - **SEC EDGAR** consists of corporate regulatory filings (Form 10-K, 8-K), not emails.
> - **FBI IC3** consists of investigative crime reports and advisories, not emails.
> - **OWASP Top 10 for LLMs** consists of vulnerability guidance and isolated prompt payloads, not emails.
> - **Mendeley Phishing Dataset** contains tabular text with pre-extracted bodies, but lacks raw RFC 822 transport headers.
>
> Claiming that SEC EDGAR or FBI IC3 represent "independently sourced real-world emails" is scientifically indefensible. This audit corrects these provenance errors.

---

## 2. Individual Source Audit (10-Point Verification Matrix)

Each source is audited against 10 mandatory criteria:
1. **Official Publisher**
2. **Official Repository / URL**
3. **Exact License / Terms of Use**
4. **Research Use Permitted?**
5. **Raw Data Stored Locally?**
6. **Redistribution Permitted?**
7. **Complete Emails vs Documents / Payloads**
8. **Header / Transport Metadata Availability**
9. **Nature of Data (Real, Anonymized, Adapted, Synthetic)**
10. **Defensibility of Proposed Category Assignment**

---

### Source 1: Enron Email Corpus
- **1. Publisher**: Federal Energy Regulatory Commission (FERC) / Organized by Carnegie Mellon University (Prof. William W. Cohen) / MIT.
- **2. Official Repository**: `https://www.cs.cmu.edu/~enron/`
- **3. License / Terms**: Public domain administrative regulatory disclosure (FERC Docket No. EL02-111). Prepared for academic research.
- **4. Research Use Permitted**: **YES**. Standard foundational research corpus in NLP and information retrieval.
- **5. Local Storage Permitted**: **YES**. Downloadable tarball archives intended for local computational research.
- **6. Redistribution Permitted**: **YES** (with ethical redaction of personal phone numbers, home addresses, and financial account numbers).
- **7. Content Type**: **COMPLETE RFC 822 EMAIL MESSAGES**. Contains raw MIME files with full header envelopes.
- **8. Headers / Metadata Available**: `From:`, `To:`, `Cc:`, `Bcc:`, `Subject:`, `Date:`, `Message-ID:`, `X-From:`, `X-To:`, and complete body text. Authentic transport timestamps.
- **9. Data Nature**: **Real historical corporate emails** (1999–2002).
- **10. Category Defensibility**: **DEFENSIBLE FOR TRACK A (ORDINARY LEGITIMATE)**. Authentic internal and external corporate dialogue.
  - *Limitation*: Era constraint (1999–2002). Lacks modern multi-tenant cloud authentication (Okta, Workday, Duo, Slack) and modern DKIM/SPF headers.

---

### Source 2: SEC EDGAR Corporate Filings
- **1. Publisher**: U.S. Securities and Exchange Commission (SEC).
- **2. Official Repository**: `https://www.sec.gov/edgar/searchedgar/companysearch` and EDGAR dissemination APIs.
- **3. License / Terms**: U.S. Government Work (17 U.S.C. § 105; public domain). Automated access subject to Fair Access policy ($\le 10$ req/sec, declared User-Agent).
- **4. Research Use Permitted**: **YES**. Unrestricted public access for analysis and research.
- **5. Local Storage Permitted**: **YES**.
- **6. Redistribution Permitted**: **YES**.
- **7. Content Type**: **NON-EMAIL REGULATORY FILINGS**. Contains Form 10-K, 10-Q, 8-K, proxy statements, and SEC correspondence. **Contains zero RFC 822 email messages.**
- **8. Headers / Metadata Available**: **NONE**. No email sender, no email recipient, no email subject headers, no email transport routes.
- **9. Data Nature**: Real corporate regulatory disclosures, but **completely non-email in structure and medium**.
- **10. Category Defensibility**: **INDEFENSIBLE FOR TRACK A (REAL EMAILS)**.
  - *Correction*: SEC filings cannot be counted as "legitimate emails". They may only serve as background source text for **Track B (Adapted Challenge)** corporate notifications. Excluded from Track A.

---

### Source 3: Jose Nazario Phishing Corpus
- **1. Publisher**: Dr. Jose Nazario (Monkey.org).
- **2. Official Repository**: `https://monkey.org/~jose/phishing/` (historical mbox archives).
- **3. License / Terms**: Publicly released for computer security and anti-phishing defense research.
- **4. Research Use Permitted**: **YES**. Classical baseline in academic spam and phishing literature.
- **5. Local Storage Permitted**: **YES**. Distributed as raw mbox files.
- **6. Redistribution Permitted**: **YES** (with academic attribution).
- **7. Content Type**: **COMPLETE RFC 822 EMAIL MESSAGES**. Contains raw mbox streams with complete headers, MIME boundaries, and message bodies.
- **8. Headers / Metadata Available**: `From:`, `To:`, `Subject:`, `Date:`, `Received:`, `Return-Path:`, `Message-ID:`, destination hyperlinks.
- **9. Data Nature**: **Real historical phishing emails** (collected 2005–2019, heavily centered on 2005–2007).
- **10. Category Defensibility**: **DEFENSIBLE FOR TRACK A (CONVENTIONAL PHISHING)**. Authentic mass-market credential theft and banking lures.
  - *Limitation*: Destination URLs and domains are predominantly dead; modern lookalike domain techniques and zero-link BEC are absent.

---

### Source 4: Mendeley Phishing Email Benchmark Dataset
- **1. Publisher**: Mendeley Data (Toolan & Carthy / Alshehri et al., DOI: `10.17632/x27gjprwu9.1`).
- **2. Official Repository**: `https://data.mendeley.com/datasets/x27gjprwu9/1`
- **3. License / Terms**: Creative Commons Attribution 4.0 International (`CC BY 4.0`).
- **4. Research Use Permitted**: **YES**. Permissive research and commercial evaluation permitted.
- **5. Local Storage Permitted**: **YES**.
- **6. Redistribution Permitted**: **YES** (with attribution).
- **7. Content Type**: **TABULAR DATASET (NOT RAW RFC 822 EMAILS)**. Structured CSV file containing pre-parsed text fields (`Email Text`, `Email Type`). Transport headers and raw MIME structures have been stripped.
- **8. Headers / Metadata Available**: **PARTIAL / ABSENT**. Subject and sender strings are occasionally present in text, but transport `Received:`, `Return-Path:`, and cryptographic authentication headers are completely absent.
- **9. Data Nature**: Pre-processed tabular text extracted from older mixed archives (Nazario, SpamAssassin, Enron).
- **10. Category Defensibility**: **INDEFENSIBLE FOR TRACK A AS RAW EMAILS**. Domain Analyzer V3 requires verifiable sender and envelope headers. Imputing synthetic headers into CSV text transforms it into adapted challenge data.
  - *Correction*: Excluded from Track A. Approved conditionally for **Track B (Adapted Text)** only if header synthesis is explicitly documented.

---

### Source 5: FBI IC3 (Internet Crime Complaint Center) Case Material
- **1. Publisher**: Federal Bureau of Investigation (FBI) / Internet Crime Complaint Center (IC3).
- **2. Official Repository**: `https://www.ic3.gov/` and `https://www.ic3.gov/Media/PDF/AnnualReport/` (Public Service Announcements).
- **3. License / Terms**: U.S. Federal Government public information releases (public domain).
- **4. Research Use Permitted**: **YES**.
- **5. Local Storage Permitted**: **YES**.
- **6. Redistribution Permitted**: **YES**.
- **7. Content Type**: **NARRATIVE INVESTIGATIVE REPORTS & ADVISORIES**. The FBI publishes loss statistics, victim narratives, and scenario descriptions. **The FBI does NOT publish raw email messages or downloadable email corpora.**
- **8. Headers / Metadata Available**: **NONE**. No raw sender addresses, no RFC 822 envelopes, no authentic headers, no raw payloads.
- **9. Data Nature**: Investigative summaries and loss reports; **completely non-email in form**.
- **10. Category Defensibility**: **INDEFENSIBLE FOR TRACK A (REAL EMAILS)**.
  - *Correction*: Claiming FBI IC3 provides "450 real sophisticated phishing emails" is an outright falsehood. IC3 reports may only provide narrative blueprints for **Track B (Controlled Synthetic BEC Challenge)**. Excluded from Track A.

---

### Source 6: OWASP Top 10 for LLMs Benchmark Suite
- **1. Publisher**: OWASP Foundation (Open Worldwide Application Security Project).
- **2. Official Repository**: `https://owasp.org/www-project-top-10-for-large-language-model-applications/` / GitHub.
- **3. License / Terms**: Creative Commons Attribution-ShareAlike 4.0 (`CC BY-SA 4.0`).
- **4. Research Use Permitted**: **YES**.
- **5. Local Storage Permitted**: **YES**.
- **6. Redistribution Permitted**: **YES** (with ShareAlike attribution).
- **7. Content Type**: **ISOLATED PROMPT INJECTION PAYLOAD STRINGS**. Guidance documents and isolated test prompts (e.g., `Ignore previous instructions and do X`). **Contains zero email messages.**
- **8. Headers / Metadata Available**: **NONE**. No sender, recipient, subject, or email transport envelope.
- **9. Data Nature**: Isolated adversarial test vectors; non-email text strings.
- **10. Category Defensibility**: **INDEFENSIBLE FOR TRACK A (REAL EMAILS)**.
  - *Correction*: Strictly assigned to **Track B (Controlled Challenge Suite)**, where payloads are embedded into synthetic email envelopes to probe Stage 1.5 sanitizer behavior.

---

### Source 7: Red-Team & IFSI Injection Scenarios
- **1. Publisher**: IFSI Research Team / Internal Defensive Engineering.
- **2. Official Repository**: Internal project repository (`D:\Project\IFSI-for-phishing-email-detection\data\evaluation\`).
- **3. License / Terms**: Proprietary project research artifacts.
- **4. Research Use Permitted**: **YES**.
- **5. Local Storage Permitted**: **YES**.
- **6. Redistribution Permitted**: Project-restricted.
- **7. Content Type**: **SYNTHETIC / ADAPTED EMAIL ENVELOPES**. Handcrafted messages simulating sophisticated BEC, lookalike domains, and CJK injection attacks.
- **8. Headers / Metadata Available**: Synthetically populated RFC 822 headers.
- **9. Data Nature**: **Synthetic / adapted test vectors**.
- **10. Category Defensibility**: **INDEFENSIBLE FOR TRACK A (REAL EMAILS)**.
  - *Correction*: Belongs strictly to **Track B (Controlled Challenge Suite)**.

---

## 3. Summary Classification Table

| Source | Content Type | Headers Present? | Actual Emails? | Track A (Real Emails) | Track B (Challenge Suite) | Action / Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Enron Email Corpus** | RFC 822 Email Files | YES | **YES** | **APPROVED** | N/A | Approved for Track A (Ordinary Legitimate) |
| **Jose Nazario Corpus** | RFC 822 mbox Streams | YES | **YES** | **APPROVED** | N/A | Approved for Track A (Conventional Phishing) |
| **SEC EDGAR Filings** | Regulatory SEC Filings | NO | **NO** | **EXCLUDED** | **APPROVED (Text)** | Excluded from Track A; blueprint text for Track B |
| **Mendeley Dataset** | Structured CSV Text | NO | **PARTIAL** | **EXCLUDED** | **CONDITIONAL** | Excluded from Track A (stripped transport headers) |
| **FBI IC3 Reports** | Investigative Bulletins | NO | **NO** | **EXCLUDED** | **APPROVED (Blueprints)**| Excluded from Track A; scenario designs for Track B |
| **OWASP LLM Top 10** | Prompt Injection Strings | NO | **NO** | **EXCLUDED** | **APPROVED (Payloads)** | Excluded from Track A; payload library for Track B |
| **IFSI Red-Team** | Synthetic Envelopes | YES (Synthetic)| **NO (Synthetic)**| **EXCLUDED** | **APPROVED (Synthetic)**| Excluded from Track A; challenge suite for Track B |

---

## 4. Conclusion & Remediation Directives

1. **Exclusion from Track A**: SEC EDGAR, Mendeley CSV, FBI IC3, and OWASP LLM are **formally excluded** from Track A independent real-world email evaluation.
2. **Two-Track Architecture**: Evaluation must be divided into **Track A (Independently Sourced Real Emails)** and **Track B (Controlled Challenge Corpus)**.
3. **No Cross-Contamination of Results**: Track A metrics and Track B metrics must be reported separately. It is strictly forbidden to blend Track B synthetic results with Track A real emails to claim "real-world generalization."
