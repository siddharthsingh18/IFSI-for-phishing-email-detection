# Phase 8.0: Large-Scale Independent Evaluation Readiness Report

## 1. Executive Summary & Recommendation

Phase 8.0 establishes the scientific, legal, ethical, and statistical foundation for conducting a large-scale independent evaluation of the **IFSI Phishing Email Detection Pipeline**.

Following the successful precision refinement achieved in Phase 7 (where Config B / Domain Analyzer V3 achieved 99.58% accuracy, 0.77% FPR, and 100.0% sophisticated phishing recall on a controlled 240-email benchmark), this phase delivers a fully articulated, pre-registered evaluation protocol designed to evaluate generalization across **$N = 3,000$ independent emails**.

### Definitive Recommendation

### **READY FOR DATASET ACQUISITION.**

*(This recommendation authorizes progressing to Phase 8.1: Dataset Acquisition & Screening. It does **NOT** authorize production promotion or benchmark inference execution until all pre-registered acceptance gates are satisfied.)*

---

## 2. Synthesis of Phase 8.0 Deliverables & Specifications

| Deliverable Document | Core Purpose & Scope | Key Specifications & Standards |
| :--- | :--- | :--- |
| **[`evaluation_protocol.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/evaluation_protocol.md)** | Master experimental protocol | Paired double-blind evaluation of Config A vs Config B; identical inputs; local Ollama `qwen3.5:4b` (`temp=0.0`, `num_predict=512`); top-3 clean FAISS retrieval. |
| **[`dataset_source_registry.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/dataset_source_registry.md)** | Multi-source feasibility audit | 6 authorized research corpora (Enron clean, Nazario, Mendeley, IWSPA, OWASP LLM, SEC EDGAR); absolute prohibition of leaked/hacked inboxes. |
| **[`provenance_and_licensing.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/provenance_and_licensing.md)** | Legal & privacy framework | Mandatory regex PII scrubbing; structural domain and routing header preservation; auditable cryptographic provenance schema (`origin_type`). |
| **[`dataset_composition_plan.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/dataset_composition_plan.md)** | Target corpus distribution | Target $N = 3,000$: 900 Ordinary Legitimate (30%), 600 Difficult Legitimate (20%), 750 Conventional Phishing (25%), 450 Sophisticated Phishing (15%), 300 Prompt Injections (10%). |
| **[`annotation_guidelines.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/annotation_guidelines.md)** | Independent ground-truth assignment | Zero model-in-the-loop annotation; explicit evidentiary criteria for phishing vs legitimate; dual-annotation on 20% validation subset; mandatory Cohen's Kappa $\kappa \ge 0.85$. |
| **[`leakage_prevention_protocol.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/leakage_prevention_protocol.md)**| Contamination elimination | 7-tier screening pipeline: 0 SHA-256 collisions, 0 normalized collisions, MinHash Jaccard $\le 0.70$, FAISS cosine $\le 0.95$, template deduplication, split isolation. |
| **[`statistical_analysis_plan.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/statistical_analysis_plan.md)**| Formal hypothesis testing | Pre-registered McNemar's test ($\alpha = 0.01$); 95% Wilson Score confidence intervals; Wilcoxon signed-rank latency test; power $> 0.95$ across all sub-cohorts. |
| **[`acceptance_gates.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/acceptance_gates.md)** | Pre-registered gate thresholds | 7 sequential gates; explicit production readiness thresholds: Accuracy $\ge 98.5\%$, Sophisticated Recall $\ge 98.0\%$, FPR $\le 1.0\%$, Injection Containment $= 100.0\%$, P95 Latency $\le 6,000$ ms. |

---

## 3. Explicitly Identified Data Source Constraints

In accordance with Section 10 of the design mandate, the following data sources were audited and identified as **unavailable, restricted, or inadmissible**:

1. **Private Enterprise Telemetry**: Real-world corporate gateway logs from enterprise partners cannot be utilized without formal enterprise NDA/DPA agreements and multi-tenant cryptographic sanitization.
2. **Leaked/Stolen Inbox Corpora**: Publicly circulating dumps from criminal breaches (DNC, Sony Pictures, Hacking Team) are **inadmissible** due to severe ethical and legal prohibitions (GDPR Article 5, unauthorized possession of confidential personal communications).
3. **Uncurated Web Scrapes**: Unverified submissions on public paste sites (Pastebin, GitHub gists) are **inadmissible** due to unverified provenance and high vulnerability to data poisoning.
4. **IWSPA Derived Redistribution**: While IWSPA datasets are authorized for local academic research evaluation, derived copies cannot be publicly redistributed without permission from IEEE IWSPA organizers.

---

## 4. Phase 8 Roadmap & Resource Planning

With Phase 8.0 research design complete, the execution roadmap comprises:

```
Phase 8.0: Large-Scale Independent Evaluation Design (COMPLETED)
    │
    ▼
Phase 8.1: Dataset Acquisition, Screening & Curation (NEXT STEP)
    ├── Acquire candidate records from authorized registries (Enron, Nazario, Mendeley, SEC, OWASP)
    ├── Execute automated PII redaction and security evidence preservation
    ├── Run automated 7-tier leakage prevention protocol (tools/audit_phase8_dataset_independence.py)
    └── Conduct independent dual-annotation and verify Cohen's Kappa (kappa >= 0.85)
    │
    ▼
Phase 8.2: Paired Benchmark Execution (N = 3,000)
    ├── Pre-execution Gate 5 Architecture Freeze audit (SHA-256 verification)
    ├── Execute sequential double-blind evaluation: Config A (3,000) vs Config B (3,000)
    └── Flush raw predictions sequentially with safe checkpointing
    │
    ▼
Phase 8.3: Independent Forensic Audit & Production Readiness Decision
    ├── Recompute metrics independently (Accuracy, FPR, Sophisticated Recall, Latency)
    ├── Execute pre-registered statistical tests (McNemar, Wilson score, Wilcoxon)
    └── Adjudicate Gate 7 Production Readiness Decision Rule
```

---

## 5. Compliance Sign-Off

- **Zero Datasets Ingested**: In strict adherence to protection rules, no external datasets were downloaded or stored during Phase 8.0.
- **Zero Inferences Executed**: No benchmark inferences were launched.
- **Zero Code Modifications**: Production M4 (`src/core/inference.py`), Frozen A1 (`src/core/inference_m4_v2.py`), Clean FAISS Index (`results/rag_index_clean/index.faiss`), and Phase 7 implementations remain 100% untouched.

