# Dataset Provenance & Classification Report: A1 Synthetic Challenge Benchmark V1

**Target Dataset:** `data/evaluation/a1_generalization_v1.jsonl`  
**Total Sample Count:** 500 unique emails  
**Dataset SHA-256:** `ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336`  
**Evaluation Scope:** Controlled A0 vs. A1 Architectural Generalization Study  
**Formal Dataset Classification:** **Synthetic Challenge Benchmark** (Predominantly Synthetic & Adapted Lure Corpus)  

---

## 1. Critical Provenance Clarification & Dataset Classification

> [!IMPORTANT]
> **Scientific Integrity Notice:**  
> Although `data/evaluation/a1_generalization_v1.jsonl` achieves verified 0.00% cryptographic and n-gram overlap with all prior project datasets and RAG corpora, an exhaustive forensic inspection confirms that the dataset is **predominantly synthetic and template-adapted**.
> 
> Therefore, this dataset is formally classified as a **Synthetic Challenge Benchmark** rather than an organic real-world email collection. Evaluation findings must be interpreted as **stress-test generalization under synthetic adversarial and distributional shifts**, and must NOT be characterized as proof of in-the-wild real-world generalization.

### Exact Provenance Breakdown ($N = 500$)

| Provenance Stream | Sample Count | Percentage | Classification Description |
|:---|:---:|:---:|:---|
| **Raw Unedited Real-World Emails** | **0** | **0.0%** | Zero raw, unedited external emails were ingested into this dataset, ensuring complete protection of PII, internal credentials, and proprietary communications. |
| **Adapted / Transformed Real-World Templates** | **104** | **20.8%** | Standardized templates derived from public research archives (Apache SpamAssassin ham and Jose Nazario phishing), normalized to contemporary enterprise formatting with sanitized recipient identifiers. |
| **Newly Generated Synthetic Challenge Emails** | **396** | **79.2%** | Curated scenarios crafted to test edge-case decision boundaries (difficult corporate compliance, sophisticated BEC pretexting, multi-lingual prompt injections, and quoted security advisories). |
| **TOTAL** | **500** | **100.0%** | **Predominantly Synthetic Challenge Corpus (79.2% Synthetic / 20.8% Adapted)** |

---

## 2. Target Composition & Balanced Ground Truth

The 500 challenge samples provide a symmetrical 50/50 balance across ground-truth labels and represent five diverse operational categories:

| Category | Sample ID Range | Total Emails | Phishing ($y=1$) | Legitimate ($y=0$) | Active Injection | Quoted Injection | Challenge Boundary Evaluated |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Ordinary Legitimate** | `gen-ord-001` - `100` | 100 | 0 | 100 | 0 | 0 | Routine team syncs, sprint reviews, SaaS receipts, and library notices. |
| **Difficult Legitimate** | `gen-dif-001` - `100` | 100 | 0 | 100 | 0 | 0 | High-pressure corporate compliance, benefits deadlines, W-2 tax forms, and password expirations. |
| **Conventional Phishing** | `gen-con-001` - `100` | 100 | 100 | 0 | 0 | 0 | Mass-scale M365 credential harvesting, fake DocuSign agreements, and delivery fee fraud. |
| **Sophisticated Phishing** | `gen-sop-001` - `100` | 100 | 100 | 0 | 0 | 0 | Low-urgency executive BEC wire fraud, vendor onboarding, and academic peer-review traps. |
| **Prompt Injection** | `gen-inj-001` - `100` | 100 | 50 | 50 | 50 | 50 | 50 active malicious phishing overrides + 50 quoted benign security advisories / bug reports. |
| **TOTAL** | `gen-ord-001` - `gen-inj-100` | **500** | **250 (50.0%)** | **250 (50.0%)** | **50 (10.0%)** | **50 (10.0%)** | **Symmetrically balanced 50/50 ground-truth distribution** |

---

## 3. Cryptographic Leakage & Contamination Audit

To guarantee zero data leakage or evaluation memorization, all 500 emails were audited against all 7 historical training, validation, test, and FAISS index records.

| Reference Corpus Checked | Items in Corpus | Exact Text Overlaps | Near-Duplicate Overlaps (Jaccard $\ge 0.70$) | Contamination Status |
|:---|:---:|:---:|:---:|:---:|
| **Live Benchmark V1** | 40 | **0** | **0** | **VERIFIED CLEAN (0.00%)** |
| **Live Benchmark V2** | 150 | **0** | **0** | **VERIFIED CLEAN (0.00%)** |
| **Held-Out Benchmark V1** | 100 | **0** | **0** | **VERIFIED CLEAN (0.00%)** |
| **Clean Split Train** | 1,321 | **0** | **0** | **VERIFIED CLEAN (0.00%)** |
| **Clean Split Val** | 134 | **0** | **0** | **VERIFIED CLEAN (0.00%)** |
| **Clean Split Test** | 173 | **0** | **0** | **VERIFIED CLEAN (0.00%)** |
| **Clean FAISS Index Metadata** | 1,321 | **0** | **0** | **VERIFIED CLEAN (0.00%)** |
| **TOTAL UNIQUE HISTORICAL ITEMS** | **3,239** | **0 (0.00%)** | **0 (0.00%)** | **100% CONTAMINATION-FREE** |

---

## 4. Preservation of Dataset Integrity

- File: `data/evaluation/a1_generalization_v1.jsonl`
- Byte Size: `693,874` bytes
- SHA-256 Digest: `ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336`
- Status: **PRESERVED UNCHANGED**
