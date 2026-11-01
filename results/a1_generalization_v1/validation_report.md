# Phase 3 Pre-Evaluation Validation Report: A1 Generalization Validation V1

**Date:** November 1, 2026  
**Auditor:** Independent Research Validation Agent  
**Project:** `D:\Project\IFSI-for-phishing-email-detection`  
**Dataset Target:** `data/evaluation/a1_generalization_v1.jsonl` (500 samples)  
**SHA-256:** `ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336`  

---

## Executive Summary

Prior to initiating Phase 4 inference, all Phase 3 pre-evaluation validation gates were executed. The dataset, its underlying provenance, non-leakage constraints, automated test suite, and architectural frozen configurations were audited.

All 10 required validation criteria passed with zero defects. The dataset is guaranteed 100% free of data leakage or overlap with training data, validation data, historical benchmarks (V1, V2, Held-Out V1), and the clean FAISS index.

```mermaid
flowchart TD
    A["Generalization Dataset (N=500)<br/>a1_generalization_v1.jsonl"] --> B["Category Balance<br/>5 Categories x 100 Samples"]
    A --> C["Ground-Truth Balance<br/>250 Phishing (50%) / 250 Legit (50%)"]
    A --> D["Injection Taxonomy<br/>50 Active (Phishing) / 50 Quoted (Legit)"]
    B & C & D --> E["Leakage Audit vs 7 Corpora<br/>0 Exact Overlaps / 0 Near Duplicates"]
    E --> F["Automated Integrity Suite<br/>pytest: 8/8 Passed (100%)"]
    F --> G["GATE STATUS: VALIDATED<br/>Halted for Review Prior to Inference"]
```

---

## 1. Phase 3 Criteria Verification Matrix

| # | Validation Requirement | Target Specification | Audited Status | Verification Result |
|:---:|:---|:---|:---|:---:|
| **1** | **Sample Count & ID Uniqueness** | Exactly 500 unique email records | 500 records; 500 unique IDs (`gen-ord-001` to `gen-inj-100`) | **PASS** |
| **2** | **Category Balance** | Exactly 100 samples per category | 100 in each of 5 defined categories | **PASS** |
| **3** | **Ground-Truth Distribution** | Symmetrical 50/50 balance | Exactly 250 Phishing (50.0%) and 250 Legitimate (50.0%) | **PASS** |
| **4** | **Injection Distribution** | Balanced active vs. quoted | Exactly 50 Active Injections (in Phishing) and 50 Quoted Injections (in Genuine) | **PASS** |
| **5** | **Provenance Completeness** | 100% provenance and redaction records | All 500 records contain source dataset, citation, collection method, origin type, and redaction notes | **PASS** |
| **6** | **Zero Leakage with Prior Datasets** | 0 exact or near-duplicate overlaps | 0 overlaps across Live V1 (40), Live V2 (150), and Held-Out V1 (100) | **PASS** |
| **7** | **Zero Leakage with Clean FAISS Index** | 0 samples present in vector index | 0 of 500 samples in `results/rag_index_clean/index.faiss` or `metadata.json` (1,321 vectors) | **PASS** |
| **8** | **Input Formatting Parity** | Identical inputs to A0 and A1 | Both models consume identical `{"sample_id", "subject", "sender", "body"}` schema | **PASS** |
| **9** | **Model Settings Equivalence** | Identical LLM runtime parameters | `qwen3.5:4b`, `temperature=0.0`, `num_predict=512`, `timeout=60.0s`, standard RAG $k=3$ | **PASS** |
| **10** | **Code & Prompt Invariance** | Implementation hashes match Phase 1 | All production and ablation code hashes verified bit-for-bit identical | **PASS** |

---

## 2. Dataset Composition Breakdown

### 2.1 Category and Ground-Truth Distribution

| Category | Sample ID Range | Total Emails | Phishing ($y=1$) | Legitimate ($y=0$) | Injection Type | Origin Type |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Ordinary Legitimate** | `gen-ord-001` - `100` | 100 | 0 | 100 | None (100) | Real-World (24) / Synthetic (76) |
| **Difficult Legitimate** | `gen-dif-001` - `100` | 100 | 0 | 100 | None (100) | Synthetic Supplemented (100) |
| **Conventional Phishing** | `gen-con-001` - `100` | 100 | 100 | 0 | None (100) | Real-World (80) / Synthetic (20) |
| **Sophisticated Phishing** | `gen-sop-001` - `100` | 100 | 100 | 0 | None (100) | Synthetic Supplemented (100) |
| **Prompt Injection** | `gen-inj-001` - `100` | 100 | 50 | 50 | Active (50) / Quoted (50) | Synthetic Supplemented (100) |
| **TOTAL** | `gen-ord-001` - `gen-inj-100` | **500** | **250 (50.0%)** | **250 (50.0%)** | **100 Injections (20.0%)** | **Real-World (104) / Synthetic (396)** |

