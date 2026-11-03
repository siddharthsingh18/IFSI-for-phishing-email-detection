# Phase 8.1B: Final Governance Decision & Track A Redesign Authorization Status

## 1. Formal Phase 8.1B Decision

Out of the three permitted governance outcomes specified for Phase 8.1B:
- *A feasible, source-diverse Track A design exists and is ready for a separate acquisition preflight.*
- *A smaller Track A design is feasible, but 2,000 independent messages are not currently justified.*
- *No defensible Track A design is currently feasible.*

**Selected Verdict:**

> **`A smaller Track A design is feasible, but 2,000 independent messages are not currently justified.`**

---

## 2. Scientific & Legal Rationale for This Verdict

1. **Why a Defensible Smaller Track A (`N = 800` Test + `N = 200` Disjoint Validation) Is Feasible**:
   - Five genuinely independent, raw RFC 822 / `.eml` / `.mbox` real-email sources with **zero prior IFSI training, RAG, or benchmark overlap** have been identified and audited (`APPROVED FOR FURTHER REVIEW`):
     1. **`trecc07p_dual`** (`https://plg.uwaterloo.ca/~gvcormac/treccorpus07/`) — **`240` test (`120` Legit + `120` verified Phish) = `30.0%`** (+ `60` val): single-MTA dual-class de-confounding anchor (`BA_source = 0.50`).
     2. **`phishing_pot`** (`https://github.com/rf-peixoto/phishing_pot`) — **`180` test (`0` Legit + `180` Phish) = `22.5%`** (+ `45` val): contemporary `2022–2025` wire `.eml` captures (`SPF/DKIM/DMARC`, `CC BY-NC 4.0`).
     3. **`ietf_mailarchive`** (`https://mailarchive.ietf.org/`) — **`160` test (`160` Legit + `0` Phish) = `20.0%`** (+ `40` val): contemporary `2021–2025` multi-enterprise correspondence (`DKIM/ARC`, IETF Note Well / TLP).
     4. **`asf_lists_mbox`** (`https://lists.apache.org/`) — **`120` test (`120` Legit + `0` Phish) = `15.0%`** (+ `30` val): contemporary `2021–2025` human organizational/security-ops mail (`SPF/DKIM`, ASF Public Forum Policy).
     5. **`untroubled_phish`** (`http://untroubled.org/spam/`) — **`100` test (`0` Legit + `100` verified Phish) = `12.5%`** (+ `25` val): independent bait sinkhole RFC 822 phishing (`2022–2025`, explicit R&D permission notice).
   - **Every gate in [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml) is preserved without silent relaxation**:
     - `maximum_source_fraction: 0.40` $\rightarrow$ **Preserved** (`max = 30.0%`).
     - `minimum_test_records_per_class: 300` $\rightarrow$ **Preserved** (`400` Legitimate, `400` Phishing).
     - `minimum_validation_records_per_class: 100` $\rightarrow$ **Preserved** (`100` Legitimate, `100` Phishing).
     - `minimum_minority_fraction: 0.20` $\rightarrow$ **Preserved** (`0.50`).

2. **Why `2,000` Independent Messages Are Not Currently Justified**:
   - No open-access, license-clear, modern private enterprise mailbox dataset exists to replace Enron (`Avocado LDC2015T03` requires a paid `~$2,000–$3,000` LDC license and lacks SMTP/DKIM headers; scaling `IETF` + `ASF` public mailing lists to `1,000` ham degrades enterprise construct validity).
   - Genuine phishing represents `<5%` of `trecc07p` and `untroubled.org` spam streams and suffers `5x–15x` phish-kit campaign deduplication collapse; forcing `1,000` unique-campaign phishing records without Nazario or contaminated Zenodo/Kaggle CSV composites would either require manual dual-review of `~20,000–30,000+` raw spam emails or tempt silent relaxation of `phishing != spam` and `0.70` shingle-deduplication gates.
   - Zero open raw-`.eml` Business Email Compromise (BEC) corpora exist publicly outside closed NDAs (`APWG eCX`).
   - Per IFSI research governance, **a smaller, rigorously de-duplicated, dual-annotated `800`-message Track A benchmark is scientifically superior to an inflated `2,000`-message corpus compromised by mailing-list skew, spam mislabeling, or campaign duplication**.

