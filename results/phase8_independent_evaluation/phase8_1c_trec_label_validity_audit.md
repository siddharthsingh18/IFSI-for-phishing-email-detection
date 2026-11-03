# Phase 8.1C: NIST / Waterloo TREC 2007 (`trec07p`) Label Validity & Phishing Separation Audit

## 1. Scope & Governance Mandate

This audit conducts a conservative, metadata-only preflight of the highest-priority candidate from Phase 8.1B: the **2007 TREC Public Spam Corpus (`trec07p`)** hosted at https://plg.uwaterloo.ca/~gvcormac/treccorpus07/ (Gordon V. Cormack & Thomas R. Lynam, University of Waterloo / NIST TREC 2007 Spam Track, NIST SP 500-274).

No files or archives were downloaded, scraped, or parsed during this audit. All Phase 8.1A (`phase8_1a_*.md`) and Phase 8.1B (`phase8_1b_*.md`) deliverables remain preserved unmodified.

---

## 2. Primary-Source Corpus Composition & Native Label Structure

### 2.1 Confirmed Primary-Source Facts
1. **Archive & Chronology**: `trec07p.tgz` contains **75,419** chronologically ordered email messages (`data/inmail.1` through `data/inmail.75419`) delivered to a single mail server over an 89-day window from **April 8, 2007 through July 6, 2007** (Cormack, *TREC 2007 Spam Track Overview*, NIST SP 500-274).
2. **Native Gold-Standard Classes (`full/index`)**:
   - **`ham` (Legitimate)**: **25,220** messages (`33.44%`), adjudicated via human review atop pre-adjudication filtering.
   - **`spam` (Unsolicited / Malicious Bulk Mail)**: **50,199** messages (`66.56%`).
   - **Auxiliary Index Files**: `delay/index` and `partial/index` define delayed/recipient-subset feedback schedules for online spam filters over the exact same `75,419` `inmail.*` files; neither adds finer semantic labels.
   - **Native `phishing` Label Count**: **`0` (NONE)**. Native `trec07p` is strictly a binary `ham`-vs-`spam` anti-spam benchmark, **not** a curated phishing corpus.
3. **Original Messages & Headers**:
   - Raw RFC 2822 message files preserve delivery headers (`Received:`, `Return-Path:`, `Message-ID:`, `From:`, `To:`, `Subject:`, `Date:`, `MIME-Version:`, `Content-Type:`) and raw MIME payloads, with minor systematic substitutions of local server/recipient identifiers applied by Cormack & Lynam for privacy.
4. **Recipient-Account Asymmetry Within the Same Server (Critical Nuance)**:
   - Cormack (2007) explicitly documents: *"The server contains many accounts that have fallen into disuse but continue to receive a lot of spam. To these accounts were added a number of 'honeypot' accounts published on the web."*
   - Consequently, although `ham` and `spam` traversed the same receiving MTA, `ham` arrived at **active user mailboxes** whereas a substantial share of `spam` arrived at **disused or web-published spam-trap accounts**. Unmasked `To:` / `Delivered-To:` headers would leak account status unless masked uniformly to `<REDACTED_RECIPIENT>`.

