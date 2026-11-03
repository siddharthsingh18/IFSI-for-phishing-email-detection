# Phase 8.1A: Final Preflight & Source Independence Decision

## 1. Formal Acquisition Decision

> **Neither source cleared for acquisition.**

*(Selected conservatively from the three authorized Phase 8.1A dispositions: `Both sources conditionally cleared for a limited pilot.` | `Only one source conditionally cleared for a limited pilot.` | **`Neither source cleared for acquisition.`**)*

This decision **supersedes and places an immediate governance hold** on the earlier Phase 8.0.1 authorization (`phase8_1_readiness_decision.md`) prior to any dataset download, scraping, or ingestion.

---

## 2. Separated Three-Axis Determination per Source

Per Phase 8.1A governance rules, **Legal Clearance**, **Technical Suitability**, and **Independence Status** are evaluated as three distinct, non-interchangeable decisions for each corpus:

| Decision Axis | Enron Email Corpus (`https://www.cs.cmu.edu/~enron/`) | Jose Nazario Phishing Corpus (`https://monkey.org/~jose/phishing/`) |
| :--- | :--- | :--- |
| **1. Legal Clearance** | **UNRESOLVED (No Explicit License; Redistribution Prohibited)**<br>• Publicly available via CMU & entered into public record by FERC (`PA02-2-000` / `EL02-111`), **not** statutory public domain (`17 U.S.C. § 105` inapplicable to private employee/third-party writings).<br>• Zero explicit SPDX/open reuse license exists on CMU's site; [`data/manifests/enron.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/enron.json) sets `"redistribution_allowed": false`.<br>• Local-only research evaluation is plausible only under U.S. fair use (`17 U.S.C. § 107`) + [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md) non-redistribution, requiring explicit researcher/institutional sign-off and upgraded PII exclusion (`23.6%` unredacted phone numbers and HR promotion tables found in `enron_clean_500.jsonl`). | **UNRESOLVED (Upstream `LICENSE.txt` Unverified Locally; Redistribution Prohibited)**<br>• Upstream directory contains `LICENSE.txt` (~18 KB) and `README.txt` (~961 B), which could **not** be downloaded during Phase 8.1A.<br>• An informal academic release is not an explicit license, and Dr. Nazario does not hold third-party sender or spoofed-brand HTML/logo copyrights; [`data/manifests/nazario.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/nazario.json) sets `"license": "Source terms; verify"` and `"redistribution_allowed": false`.<br>• Cannot claim legal clearance until `LICENSE.txt` & `README.txt` are directly inspected and hashed. |
| **2. Technical Suitability** | **LIMITED / CONDITIONAL (PST Header Deficits & Confounding)**<br>• Contains real 1999–2002 corporate messages with `From:`, `To:`, `Date:`, `Subject:`, `Message-ID:`.<br>• **Lacks authentic SMTP transport headers** (`Received:`, `Return-Path:`, `SPF/DKIM/DMARC`) and stripped attachments due to Exchange/Notes PST export.<br>• Contains non-business personal folders and bulk humor spam (`flowgo.com`, `send4fun.com`).<br>• Pre-SaaS era cannot test modern cloud auth false positives; pairing 1:1 with Nazario violates [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml) (`maximum_source_fraction: 0.40`). | **CONDITIONAL (Requires HTML-Aware Parser & Honeypot De-Confounding)**<br>• Preserves authentic wire-level RFC 822 headers (`Received:`, `Return-Path:`, `From:`, `Reply-To:`, `Date:`, MIME parts).<br>• Legacy `text/plain`-only parsing caused **`196 / 441` (`44.4%`) empty bodies** (`source_manifest.json`); HTML-aware parsing preserving `<a href>` URLs is mandatory.<br>• Honeypot recipient headers (`To: jose@monkey.org`) create a trivial source-label shortcut unless normalized.<br>• High intra-archive campaign burstiness requires template clustering. |
| **3. Independence Status** | **COMPROMISED AT CORPUS/RAG LEVEL; UNRESOLVED AT MESSAGE LEVEL**<br>• **`369` Enron records (`344` `@enron.com`) are embedded in the active frozen Clean FAISS Index** ([`results/rag_index_clean/index.faiss`](file:///d:/Project/IFSI-for-phishing-email-detection/results/rag_index_clean/index.faiss)). Enron is **not** an external unseen source.<br>• Local `enron_clean_500.jsonl` is `100%` single custodian (`blair-l`) with `46` multi-message threads and `17` split-crossing thread stems in `clean_split_v1`.<br>• Raw tarball and V1 `nazario_enron` (`441` Enron messages, `c1121951...`) are absent locally, so message/thread disjointness against historical V1 runs cannot yet be verified. | **UNRESOLVED (`phishing3.mbox` 100% Exhausted; Raw Archives Absent Locally)**<br>• Historical `phishing3.mbox` (`b29336d2...`, `2,241` usable messages) was **100% consumed** in historical `review_split_seed42` (`1,745+286+210 = 2,241`) and V1 `nazario_enron` (`441`).<br>• Active local `"nazario"` records in `rag_index_clean` (`502`) are `100%` synthetic `seed_splits.py` templates (so modern `.mbox` files avoid active RAG collision), **but** neither `phishing3.mbox`, `nazario_enron`, nor `phishing-2015..2025` is present locally to verify cross-archive duplicate/campaign disjointness. |

---

## 3. Why Conservative Rejection Is Required Now

Under Phase 8.1A rules (*"Do NOT claim that a source is legally cleared without identifiable supporting evidence"*, *"Do NOT classify a corpus as independent merely because it is downloaded again"*, and *"Be conservative. If licensing or independence cannot be established, mark it unresolved rather than assuming approval"*):

1. **Neither source has verified legal clearance on record today**: Enron has no reuse license (requiring explicit fair-use non-redistribution governance approval), and Nazario's upstream `LICENSE.txt` has not yet been inspected under the Phase 8.1A no-download constraint.
2. **Neither source has established full historical data independence today**: Missing local copies of `data/raw/` and historical V1 `nazario_enron` (`c1121951...`) prevent deterministic message/campaign deduplication today; additionally, `phishing3.mbox` is 100% exhausted and Enron is already indexed in `rag_index_clean` (`369` vectors).

---

## 4. Exact Prerequisites to Unlock a Future Stage 8.1B Limited Pilot (`N = 50`)

Acquisition may be reconsidered **only** for the staged `N = 50` pilot defined in [`phase8_1a_acquisition_pilot_plan.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1a_acquisition_pilot_plan.md) if and when the user/project authorizes all four steps below:

1. **Authorize Metadata-Only License Fetch for Nazario**: Permit fetching *only* `https://monkey.org/~jose/phishing/README.txt` and `LICENSE.txt` (zero `.mbox` data) to verify exact license terms and record their SHA-256 digests.
2. **Confirm Local-Only Fair-Use Governance for Enron (or Replace Enron)**: Explicitly sign off on non-redistributed local evaluation (`redistribution_allowed: false` per [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md)) **and** reclassify Enron results as *unseen-custodian intra-corpus holdout* rather than independent external-domain generalization.
3. **Eliminate Single-Source Confounding**: Satisfy [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml) (`maximum_source_fraction: 0.40`) by either adding verified multi-source ham/phish corpora or restricting claims to source-conditioned slice benchmarks with recipient-header normalization.
4. **Enforce Blacklists & 8-Gate Screening**: Permanently blacklist `maildir/blair-l/*` (+ its correspondent/thread graph) and `phishing0.mbox`–`phishing3.mbox`, recover or bound V1 `nazario_enron` IDs, and keep Track B2 standalone documents strictly outside email classification metrics per [`phase8_1a_track_b_clarifications.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1a_track_b_clarifications.md).

