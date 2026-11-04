# Phase 8.1C — Primary-Source Legal, Format, and Provenance Verification

## Evidence standard

This report records only metadata and policy pages. No dataset archive, repository email, `.eml`, `.mbox`, `.7z`, attachment, or message body was downloaded. A public page or repository description is not treated as legal clearance. Exact license/policy text must be captured and hashed during a separately approved acquisition preflight.

Evidence examined on 2026-11-06:

- TREC: <https://plg.uwaterloo.ca/~gvcormac/treccorpus07/>, <https://trec.nist.gov/pubs/trec16/papers/SPAM.OVERVIEW16.pdf>
- Phishing Pot: <https://github.com/rf-peixoto/phishing_pot>, its `README.md`, `DATASET_CARD.md`, and `LICENSE` pages/raw text
- Untroubled: <http://untroubled.org/spam/>
- IETF: <https://mailarchive.ietf.org/>, <https://www.ietf.org/about/open-records/>, <https://datatracker.ietf.org/doc/rfc5378/>, <https://trustee.ietf.org/documents/trust-legal-provisions/>, <https://trustee.ietf.org/documents/copyright-policy-and-tlp-faq/>
- ASF: <https://lists.apache.org/>, <https://apache.org/dev/>, <https://www.apache.org/foundation/public-archives.html>, <https://ponymail.apache.org/>

## Source assessments

### A. `rf-peixoto/phishing_pot`

**Confirmed:** The repository is a rolling GitHub repository. Its README says contributors should provide anonymized samples in `.eml` format and that `.msg`/`.pst` files are rejected. The dataset card describes real-world samples that can include original `.eml` content, SMTP/routing headers, sender/recipient metadata, authentication information, URLs, attachments, phishing, spam, fraud, and malware. The repository’s `LICENSE` is the Creative Commons Attribution-NonCommercial 4.0 text; the dataset card states non-commercial use and attribution to the repository and maintainer.

**Version:** No immutable commit, release, or sample count was pinned in this preflight. `main` and the GitHub commit history are not a reproducible dataset version. A future approval must pin a full commit SHA and record the tree/file manifest and hashes.

**Permission and restrictions:** CC BY-NC 4.0 provides only rights the licensor can grant, does not license privacy, publicity, patent, or trademark rights, and limits licensed sharing to non-commercial purposes. The dataset card itself warns that real-world messages may contain sensitive information and are not statistically representative. Local non-commercial processing may be possible after institutional review; raw or sanitized body redistribution is not approved.

**PII/label risk:** Honeypot collection can contain third-party addresses, forwarded content, credentials, malware, ordinary spam, and mixed labels. The repository description is not message-level ground truth. `C1`/`C2` versus `C3`/`C4` still requires dual review.

**Quota status:** The proposed `180` test + `45` validation messages is an **estimate only**. No metadata-only evidence establishes a usable post-deduplication count.

**Decision:** `CONDITIONALLY SUITABLE` for a separate approval, subject to a pinned commit, exact license hash, non-commercial institutional sign-off, privacy/malware handling plan, and measured yield.

### B. Untroubled.org spam archive

**Confirmed:** The landing page says it contains spam received since early 1998, collected using bait addresses, and that archives are recompressed with p7zip. It grants permission to use the archive without restriction for research and software development, requests citation, warns that headers are often forged, and asks users not to repeatedly refetch the daily-updated files. The page also notes that the archive may be less useful after the bait-domain change in April 2018.

**Version and format:** The live page is not a versioned release. A specific month/year archive, directory listing, archive hash, and extracted member inventory were not captured. The page describes archive files and filename conventions, but exact RFC 822/header preservation and usable message count remain unverified until an approved sample inspection.

**Permission and restrictions:** The maintainer’s research/development permission supports a possible local-processing path, but it is not an SPDX license, does not settle third-party sender copyright, privacy, or publicity rights, and does not authorize public redistribution of raw mail. Keep `redistribution_allowed: false` unless counsel establishes otherwise.

**PII/security/label risk:** The page explicitly warns that `From:` is often forged. Bait mail can contain personal addresses, forwarded content, URLs, and active malware. The archive is an unlabeled spam collection; no phishing count or source-specific phishing label is established.

**Quota status:** The proposed `100` test + `25` validation phishing messages is **unsupported**. It is not evidence-based and cannot be converted from “spam” to “phishing” by keyword filtering.

**Decision:** `CONDITIONALLY SUITABLE` only as a possible supplementary source after a safety-controlled, approved pilot and dual annotation. It is not acquisition-ready.

### C. IETF public mail archives

**Confirmed:** IETF’s open-records page says that the Mail Archive provides a unique permanent URL for public-list messages, allows archive downloads, and documents `rsync.ietf.org::mailman-archive` for local processing. The archive site is a live service, not a fixed release. The IETF Trust FAQ states that an email to an IETF mailing list can be an IETF Contribution; RFC 5378 and the Trust Legal Provisions define rights and restrictions for IETF Contributions and Documents.

