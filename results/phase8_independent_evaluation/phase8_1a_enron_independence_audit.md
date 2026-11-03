# Phase 8.1A: Enron Email Corpus — Historical Data Independence Audit

## 1. Executive Summary & Independence Verdict

This document reports a read-only forensic independence audit of the **Enron Email Corpus** (`https://www.cs.cmu.edu/~enron/`) against all locally available IFSI training splits, RAG retrieval indices, processed corpora, manifests, and historical evaluation benchmarks.

### Overall Enron Independence Status: **NOT INDEPENDENT AT CORPUS/DOMAIN LEVEL; UNRESOLVED AT MESSAGE/THREAD LEVEL**

1. **Corpus-Level & RAG Retrieval Independence — COMPROMISED (FAILS EXTERNAL INDEPENDENCE)**:
   - The frozen **Clean FAISS Index** ([`results/rag_index_clean/index.faiss`](file:///d:/Project/IFSI-for-phishing-email-detection/results/rag_index_clean/index.faiss) and [`results/rag_index_clean/metadata.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/rag_index_clean/metadata.json), `1,321` vectors total) actively used at inference time by both **Config A** and **Config B** embeds **`369` Enron records** (`27.93%` of the entire retrieval bank), including **`344` `@enron.com` sender records**.
   - Consequently, **no newly extracted Enron email can ever constitute an unseen external organization or source-independent corpus** for IFSI. At best, additional Enron emails from disjoint custodians represent *within-corpus unseen-mailbox holdout* rather than independent cross-domain generalization.
2. **Message-Level & Thread-Level Independence — UNRESOLVED (MISSING RAW & V1 ARTIFACTS)**:
   - While `500` locally stored Enron records exist in [`data/processed/enron_ingested/enron_clean_500.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/processed/enron_ingested/enron_clean_500.jsonl), neither the raw CMU archive (`data/raw/enron/enron_mail_20150507.tar.gz`) nor the legacy V1 cross-dataset split (`../v1/data/processed/nazario_enron/nazario_enron_test.jsonl`, `441` Enron messages) is present locally.
   - Therefore, exact message, normalized text, near-duplicate, and thread independence between any newly proposed Enron candidates and the missing `441`-record V1 Enron test set **cannot be established yet**.

---

## 2. Complete Inventory of Enron Occurrences Across the Repository

Read-only inspection of all files under `data/`, `results/`, `experiments/`, `tools/`, and `src/` identified **seven** distinct Enron footprints:

| Artifact / Split | File Path | SHA-256 (Prefix / Full) | Total Records | Enron Records | Provenance & Nature of Enron Content |
| :--- | :--- | :--- | ---: | ---: | :--- |
| **Ingested Enron Pool** | [`data/processed/enron_ingested/enron_clean_500.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/processed/enron_ingested/enron_clean_500.jsonl) | `e3130630bb0d...` | 500 | **500** | Real CMU Enron messages extracted by [`ingest_enron_corpus.py`](file:///d:/Project/IFSI-for-phishing-email-detection/tools/data/ingest_enron_corpus.py); **100% from single custodian `maildir/blair-l/`**. |
| **Enron-Augmented Train** | [`data/splits/enron_augmented/train.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/splits/enron_augmented/train.jsonl) | `9dbe7db6236d...` | 1,000 | **500** | Exact `500` records from `enron_clean_500.jsonl` paired with `500` synthetic `seed_splits.py` phishing templates. |
| **Legacy Enron RAG Index** | [`results/rag_index_enron/metadata.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/rag_index_enron/metadata.json) | `fd3a888b0d0a...` | 1,000 | **500** | FAISS index over `enron_augmented/train.jsonl` (`500` Enron vectors). |
| **Clean Split V1 (Train / Val / Test)** | [`data/splits/clean_split_v1/`](file:///d:/Project/IFSI-for-phishing-email-detection/data/splits/clean_split_v1/MANIFEST.json) | `2f5e3d7e6300...` / `f21a88394001...` / `412a1258b9e7...` | 1,628 | **500** (`369` train, `71` val, `60` test) | Partition of all `500` `enron_clean_500.jsonl` records via [`build_clean_reproducible_split.py`](file:///d:/Project/IFSI-for-phishing-email-detection/tools/data/build_clean_reproducible_split.py). |
| **Active Protected Clean FAISS Index** | [`results/rag_index_clean/metadata.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/rag_index_clean/metadata.json) | `4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece` | 1,321 | **369** | **Active production/candidate RAG bank** (`344` `@enron.com` + `25` external senders to `blair-l`). |
| **Historical V1 Cross-Dataset Split (ABSENT LOCALLY)** | Referenced in [`data/metadata/source_manifest.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/source_manifest.json) & [`preparation_report.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/preparation_report.json) | `c11219516b077169937ea29cc87240bc19ec5f515d06acb4b25bf1922d33d887` | 882 | **441** | Extracted from `enron_mail_20150507.tar.gz` (`b3da1b3f...`); files at `../v1/data/...` and `data/processed/nazario_enron_reused/` are **not present on disk**. |
| **Synthetic Benchmark Provenance Tags** | [`a1_generalization_v1.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/a1_generalization_v1.jsonl) & [`phase5_regression_160.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/phase5_regression_160.jsonl) | `ab602982e740...` / `325bf42f2441...` | 500 / 160 | `13` / `3` (tag only) | Synthetically generated templates in [`ordinary_legitimate.py`](file:///d:/Project/IFSI-for-phishing-email-detection/tools/dataset_builder/ordinary_legitimate.py) (`@enterprise-corp.com`, `@global-logistics.org`) carrying `"source_dataset": "Enron Clean Research Archive"`—zero actual Enron text. |

---

## 3. Forensic Characterization of Local Enron Records (`enron_clean_500.jsonl`)

Inspection of all `500` local Enron records reveals acute concentration, residual spam contamination, and multi-message thread clustering:

1. **Single-Custodian Concentration (`100%` `blair-l`)**:
   - Because [`ingest_enron_corpus.py`](file:///d:/Project/IFSI-for-phishing-email-detection/tools/data/ingest_enron_corpus.py) iterated sequentially over `enron_mail_20150507.tar.gz` and halted at `--limit 500`, **all `500 / 500` (`100.0%`) local Enron messages come from a single custodian**: **Lynn Blair (`maildir/blair-l/*`)**, Director of Gas Logistics (Northern Natural Gas / Transwestern Pipeline).
   - Top folders: `blair-l/inbox` (`275`), `blair-l/customer___oneok` (`42`), `blair-l/meetings` (`27`), `blair-l/meetings___nng_customer_mtg` (`18`), `blair-l/itinerary_off_duty` (`15`), `blair-l/meetings___general` (`15`), `blair-l/dra_info` (`14`), `blair-l/customer___virginia_power_dominion` (`10`), `blair-l/presentations` (`10`), `blair-l/vacations_2001` (`9`).
2. **Sender Domain & Bulk/Joke Mail Contamination**:
   - `471 / 500` (`94.2%`) use `@enron.com` (plus `1` `@mailman.enron.com`); `28 / 500` (`5.6%`) come from `15` external domains (`pge.com: 10`, `dom.com: 2`, `southerngas.org: 2`, `flowgo.com: 2`, `send4fun.com: 2`, `oneok.com: 1`, `socalgas.com: 1`, `reliantenergy.com: 1`, `midamerican.com: 1`, `quickinspirations.com: 1`, `coair.rsc01.com: 1`, `mail.ev1.net: 1`, `real-net.net: 1`).
   - Crucially, at least **`5` messages** (`flowgo.com`, `send4fun.com`, `quickinspirations.com`) are external consumer e-card/humor bulk mailers automatically labeled `legitimate` solely because they resided in an Enron inbox.
3. **High Internal Thread Multiplicity & Proven Cross-Split Thread Leakage**:
   - Stripping `RE:` / `FW:` / `FWD:` prefixes reveals **`46` multi-message subject-stem threads accounting for `113 / 500` (`22.6%`)** of `enron_clean_500.jsonl` (e.g., `'northern v. oneok'`: `7` messages; `'gas logistics presentation'`: `4`; `'pipeline interconnect forum information'`: `4`).
   - Even after [`build_clean_reproducible_split.py`](file:///d:/Project/IFSI-for-phishing-email-detection/tools/data/build_clean_reproducible_split.py) applied sender-grouped splitting and `0.85` MinHash Jaccard deduplication on `clean_split_v1`, **`17` Enron subject-stem threads still leaked across splits**:
     - **`13` stems shared between `train` (Clean FAISS Index) and `val`**: including `'northern v. oneok'`, `'demarc allocation conference call - 11/06/01'`, `'gas logistics presentation'`, `'fyi - 637 imbal mtg'`, `'meeting on gas quality'`, `'job duties'`, `'org charts'`.
     - **`4` stems shared between `train` (Clean FAISS Index) and `test`**: `'account receivables'`, `'business objects training'`, `'mt. jesus condensate'`, and `'nng letter asking for written clarifications'`.
   - *Implication for Phase 8*: Sampling a different Enron custodian (e.g., `lokey-t`, `corman-s`, `fossum-d`, or any ETS/NNG colleague who corresponded with Lynn Blair) without **cross-custodian thread, `Message-ID`, quoted-reply, and correspondent-graph exclusion** will leak verbatim reply chains already indexed in `rag_index_clean`!

---

## 4. Exact Overlap Checks Performed Locally

All `500` local Enron messages (`enron_clean_500.jsonl`, containing all `369` Clean FAISS Enron exemplars plus the `131` `val`/`test` Enron records) were compared against every local split and evaluation dataset across **six** criteria:
1. **Exact Body SHA-256** (`exact_sha256`)
2. **Normalized Text** (`NFKC` + `casefold` + collapsed whitespace over body and `Subject + From + Body`)
3. **Near-Duplicate Shingle Jaccard** (3-word shingle Jaccard $\ge 0.70$)
4. **Exact Sender Address** (`sender`)
5. **Corporate Root Domain** (`@enron.com` in sender)
6. **Thread Subject-Stem** (normalized subject after recursive `RE:/FW:/FWD:` stripping)

| Local Dataset / Split Inspected | Total $N$ | Exact Body SHA-256 | Normalized Body Match | 3-Shingle Jaccard $\ge 0.70$ | Exact Sender Overlap | `@enron.com` Sender | Subject-Stem Overlap |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [`data/splits/clean_split_v1/train.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/splits/clean_split_v1/train.jsonl) (**= Clean FAISS Index**) | 1,321 | **369** | **369** | **369** | **369** | **344** | **362** |
| [`data/splits/clean_split_v1/val.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/splits/clean_split_v1/val.jsonl) | 134 | **71** | **71** | **71** | **71** | **68** | **71** |
| [`data/splits/clean_split_v1/test.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/splits/clean_split_v1/test.jsonl) | 173 | **60** | **60** | **60** | **60** | **60** | **60** |
| [`data/splits/enron_augmented/train.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/splits/enron_augmented/train.jsonl) | 1,000 | **500** | **500** | **500** | **500** | **471** | **493** |
| [`data/splits/review_seed42/train.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/splits/review_seed42/train.jsonl) | 1,000 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/splits/review_seed42/val.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/splits/review_seed42/val.jsonl) | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/splits/review_seed42/test.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/splits/review_seed42/test.jsonl) | 522 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/diagnostic_suite.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/diagnostic_suite.json) | 20 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/evaluation/heldout_benchmark_v1.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/heldout_benchmark_v1.jsonl) | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/evaluation/live_benchmark_v1.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/live_benchmark_v1.jsonl) | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/evaluation/live_benchmark_v2.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/live_benchmark_v2.jsonl) | 150 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/evaluation/a1_generalization_v1.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/a1_generalization_v1.jsonl) | 500 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/evaluation/phase5_regression_160.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/phase5_regression_160.jsonl) | 160 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/evaluation/phase6_domain_challenge.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/phase6_domain_challenge.jsonl) | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| [`data/evaluation/phase7_precision_challenge.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/phase7_precision_challenge.jsonl) | 40 | 0 | 0 | 0 | 0 | 0 | 0 |

---

## 5. Overlap Checks NOT Possible Locally (Blocking Full Independence Certification)

1. **Candidate Pool vs. Upstream CMU Tarball (`data/raw/enron/` Missing)**:
   - `data/raw/` does not exist in the workspace, and Phase 8.1A prohibits downloading `enron_mail_20150507.tar.gz`. Thus, candidate unseen custodians cannot yet be screened for cross-mailbox forwarded/quoted overlap against `blair-l`.
2. **Candidate Pool vs. Historical V1 `nazario_enron` Split (`441` Enron Records Missing)**:
   - [`data/metadata/source_manifest.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/source_manifest.json) and [`data/metadata/preparation_report.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/metadata/preparation_report.json) document `441` Enron legitimate messages in `../v1/data/processed/nazario_enron/nazario_enron_test.jsonl` (SHA-256 `c11219516b077169937ea29cc87240bc19ec5f515d06acb4b25bf1922d33d887`) and `data/processed/nazario_enron_quality_seed_42/selected_original_ids.json`—neither of which is present on disk. Without those `441` `original_id` paths or message hashes, independence from historical V1/V2 PhishBench evaluations **cannot be verified**.
3. **Dense FAISS Retrieval Shortcut & Source-Label Confounding**:
   - Because `369` Enron messages already populate `rag_index_clean` (all labeled `legitimate`), top-3 Stage 2 RAG retrieval on new `@enron.com` emails will systematically retrieve `@enron.com` legitimate exemplars, creating an architectural in-domain shortcut. Moreover, pairing `1,000` Enron legitimate emails against `1,000` Nazario phishing emails creates a **100% source-label confound** (`enron -> legitimate`, `nazario -> phishing`), violating this repository's own [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml) (`maximum_source_fraction: 0.40`, `source_only_balanced_accuracy_max: 0.65`).