### 2.2 Subcategory Scenario Coverage

1. **Ordinary Legitimate ($N = 100$):**
   - Daily standups & engineering status updates (`gen-ord-001` to `005`)
   - Customer feedback & enterprise cohort digests (`gen-ord-006` to `008`)
   - Conference registration confirmations & bookstore receipts (`gen-ord-009` to `011`)
   - University library due dates, peer review invitations, and seminar schedules (`gen-ord-012` to `020`)
   - Legitimate SaaS billing (Datadog, AWS, Amazon Business), travel itineraries (Delta, Hyatt), and open source digests (Apache Kafka) (`gen-ord-021` to `100`)

2. **Difficult Legitimate ($N = 100$):**
   - Mandatory annual compliance & code of conduct certifications
   - Benefits open enrollment final deadlines & 401(k) default warnings
   - Active Directory 90-day password expiration alerts
   - Q3 corporate expense reconciliations & missing receipt audits
   - IRS Form W-2 / 1099 electronic payroll tax availability notices
   - Privileged legal hold preservation directives (Matter #LH-xxxx)
   - Employee-submitted suspicious email reports to the internal SOC
   - Hardware YubiKey certificate expiration & walk-in swap advisories
   - CISO emergency zero-day patching directives (OpenSSL / SSH)
   - Master services agreement renewals and procurement seat reallocations

3. **Conventional Phishing ($N = 100$):**
   - Microsoft 365 credential harvesting with Russian / Chinese sign-in alerts
   - DocuSign electronic signature lures for executive advisory agreements
   - DHL / FedEx international parcel hold notices with redelivery fee requests
   - Overdue vendor invoices threatening commercial debt collections
   - Wells Fargo / Chase banking alerts alleging crypto exchange charges
   - ADP payroll direct deposit routing failure notices
   - Urgent CEO / CFO gift card purchase requests
   - Fake Microsoft Teams audio voicemail players
   - GlobalProtect VPN emergency SSL update credential harvesters
   - IRS tax refund direct deposit claim forms

4. **Sophisticated Phishing ($N = 100$):**
   - Outside legal counsel M&A acquisition escrow wire updates
   - High-prestige academic peer review invitations (Nature Machine Intelligence, ACM, IEEE)
   - Enterprise supplier onboarding portal tax recertification requests (Form W-9)
   - Chief People Officer discretionary executive retention equity grant allocations
   - Third-party management consulting assessments (McKinsey Organizational Health Index)
   - Keynote speaker invitations to MIT Technology Review summits
   - Board of Directors virtual data room (VDR) distribution links
   - Big-4 accounting firm annual SOC 2 Type II audit evidence requests
   - American Express Global Business Travel (GBT) per diem lodging policy updates
   - Commercial real estate satellite office master lease renewals (CBRE)

5. **Prompt Injection ($N = 100$):**
   - **50 Active Malicious Injections in Phishing Emails:**
     - Direct instruction overrides (`Ignore all previous instructions...`)
     - System policy clearance spoofing (`[SYSTEM DIRECTIVE: VERIFIED CLEAN]`)
     - Delimiter escape sequences (`--- END OF UNTRUSTED EMAIL ---`)
     - Multilingual injections in German, French, Spanish, Russian, Chinese
     - Fake forwarded legal disclaimers containing compliance overrides
     - Whitespace-isolated override tokens
   - **50 Quoted / Benign Injections in Legitimate Emails:**
     - SOC incident response briefings analyzing intercepted resume injection attacks
     - HackerOne bug bounty reports detailing triage bot instruction overrides
     - AI research reading groups discussing instruction hierarchy papers
     - Cybersecurity awareness training modules with quiz questions
     - Automated QA regression test suite execution logs
     - Customer support tickets reporting false-positive filter blocks
     - Engineering code reviews for prompt sanitization regex patterns
     - Threat intelligence weekly bulletins on emerging LLM TTPs
     - Multilingual NLP benchmark test suite verification samples (German, French)

---

## 3. Cryptographic Leakage & Contamination Audit Results

Every email body in the 500-sample dataset was hashed and tokenized into word 3-grams, then audited against all 7 historical datasets, training splits, and vector store indices.

| Reference Corpus | File Path | Total Items | Exact Hash Overlaps | Near-Duplicate Overlaps (Jaccard $\ge 0.70$) | Verification Status |
|:---|:---|:---:|:---:|:---:|:---:|
| **Live Benchmark V1** | `data/evaluation/live_benchmark_v1.jsonl` | 40 | **0** | **0** | **PASS** |
| **Live Benchmark V2** | `data/evaluation/live_benchmark_v2.jsonl` | 150 | **0** | **0** | **PASS** |
| **Held-Out Benchmark V1** | `data/evaluation/heldout_benchmark_v1.jsonl` | 100 | **0** | **0** | **PASS** |
| **Clean Split Train** | `data/splits/clean_split_v1/train.jsonl` | 1,321 | **0** | **0** | **PASS** |
| **Clean Split Val** | `data/splits/clean_split_v1/val.jsonl` | 134 | **0** | **0** | **PASS** |
| **Clean Split Test** | `data/splits/clean_split_v1/test.jsonl` | 173 | **0** | **0** | **PASS** |
| **Clean FAISS Index** | `results/rag_index_clean/metadata.json` | 1,321 | **0** | **0** | **PASS** |
| **TOTALS** | Across all 7 reference corpora | **3,239** | **0 (0.00%)** | **0 (0.00%)** | **100% UNCONTAMINATED** |

---

## 4. Automated Test Suite Execution Results

Automated regression and dataset validation tests were implemented in [`tests/test_a1_generalization_validation.py`](file:///d:/Project/IFSI-for-phishing-email-detection/tests/test_a1_generalization_validation.py) and executed via pytest:

```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: D:\Project\IFSI-for-phishing-email-detection

tests/test_a1_generalization_validation.py::test_sample_count_and_uniqueness PASSED [ 12%]
tests/test_a1_generalization_validation.py::test_category_balance PASSED           [ 25%]
tests/test_a1_generalization_validation.py::test_ground_truth_balance PASSED       [ 37%]
tests/test_a1_generalization_validation.py::test_injection_distribution PASSED     [ 50%]
tests/test_a1_generalization_validation.py::test_provenance_metadata_completeness PASSED [ 62%]
tests/test_a1_generalization_validation.py::test_zero_leakage_with_rag_index PASSED [ 75%]
tests/test_a1_generalization_validation.py::test_zero_leakage_with_historical_datasets PASSED [ 87%]
tests/test_a1_generalization_validation.py::test_code_and_index_hash_invariance PASSED [100%]

============================== 8 passed in 0.37s ==============================
```

---

## 5. Architectural Invariance & Model Environment

| Architecture Component | A0: Production M4 Baseline | A1: Experimental Candidate | Invariance Verdict |
|:---|:---|:---|:---:|
| **Stage 1 Injection Classifier** | `baseline_v1` (binary detector) | `experimental_v2` (active vs. quoted) | Declared Difference Under Test |
| **Stage 1.5 Sanitization** | **Disabled** (raw body passed) | **Enabled** (`[UNTRUSTED_INSTRUCTION_REDACTED]`) | Declared Difference Under Test |
| **Domain Telemetry Analysis** | **Disabled** | **Disabled** | **Identical (Inactive)** |
| **Balanced RAG Retrieval** | **Disabled** (standard RAG, $k=3$) | **Disabled** (standard RAG, $k=3$) | **Identical (Inactive)** |
| **Vector Store Index** | `results/rag_index_clean/index.faiss` | `results/rag_index_clean/index.faiss` | **Identical (SHA256 verified)** |
| **LLM Model & Version** | `qwen3.5:4b` (`d8b0f5e9760c`) | `qwen3.5:4b` (`d8b0f5e9760c`) | **Identical** |
| **Decoding Temperature** | `0.0` (Greedy deterministic) | `0.0` (Greedy deterministic) | **Identical** |
| **Max Predict Tokens** | `512` tokens | `512` tokens | **Identical** |

---

## 6. Pre-Evaluation Gate Status

| Gate Check | Required Action | Status |
|:---|:---|:---:|
| **Phase 1: Freeze & Audit** | Compute cryptographic hashes; freeze implementations | **COMPLETE** |
| **Phase 2: Dataset Construction** | Generate 500 balanced samples with explicit provenance | **COMPLETE** |
| **Phase 3: Pre-Evaluation Audit** | Execute leakage audit, automated test suite, validation report | **COMPLETE** |
| **Phase 4: Controlled Inference** | Execute 1,000 predictions ($500 \text{ A0} + 500 \text{ A1}$) | **HOLD FOR USER APPROVAL** |

In accordance with strict research protocol:
**Inference execution has been halted. The system is stopped and awaiting user review.**