---

## 3. Preservation of Prior Holds & Track B Firewall

1. **Phase 8.1A Holds Preserved Unmodified**:
   - **Enron Email Corpus** (`https://www.cs.cmu.edu/~enron/`) and **Jose Nazario Phishing Corpus** (`https://monkey.org/~jose/phishing/`) remain **ON ACQUISITION HOLD** and **EXCLUDED** from Track A. All six Phase 8.1A audit documents (`phase8_1a_*.md`) remain untouched.
   - Reconsideration of Enron (solely as a non-independent unseen-custodian side-slice) or post-2020 Nazario annual `.mbox` files would require the exact legal sign-offs, upstream `LICENSE.txt` hash verifications, and V1 `nazario_enron` ID recoveries documented in [`phase8_1a_final_decision.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1a_final_decision.md).
2. **Track B Separation Preserved**:
   - **Track B1** (`N = 800` synthetic and adapted email challenges: modern multi-tenant SaaS headers, zero-link BEC, lookalike domains, in-email active/quoted prompt injections) and **Track B2** (`N = 200` standalone non-email documents and injection stress tests, `is_email: false`, never wrapped in fabricated email headers) remain strictly segregated in files, schemas, and metrics from **Track A** (`N = 800` real emails).

---

## 4. Mandatory Prerequisites Before Any Data Acquisition (Phase 8.1C Gate)

**`APPROVED FOR FURTHER REVIEW` is NOT authorization to download email archives.** No email bytes may be fetched until a dedicated **Phase 8.1C Acquisition Preflight** completes all five steps below:

1. **Metadata-Only License & Policy Capture**: Fetch and record verbatim text + SHA-256 hashes of *only* the upstream license/policy documents (`phishing_pot` `LICENSE` at pinned commit; `untroubled.org/spam/` R&D notice; Waterloo `trecc07p` usage agreement; IETF Note Well / `mailarchive` export terms; ASF Public Forum Archive Policy), and confirm institutional acceptance of `CC BY-NC 4.0` and TREC non-commercial research terms.
2. **Local-Only Git-Ignored Storage Verification**: Confirm `.gitignore` blocks `data/raw/`, `data/processed/`, `data/evaluation/phase8/*.jsonl`, `*.eml`, `*.mbox`, `*.tgz`, and `*.7z`, enforcing `redistribution_allowed: false` across all 5 sources per [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md).
3. **Sandboxed `25`-Sample/Source Dry-Run Pilot (`125` Messages)**: Verify attachment stripping (zero execution of `.exe`/`.iso`/`.zip`/HTML scripts), intact `From:`/`Reply-To:`/`Received:`/`SPF`/`DKIM` parsing, symmetric `List-*` stripping, and `<REDACTED_RECIPIENT>` normalization.
4. **Validation-Slice Confounding Gate (`N_val = 200`)**: Execute [`confounding_audit.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/tools/diagnostics/confounding_audit.py) on the disjoint `200`-record validation slice and verify `format_only_balanced_accuracy <= 0.85`, `full_minus_format_balanced_accuracy >= 0.05`, and `held_out_source` `source_only_balanced_accuracy == 0.50 <= 0.65`.
5. **Dual-Analyst Blind Annotation & Zero-Contamination Audit**: Require Cohen's $\kappa \ge 0.85$, strict rejection of non-phishing commercial spam (`EXCL_NON_PHISH_SPAM`), quarantine of `ambiguous` items outside binary denominators, and `0` matches across exact SHA-256, `0.70` shingle Jaccard, and `0.90` FAISS cosine similarity against `rag_index_clean`.