### 2.2 Technical & Era Limitations Affecting Phishing Extraction
- **2007 Spam Composition (`Storm` / Image-Spam / Stock-Pump Era)**: Mid-2007 botnet traffic heavily featured **inline GIF/PNG image spam** and **PDF attachment penny-stock pump-and-dump spam** carrying empty text parts or random word-salad ("Bayes-poisoning" prose), alongside pharmaceutical, replica-watch, casino, and adult commercial spam.
- **IFSI Parser Interaction**: [`src/tools/data/parsers/common.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/tools/data/parsers/common.py) extracts `text/plain` (falling back to non-attachment `text/*`). Image-only or PDF-only `2007` messages yield empty or gibberish text and **cannot** serve as valid text/header phishing test cases.
- **Pre-Modern Authentication Era**: `Apr–Jul 2007` predates `DMARC` (`RFC 7489`, 2015), `ARC` (`RFC 8617`, 2019), and modern multi-tenant SaaS `DKIM` ecosystems (`SendGrid`, `Workday`, `Okta`), limiting what `trec07p` can test in [`domain_analyzer_v3.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/experiments/phase7_domain_precision/domain_analyzer_v3.py) to URL/display-name/`From:`/`Reply-To:`/`Return-Path:` mismatches rather than modern SaaS authentication alignment.

---

## 3. Research Usage Agreement & Institutional Requirements

- **Confirmed Agreement Structure**: Access at https://plg.uwaterloo.ca/~gvcormac/treccorpus07/ is governed by the **TREC Public Spam Corpus Usage Agreement** (*"By downloading and using this data, you accept the terms of agreement for use of the TREC public spam corpus..."*).
- **Known Terms**:
  1. Permitted solely for non-commercial academic research, development, and evaluation.
  2. Public republication or redistribution of raw/derived message files (`trec07p.tgz` or extracted `inmail.*` texts) is **prohibited** (`redistribution_allowed: false` under [PUBLIC_RELEASE.md](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md)).
  3. Users acknowledge raw messages may contain offensive content, PII, or live malicious payloads.
- **Unresolved Institutional/Legal Questions (Must Resolve Prior to Any Download)**:
  1. Because Phase 8.1C prohibits fetching external files/gateways, the **exact verbatim HTML/text and SHA-256** of the Waterloo usage agreement page have not yet been archived locally.
  2. Unlike NIST's TREC Enterprise `W3C` track (which requires bilateral signed Organizational + Individual User Agreements submitted to NIST), Waterloo's `trec07p` uses researcher acceptance on the Waterloo host; however, institutional counsel/PI sign-off must confirm whether researcher click-through acceptance is authorized under local university/lab policy.

---

## 4. Can `trec07p` Spam Be Reliably Separated into Phishing vs. Ordinary Spam?

**Verdict: Reliable separation is IMPOSSIBLE from index metadata or automated heuristics alone, and is ONLY valid at the message level via strict dual-human annotation with mandatory `Ordinary Spam`, `Malware Delivery`, and `Ambiguous` exclusions.**

### Mandatory 6-Class Annotation Taxonomy for `trec07p` (and All Raw Sinkhole Candidates)

| Class ID | Taxonomy Label | Operational Definition & Required Message-Level Evidence | Track A Disposition |
| :---: | :--- | :--- | :--- |
| **`C1`** | **`Credential theft / phishing`** | Impersonates a specific trusted brand, financial institution, ISP, university, or IT administrator **and** solicits login credentials, passwords, PINs, account verification, or session authentication via a deceptive link, HTML form, or reply address. | **INCLUDE as `phishing` (`label = 1`)** |
| **`C2`** | **`Financial fraud / impersonation`** | Uses deceptive identity spoofing, falsified authority, or targeted social engineering to induce unauthorized wire transfer, invoice diversion, banking/payment-card disclosure, fake tax/escrow settlement, or advance-fee payment (`419` advance-fee capped at $\le 10\%$ of source phishing quota to prevent genre domination). | **INCLUDE as `phishing` (`label = 1`)** |
| **`C3`** | **`Malware delivery`** | Delivers an executable/archive/macro attachment (`.exe`, `.zip`, `.scr`, `.doc`) or exploit link **without** clear credential-harvesting or financial-impersonation prose, or relies on binary payload inspection rather than email text/headers. | **EXCLUDE (`EXCL_MALWARE_DELIVERY`)** *(strip attachments; do not map to phishing unless independent `C1`/`C2` text evidence holds)* |
| **`C4`** | **`Ordinary unsolicited commercial spam`** | Unsolicited bulk marketing, pharmaceutical/pill ads, replica luxury goods, penny-stock pump-and-dump promotions, casino/adult spam, SEO link spam, or commercial newsletters lacking deceptive identity impersonation for credential/financial theft ([docs/V2_RESEARCH_SPEC_ZH.md](file:///d:/Project/IFSI-for-phishing-email-detection/docs/V2_RESEARCH_SPEC_ZH.md) §2.2). | **EXCLUDE (`EXCL_ORDINARY_SPAM`)** *(never map to `phishing` or `legitimate`)* |
| **`C5`** | **`Legitimate email`** | Authentic benign personal, academic, administrative, or operational correspondence from the `ham` pool (`full/index == ham`) verified free of mislabeled spam, commercial bulk blasts, or phishing lures. | **INCLUDE as `legitimate` (`label = 0`)** |
| **`C6`** | **`Ambiguous`** | Image-only/empty-text `2007` messages; dead/truncated `2007` URLs where deceptive impersonation cannot be confirmed from preserved headers + body + literal URL string; aggressive greymail; or unresolved annotator disagreement. | **QUARANTINE (`track_a_ambiguous_quarantine.jsonl`)** *(excluded from binary denominators; reported separately)* |

### Dual-Annotator Labeling & Disagreement Adjudication Protocol
1. **Blind Independent Dual Labeling**: Two human cybersecurity annotators independently inspect sanitized RFC 2822 headers + body + literal URLs (with active network rendering disabled) and assign both a 6-class category (`C1`–`C6`) and an `injection_status` tag, **strictly blind to each other and blind to `A0`/`A1`/Config A/Config B predictions**.
2. **Inter-Annotator Reliability Gate**:
   - Minimum unweighted 6-class Cohen's $\kappa \ge 0.80$.
   - Minimum binary Cohen's $\kappa \ge 0.85$ across items assigned `C1/C2` vs. `C5`.
3. **Conservative Adjudication Rules**:
   - **Exact Match (`C1` or `C2` by both, or `C1`+`C2`)**: Accepted as `phishing` (`C1` vs `C2` subtype adjudicated by senior third reviewer for subtype reporting).
   - **Exact Match (`C5` by both)**: Accepted as `legitimate`.
   - **Any `C3` or `C4` Consensus**: Logged in `exclusion_log.jsonl` and discarded.
   - **Boundary Disagreement (`C1/C2` vs. `C3/C4/C6`)**: Escalated to a blind senior third adjudicator. Unless the third adjudicator documents explicit message-level impersonation + credential/financial solicitation evidence, the record defaults to **`C4` (`EXCL_ORDINARY_SPAM`) or `C6` (`Ambiguous`)**—never `phishing`.
   - **Opposite-Polarity Disagreement (`C1/C2` vs. `C5`)**: **Mandatory automatic quarantine as `C6` (`Ambiguous`)**; no tie-breaker may promote a `phishing`-vs-`legitimate` human conflict into the clean binary benchmark.

---

## 5. Reality Check on Phase 8.1B Quotas (`120` Phishing + `120` Legitimate Test; `30 + 30` Val)

| Proposed `trec07p` Quota (Phase 8.1B) | Evidence Status | Preflight Verdict & Conservative Revision |
| :--- | :--- | :--- |
| **`120` Test + `30` Val = `150` Legitimate (`ham`)** | **EVIDENCE-BASED** (`25,220` human-adjudicated `ham` in `full/index`; `150` is `0.59%` of `ham`) | **Supported** — Adjusted proportionally in Phase 8.1C to **`105` Test + `35` Val = `140` Legitimate** (`0.56%` of `ham`). |
| **`120` Test + `30` Val = `150` Phishing (from `spam`)** | **UNVERIFIED ESTIMATE (NOT EVIDENCE-BASED)** — Zero published phishing count in Cormack (2007); `2007` `spam` heavily dominated by image/PDF stock/pharma spam; 89-day single-server window risks severe phish-kit burst collapse under `0.70` shingle Jaccard deduplication. | **REJECTED (`120 + 30` quota rejected)** — Misrepresents an ordinary-spam benchmark as a `50/50` phishing core. Slashed by **`60%`** to a strictly conditional ceiling of **`45` Test + `15` Val = `60` verified phishing** (`0.12%` of `50,199` spam: `1.2` per `1,000` spam messages), making `trec07p` `70%` `ham` / `30%` verified phishing. |