**Version and format:** Freeze an exact list set and UTC date interval, then hash the export. The metadata pages support public archive and mbox/rsync access, but this preflight did not verify every message’s headers, MIME completeness, or the selected pool size.

**Permission and restrictions:** Public availability and IETF Trust terms are not a blanket license for every author’s prose, personal data, or quoted third-party material. The exact applicable TLP version, list terms, retention/deletion conditions, and the institution’s authority to process and publish derived text remain legal questions. Raw bodies remain local-only.

**PII/label risk:** Names, addresses, signatures, quoted private material, and occasional spam/off-topic posts may occur. Public-list membership does not make every message a legitimate-business example. Human screening is required.

**Quota status:** The proposed `160` test + `40` validation legitimate messages is **plausible but estimated**, not a confirmed usable yield. It must be sampled across lists, threads, domains, and time after acquisition approval.

**Decision:** `CONDITIONALLY SUITABLE` for a separate approval; not legally cleared and not yield-verified.

### D. Apache Software Foundation public mail archives

**Confirmed:** The ASF archive homepage describes public searchable mailing-list archives. ASF developer documentation identifies raw monthly mbox access through the `lists.apache.org` API. The Public Forum Archive Policy says public-forum communications are published by the sender and may remain public indefinitely; it describes limited archive modification for exceptional disclosures such as secrets or social-security numbers. Pony Mail documents mbox import/export capability for archive systems.

**Version and format:** The service is continuously changing. Freeze exact list names, months, filters, and export hashes. This preflight did not fetch an mbox or verify per-message headers, MIME bodies, or post-filter usable volume.

**Permission and restrictions:** The Public Forum Archive Policy establishes public publication and archive operation; it does not by itself provide a blanket copyright, privacy, or redistribution license for third-party email prose. Apache-2.0 software licensing must not be applied to list messages. Raw and sanitized message bodies remain local-only pending legal review.

**PII/label risk:** Public contact details, signatures, quoted material, confidential disclosures, bots, CI, Jira, and spam may appear. Exclude automation and non-human noise by a documented rule and manually verify the legitimate class.

**Quota status:** The proposed `120` test + `30` validation legitimate messages is **plausible but estimated**, not confirmed from a frozen pool.

**Decision:** `CONDITIONALLY SUITABLE` for a separate approval; not legally cleared and not yield-verified.

### E. TREC 2007 public corpus

**Confirmed:** The NIST TREC overview reports `25,220` ham and `50,199` spam messages (`75,419` total), delivered to one server from 8 April to 6 July 2007, with disused and honeypot accounts included. It is a spam/ham corpus, not a phishing-labeled corpus.

**Version and format:** The official Waterloo distribution URL is the source of the corpus and usage gate. The NIST overview describes public email messages plus gold-standard indexes and says the messages were unaltered except for systematic name substitutions. Exact current archive contents and field preservation were not inspected.

**Permission and restrictions:** The Waterloo usage-agreement text was not captured or hashed in this metadata-only pass. Therefore the exact research-use terms, redistribution restrictions, acceptance mechanism, and any institutional requirements remain unresolved. No legal clearance is claimed.

**PII/label risk:** The described systematic substitutions reduce some identity exposure, but do not establish that all personal information or payloads are absent. The source’s `spam` label cannot establish phishing.

**Quota status:** `150` ham is capacity-plausible; `150` phishing is unsupported. The phishing quota is rejected pending message-level evidence.

**Decision:** `UNVERIFIED` for the proposed dual-class use; it may be reconsidered for a ham slice and separately audited spam slice after the agreement is captured and approved.

## Legal/technical separation

| Source | Legal clearance | Technical format suitability | Independence | Usable yield |
|---|---|---|---|---|
| Phishing Pot | Unresolved; CC BY-NC is visible but exact pinned version and third-party rights are unresolved | Likely suitable `.eml`, to be verified | Not established from source bytes in this pass | Estimated only |
| Untroubled | Informal research permission; third-party rights unresolved | Likely raw p7zip mail, to be verified | Not established from source bytes in this pass | Unsupported for phishing |
| IETF | Public archive and Trust framework; exact reuse scope unresolved | Public archive/rsync/mbox path documented | Not established from source bytes in this pass | Estimated only |
| ASF | Public-archive policy; no blanket message license established | Public mbox path documented | Not established from source bytes in this pass | Estimated only |
| TREC 2007 | Agreement not captured; unresolved | Public email corpus documented | Not established from source bytes in this pass | Ham plausible; phish unknown |

No source is marked `READY FOR A SEPARATE ACQUISITION APPROVAL` because the required exact legal text, pinned version, and yield gates have not all been completed.
