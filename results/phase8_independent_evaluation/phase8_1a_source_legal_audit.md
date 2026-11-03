# Phase 8.1A: Source Legal, Provenance & Reuse Governance Audit (Enron & Jose Nazario)

## 1. Executive Summary & Governance Scope

This audit evaluates the legal provenance, copyright posture, reuse authorization, header fidelity, and privacy risk of the two external email corpora proposed for Phase 8 Track A:
1. **Enron Email Corpus** (`https://www.cs.cmu.edu/~enron/`)
2. **Jose Nazario Phishing Corpus** (`https://monkey.org/~jose/phishing/`)

> [!IMPORTANT]
> **Strict Phase 8.1A Non-Acquisition Compliance**:
> No datasets, archives, or upstream files were downloaded, scraped, ingested, or transformed during this audit. Conclusions combine publicly documented provenance facts with read-only forensic inspection of existing repository manifests ([`data/manifests/enron.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/enron.json), [`data/manifests/nazario.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/nazario.json), [`data/metadata/source_manifest.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/source_manifest.json), [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md)) and existing local artifacts ([`data/processed/enron_ingested/enron_clean_500.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/processed/enron_ingested/enron_clean_500.jsonl)).

### Summary Legal Verdict

| Dimension | Enron Email Corpus (`cs.cmu.edu/~enron/`) | Jose Nazario Phishing Corpus (`monkey.org/~jose/phishing/`) |
| :--- | :--- | :--- |
| **Public Availability** | **YES** (Unauthenticated HTTP archive download) | **YES** (Unauthenticated HTTP `.mbox` directory) |
| **Public-Record Status** | **YES** (FERC administrative docket disclosure) | **NO** (Privately curated security researcher honeypot/archive) |
| **Underlying Copyright Status** | **PRIVATE COPYRIGHTS RETAINED** (Authored by Enron Corp employees & external third parties; **NOT** U.S. Gov work under `17 U.S.C. § 105`) | **THIRD-PARTY COPYRIGHTS UNCLEARED** (Compilation curated by J. Nazario; underlying message text & spoofed brand HTML/logos belong to third parties) |
| **Explicit Reuse License** | **NONE** (No SPDX, Creative Commons, or statutory license on CMU page; provided "as-is" for research) | **UNVERIFIED IN PHASE 8.1A** (`LICENSE.txt` [18 KB] exists upstream at `monkey.org/~jose/phishing/LICENSE.txt` but was not downloaded per Phase 8.1A rules; secondary mirrors cite `CC BY 4.0`, while local `data/manifests/nazario.json` states `"Source terms; verify"`) |
| **Local Research Evaluation (No Redistribution)** | **CONDITIONALLY PERMISSIBLE UNDER FAIR USE (`17 U.S.C. § 107`)**, subject to institutional/researcher governance sign-off, strict PII/folder exclusions, and git-ignored local-only storage | **UNRESOLVED PENDING `LICENSE.txt` & `README.txt` INSPECTION**, and conditional on local-only non-redistribution per [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md) |
| **Public Redistribution of Raw or Sanitized Messages** | **NOT PERMITTED / UNCLEARED** (`redistribution_allowed: false` in `data/manifests/enron.json`) | **NOT PERMITTED / UNCLEARED** (`redistribution_allowed: false` in `data/manifests/nazario.json`) |
| **Overall Legal Clearance Status** | **UNRESOLVED (Requires Fair-Use Non-Redistribution Sign-Off)** | **UNRESOLVED (Requires Direct `LICENSE.txt` Verification)** |

> [!WARNING]
> **Formal Correction to Phase 8.0 / 8.0.1 Documents**:
> Earlier Phase 8 planning drafts loosely described Enron as *"Public Domain (FERC)"* with *"Permitted Public Redistribution: YES"* and Nazario as *"Open Academic Security Research License — Redistribution: YES"*. Those characterizations conflated public availability with copyright licensing and contradicted this repository's own [`data/manifests/enron.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/enron.json), [`data/manifests/nazario.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/nazario.json), and [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md). This document supersedes those claims.

---

## 2. Source 1 Audit: Enron Email Corpus

