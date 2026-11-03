# Phase 8.1A: Conditional Staged Acquisition Pilot Plan (`N = 50` per Source)

> [!CAUTION]
> **Design-Only Governance Specification — DO NOT EXECUTE IN PHASE 8.1A**:
> Per [`phase8_1a_final_decision.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1a_final_decision.md), **neither source is currently cleared for acquisition**. Zero archives have been downloaded in this phase. Execution of even this small staged pilot is strictly gated on resolving the legal and historical-independence prerequisites enumerated in Section 1.

---

## 1. Pre-Pilot Entry Gates (Mandatory Blockers Before Fetching Any Byte)

1. **Nazario License Verification Gate**:
   - Inspect only the upstream plain-text metadata files `https://monkey.org/~jose/phishing/README.txt` and `https://monkey.org/~jose/phishing/LICENSE.txt`, record their exact verbatim contents and SHA-256 digests in [`phase8_1a_source_legal_audit.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1a_source_legal_audit.md), and confirm that local non-redistributed research evaluation is permitted without viral copyleft contamination of repository code.
2. **Enron Non-Redistribution Governance Sign-Off & Scope Reframing**:
   - Obtain explicit researcher/institutional sign-off to process Enron locally under U.S. fair use (`17 U.S.C. § 107`) with `redistribution_allowed: false` per [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md).
   - Formally reclassify any Enron pilot slice from *"external source-independent generalization"* to **"within-corpus unseen-custodian holdout"**, because `369` Enron records already reside in the frozen [`results/rag_index_clean/index.faiss`](file:///d:/Project/IFSI-for-phishing-email-detection/results/rag_index_clean/index.faiss). Furthermore, per [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml) (`maximum_source_fraction: 0.40`), Enron cannot serve as the sole legitimate source in Track A.
3. **Historical V1 / `phishing3.mbox` Exclusion Manifest Recovery**:
   - Recover the historical `original_id` / SHA-256 manifest for V1 `nazario_enron` (`441` Enron + `441` Nazario, SHA-256 `c1121951...`) or restrict Nazario pilot sampling exclusively to post-2020 annual archives (`phishing-2021`–`phishing-2024`) while permanently blacklisting `phishing0.mbox`–`phishing3.mbox`.

---

## 2. Pilot Sample Sizing (`N = 50` Candidates per Source, Not `2,000`)

Rather than ingesting `2,000` messages upfront, Stage 1 of acquisition is restricted to a **micro-pilot of `N = 50` candidate messages per cleared source** (`100` messages total):

| Pilot Cohort | Candidate Count | Sampling Stratification Rule | Prohibited Upstream Subsets |
| :--- | ---: | :--- | :--- |
| **Enron Unseen-Custodian Pilot** | `50` (`10` msgs $\times$ `5` custodians) | Select `5` custodians outside Enron Transportation Services / Northern Natural Gas with zero email exchange with `blair-l`; sample only business operational folders (`projects`, `logistics`, `deals`). | Entire `maildir/blair-l/*` custodian (`500` records already used); any custodian appearing in `blair-l` `From`/`To`/`Cc`; all HR/personal folders. |
| **Nazario Modern Archive Pilot** | `50` (`25` msgs $\times$ `2` annual files) | Stratified sample across distinct sender domains and phish-kit DOM clusters (max `2` messages per campaign cluster) from post-2020 annual `.mbox` files. | `phishing0.mbox`, `phishing1.mbox`, `phishing2.mbox`, and **`phishing3.mbox`** (`100%` exhausted in `review_split_seed42` & `nazario_enron`). |

---

## 3. Three-Tier Immutable Local Storage Architecture

All three storage tiers contain unlicensed/third-party email text and **must remain strictly git-ignored** under `.gitignore` and verified by [`src/tools/release/check_public_release.sh`](file:///d:/Project/IFSI-for-phishing-email-detection/src/tools/release/check_public_release.sh). Only aggregate pilot audit statistics and hash-only manifests may be tracked in `results/phase8_independent_evaluation/`.

```text
data/                                              [GIT-IGNORED LOCAL STORAGE]
├── raw/phase8_pilot/                              [TIER 1: IMMUTABLE RAW BYTES (chmod read-only)]
│   ├── enron/enron_mail_20150507.tar.gz           (Verify SHA-256 == b3da1b3fe0369ec3...)
│   ├── nazario/<pinned_annual_mbox>               (Record exact archive SHA-256 on receipt)
│   └── raw_pilot_slice/                           (Exact unmodified RFC 822 .eml / mbox slices)
├── processed/phase8_pilot_sanitized/              [TIER 2: PII-REDACTED & MIME-EXTRACTED]
│   ├── enron_pilot_50_sanitized.jsonl
│   ├── nazario_pilot_50_sanitized.jsonl
│   ├── transformation_log.jsonl                   (Per-message header/body redaction audit log)
│   └── exclusion_log.jsonl                        (Every rejected raw candidate + reason code)
└── evaluation/phase8/pilot_candidates/            [TIER 3: DUAL-VERIFIED, OVERLAP-CLEARED READY]
    ├── track_a_pilot_verified.jsonl               (Only dual-annotated, 8-gate cleared records)
    └── pilot_manifest.sha256                      (Archive, raw-msg, and sanitized record hashes)
```

---

## 4. Provenance Manifests, Source Identifiers & Multi-Level SHA-256 Hashing

Every candidate record must carry deterministic, auditable lineage fields:
- `pilot_record_id`: e.g., `p8-pil-enr-0001` or `p8-pil-naz-0001`
- `source_corpus`: `"enron_cmu_20150507"` or `"nazario_monkey_mbox"`
- `upstream_url`: Exact download URL
- `upstream_archive_sha256`: Full 64-hex SHA-256 of the compressed archive/mbox file
- `source_member_id`:
  - Enron: exact tar member path (e.g., `maildir/<custodian>/<folder>/<msg_id>`) + `Message-ID` header
  - Nazario: `<mbox_filename>:index=<idx>:byte_offset=<start>-<end>` + `Message-ID` header
- `raw_rfc822_sha256`: SHA-256 of the unmodified raw RFC 822 message bytes prior to any parsing or PII scrubbing
- `sanitized_record_sha256`: SHA-256 of the canonical JSON serialized sanitized record

---

## 5. Header-Preservation & MIME Parsing Requirements

To avoid the two historical pipeline bugs uncovered in Phase 8.1A—(a) [`ingest_enron_corpus.py`](file:///d:/Project/IFSI-for-phishing-email-detection/tools/data/ingest_enron_corpus.py) stripping `Date`, `To`, `Cc`, `Message-ID` headers, and (b) V1 Nazario parser dropping `44.4%` (`196/441`) HTML-only bodies:

1. **Zero Header Fabrication**:
   - Store the complete original RFC 822 header block in `raw_headers` (subject only to recipient/PII token masking logged in `transformation_log.jsonl`).
   - **Never synthesize missing `Received:`, `Return-Path:`, `SPF`, `DKIM`, or `DMARC` headers** on Enron PST-reconstructed records.
2. **HTML-Aware Lossless MIME Extraction**:
   - Parse MIME parts using Python `email.policy.default`. Prefer `text/plain` when substantive; when `text/plain` is absent or matches `MIME_PLACEHOLDER_RE` (`"HTML file is required..."`), extract visible text from `text/html` while **explicitly preserving all `<a href="...">` target URLs** in `extracted_urls` so Domain Analyzer V3 receives authentic link-domain evidence.
3. **Honeypot Recipient De-Confounding**:
   - Normalize recipient headers (`To:`, `Delivered-To:`, `X-Original-To:`) across *both* sources to a neutral placeholder (`<REDACTED_RECIPIENT>`) in the model-input view while preserving `From:`, `Sender:`, `Reply-To:`, `Return-Path:`, and `Subject:` intact, preventing trivial `jose@monkey.org` vs. `@enron.com` recipient-header shortcuts.

---

## 6. Mandatory PII Redaction & Hard Exclusion Rules

### 6.1 Hard Exclusion (Drop Entire Candidate Before Storage in Tier 2)
- **Enron Folder Blocklist**: Immediately reject any path matching `personnel*`, `hr*`, `promotion*`, `salary*`, `compensation*`, `medical*`, `health*`, `family*`, `personal*`, `vacation*`, `itinerary_off_duty*`, `resume*`, or `legal_privileged*`.
- **Attachment-Stub / Empty Body**: Reject messages with $< 40$ alphanumeric characters after MIME extraction or predominantly stripped attachment placeholders (`<<...DOC>>`).
- **Third-Party Private Individuals**: Reject emails sent from consumer webmail (`@aol.com`, `@hotmail.com`, `@yahoo.com`, `@msn.com`) discussing private non-business matters.

### 6.2 Deterministic PII Redaction (Logged in `transformation_log.jsonl`)
- U.S. / international telephone and fax numbers (`23.6%` prevalence in `enron_clean_500`) $\rightarrow$ `[PHONE_REDACTED]`
- SSNs, taxpayer IDs, bank routing/account numbers, payment card numbers $\rightarrow$ `[FINANCIAL_PII_REDACTED]`
- Physical home street addresses $\rightarrow$ `[ADDRESS_REDACTED]`
- **Strict Security Invariant**: Never redact sender domains (`From:`/`Reply-To:`/`Return-Path:` domain part) or hyperlink domains/paths needed for phishing verification.

---

## 7. Transformation & Exclusion Logging Schema

1. **`exclusion_log.jsonl`**: Every skipped archive member records `{timestamp_utc, source_member_id, raw_rfc822_sha256, stage, exclusion_code, detail}` (e.g., `EXCL_FOLDER_SENSITIVE`, `EXCL_EMPTY_HTML_STUB`, `EXCL_THREAD_OVERLAP_RAG`, `EXCL_NON_PHISH_BULK_SPAM`).
2. **`transformation_log.jsonl`**: Every retained candidate records `{pilot_record_id, raw_rfc822_sha256, sanitized_record_sha256, mime_part_used, extracted_url_count, redactions_applied: {phone: int, financial: int, address: int, recipient_header: int}}`.

---

## 8. Human Label Verification & Ambiguous-Message Handling

Because archive membership does **not** guarantee ground-truth class purity (as proven by `flowgo.com` / `send4fun.com` e-card spam inside `enron_clean_500.jsonl`):
- **100% Dual-Analyst Blind Verification**: Unlike a 20% spot check, **100% of the `100` pilot messages** must be independently labeled by two human reviewers on both `(email_phishing_status, injection_status)` without viewing IFSI model outputs.
- **Unsolicited Commercial Spam / Newsletter Rule**: Unsolicited bulk marketing or humor mail lacking credential theft, impersonation, or financial fraud (e.g., `flowgo.com`) must be excluded (`EXCL_NON_PHISH_SPAM`) or labeled `Ambiguous`, **never** forced into `Phishing` or clean corporate `Legitimate`.
- **Ambiguous Quarantine**: Any sample where reviewers disagree without consensus adjudication, or where offline dead links prevent confirming deceptive intent, is assigned `email_phishing_status = "ambiguous"` and excluded from binary Track A accuracy/recall/FPR denominators (reported separately in a quarantine table).

---

## 9. Eight-Gate Pre-Track-A Overlap & Confounding Verification

Before **any** pilot record can graduate to `track_a_pilot_verified.jsonl`, an automated gatekeeper must verify **zero violations** against all local splits (`enron_clean_500`, `clean_split_v1`, `enron_augmented`, `review_seed42`), `rag_index_clean` (`1,321` vectors), all Phase 4–7 evaluation JSONLs, and recovered V1 manifests:

1. **Exact Raw & Body SHA-256 Match** == `0`
2. **NFKC Casefolded Whitespace-Normalized Text Match** == `0`
3. **Word 3-Shingle & 5-Shingle Jaccard Similarity $\ge 0.70$** == `0`
4. **Quoted-Reply Substring Containment**: Zero contiguous $\ge 15$-token spans shared with any message in `enron_clean_500.jsonl` or `rag_index_clean` (blocks cross-custodian forwarded chain leakage).
5. **Thread Subject-Stem & `In-Reply-To`/`References` Disjointness**: Zero normalized subject-stem or `Message-ID` overlap with `enron_clean_500.jsonl` (`493` stems) or historical benchmarks.
6. **Correspondent-Graph Disjointness (Enron)**: Zero overlap with any sender/recipient email address present in `blair-l`.
7. **FAISS Dense Cosine Similarity Check**: Compute `all-MiniLM-L6-v2` cosine similarity against all `1,321` `rag_index_clean` vectors; reject any candidate with $\cos > 0.90$.
8. **Source-Confound Audit**: Measure metadata/format-only classifier balanced accuracy per [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml) before authorizing any scale-up beyond `N = 50`.

