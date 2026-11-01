# Phase 8.0: Data Leakage Prevention & Independence Protocol

## 1. Executive Summary & Independence Mandate

A recurring flaw in machine learning security evaluation is **data contamination**—where evaluation samples unintentionally leak from training corpora, tuning sets, or retrieval indices, producing artificially inflated performance metrics.

To ensure that Phase 8 measures genuine, unassisted generalization to unseen communications, this protocol defines a **7-tier contamination elimination pipeline**. Every proposed candidate sample must pass all seven screening gates prior to admission into the Phase 8 benchmark suite.

---

## 2. Protected Baseline Corpora (Contamination Boundaries)

The Phase 8 evaluation corpus must possess **zero contamination** against all historical IFSI datasets:

| Historical Corpus | Location | Record Count | Role in IFSI Architecture | Contamination Risk |
| :--- | :--- | :--- | :--- | :--- |
| **`clean_split_v1` (Train/Test)** | `data/splits/clean_split_v1/` | 1,321 train / 331 test | Clean training split; source of clean FAISS index | Direct training data memorization |
| **Clean FAISS Index** | `results/rag_index_clean/index.faiss` | 1,321 vectors | RAG retrieval reference bank | Retrieval shortcut / exemplar identity leakage |
| **`live_benchmark_v1`** | `data/splits/live_benchmark_v1/` | 150 samples | Historical benchmark suite | Overfitting to initial validation distribution |
| **`live_benchmark_v2`** | `data/splits/live_benchmark_v2/` | 150 samples | Historical benchmark suite | Memorization of V2 adversarial cases |
| **`heldout_benchmark_v1`** | `data/splits/heldout_benchmark_v1/` | 100 samples | Historical ablation holdout | Test set leakage |
| **`phase5_regression_160`**| `data/evaluation/phase5_regression_160.jsonl` | 160 samples | Regression suite (A1-Opt) | Regressive memorization |
| **`phase6_domain_challenge`**| `data/evaluation/phase6_domain_challenge.jsonl` | 40 samples | Phase 6 domain challenge | Memorization of V2 domain edge cases |
| **`phase7_precision_challenge`**| `data/evaluation/phase7_precision_challenge.jsonl`| 40 samples | Phase 7 precision challenge | Memorization of V3 precision edge cases |

---

## 3. Seven-Tier Leakage Screening Pipeline

```mermaid
flowchart TD
    RawCandidate["Candidate Email Sample"] --> Tier1["Tier 1: Exact SHA-256 Collision Check"]
    Tier1 -->|Pass (Zero Collision)| Tier2["Tier 2: Normalized Text Collision Check"]
    Tier2 -->|Pass (Zero Collision)| Tier3["Tier 3: MinHash / Jaccard Near-Duplicate Screening (Threshold > 0.70)"]
    Tier3 -->|Pass (Jaccard <= 0.70)| Tier4["Tier 4: Embedding Cosine Similarity Screening vs FAISS (Threshold > 0.95)"]
    Tier4 -->|Pass (Cosine <= 0.95)| Tier5["Tier 5: Campaign & Phish-Kit Template Deduplication"]
    Tier5 -->|Pass (Unique Template)| Tier6["Tier 6: Domain / Context Overlap Sanity Audit"]
    Tier6 -->|Pass (Independent)| Tier7["Tier 7: Cryptographic Provenance Sign-Off"]
    Tier7 --> ApprovedCorpus["Admitted into Phase 8 Evaluation Suite"]
```

### 3.1 Tier 1: Exact Cryptographic SHA-256 Collision Check
- **Criterion**: $H_{\text{SHA-256}}(\text{text}_{\text{candidate}}) \cap H_{\text{SHA-256}}(\text{historical}) = \emptyset$.
- **Action on Violation**: Immediate permanent discard. Zero exact duplicates permitted.

### 3.2 Tier 2: Normalized Text Collision Check
- **Normalization Routine**: Lowercasing, Unicode NFKC canonical decomposition, removal of whitespace/punctuation sequences, and stripping of standard RFC822 transport headers (Received, X-Mailer, Message-ID).
- **Criterion**: $H_{\text{norm}}(\text{text}_{\text{candidate}}) \cap H_{\text{norm}}(\text{historical}) = \emptyset$.
- **Action on Violation**: Immediate permanent discard. Catches template reuse where only timestamp or whitespace varied.

### 3.3 Tier 3: MinHash & Jaccard Shingling Near-Duplicate Screening
- **Methodology**: 5-gram word shingling with 128 MinHash permutations.
- **Criterion**: $\text{Jaccard}(S_{\text{candidate}}, S_{\text{historical}}) \le 0.70$.
- **Action on Violation**: Discard. Any sample sharing $> 70\%$ 5-gram overlap with an existing training exemplar or historical benchmark sample is classified as a near-duplicate.

### 3.4 Tier 4: Dense Embedding Cosine Similarity vs Clean FAISS Index
- **Methodology**: Encoding using `sentence-transformers/all-MiniLM-L6-v2` and computing cosine similarity against all 1,321 clean FAISS index exemplars.
- **Criterion**: $\cos(\vec{v}_{\text{candidate}}, \vec{v}_{\text{exemplar}}) \le 0.95$.
- **Action on Violation**: Manual security analyst audit. If similarity $> 0.95$, the candidate is inspected to confirm it is not a direct syntactic paraphrase of an indexed exemplar.

### 3.5 Tier 5: Campaign & Phish-Kit Template Deduplication
- **Methodology**: Clustering mass phishing samples (from Nazario/Mendeley) by DOM tree structure and lexical boilerplate.
- **Criterion**: Maximum of **3 samples per phishing campaign template** allowed in the final 3,000 corpus.
- **Rationale**: Prevents mass spam runs (e.g. 500 identical Nigerian 419 letters or PayPal invoice notices) from artificially dominating benchmark metrics.

### 3.6 Tier 6: Sender Domain & Context Overlap Sanity Audit
- **Distinction Between Acceptable and Invalidating Overlap**:
  - **Acceptable Overlap**: Legitimate enterprise root domains (e.g., `@enterprise-corp.com`, `@amazon.com`, `@google.com`, `@workday.com`) naturally recur across different emails. This is realistic and representative of corporate email environments.
  - **Invalidating Overlap**: Identical phishing attack narratives, identical spoofed URLs, or identical prompt injection strings with only superficial recipient name swaps.

### 3.7 Tier 7: Cryptographic Independence Attestation
- All passing samples are sealed with a SHA-256 manifest: `data/evaluation/phase8/dataset_manifest.sha256`.

---

## 4. Verification Check Script Specification

Phase 8.1 will implement `tools/audit_phase8_dataset_independence.py` enforcing these screening tiers. Any dataset candidate failing any tier is rejected before benchmark execution.

