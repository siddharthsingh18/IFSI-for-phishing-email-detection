# Phase 8.1B: Candidate Source Licensing, Copyright & Provenance Audit

## 1. Executive Summary & Evidentiary Standards

This audit evaluates the legal basis, intellectual property chain of title, data-use agreements (DUAs), redistribution boundaries, and privacy/PII obligations across all 21 candidate sources cataloged in [`phase8_1b_alternative_source_registry.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1b_alternative_source_registry.md).

### Core Legal Governance Principles Enforced
1. **No Unverified Clearance Claims**: Because Phase 8.1B strictly prohibits downloading files or scraping external repositories, **zero candidate sources are declared "legally cleared for immediate download" today**. Candidates marked `APPROVED FOR FURTHER REVIEW` have identifiable public licensing/policy frameworks documented at their official URLs, **but** require a dedicated **Phase 8.1C Metadata-Only Preflight** to download, inspect verbatim, and SHA-256 hash their `LICENSE` / usage-agreement text before fetching any email bytes.
2. **Curator Compilation License $\neq$ Underlying Third-Party Sender Copyright**: Under `17 U.S.C. § 103(b)`, copyright in a compilation extends *only* to the material contributed by the compiler (selection, coordination, honeypot capture), **not** to pre-existing text authored by third-party email senders or HTML/trademarks misappropriated by attackers from impersonated brands.
3. **Universal Non-Redistribution Rule for Track A**: Consequently, **every real-email source investigated requires `redistribution_allowed: false`** under [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md). Raw archives, sanitized `.jsonl` evaluation splits, and per-sample LLM prediction traces quoting email text must remain strictly local and git-ignored; only aggregate metrics, code, message-ID/offset manifests, and SHA-256 digests may be published.
4. **Rejection of Secondary "License Laundering"**: Secondary aggregators on Zenodo, Kaggle, or HuggingFace (e.g., `10.5281/zenodo.8339691`, `MeAJOR`) that repackage Enron, Nazario, SpamAssassin, and TREC under a `CC BY 4.0` badge cannot grant rights that the upstream publishers never possessed.

---

## 2. Detailed Legal & Privacy Audit of Shortlisted Candidates (`APPROVED FOR FURTHER REVIEW`)

### 2.1 `rf-peixoto/phishing_pot` (`https://github.com/rf-peixoto/phishing_pot`)
- **Verified Evidence**:
  - Publicly documented by curator Rodrigo Peixoto under **Creative Commons Attribution-NonCommercial 4.0 International (`CC BY-NC 4.0`)** specifically for threat-intelligence researchers, academic researchers, and detection developers.
  - Explicit attribution requirements documented: link to `https://github.com/rf-peixoto/phishing_pot` and maintainer profile `https://www.linkedin.com/in/rf-peixoto`.
  - Recipient mailbox PII is upstream-sanitized to `phishing@pot` prior to commit.
- **Lifecycle Permissions & Restrictions**:
  - *Local Storage & Non-Commercial Research Evaluation*: **Permitted** under `CC BY-NC 4.0` Section 2(a)(1), provided evaluation is strictly non-commercial academic/research benchmarking.
  - *Commercial Use*: **Strictly Prohibited** (cannot be used to train, tune, or market commercial paid services/products without separate written permission from the maintainer).
  - *Derived Records & Public Redistribution*: Kept **local-only (`redistribution_allowed: false`)** because underlying attacker lure prose and spoofed brand HTML/logos (`Microsoft`, `PayPal`, `DHL`, etc.) belong to third parties outside the curator's compilation copyright.
- **Unresolved Legal Questions for Phase 8.1C Preflight**:
  1. Fetch and record the exact SHA-256 of the upstream `LICENSE` and `README.md` at a pinned Git commit SHA.
  2. Confirm institutional/project alignment with the **NonCommercial (`NC`)** restriction (since IFSI repository code is `MIT` in `LICENSE`, keeping `phishing_pot` data strictly git-ignored and local prevents `CC BY-NC 4.0` from encumbering the `MIT` software repository).

### 2.2 `Untroubled.org` Bait Sinkhole Archive (`http://untroubled.org/spam/`)
- **Verified Evidence**:
  - Published by Bruce Guenter since 1998 as monthly `.7z` archives of raw bait-address mail, accompanied by an explicit site statement granting permission to use the archive without restriction for research and development (with optional citation).
- **Lifecycle Permissions & Restrictions**:
  - *Local Storage & Research Processing*: **Permitted** as to curator compilation rights + transformative U.S. research fair use (`17 U.S.C. § 107`) for local security evaluation.
  - *Derived Records & Public Redistribution*: **Prohibited (`redistribution_allowed: false`)** — Bruce Guenter does not hold third-party sender copyrights, and occasional misdirected third-party correspondence or embedded victim email addresses may appear in raw sinkhole captures.
- **Unresolved Legal & Privacy Questions for Phase 8.1C Preflight**:
  1. Archive the exact verbatim text and SHA-256 of the `http://untroubled.org/spam/` landing-page permission notice prior to downloading any `.7z` file.
  2. Enforce strict PII redaction + attachment stripping (raw bait mail can carry executable malspam attachments and third-party forwarded PII).

### 2.3 IETF Public Mail Archive (`https://mailarchive.ietf.org/`)
- **Verified Evidence**:
  - Hosted by the IETF / IETF Trust. Contributors post to public IETF working-group and operational lists under the **IETF Note Well (`BCP 78` / `RFC 5378`)** and **IETF Trust Legal Provisions (TLP)**, which explicitly notify senders that messages are permanently archived and publicly distributed via web and `.mbox`/rsync interfaces.
  - Archive software (`ietf-tools/mailarchive`) is `BSD-3-Clause`, which governs the software, **not** individual message prose (individual authors retain copyright in their emails while granting public archival/distribution licenses to the IETF Trust).
- **Lifecycle Permissions & Restrictions**:
  - *Acquisition Method*: Must use official bulk `.mbox` export / `rsync` endpoints — **never automated HTML web scraping**.
  - *Local Storage & Research Evaluation*: **Permitted** under fair use (`17 U.S.C. § 107`) over voluntarily published public standards correspondence; **zero public redistribution** of message bodies (`redistribution_allowed: false`).
- **PII & Unresolved Questions for Phase 8.1C Preflight**:
  1. Verify exact `rsync` / `.mbox` terms of service and acceptable-use rate limits on `ietf.org`.
  2. Redact personal phone numbers/street addresses in email signatures and exclude personal/non-technical administrative complaints (GDPR Art. 5(1)(c) data minimization).

### 2.4 Apache Software Foundation Public Mail Archives (`https://lists.apache.org/`)
- **Verified Evidence**:
  - Governed by the **ASF Public Forum Archive Policy** and **ASF Privacy Policy**. Senders posting to public `@apache.org` lists explicitly consent to permanent public archiving and `.mbox` download access, while retaining individual copyright in message prose (casual list emails are **not** automatically licensed under `Apache-2.0`, which applies to code/CLA contributions).
  - ASF policy explicitly forbids harvesting addresses for unsolicited commercial email or republishing modified archives as official ASF records.
- **Lifecycle Permissions & Restrictions**:
  - *Local Storage & Research Evaluation*: **Permitted** for local non-redistributed classifier evaluation (`17 U.S.C. § 107` fair use); `redistribution_allowed: false` per [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md).
- **Unresolved Questions for Phase 8.1C Preflight**:
  1. Record verbatim ASF Public Forum Archive Policy and Pony Mail `.mbox` API usage rules before fetching any monthly `.mbox` file.
  2. Scrub personal phone numbers and contributor home addresses from email footers.

### 2.5 NIST / Waterloo TREC 2007 Public Corpus (`https://plg.uwaterloo.ca/~gvcormac/treccorpus07/`)
- **Verified Evidence**:
  - Compiled by Gordon V. Cormack & Thomas R. Lynam (University of Waterloo) for the NIST TREC 2007 Spam Track (`trec07p.tgz`).
  - Governed by a specific **TREC Spam Track Research & Evaluation Usage Agreement** on the Waterloo distribution page: free for non-commercial academic/scientific research and evaluation, with strict prohibitions against third-party redistribution and against using TREC evaluation scores in commercial product advertising.
- **Lifecycle Permissions & Restrictions**:
  - *Local Storage & Non-Commercial Research Evaluation*: **Conditionally Permitted** upon reading, accepting, and archiving the exact Waterloo usage agreement text.
  - *Public Redistribution*: **Strictly Prohibited (`redistribution_allowed: false`)**.
- **Unresolved Questions for Phase 8.1C Preflight**:
  1. Inspect `https://plg.uwaterloo.ca/~gvcormac/treccorpus07/` agreement text directly (without downloading `trec07p.tgz` until signed/accepted) to confirm whether individual click-through acceptance suffices or whether institutional signature is required.

---

## 3. Legal & Ethical Audit of Conditional, Unverified & Excluded Sources

| Source | Official URL | Verified Legal Instrument / Barrier | Why Not Immediately Usable or Why Excluded |
| :--- | :--- | :--- | :--- |
| **`Avocado` (`LDC2015T03`)** | `https://catalog.ldc.upenn.edu/LDC2015T03` | Formal bilateral **LDC End User Agreement** + paid membership/corpus fee (`~$2k–$3k` non-member) | Legally sound once licensed, **but** blocked without paid institutional execution; strict non-redistribution. |
| **`TREC W3C Corpus`** | `https://trec.nist.gov/data/enterprise.html` | Formal **NIST Organizational + Individual User Agreements** | Requires institutional signatory execution and NIST approval before access; prohibits redistribution. |
| **`CEAS 2008` (`ceascorpus`)** | `http://plg.uwaterloo.ca/~gvcormac/ceascorpus/` | Implied academic release (no SPDX license) | No explicit reuse license; intermittent host availability; third-party Kaggle copies launder licenses and strip headers. |
| **`MalwareBazaar` (`.eml`)** | `https://bazaar.abuse.ch/` | Abuse.ch API ToS (`CC0` covers YARA/metadata, **not** victim `.eml` PII) | Unredacted real corporate victim `To:` headers create acute GDPR/privacy liability; live malware payloads. |
| **`APWG eCX`** | `https://apwg.org/ecx/` | Bilateral **APWG Data Sharing Agreement (DSA)** / Researcher Grant | Closed clearinghouse; zero access permitted without executed organizational DSA. |
| **`Enron` & `Jose Nazario`** | `https://www.cs.cmu.edu/~enron/` & `https://monkey.org/~jose/phishing/` | Enron: **None** (`redistribution_allowed: false`); Nazario: `LICENSE.txt` unverified in 8.1A | **Preserved on Phase 8.1A Hold** (legal + RAG/exhaustion contamination). |
| **`PhishFuzzer Seed v1`** | `https://github.com/DataPhish/PhishFuzzer` | **None** (`source_manifest.json`: no `LICENSE`/`COPYING` at commit `1e21dd4e...`) | Unlicensed + 100% consumed in V2 + stripped JSON without RFC 822 headers. |
| **`SpamAssassin` & `Nigerian 419`** | `https://spamassassin.apache.org/old/publiccorpus/` & `https://www.cl.cam.ac.uk/~rnc1/naivebayes.html` | Corpus warnings only; original sender copyrights retained | Already consumed/registered in IFSI manifests with `redistribution_allowed: false`. |
| **`EPVME`** | `https://github.com/antispam-research/EPVME` | `GPL-3.0` repo wrapper + unverified embedded email copyrights | Copyleft wrapper cannot clear embedded third-party emails; excluded as adversarial in `corpora.yaml`. |
| **`IWSPA-AP 2018 / 2023`** | `https://www2.cs.uh.edu/~rmverma/` | Bilateral DUA (2018); **contains leaked WikiLeaks/DNC emails** | **Permanently disqualified**: incorporates criminally exfiltrated DNC correspondence alongside Enron/Nazario/SA. |
| **`Zenodo 8339691` / `MeAJOR`** | `https://doi.org/10.5281/zenodo.8339691` | Secondary `CC BY 4.0` tag applied to 11 scraped/merged legacy corpora | **Invalid chain of title (license laundering)** over Enron, Nazario, SpamAssassin, and TREC + stripped CSV format. |
| **`U.S. Federal FOIA PDFs`** | `https://foia.state.gov/` / `https://www.archives.gov/` | `17 U.S.C. § 105` covers federal employee works *only*, not inbound citizen emails | Inbound third-party copyrights retained + PDF redactions destroy RFC 822 structure. |