- **Official Source URL**: `https://www.cs.cmu.edu/~enron/`
- **Pinned Archive Referenced in Local Metadata**: `https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz` (SHA-256 `b3da1b3fe0369ec3140bb4fbce94702c33b7da810ec15d718b3fadf5cd748ca7` recorded in [`data/metadata/source_manifest.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/source_manifest.json)).

### 2.1 Original Publisher & Collection History
1. **Originating Mailboxes (1999–2002)**: Internal and external correspondence from approximately 150 senior managers, traders, and executives of Enron Corporation and its subsidiaries (e.g., Enron Transportation Services / Northern Natural Gas).
2. **FERC Regulatory Seizure & Public Posting (2002–2003)**: During its formal investigation into Western U.S. energy market manipulation following Enron's December 2001 bankruptcy (FERC Docket Nos. `PA02-2-000` / `EL02-111`), the **Federal Energy Regulatory Commission (FERC)** subpoenaed Enron's Microsoft Exchange / Lotus Notes email stores and placed over 600,000 messages online in May 2002 to enable public inspection of the investigative record. Following privacy objections and court/agency review, FERC removed sensitive personal/SSN-bearing records and reissued a reduced corpus.
3. **MIT Acquisition & DARPA CALO Cleaning (2003–2004)**: Prof. Leslie Pack Kaelbling (MIT) purchased/obtained a copy of the FERC dataset. Researchers under the **DARPA CALO Project** (*A Cognitive Assistant that Learns and Organizes*), led by SRI International (Melinda Gervasio), fixed file-integrity corruption, stripped binary attachments, and structured the maildir hierarchy (`~517,401` messages across `150` user folders).
4. **CMU Research Hosting (2004–2015)**: **Prof. William W. Cohen** at Carnegie Mellon University (`https://www.cs.cmu.edu/~enron/`) hosted the cleaned CALO dataset for scientific research, periodically issuing updated tarballs (culminating in the May 7, 2015 release `enron_mail_20150507.tar.gz`) after deleting specific messages upon takedown/privacy requests from affected former employees.

### 2.2 Explicit Four-Way Legal Distinction
A rigorous governance audit must separate four distinct legal concepts that are frequently conflated in machine learning literature:

1. **Public Availability**:
   - `enron_mail_20150507.tar.gz` is openly accessible via standard HTTP from CMU without clickwrap agreements, credentials, or paywalls.
   - *Governance implication*: Technical accessibility does **not** grant intellectual property rights or waive privacy obligations.
2. **Public-Record Status**:
   - The corpus became accessible because FERC entered seized corporate records into a public federal regulatory docket under its statutory investigative authority.
   - *Governance implication*: Public-record disclosure establishes *lawful initial public access* (distinguishing Enron fundamentally from criminally hacked/stolen dumps like Sony Pictures or DNC leaks), **but** regulatory docket placement does not transfer private copyrights to the public.
3. **Copyright Status**:
   - Under `17 U.S.C. § 105`, statutory public-domain status in the United States applies solely to *"any work of the United States Government"*—defined in `17 U.S.C. § 101` as a work prepared by an officer or employee of the U.S. Government as part of that person's official duties.
   - Enron emails were authored by **private corporate employees of Enron Corp** and **unaffiliated external third parties** (customers, utilities, law firms, vendors, family members). Submitting or subpoenaing private writings into a federal regulatory proceeding does **not** convert them into U.S. Government works or extinguish underlying literary copyright (`17 U.S.C. § 102`).
   - Forensic verification on [`enron_clean_500.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/processed/enron_ingested/enron_clean_500.jsonl) confirms that `7/500` locally stored Enron records even retain explicit proprietary footers: *"This e-mail is the property of Enron Corp. and/or its relevant affiliate and may contain confidential and privileged material..."*
4. **Actual Reuse License**:
   - **No explicit reuse license exists.** Neither FERC, SRI/CALO, nor Prof. William W. Cohen's CMU landing page (`https://www.cs.cmu.edu/~enron/`) grants an SPDX license (such as CC0, CC BY, MIT, or Apache-2.0)—understandably, because neither FERC nor CMU owned the underlying copyrights of Enron Corp or external senders.
   - Consistent with this fact, [`data/manifests/enron.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/enron.json) in this repository explicitly records:
     ```json
     {
       "license": "Original corpus terms; verify",
       "redistribution_allowed": false
     }
     ```

### 2.3 Permissions & Restrictions by Lifecycle Action
- **Local Storage & Computational Processing**: Relies on **non-commercial research fair use (`17 U.S.C. § 107`)**, not an explicit license. Transformative statistical evaluation of classifier accuracy/FPR causes zero market harm to twenty-five-year-old operational memos and aligns with two decades of academic NLP practice, *provided* copies remain strictly local and access-controlled.
- **Derived Records (Sanitized JSONL / Per-Sample Model Traces)**: Derived JSONL records that retain full or lightly redacted email bodies, as well as LLM Stage 1/Stage 2 raw traces quoting email text, remain derivative copies of unlicensed text. Under [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md), they must remain git-ignored and local-only.
- **Publication of Aggregate Metrics & Provenance Manifests**: Publishing aggregate evaluation statistics (accuracy, recall, FPR, Wilson CIs, latency), deterministic selection scripts, SHA-256 digests, and archive member identifiers (`maildir/<custodian>/<folder>/<msg>`) conveys non-copyrightable facts and ideas and is permissible.
- **Redistribution of Raw or Sanitized Messages**: **Prohibited (`redistribution_allowed: false`).** Neither raw archives nor evaluation `.jsonl` files containing Enron email bodies may be committed to a public repository or redistributed as a downloadable dataset.

### 2.4 Availability & Integrity of Original RFC 822 Headers
- **Available Headers in Raw CMU Tarball**: Each file in `maildir/<user>/<folder>/` contains reconstructed RFC 822 headers: `Message-ID:`, `Date:`, `From:`, `To:`, `Cc:`, `Bcc:`, `Subject:`, `Mime-Version:`, `Content-Type:`, `Content-Transfer-Encoding:`, and CALO/PST metadata headers (`X-From:`, `X-To:`, `X-cc:`, `X-bcc:`, `X-Folder:`, `X-Origin:`, `X-FileName:`).
- **Critical Header Integrity Deficits**:
  1. **No Authentic SMTP Transport Headers**: Because FERC/CALO exported messages from internal Exchange/Lotus Notes mail stores rather than gateway SMTP wire captures, **authentic `Received:` hop chains, `Return-Path:`, `Received-SPF:`, `DKIM-Signature:`, and `Authentication-Results:` headers are absent**.
  2. **Stripped Binary Attachments**: CALO removed attachments, leaving inline placeholders (e.g., `<<winteropsAGENDA.DOC>>`, `<Embedded Picture (Metafile)>`).
  3. **Prior Local Ingestion Lossiness**: In [`tools/data/ingest_enron_corpus.py`](file:///d:/Project/IFSI-for-phishing-email-detection/tools/data/ingest_enron_corpus.py) (lines 153–176), IFSI previously discarded `Date:`, `To:`, `Cc:`, `Message-ID:`, and `X-*` headers, synthesizing `"Subject: ...\nFrom: ...\n\n<body>"`. Any future pilot must preserve the intact raw header block without fabricating missing SMTP headers.

### 2.5 Empirical PII & Sensitive Information Risks
Read-only audit of the 500 already-ingested Enron records in [`data/processed/enron_ingested/enron_clean_500.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/processed/enron_ingested/enron_clean_500.jsonl) (which had only SSN and 16-digit payment-card regexes applied) demonstrates substantial residual privacy exposure:
- **Unredacted Telephone & Fax Numbers**: **`118 / 500` (`23.6%`)** contain live-formatted U.S. direct dial or fax numbers in message bodies.
- **External Third-Party Email Addresses**: **`61 / 500` (`12.2%`)** embed non-Enron personal or client email addresses inside bodies/quoted chains (e.g., `@oneok.com`, `@dom.com`, `@semcoenergy.com`, `@jhenergy.com`), plus `29 / 500` external envelope senders (`@pge.com`, `@socalgas.com`, etc.) who never worked at Enron.
- **Embedded Multi-Party Quoted Threads**: **`189 / 500` (`37.8%`)** contain `-----Original Message-----` or `-----Original Appointment-----` blocks exposing secondary correspondents and internal deliberations.
- **Sensitive HR & Personal Folders**: Record #1 (`maildir/blair-l/personnel___promotions/1.`) contains an internal HR table naming nine real employees alongside their mid-year promotion verdicts (`Yes/No`). Other folders in `blair-l` include `vacations_2001` (`9` messages) and `itinerary_off_duty` (`15` messages).
- **Affected-Employee Redaction Norm**: CMU explicitly notes that messages were deleted over time in response to privacy requests from affected individuals; redistributing extracted copies undermines upstream takedown compliance.

### 2.6 Feasibility of Non-Redistributed Research Evaluation
Enron **can** be evaluated locally without redistributing raw messages by following the repository's existing [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md) model:
- Keep `data/raw/`, `data/processed/`, per-sample evaluation `.jsonl` inputs, and raw model response logs strictly git-ignored on local storage.
- Publish only deterministic extraction code, pinned upstream archive SHA-256 (`b3da1b3fe0369ec3140bb4fbce94702c33b7da810ec15d718b3fadf5cd748ca7`), selected `maildir/...` path manifests, per-record SHA-256 hashes, exclusion counts, and aggregate benchmark metrics.

---

## 3. Source 2 Audit: Jose Nazario Phishing Corpus

- **Official Source URL**: `https://monkey.org/~jose/phishing/`
- **Pinned Archive Referenced in Local Metadata**: `https://monkey.org/~jose/phishing/phishing3.mbox` (SHA-256 `b29336d2e31c2dff19639415e98ed2aced5b4d63675ea5e29bea1a7d4e452841` recorded in [`data/manifests/nazario.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/nazario.json) and [`data/metadata/source_manifest.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/source_manifest.json)).

### 3.1 Original Publisher & Collection History
1. **Curator & Publisher**: **Dr. Jose Nazario**, security researcher (`monkey.org`).
2. **Collection History (~2004/2005–Present)**: Aggregated real-world phishing lures received in personal/honeypot mailboxes and contributed samples, published sequentially as Berkeley `.mbox` files (`phishing0.mbox` through `phishing3.mbox` covering roughly 2005–2007, followed by annual `.mbox` archives such as `phishing-2015` through `phishing-2025`).

### 3.2 Exact License, Terms of Use & Evidentiary Boundaries
1. **Upstream License Files Exist, But Are Unverified in Phase 8.1A**:
   - Public directory indexing of `https://monkey.org/~jose/phishing/` shows two documentation files alongside the `.mbox` archives:
     - `https://monkey.org/~jose/phishing/README.txt` (~961 bytes)
     - `https://monkey.org/~jose/phishing/LICENSE.txt` (~18 KB)
   - Because Phase 8.1A strictly forbids downloading upstream files, the exact verbatim text of `LICENSE.txt` and `README.txt` has **not** been fetched or cryptographically hashed in this workspace.
   - While third-party academic mirrors (e.g., HuggingFace/GitHub derivatives) cite `CC BY 4.0`, third-party metadata is **not** primary legal evidence. Moreover, an 18 KB `LICENSE.txt` could correspond to either `CC BY 4.0` legalcode (~18.6 KB) or `GNU GPL v2` (~18.0 KB) or custom terms—each carrying materially different obligations.
   - Crucially, this repository's own [`data/manifests/nazario.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/nazario.json) and [`data/metadata/source_manifest.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/source_manifest.json) explicitly record:
     ```json
     {
       "license": "Source terms; verify",
       "redistribution_allowed": false
     }
     ```
2. **Distinction Between Academic Release, Compilation License, and Underlying Message Rights**:
   - An informal academic research release is **not** an explicit license.
   - Even if `LICENSE.txt` grants an explicit open license over Dr. Nazario's *compilation* (`17 U.S.C. § 103`, covering selection and arrangement of the `.mbox` files), Dr. Nazario does **not** own copyright in:
     1. Original text composed by third-party senders, or
     2. Misappropriated HTML templates, CSS, graphics, and registered trademarks copied verbatim by attackers from impersonated institutions (e.g., PayPal, eBay, Wells Fargo, Microsoft, DHL).
   - Furthermore, `.mbox` headers contain recipient/forwarding addresses (such as `jose@monkey.org` or third-party victim headers) requiring privacy review.

### 3.3 Permissions & Restrictions by Lifecycle Action
- **Local Storage & Research Processing**: Conditional on first inspecting and recording the exact SHA-256 and verbatim terms of `https://monkey.org/~jose/phishing/README.txt` and `LICENSE.txt`. Anti-phishing evaluation on locally stored `.mbox` files aligns with the stated purpose of the repository and fair use (`17 U.S.C. § 107`).
- **Sanitized Examples & Derived Evaluation Records**: Must remain **local-only and git-ignored** (`redistribution_allowed: false` in `data/manifests/nazario.json` and [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md)). Neither raw `.mbox` files nor derived `.jsonl` email bodies may be publicly redistributed without both (a) verifying `LICENSE.txt` share-alike/attribution conditions and (b) clearing third-party content/privacy constraints.
- **Publication of Aggregate Results & Hash Manifests**: Permitted once upstream attribution terms in `README.txt` / `LICENSE.txt` are verified and satisfied.

### 3.4 Availability & Integrity of Headers, Dates, MIME & Campaign Information
- **Header Completeness**: Unlike Enron's PST exports, raw Nazario `.mbox` streams preserve genuine wire-level RFC 822 headers, including `Received:` server chains, `Return-Path:`, `Message-ID:`, `Date:`, `From:`, `To:`, `Reply-To:`, `Subject:`, `MIME-Version:`, and `Content-Type:`.
- **Documented Technical Integrity Pitfalls**:
  1. **HTML-Only & Placeholder MIME Bodies**: [`data/metadata/source_manifest.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/source_manifest.json) (line 10) and [`src/phishbench/filter_nazario_enron_quality.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/phishbench/filter_nazario_enron_quality.py) prove that in `phishing3.mbox`, `38 / 2,279` messages had empty or placeholder bodies (`"HTML file is required for this message"`), and a legacy `text/plain`-only parser produced empty bodies on **`196 / 441` (`44.4%`)** of phishing test items! Any parser must extract `text/html` cleanly while preserving anchor `href` target URLs.
  2. **Honeypot Recipient Header Confound (`To: jose@monkey.org` / `Delivered-To:`)**: Authentic Nazario messages share recipient/delivery headers tied to `monkey.org`. If `To:` or `Delivered-To:` is passed raw alongside Enron (`@enron.com`), any model or heuristic can trivially separate sources by recipient domain rather than phishing evidence.
  3. **Campaign Burstiness & Dormant Infrastructure**: Single phish-kit campaigns often appear dozens of times in one `.mbox` with minor random token changes, and historical URLs/domains in older `.mbox` files (`2005–2019`) are offline, precluding live DNS lookups (note: Domain Analyzer V3 operates offline on structural header/URL strings, which remains compatible, provided historical pre-SaaS lures are distinguished from contemporary threats).
  4. **Historical Overlap with IFSI**: As proved in [`phase8_1a_nazario_independence_audit.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1a_nazario_independence_audit.md), `phishing3.mbox` (`2,241` usable messages) was **100% consumed** in prior IFSI splits (`review_split_seed42` and `nazario_enron`).

---

## 4. Unresolved Legal & Governance Questions Blocking Immediate Acquisition

1. **Nazario `LICENSE.txt` & `README.txt` Uninspected**: Exact verbatim license text at `https://monkey.org/~jose/phishing/LICENSE.txt` must be read and archived before any `.mbox` file is fetched.
2. **Enron Fair-Use Non-Redistribution Sign-Off**: Because Enron carries **no explicit license**, using additional Enron messages requires explicit project/institutional sign-off to rely on local-only U.S. fair use (`17 U.S.C. § 107`) under the strict non-redistribution rules of [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md) (including git-ignoring `results/phase8_independent_evaluation/*predictions*.jsonl` if they embed email text or reasoning quotes).
3. **PII & Third-Party Correspondent Protection**: Existing regex scrubbing in `ingest_enron_corpus.py` left `23.6%` phone numbers, `12.2%` third-party emails, and HR promotion tables intact; stricter folder/content exclusion rules are mandatory before touching additional raw mailboxes.

