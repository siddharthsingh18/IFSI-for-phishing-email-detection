# Phase 8.0 / 8.0.1: Dataset Source Registry & Feasibility Analysis

## 1. Executive Summary

This registry documents external data sources investigated for the Phase 8 large-scale independent evaluation. Following the **Phase 8.0.1 Source Suitability Audit**, candidate corpora are rigorously segregated into:
1. **Track A (Independently Sourced Real Emails)**: Authentic RFC 822 messages with verified provenance and intact transport headers.
2. **Track B (Controlled Challenge Suite)**: Synthetic emails, adapted scenarios, and prompt injection payloads.

> [!WARNING]
> **Strict Phase 8.0 / 8.0.1 Prohibition**: In accordance with protection rules, **no datasets are downloaded, scraped, or ingested during this phase**. This registry serves solely as an architectural feasibility, provenance, and licensing audit.

---

## 2. Investigated Candidate Datasets & Clearance Status

### 2.1 Academic & Open-Source Research Corpora

#### Source 1: Enron Email Corpus (Curated Clean Subset)
- **Publisher / Maintainers**: Federal Energy Regulatory Commission (FERC) / Carnegie Mellon University (Cohen et al.).
- **Official Source**: `https://www.cs.cmu.edu/~enron/`
- **License**: Public Domain (US Federal Government regulatory release, FERC Docket EL02-111).
- **Approximate Size**: ~500,000 corporate emails.
- **Collection Period**: 1999–2002.
- **Format**: Raw RFC 822 text files with complete internal and external corporate headers.
- **Track Mapping**: **Track A (Ordinary Legitimate)** ($N = 1,000$ candidate samples).
- **Authentic Email Check**: **CONFIRMED REAL RFC 822 EMAILS**.
- **Clearance Status**: **APPROVED FOR TRACK A**.

---

#### Source 2: Jose Nazario Phishing Corpus
- **Publisher / Maintainer**: Dr. Jose Nazario (Monkey.org).
- **Official Repository**: `https://monkey.org/~jose/phishing/`
- **License**: Publicly released for computer security research (unrestricted academic use).
- **Approximate Size**: ~4,500 raw mbox phishing emails.
- **Collection Period**: 2005–2019.
- **Format**: Raw RFC 822 / mbox including full message headers and multipart MIME bodies.
- **Track Mapping**: **Track A (Conventional Phishing)** ($N = 1,000$ candidate samples).
- **Authentic Email Check**: **CONFIRMED REAL RFC 822 EMAILS**.
- **Clearance Status**: **APPROVED FOR TRACK A**.

---

#### Source 3: Mendeley Phishing Email Benchmark Dataset
- **Publisher / Authors**: Mendeley Data (Alshehri et al. / Toolan & Carthy, DOI: 10.17632/x27gjprwu9.1).
- **Official Repository**: `https://data.mendeley.com/datasets/x27gjprwu9/1`
- **License**: Creative Commons Attribution 4.0 International (`CC BY 4.0`).
- **Approximate Size**: ~10,000 labeled email records.
- **Format**: Structured CSV containing extracted body text and binary labels. Full RFC 822 transport headers (`Received:`, `Authentication-Results:`) are stripped.
- **Authentic Email Check**: **PARTIAL / TABULAR ONLY (NO RAW HEADERS)**.
- **Clearance Status**: **EXCLUDED FROM TRACK A**. Conditionally approved for Track B body text adaptation only.

---

#### Source 4: SEC EDGAR Corporate Filings
- **Publisher**: U.S. Securities and Exchange Commission (SEC).
- **Official Source**: `https://www.sec.gov/edgar/searchedgar/companysearch`
- **License**: Public Domain (17 U.S.C. § 105).
- **Content Type**: Form 10-K, 10-Q, 8-K regulatory disclosures.
- **Authentic Email Check**: **NON-EMAIL REGULATORY FILINGS (NO EMAIL HEADERS)**.
- **Clearance Status**: **EXCLUDED FROM TRACK A**. Approved as background reference text for Track B corporate notifications.

---

#### Source 5: FBI IC3 (Internet Crime Complaint Center) Case Material
- **Publisher**: Federal Bureau of Investigation (FBI) / IC3.
- **Official Source**: `https://www.ic3.gov/`
- **License**: Public Domain (U.S. Federal Government information).
- **Content Type**: Investigative PSAs, annual reports, and crime narrative summaries.
- **Authentic Email Check**: **NON-EMAIL INVESTIGATIVE REPORTS (NO RAW EMAILS)**.
- **Clearance Status**: **EXCLUDED FROM TRACK A**. Approved as threat scenario blueprints for Track B synthetic BEC attacks.

---

#### Source 6: OWASP Top 10 for LLMs Benchmark Suite
- **Publisher**: OWASP Foundation.
- **Official Source**: `https://owasp.org/www-project-top-10-for-large-language-model-applications/`
- **License**: Creative Commons Attribution-ShareAlike 4.0 (`CC BY-SA 4.0`).
- **Content Type**: Isolated prompt injection test strings (e.g. `Ignore previous instructions`).
- **Authentic Email Check**: **NON-EMAIL ATTACK PAYLOADS**.
- **Clearance Status**: **EXCLUDED FROM TRACK A**. Approved for Track B prompt injection challenge envelopes.

---

### 2.2 Explicitly Prohibited & Inadmissible Sources

| Source Category | Representative Examples | Rationale for Absolute Inadmissibility |
| :--- | :--- | :--- |
| **Leaked / Hacked Inboxes** | DNC email dump, Sony Pictures hack, Hacking Team leak | **Illegal & Unethical**: Sourced from unlawful cyber-espionage and data theft; contains unredacted personal, financial, and confidential data. Violates GDPR Art 5 and IEEE Ethics Code. |
| **Private Personal Inboxes** | Researcher personal mailboxes, employee personal accounts | **Privacy Violation**: Violates GDPR/CCPA; unfeasible to obtain irrevocable third-party consent from all conversation participants. |
| **Undocumented Scraping** | Web scraping from public forums, paste sites (Pastebin) | **Unverifiable Ground Truth**: High risk of synthetic hallucinations, unconfirmed provenance, and poisoned data. |
| **Restricted Academic Corpora** | IWSPA Shared Task (Verma et al.) | **Redistribution Banned**: Requires private institutional DUA forbidding public benchmark artifact redistribution. |

---

## 3. Revised Dual-Track Sourcing Architecture

```
[Target: 3,000 Evaluated Samples]
  │
  ├── TRACK A: INDEPENDENTLY SOURCED REAL EMAILS (N = 2,000)
  │     ├── Enron Email Corpus (Curated Clean Subset): Real Legitimate (N = 1,000)
  │     └── Jose Nazario Phishing Corpus: Real Phishing (N = 1,000)
  │
  └── TRACK B: CONTROLLED ADVERSARIAL CHALLENGE SUITE (N = 1,000)
        ├── Difficult Legitimate SaaS & Secondary Domains (N = 350)
        ├── Sophisticated Phishing BEC & Lookalikes (N = 350)
        └── Prompt Injection Suite (OWASP Payloads) (N = 300)
              ├── Active Malicious Overrides (N = 150)
              └── Quoted Benign Security Excerpts (N = 150)
```
