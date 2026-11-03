# Phase 8.1B: Revised Source-Diverse Track A Design (`N = 800` Primary Evaluation Corpus)

## 1. Design Summary & Why Track A Is Sized at `N = 800` (Not `2,000`)

Because Enron and Jose Nazario remain on Phase 8.1A hold and composite CSV mirrors (`Zenodo 8339691`, `MeAJOR`, `IWSPA`) are disqualified for contamination and stripped headers, Track A is redesigned from scratch around **five genuinely independent, raw RFC 822 sources** with **zero prior IFSI usage**.

Rather than inflating Track A to `2,000` messages by relaxing deduplication, mixing generic spam into phishing, or over-sampling open-source mailing lists, Phase 8.1B establishes a **scientifically defensible `N = 800` Track A Evaluation Corpus (`400` Legitimate + `400` Phishing)**—backed by a disjoint **`N = 200` Validation/Calibration Partition (`100` Legitimate + `100` Phishing)** used exclusively to run [`confounding_audit.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/tools/diagnostics/confounding_audit.py) and parser/canonicalizer checks without touching test metrics.

### Verification Against `config/dataset_gates.yaml` (Zero Silent Relaxations)
- **`maximum_source_fraction: 0.40`** $\rightarrow$ **PRESERVED**: Largest source is **`30.0%`** (`240 / 800`), `10` percentage points below the `40.0%` cap.
- **`minimum_test_records_per_class: 300`** $\rightarrow$ **PRESERVED**: `400` Legitimate ($\ge 300$) and `400` Phishing ($\ge 300$).
- **`minimum_validation_records_per_class: 100`** $\rightarrow$ **PRESERVED**: Disjoint `100` Legitimate + `100` Phishing preflight/confounding validation slice (`N_val = 200`, same source proportions).
- **`minimum_minority_fraction: 0.20`** $\rightarrow$ **PRESERVED**: Exact `50.0% / 50.0%` class balance (`0.50 >= 0.20`).

---

## 2. Proposed Track A Source Allocation (`N = 800` Test + `N = 200` Disjoint Validation)

| Source ID | Candidate Corpus | Era & Wire Format | Test Legitimate | Test Phishing | Test Total ($N=800$) | Source Share ($\le 40\%$) | Disjoint Val ($N=200$) | Primary Evaluation Role & Metric Policy |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| **`trecc07p_dual`** | **NIST/Waterloo TREC 2007 (`trecc07p`)** (`plg.uwaterloo.ca/~gvcormac/treccorpus07/`) | `2007` Live-MTA raw RFC 822 | **120** | **120** *(hand-verified phish from `spam`)* | **240** | **`30.0%`** | `60` (`30`L / `30`P) | **De-Confounded Dual-Class Anchor** (`metrics_policy: "full"` — `BA_source = 0.50`, identical receiving server across classes) |
| **`phishing_pot`** | **`rf-peixoto/phishing_pot`** (`github.com/rf-peixoto/phishing_pot`) | `2022–2025` Honeypot `.eml` (`SPF/DKIM/DMARC`) | 0 | **180** | **180** | **`22.5%`** | `45` (`0`L / `45`P) | **Contemporary Credential & Cloud Phishing** (`metrics_policy: "recall_only"` per-source + contemporary slice) |
| **`ietf_mailarchive`** | **IETF Public Mail Archive** (`mailarchive.ietf.org`) | `2021–2025` Multi-org `.mbox` (`DKIM/ARC`) | **160** | 0 | **160** | **`20.0%`** | `40` (`40`L / `0`P) | **Contemporary Multi-Enterprise Legitimate** (`metrics_policy: "fpr_only"` per-source; max `3` msgs/domain, `1`/thread) |
| **`asf_lists_mbox`** | **Apache Software Foundation Archives** (`lists.apache.org`) | `2021–2025` Governance/ops `.mbox` (`SPF/DKIM`) | **120** | 0 | **120** | **`15.0%`** | `30` (`30`L / `0`P) | **Contemporary Org/Security Operations Legitimate** (`metrics_policy: "fpr_only"` per-source; human mail only, zero CI bots) |
| **`untroubled_phish`** | **`Untroubled.org` Bait Sinkhole** (`untroubled.org/spam/`) | `2022–2025` Raw RFC 822 (`.7z`) | 0 | **100** *(hand-verified phish)* | **100** | **`12.5%`** | `25` (`0`L / `25`P) | **Contemporary Independent Sinkhole Phishing** (`metrics_policy: "recall_only"` per-source; `<5%` phish extracted from spam) |
| **TOTAL** | **5 Independent Real-Email Sources** | **Raw RFC 822 / `.eml` / `.mbox`** | **400 (`50.0%`)** | **400 (`50.0%`)** | **800** | **`100.0%` (Max `30.0%`)** | **200 (`100`L / `100`P)** | **Zero IFSI Overlap; Source-Separated + Dual-Class Reporting** |

### Optional Enterprise Substitution (If Institutional LDC License Is Executed)
If the research team holds or acquires an institutional **Linguistic Data Consortium** license for **Avocado (`LDC2015T03`)**, `80` records from `ietf_mailarchive` and `40` records from `asf_lists_mbox` may be replaced by **`120` `avocado_enterprise` messages (`15.0%`)** sampled across disjoint corporate finance, HR, legal, and vendor-management accounts, adding private non-mailing-list enterprise correspondence while keeping every source $\le 30.0\%$.

---

## 3. Anti-Confounding Header Canonicalization & Source-Level Reporting Protocol

### 3.1 Symmetric Envelope Canonicalization (Without Fabricating Headers)
As proven by [`confounding_audit.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/tools/diagnostics/confounding_audit.py), raw mailing-list headers (`List-Id:`, `List-Unsubscribe:`, `Archived-At:`) on `ietf_mailarchive`/`asf_lists_mbox` and honeypot recipient headers (`To: phishing@pot`, bait `Delivered-To:`) on `phishing_pot`/`untroubled_phish` would create trivial format shortcuts. Therefore, Tier 2 sanitization applies **strictly subtractive/masking canonicalization** symmetrically across all 5 sources (logged byte-for-byte in `transformation_log.jsonl`, while unmodified headers remain in Tier 1 `data/raw/`):
1. Strip mailing-list transport metadata headers (`List-*`, `Mailing-List:`, `Precedence: list`, `X-BeenThere:`, `Archived-At:`) and leading `[list-tag]` subject brackets.
2. Mask recipient-identifying headers (`To:`, `Cc:`, `Delivered-To:`, `X-Original-To:`, and recipient clauses inside topmost `Received:` hops) uniformly to `<REDACTED_RECIPIENT>` across all 5 sources.
3. **Never fabricate missing headers** and **preserve `From:`, `Sender:`, `Reply-To:`, `Return-Path:`, `Subject:`, `Date:`, `Message-ID:`, `Authentication-Results:`, `Received-SPF:`, `DKIM-Signature:`, and body URLs intact**.
4. **Hard Preflight Gate**: On the `N = 200` validation slice, [`confounding_audit.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/tools/diagnostics/confounding_audit.py) must confirm `format_only_balanced_accuracy <= 0.85` and `full_minus_format_balanced_accuracy >= 0.05` (and `held_out_source` `source_only_balanced_accuracy == 0.50 <= 0.65` against `clean_split_v1`) before freezing the `N = 800` test set.

### 3.2 Mandatory Multi-View Reporting Hierarchy
To prevent residual single-class source differences (`2007` vs `2022–2025`, mailing-list prose vs consumer/enterprise phishing lures) from masquerading as model generalization, Track A results must always be reported in **three mandatory tables**:
1. **Table A-1 (Unconfounded Single-MTA Dual-Class Benchmark — `trecc07p_dual`, `N = 240`)**: Full binary metrics (`Accuracy`, `Phishing Recall`, `Legitimate FPR`, `Precision`, `MCC`, paired McNemar $p$-value, 95% Wilson CIs) where `source_only_balanced_accuracy == 0.50`.
2. **Table A-2 (Per-Source Slice Matrix Across All 5 Sources)**:
   - `ietf_mailarchive` (`N = 160`): Legitimate **FPR** + 95% Wilson CI (and Domain Analyzer V3 domain-flag rate).
   - `asf_lists_mbox` (`N = 120`): Legitimate **FPR** + 95% Wilson CI.
   - `phishing_pot` (`N = 180`): Phishing **Recall** + 95% Wilson CI (stratified by credential harvester vs brand impersonation vs attachment/invoice lure).
   - `untroubled_phish` (`N = 100`): Phishing **Recall** + 95% Wilson CI.
3. **Table A-3 (Pooled Track A Summary, `N = 800`)**: Reported *only alongside Tables A-1 and A-2* with explicit disclosure of the `70%` single-class source share (`in-Track-A BA_source = 0.85`, `held-out-from-train BA_source = 0.50`).

---

## 4. Independent Labeling, Spam Exclusion & Ambiguous-Message Quarantine

1. **100% Dual-Analyst Blind Annotation**: Every candidate record across all 5 sources (`800` test + `200` val = `1,000` records) is independently annotated by two human reviewers on `(email_phishing_status, injection_status)` **without access to IFSI Config A/B predictions**. Required agreement: **Cohen's $\kappa \ge 0.85$**.
2. **Strict `Phishing != Spam` Enforcement (`trecc07p` & `untroubled` Critical Rule)**:
   - Unsolicited commercial bulk mail, newsletters, adult/pharmacy ads, and SEO spam lacking deceptive identity spoofing, credential harvesting, or fraudulent financial/action inducement (`docs/V2_RESEARCH_SPEC_ZH.md` §2.2) **must be rejected (`EXCL_NON_PHISH_SPAM`)**, never labeled `phishing` or `legitimate`.
3. **Explicit `Ambiguous` Quarantine**:
   - Messages where dead historical links or truncated context prevent confirming deceptive intent, or where dual annotators + lead adjudicator cannot reach high-confidence consensus, are labeled `email_phishing_status = "ambiguous"`, stored in `data/evaluation/phase8/track_a_ambiguous_quarantine.jsonl`, **excluded from binary Recall/FPR denominators**, and reported in a dedicated prediction-distribution audit table.

---

## 5. Contamination Screening, Storage, Provenance & PII Controls

1. **Three-Tier Local-Only Git-Ignored Storage (`redistribution_allowed: false`)**:
   - Tier 1 Immutable Raw: `data/raw/phase8_track_a/<source>/` (pinned commit/archive SHA-256; read-only).
   - Tier 2 Sanitized & Canonicalized: `data/processed/phase8_track_a_sanitized/` + `transformation_log.jsonl` + `exclusion_log.jsonl`.
   - Tier 3 Frozen Evaluation Ready: `data/evaluation/phase8/track_a_real_emails_800.jsonl` (git-ignored) + public hash-only manifest `results/phase8_independent_evaluation/track_a_manifest.sha256` recording `{record_id, source, upstream_archive_sha256, source_member_id, raw_rfc822_sha256, sanitized_sha256}`.
2. **Malware & PII Safety Rules**:
   - Strip all binary/executable MIME attachments (`.exe`, `.iso`, `.zip`, `.htm` attachments, macros) in an isolated parser pass without executing or rendering external resources.
   - Mask phone/fax numbers (`[PHONE_REDACTED]`), SSNs/payment cards/account numbers (`[FINANCIAL_PII_REDACTED]`), and street addresses (`[ADDRESS_REDACTED]`) while preserving sender/reply-to/URL domain tokens.
3. **Eight-Gate Zero-Contamination Check**:
   - Reject any candidate failing exact SHA-256, NFKC normalized text, 3-shingle/5-shingle Jaccard $\ge 0.70$ (both against all IFSI historical splits/benchmarks **and** across the 5 Track A sources themselves, max `2` samples per phishing campaign cluster, max `1` sample per mailing-list thread), `>= 15`-token quoted-reply overlap, or `all-MiniLM-L6-v2` cosine similarity $> 0.90$ against [`results/rag_index_clean/index.faiss`](file:///d:/Project/IFSI-for-phishing-email-detection/results/rag_index_clean/index.faiss).

---

## 6. Strict Preservation of Track B Separation

Per [`phase8_1a_track_b_clarifications.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1a_track_b_clarifications.md), Track B remains completely separate in storage, schema, execution reporting, and scientific claims:
- **Track B1 (`N = 800` Controlled Email Challenges)**: `synthetic_email_envelope` and `adapted_email_example` items (`is_email: true`) testing modern multi-tenant SaaS false-positive traps (`Workday`, `Okta`, `AWS`), zero-link executive BEC, lookalike domains, and in-email active/quoted prompt injections.
- **Track B2 (`N = 200` Standalone Non-Email Documents)**: `standalone_non_email_document` research papers, CVE advisories, and raw injection payloads (`is_email: false`, `header_origin: "none"`, **never** given fabricated email headers, and **never** included in email classification metrics).
- **Binding Firewall**: Track B1 and Track B2 metrics must **never** be combined with Track A real-email metrics.

