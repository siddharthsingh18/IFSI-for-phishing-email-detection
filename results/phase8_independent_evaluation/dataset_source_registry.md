# Phase 8.0: Dataset Source Registry & Feasibility Analysis

## 1. Executive Summary

This registry documents potential external email corpora investigated for Phase 8 large-scale independent evaluation. Sourcing 3,000 independent emails requires a multi-source compilation strategy balancing:
1. **Provenance Authenticity**: Real-world communication patterns and authentic header structures.
2. **Modern Attack Relevance**: Sophisticated BEC, SaaS credential theft, and adversarial prompt injections.
3. **Legal & Ethical Feasibility**: Permissive research licensing, privacy protection, and zero reliance on stolen or leaked personal mailboxes.

> [!WARNING]
> **Strict Phase 8.0 Prohibition**: In accordance with Phase 8.0 protection rules, **no datasets are downloaded, scraped, or ingested during this phase**. This registry serves solely as an architectural feasibility and licensing audit.

---

## 2. Investigated Candidate Datasets

### 2.1 Academic & Open-Source Research Corpora

#### Source 1: Nazario Phishing Corpus
- **Publisher / Maintainer**: Dr. Jose Nazario (Monkey.org).
- **Official Repository**: `https://monkey.org/~jose/phishing/`
- **License**: Publicly released for computer security research (unrestricted academic use).
- **Approximate Size**: ~4,500 raw mbox phishing emails.
- **Collection Period**: 2005–2019.
- **Format**: Raw RFC822 / mbox including full message headers and multipart MIME bodies.
- **Target Category Mapping**: **Conventional Phishing** ($N \approx 400$ candidate samples).
- **Known Biases & Limitations**: Historical phishing templates; modern lookalike domain attacks and zero-link BEC are underrepresented; destination URLs are primarily dormant.
- **Feasibility Assessment**: **FEASIBLE**. Permissive academic security research license; provides raw headers suitable for domain extraction.

---

#### Source 2: IWSPA Anti-Phishing Shared Task Corpora
- **Publisher**: ACM / IEEE International Workshop on Security and Privacy Analytics (Verma et al., University of Houston).
- **Official Source**: `https://www2.cs.uh.edu/~rmverma/` / IEEE IWSPA Archive.
- **License**: Academic Research Use Only (Agreement required).
- **Approximate Size**: ~9,000 emails (split between ham and phishing).
- **Collection Period**: 2018–2020.
- **Format**: Text files with sanitized headers and body text.
- **Target Category Mapping**: **Ordinary Legitimate** ($N \approx 500$) and **Conventional Phishing** ($N \approx 350$).
- **Known Biases & Limitations**: Partial header redaction; some synthetic anonymization alters domain consistency.
- **Feasibility Assessment**: **FEASIBLE (WITH PERMISSION)**. Requires formal academic registration and approval prior to ingestion.

---

#### Source 3: Mendeley Phishing Email Benchmark Dataset
- **Publisher / Authors**: Mendeley Data (Alshehri et al. / Toolan & Carthy).
- **Official Repository**: `https://data.mendeley.com/datasets/x27gjprwu9/1` (DOI: 10.17632/x27gjprwu9.1).
- **License**: Creative Commons Attribution 4.0 International (`CC BY 4.0`).
- **Approximate Size**: ~10,000 labeled email records.
- **Collection Period**: 2017–2022.
- **Format**: Structured CSV/JSON containing extracted subject, sender, body text, and binary phishing labels.
- **Target Category Mapping**: **Ordinary Legitimate** ($N \approx 400$) and **Conventional Phishing** ($N \approx 300$).
- **Known Biases & Limitations**: Pre-parsed tabular format; full RFC822 transport headers (e.g. Received, Authentication-Results) are stripped.
- **Feasibility Assessment**: **FEASIBLE**. Highly permissive CC BY 4.0 license; excellent for body text validation.

---

