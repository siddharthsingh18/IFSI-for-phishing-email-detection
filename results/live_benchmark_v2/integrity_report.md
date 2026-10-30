# Live Benchmark V2: Data Integrity & Leakage Verification Report

**Verification Date (UTC):** 2026-10-30T16:21:19.700444+00:00  
**Dataset Evaluated:** `data/evaluation/live_benchmark_v2.jsonl`  
**Total Records:** 150  

---

## 1. Dataset Composition & Distribution

| Metric | Count | Expected | Status |
| :--- | :---: | :---: | :---: |
| Total Samples | 150 | 150 | PASS |
| Group A: Ordinary Genuine | 30 | 30 | PASS |
| Group B: Difficult Genuine | 30 | 30 | PASS |
| Group C: Conventional Phishing | 30 | 30 | PASS |
| Group D: Sophisticated Phishing | 30 | 30 | PASS |
| Group E: Prompt Injection Attacks | 30 | 30 | PASS |
| &nbsp;&nbsp;↳ Phishing with Prompt Injection | 15 | 15 | PASS |
| &nbsp;&nbsp;↳ Genuine with Prompt Injection | 15 | 15 | PASS |
| Total Ground-Truth Phishing | 75 | 75 | PASS |
| Total Ground-Truth Legitimate | 75 | 75 | PASS |

---

## 2. Cross-Corpus Contamination & Leakage Audit

The 150 Benchmark V2 samples were systematically cross-referenced against all historical project corpora to guarantee zero train/test contamination and zero retrieval exemplar leakage.

| Corpus / Index | Records Checked | ID Collisions | Exact Text Collisions | Near-Duplicates (Jaccard > 0.8) | Leakage Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Train Set (clean_split_v1) | 1,321 | 0 | 0 | 0 | **CLEAN (0 LEAKAGE)** |
| Validation Set (clean_split_v1) | 134 | 0 | 0 | 0 | **CLEAN (0 LEAKAGE)** |
| Test Set (clean_split_v1) | 173 | 0 | 0 | 0 | **CLEAN (0 LEAKAGE)** |
| Live Benchmark V1 | 40 | 0 | 0 | 0 | **CLEAN (0 LEAKAGE)** |
| RAG Clean Index Metadata | 1,321 | 0 | 0 | 0 | **CLEAN (0 LEAKAGE)** |

---

## 3. Internal Integrity & Hygiene Verification

- **Internal Duplicate IDs:** 0 (Passed)
- **All Required Fields Present (`id`, `subject`, `sender`, `body`, `is_phishing`, `label`, `has_prompt_injection`, `category`, `subcategory`, `explanation`):** YES
- **Boolean and Numeric Label Consistency:** YES (`label=1` iff `is_phishing=True`; `label=0` iff `is_phishing=False`)

## 4. Integrity Conclusion

> [!NOTE]
> **Integrity Verification: PASSED**  
> Benchmark V2 contains exactly 150 pristine, independent email samples with zero overlap with training data, validation sets, test sets, Live Benchmark V1, or the FAISS RAG index. The dataset provides an uncompromising, uncontaminated test bed for generalization and adversarial evaluation.
