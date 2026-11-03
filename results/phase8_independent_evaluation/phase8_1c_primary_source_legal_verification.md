# Phase 8.1C: Primary-Source Legal, Format & Provenance Verification (`5` Shortlisted Sources)

## 1. Evidentiary Standard

Per Phase 8.1C governance rules:
- **Zero dataset downloads or web scraping were performed.**
- **Repository descriptions or secondary citations alone do NOT constitute legal clearance.** Every source below remains legally uncleared for ingestion until a separate, authorized **Acquisition Approval Gate** captures and hashes the verbatim upstream license/agreement file and confirms institutional compliance.
- Confirmed primary-source facts, reasoned estimates, and unresolved legal/operational questions are separated explicitly for all five Phase 8.1B shortlisted sources.

---

## 2. Source-by-Source Primary Verification

### Source A: `rf-peixoto/phishing_pot`
- **Official URL**: https://github.com/rf-peixoto/phishing_pot (Maintainer: Rodrigo Peixoto)
- **Confirmed Facts**:
  1. *Version & Layout*: Rolling Git repository (`2022–2025/2026`) storing sequential raw captures inside `email/sample-1.eml`, `email/sample-2.eml`, ..., growing past `12,000+` `.eml` files (`~7,900+` in `2024` snapshots). Must be pinned to an exact 40-char commit SHA upon approval.
  2. *Format & Headers*: Strictly `.eml` RFC 5322 wire format (`.msg`/`.pst` rejected upstream); preserves `Received:`, `Authentication-Results:`, `Received-SPF:`, `DKIM-Signature:`, `From:`, `Reply-To:`, `Return-Path:`, `Subject:`, `Date:`, `Message-ID:`, multipart MIME (`text/plain`, `text/html`), and inline URLs.
  3. *Upstream Anonymization*: Recipient mailbox fields are standardized upstream to `phishing@pot`.
  4. *Documented License*: **Creative Commons Attribution-NonCommercial 4.0 International (`CC BY-NC 4.0`)**, requiring attribution to https://github.com/rf-peixoto/phishing_pot and maintainer profile, and **strictly prohibiting commercial use** (including commercial ML/product evaluation or enrichment).
  5. *Historical IFSI Overlap*: **`0%` confirmed** across [source_manifest.json](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/source_manifest.json), `data/manifests/*.json`, `clean_split_v1`, and [metadata.json](file:///d:/Project/IFSI-for-phishing-email-detection/results/rag_index_clean/metadata.json).
- **Local Storage, Processing & Redistribution Boundaries**:
  - Non-commercial academic local storage and evaluation are permitted under `CC BY-NC 4.0` §2(a)(1).
  - **Public redistribution of raw or sanitized email bodies is PROHIBITED (`redistribution_allowed: false`)** under [PUBLIC_RELEASE.md](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md) because `CC BY-NC 4.0` licenses only the curator's compilation (`17 U.S.C. § 103(b)`), **not** third-party impersonated brand HTML/trademarks or attacker-authored text, and keeping data strictly git-ignored prevents `NC` contamination of IFSI's `MIT`-licensed code.
- **PII & Label Verification Risks**:
  - Residual PII in spoofed employee display names, `Reply-To:` addresses, or forwarded snippets requires regex scrubbing; executable/HTML-smuggling attachments must be stripped without execution.
  - Because honeypots also attract general spam (`C4`), independent human 6-class verification (`C1`/`C2` vs `C4`) is mandatory.
- **Unresolved Questions**:
  1. Exact Git commit SHA and verbatim `LICENSE` file SHA-256 have not yet been fetched/recorded locally.
  2. Written confirmation from project/institutional leads that IFSI Phase 8 benchmarking operates strictly under non-commercial academic scope (`CC BY-NC 4.0`).

---

### Source B: `Untroubled.org` Bait Sinkhole Archive
- **Official URL**: http://untroubled.org/spam/ (Maintainer: Bruce Guenter)
- **Confirmed Facts**:
  1. *Version & Layout*: Monthly `p7zip` (`.7z`) archives published continuously from `1998` through `2025/2026`, containing individual raw message files collected via spam-trap bait addresses (e.g., `<bait@em.ca>`).
  2. *Format & Headers*: Unedited raw RFC 822 headers (`Received:` traces, `From:`, `Subject:`, MIME bodies, URLs); maintainer warns `From:` headers are frequently forged by spammers.
  3. *Documented Terms*: Personal website notice explicitly grants permission to use the archive *"without restriction"* for research and software development (citation appreciated, excessive automated server fetching prohibited).
  4. *Historical IFSI Overlap*: **`0%` confirmed** in IFSI manifests/splits.
- **Local Storage, Processing & Redistribution Boundaries**:
  - Curator permits local R&D storage/processing; however, **zero SPDX license** exists and **underlying third-party sender copyrights and misdirected victim PII are uncleared**, mandating `redistribution_allowed: false` (git-ignored local storage only).
- **PII, Security & Label Verification Risks**:
  - Served over unencrypted **`http://`** (requiring strict archive SHA-256 pinning and sandboxed `7z` extraction to neutralize live malware payloads).
  - Primary literature confirms `untroubled.org/spam` is an **unlabeled general spam archive** (`>95%` bulk commercial spam `C4`); every candidate phishing record requires full dual-human 6-class verification.
- **Unresolved Questions**:
  1. Verbatim landing-page permission notice text + timestamped SHA-256 must be archived before any `.7z` download.
  2. True unique-campaign phishing density in `2023–2025` `.7z` archives is unverified prior to manual inspection (estimating `125` phishing messages in Phase 8.1B was unsupported; capped at `30` test + `10` val = `40` conditional messages in Phase 8.1C).

---

### Source C: IETF Public Mail Archive
- **Official URLs**: https://mailarchive.ietf.org/ & `rsync.ietf.org` (Publisher: Internet Engineering Task Force / IETF Trust)
- **Confirmed Facts**:
  1. *Version & Access*: Continuous public archive (`1992–2026`) across `100+` working-group/operational lists, accessible via sanctioned `rsync` (`rsync.ietf.org`) and `.mbox` exports (**never web scraping**), pinnable by list name + UTC date window (`2021–2025`).
  2. *Format & Headers*: Standard `.mbox` / RFC 5322 messages preserving `Received:`, `DKIM-Signature:`, `ARC-*`, `From:`, `To:`, `Subject:`, `Date:`, `Message-ID:`, `In-Reply-To:`, `List-*`, MIME text, and URLs.
  3. *Applicable Archive Terms*: Governed by **IETF Note Well (`BCP 78` / `RFC 5378`, `BCP 79` / `RFC 8179`)**, **IETF Trust Legal Provisions (TLP)**, and the **IETF/IRTF/IAB Privacy Statement**. Participants are explicitly notified that posts are permanently public and distributed via web/`mbox`/`rsync`; individual authors retain copyright in prose (`ietf-tools/mailarchive` `BSD-3-Clause` applies only to the archive software).
  4. *Historical IFSI Overlap*: **`0%` confirmed** on `2021–2025` messages (`spamassassin_ham` dates to `2002–2003`).
- **Local Storage, Processing & Redistribution Boundaries**:
  - Local academic evaluation of voluntarily published public standards mail is supported under public-archive terms and transformative research fair use (`17 U.S.C. § 107`); raw/sanitized bodies remain local-only (`redistribution_allowed: false`), publishing only `Message-ID`/SHA-256 manifests and aggregate metrics.
- **PII & Label Verification Risks**:
  - Contains real engineer names, corporate emails (`@google.com`, `@cloudflare.com`, `@cisco.com`, etc.), and occasional signature phone numbers (must scrub `[PHONE_REDACTED]` / `[ADDRESS_REDACTED]` and mask `To:`/`Cc:` to `<REDACTED_RECIPIENT>`).
  - Occasional spam/off-topic abuse reaches public lists, requiring dual-human verification of `C5` (`Legitimate email`).
- **Unresolved Questions**:
  1. Capture verbatim IETF `rsync` acceptable-use / TLP terms and Privacy Statement SHA-256 prior to bulk `.mbox` sync.

---

### Source D: Apache Software Foundation (ASF) Public Mail Archives
- **Official URLs**: https://lists.apache.org/ & https://www.apache.org/foundation/public-archives.html (Publisher: Apache Software Foundation)
- **Confirmed Facts**:
  1. *Version & Access*: Continuous public `.mbox` archives (`1999–2026`) across `350+` ASF project/operations lists (`Pony Mail`), pinnable by list + `YYYY-MM` (`2021–2025`).
  2. *Format & Headers*: `.mbox` / RFC 5322 with `Received:`, `SPF`/`DKIM`, `From:`, `Reply-To:`, `Subject:`, `Date:`, `Message-ID:`, `List-*`, bodies, and URLs.
  3. *Applicable Archive Terms*: **ASF Public Forum Archive Policy** (`apache.org/foundation/public-archives.html`) and **ASF Privacy Policy**. Senders unconditionally publish posts to permanent public archives (confidentiality footers explicitly declared null and void by ASF policy), while **individual authors retain copyright in email prose** (`Apache-2.0` covers code/CLA contributions, not casual list emails). Commercial address harvesting and misrepresented republication are forbidden.
  4. *Historical IFSI Overlap*: **`0%` confirmed** when restricted to `2021–2025` (`spamassassin_ham` `2003-02-28` is nearly two decades older).
- **Local Storage, Processing & Redistribution Boundaries**:
  - Local non-commercial evaluation permitted under public-archive policy + `17 U.S.C. § 107`; **zero public redistribution** of message text (`redistribution_allowed: false`).
- **PII & Label Verification Risks**:
  - Contributor names/emails and signature PII require regex redaction; high volume of automated `jira@apache.org` / `gitbox@apache.org` / GitHub Action bot mail must be deterministically excluded before human `C5` verification.
- **Unresolved Questions**:
  1. Archive verbatim `public-archives.html` + Pony Mail `.mbox` rate-limit/API terms prior to any `.mbox` retrieval.

---

### Source E: NIST / Waterloo TREC 2007 Public Corpus (`trec07p`)
- **Official URL**: https://plg.uwaterloo.ca/~gvcormac/treccorpus07/ (Coordinators: Gordon V. Cormack & Thomas R. Lynam)
- **Summary** *(full audit in [phase8_1c_trec_label_validity_audit.md](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1c_trec_label_validity_audit.md))*:
  - Confirmed `75,419` raw RFC 2822 messages (`25,220` `ham` + `50,199` `spam`, `Apr 8 – Jul 6, 2007`); `0%` IFSI overlap; governed by Waterloo TREC Public Spam Corpus Usage Agreement (`redistribution_allowed: false`).
  - *Unresolved*: Verbatim agreement page SHA-256 + institutional click-through sign-off; `0` native phishing labels in `full/index`.

---

## 3. Consolidated Legal & Governance Matrix

| Source | Exact Governing Instrument | Legal Clearance Status Today | Local Research Storage | Public Redistribution | Key Unresolved Legal / Privacy Action Before Download |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **`phishing_pot`** | `CC BY-NC 4.0` (compilation) | **UNCLEARED** *(repo metadata only)* | Permitted (`NC` only) | **PROHIBITED** (`false`) | Hash pinned `LICENSE` file; written `NonCommercial` sign-off |
| **`Untroubled.org`** | Curator R&D permission notice (`http://`) | **UNCLEARED** *(no SPDX; `http://`)* | Permitted (curator) | **PROHIBITED** (`false`) | Hash verbatim site notice; isolated malware/PII sandbox |
| **`IETF Archives`** | `BCP 78` (`RFC 5378`), TLP, Privacy Statement | **UNCLEARED** *(terms not yet hashed)* | Permitted (fair use) | **PROHIBITED** (`false`) | Hash TLP/`rsync` terms; use `rsync`/`.mbox` only (no scraping) |
| **`ASF Archives`** | ASF Public Forum Archive Policy | **UNCLEARED** *(terms not yet hashed)* | Permitted (fair use) | **PROHIBITED** (`false`) | Hash `public-archives.html` + `.mbox` export rate rules |
| **`TREC 2007`** | Waterloo TREC Spam Usage Agreement | **UNCLEARED** *(gateway not fetched)* | Permitted (`NC` research) | **PROHIBITED** (`false`) | Capture/hash Waterloo agreement; confirm institutional sign-off |