#### Source 4: Enron Email Corpus (Modern Curated Clean Subset)
- **Publisher / Maintainers**: Federal Energy Regulatory Commission (FERC) / Carnegie Mellon University (Cohen et al.).
- **Official Source**: `https://www.cs.cmu.edu/~enron/`
- **License**: Public Domain (US Federal Government regulatory release).
- **Approximate Size**: ~500,000 corporate emails.
- **Collection Period**: 1999–2002.
- **Format**: Raw RFC822 text files with complete internal and external corporate headers.
- **Target Category Mapping**: **Ordinary Legitimate** ($N \approx 500$ corporate communication samples).
- **Known Biases & Limitations**: Era limitation: lacks modern enterprise cloud references (Slack, Workday, Okta, Microsoft 365, Concur); contains high volume of casual informal internal notes.
- **Feasibility Assessment**: **FEASIBLE FOR BASELINE HAM**. Completely public domain; zero privacy violation; must be filtered for realistic enterprise communications.

---

### 2.2 Modern Adversarial & Specialized Sources

#### Source 5: OWASP LLM Prompt Injection Benchmark Suite
- **Publisher**: OWASP Foundation (Top 10 for LLM Applications Project).
- **Official Source**: `https://owasp.org/www-project-top-10-for-large-language-model-applications/`
- **License**: Creative Commons Attribution-ShareAlike 4.0 (`CC BY-SA 4.0`).
- **Approximate Size**: ~1,200 adversarial test cases.
- **Collection Period**: 2023–2026.
- **Format**: JSON structured prompt injection strings categorized by attack archetype.
- **Target Category Mapping**: **Prompt Injection** ($N = 150$ active malicious instructions; $N = 150$ quoted benign discussions).
- **Known Biases & Limitations**: Payloads are presented as isolated test prompts; must be realistically adapted into email envelopes.
- **Feasibility Assessment**: **FEASIBLE**. Standard authoritative benchmark for LLM injection security.

---

#### Source 6: SEC EDGAR & Regulatory Public Filings
- **Publisher**: U.S. Securities and Exchange Commission (SEC).
- **Official Source**: `https://www.sec.gov/edgar/searchedgar/companysearch`
- **License**: Public Domain.
- **Approximate Size**: Tens of thousands of public correspondence, legal notices, and compliance disclosures.
- **Collection Period**: 2020–2026.
- **Format**: Public corporate disclosures, compliance letters, executive correspondence.
- **Target Category Mapping**: Source templates for **Difficult Legitimate** ($N \approx 300$) and **Sophisticated Phishing BEC** ($N \approx 250$).
- **Feasibility Assessment**: **FEASIBLE**. Completely public and legally unencumbered; provides authentic, high-formality executive syntax.

---

## 3. Explicitly Prohibited & Inadmissible Sources

To protect legal, ethical, and research integrity, the following categories of data are **strictly prohibited from consideration**:

| Source Category | Representative Examples | Rationale for Absolute Inadmissibility |
| :--- | :--- | :--- |
| **Leaked / Hacked Inboxes** | DNC email dump, Sony Pictures hack, Hacking Team leak | **Illegal & Unethical**: Sourced from unlawful cyber-espionage and data theft; contains unredacted personal, financial, and confidential data. |
| **Private Personal Inboxes** | Researcher personal mailboxes, employee personal accounts | **Privacy Violation**: Violates GDPR/CCPA; unfeasible to obtain irrevocable third-party consent from all conversation participants. |
| **Undocumented Scraping** | Web scraping from public forums, paste sites (Pastebin) | **Unverifiable Ground Truth**: High risk of synthetic hallucinations, unconfirmed provenance, and poisoned data. |

---

## 4. Multi-Source Compilation Plan

To assemble the target **3,000-sample corpus**, the following multi-source sourcing plan is established:

```
[Target: 3,000 Samples]
  ├── Ordinary Legitimate (N=900)
  │     ├── Enron Curated Clean Subset (N=500)
  │     └── Mendeley / IWSPA Benign Corporate (N=400)
  ├── Difficult Legitimate (N=600)
  │     ├── Public Corporate Regulatory / SEC Notices (N=300)
  │     └── Audited Enterprise SaaS Notifications (N=300)
  ├── Conventional Phishing (N=750)
  │     ├── Nazario Phishing Corpus (N=400)
  │     └── Mendeley / IWSPA Phishing (N=350)
  ├── Sophisticated Phishing (N=450)
  │     ├── Curated BEC / Payment Redirection Corpora (N=250)
  │     └── Fresh Adversarial Lookalike / SaaS Harvesters (N=200)
  └── Adversarial Prompt Injection (N=300)
        ├── OWASP LLM Active Injections (N=150)
        └── Quoted Benign Security Bulletins (N=150)
```

