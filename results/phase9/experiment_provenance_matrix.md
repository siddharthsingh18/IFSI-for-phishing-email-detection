# Phase 9.1: Comprehensive Experiment Provenance Matrix

## 1. Governance Principles & Incompatible Metric Boundary

> [!WARNING]
> **Strict Prohibition on Cross-Dataset Metric Conflation**:
> Metrics from different experimental phases must **NEVER be mathematically pooled or averaged together**. Each phase answered a distinct scientific question and evaluated a distinct benchmark distribution:
> - **Phase 4**: Architectural ablation on synthetic/curated emails ($N = 250$).
> - **A1 Generalization**: Out-of-distribution generalization on adversarial attacks ($N = 500$).
> - **Phase 5**: Targeted latency and sanitizer regression ($N = 160$).
> - **Phase 6**: Domain lookalike challenge ($N = 200$).
> - **Phase 7**: Domain precision and secondary SaaS disambiguation ($N = 240$).
>
> Any attempt to average percentages across these sets produces invalid synthetic statistics. Each experiment stands as an independent, reproducible empirical unit.

---

## 2. Complete Cross-Phase Experiment Provenance Matrix

The following matrix maps every experimental phase, dataset input, evaluated configuration, prediction log, and audit artifact across the research lifecycle:

| Phase & Study Name | Dataset File Path & SHA-256 | Sample Volume ($N$) | Candidate Configurations | Prediction Artifact & SHA-256 | Metrics Artifact & SHA-256 | Key Audit Report | Reproducibility Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **Phase 4: Controlled M4 Ablation** | [`data/evaluation/live_benchmark_v2.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/live_benchmark_v2.jsonl) (`1c762180451b...`) + [`data/evaluation/heldout_benchmark_v1.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/heldout_benchmark_v1.jsonl) (`42722ce81def...`) | 250 (150 V2 + 100 Held-Out) | 9 Configurations: `A0`, `ISO-4`, `A1`, `A2`, `A3`, `A4` (Canonical), `ISO-1`, `ISO-2`, `ISO-3` (2,250 total inferences) | [`results/m4_ablation_v1/predictions.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/predictions.jsonl) (`4a0cb0afdda10d22420d39a2b9fff754287f9a054a9c32485a517a70a003b449`) | [`results/m4_ablation_v1/metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/metrics.json) (`1936a7064146...`) & [`independently_verified_metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/independently_verified_metrics.json) (`9dbf7689f97a...`) | [`forensic_audit.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/forensic_audit.md) & [`final_report.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/m4_ablation_v1/final_report.md) | **REPRODUCIBLE** (Exact 2,250 records verified) |
| **Phase 4.5: A1 Generalization Validation V1** | [`data/evaluation/a1_generalization_v1.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/a1_generalization_v1.jsonl) (`ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336`) | 500 (250 Legitimate + 250 Phishing; includes 200 injections + 50 quoted SOC advisories) | 2 Configurations: Baseline `A0` vs. Frozen `A1` (`src/core/inference_m4_v2.py`) (1,000 total inferences) | [`results/a1_generalization_v1/predictions.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/results/a1_generalization_v1/predictions.jsonl) (`7b1645eeae682bfbdaffb28dce7930ec71b2ccbf3cc519417ed99c4b9459589e`) | [`results/a1_generalization_v1/metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/a1_generalization_v1/metrics.json) (`d7e7d4c840fb098ce480f386b42f2e66e8ce3fe7d037623929511da2e89d8931`) | [`root_cause_analysis.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/a1_generalization_v1/root_cause_analysis.md) & [`final_report.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/a1_generalization_v1/final_report.md) | **REPRODUCIBLE** (Exact 1,000 records verified) |
| **Phase 5: A1 Sanitizer & Latency Optimization** | [`data/evaluation/phase5_regression_160.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/phase5_regression_160.jsonl) (`325bf42f244120667aa00051ed0e2086b02645958c138699cd3bd32d615fc606`) | 160 (100 Injection test cases [CJK, punctuation, whitespace] + 60 standard regression cases) | 2 Configurations: Frozen `A1` Baseline vs. `A1-Opt` (`engine_v2.py`) (320 total inferences) | [`results/phase5_a1_sanitizer_latency/predictions.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase5_a1_sanitizer_latency/predictions.jsonl) (`cf569e133a1aa3a39f8ed2b725ef5e34ce8c140be630b6b2851115d7db15847d`) | [`regression_metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase5_a1_sanitizer_latency/regression_metrics.json) (`40302cfc01fa...`) & [`independent_metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase5_a1_sanitizer_latency/independent_metrics.json) (`1678fb135d51...`) | [`independent_audit_report.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase5_a1_sanitizer_latency/independent_audit_report.md) | **REPRODUCIBLE** (Exact 320 records verified) |
| **Phase 6: Domain Evidence Integration Study** | Combined: `phase5_regression_160.jsonl` (160) + [`data/evaluation/phase6_domain_challenge.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/phase6_domain_challenge.jsonl) (`02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7`) (40) | 200 (160 regression + 40 domain challenge [20 difficult legit + 20 sophisticated phish]) | 3 Configurations: Config A (A1-Opt, 200), Config B (A1-Opt + Domain Analyzer V2, 200), Config C (Ablation, 40) (440 total inferences) | [`results/phase6_domain_evidence/predictions.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase6_domain_evidence/predictions.jsonl) (`242df69af3883d1fdac6afe4910cf9a277a1693ed700e501b0832ba92e1b246b`) | [`independent_metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase6_domain_evidence/independent_metrics.json) (`9842cec270ceedbeb44dbdb207e7d6e7a6da0896cf7ea68cca386673cbd2f718`) | [`false_positive_analysis.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase6_domain_evidence/false_positive_analysis.md) & [`promotion_readiness.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase6_domain_evidence/promotion_readiness.md) | **REPRODUCIBLE** (Exact 440 records verified) |
| **Phase 7: Domain Precision Refinement Study** | Combined: `phase5_regression_160.jsonl` (160) + `phase6_domain_challenge.jsonl` (40) + [`data/evaluation/phase7_precision_challenge.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/data/evaluation/phase7_precision_challenge.jsonl) (`a6ea7aa12d5bc997...`) (40) | 240 (160 regression + 40 P6 challenge + 40 P7 SaaS precision challenge) | 3 Configurations: Config A (P6 Baseline, 240), Config B (P7 Domain Analyzer V3, 240), Config C (Domain Ablation, 80) (560 total inferences) | [`results/phase7_domain_precision/predictions.jsonl`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase7_domain_precision/predictions.jsonl) (`2e2efbcacc597afcccd060043618ad33cfc6372d42b23b477c749c804daea724`) | [`independent_metrics.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase7_domain_precision/independent_metrics.json) (`1d576aaeb18922b2af4eaaacfac78a57691c8228a355f1801d6b3e0f678fe45d`) | [`audit_summary.json`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase7_final_audit/audit_summary.json) & [`final_recommendation.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase7_final_audit/final_recommendation.md) | **REPRODUCIBLE** (Exact 560 records verified) |

---

## 3. Detailed Study-by-Study Analysis

### 3.1 Phase 4: Controlled M4 Component Ablation
- **Scientific Objective**: Measure the individual statistical contribution of each modular enhancement added to M4 (Active vs. Quoted injection detection, Stage 1.5 sanitization, Balanced RAG, Domain Telemetry V1).
- **Dataset Provenance**:
  - `live_benchmark_v2.jsonl`: 150 real-world and synthetic emails including active injection bypass attempts from Live Benchmark V1.
  - `heldout_benchmark_v1.jsonl`: 100 held-out split samples preserving standard training distribution boundaries.
- **Key Empirical Findings**:
  - Proved canonical parity between modular ablation engine (A3) and reference M4 (A4) with 100% agreement ($\chi^2 = 0.0000, p = 1.000$).
  - Sanitization produced a net gain of $+4$ correct classifications ($p = 0.221$).
  - Balanced RAG eliminated exemplar retrieval imbalance on difficult genuine emails.
- **Known Limitations**:
  - Domain Telemetry V1 suffered from false positive instability on synthetic benchmark domains without live DNS.
  - High mean latency of full architecture (~6.7s).

### 3.2 A1 Generalization Validation V1
- **Scientific Objective**: Evaluate whether the A1 architecture generalizes across a large out-of-distribution adversarial corpus containing subtle prompt injections and security education advisories.
- **Dataset Provenance**:
  - `a1_generalization_v1.jsonl`: 500 emails (250 legitimate, 250 phishing). Contains 100 marked injections, 100 unmarked injections, and 50 quoted injection incident reports.
- **Key Empirical Findings**:
  - A1 achieved 100% containment of active prompt injections and 100% safe-delivery of quoted injection incident reports (Baseline A0 had 0% quoted accuracy).
  - Uncovered latency root cause: Stage 1 prefill of verbose prompt and multi-sentence generation caused a 2.5x to 4.1x slowdown.
- **Known Limitations**:
  - Sanitizer V1 failed on CJK and attached punctuation boundaries, occasionally corrupting non-English text.

### 3.3 Phase 5: A1 Sanitizer & Latency Optimization
- **Scientific Objective**: Fix Sanitizer V1 failure modes and reduce Stage 1 latency by $\ge 30\%$ without compromising active injection detection.
- **Dataset Provenance**:
  - `phase5_regression_160.jsonl`: 160 targeted emails (100 injection stress tests including Chinese, Japanese, Korean, Cyrillic, whitespace permutations, and 60 regression emails).
- **Key Empirical Findings**:
  - Sanitizer V2 achieved 100% redaction accuracy on all 100 adversarial stress cases with zero collateral corruption.
  - `STAGE1_COMPACT_PROMPT` reduced Stage 1 inference latency by **41.2%** (1.57s vs. 2.67s).
- **Known Limitations**:
  - A1-Opt omitted domain analysis, leaving an empirical blind spot against brand lookalike domain phishing.

### 3.4 Phase 6: Domain Evidence Integration Study
- **Scientific Objective**: Integrate structured sender and domain telemetry into A1-Opt to detect sophisticated phishing without sacrificing Phase 5 latency gains.
- **Dataset Provenance**:
  - `phase5_regression_160.jsonl` (160) + `phase6_domain_challenge.jsonl` (40: 20 difficult legit + 20 sophisticated lookalike phish).
- **Key Empirical Findings**:
  - Config B (Domain Analyzer V2) boosted sophisticated phishing recall from 62.5% to **97.5%** (+35.0 pp net gain).
  - Domain Analyzer V2 CPU time was negligible ($< 1\text{ ms}$).
- **Known Limitations**:
  - Introduced 3 false positives (`gen-ord-010`, `p6-leg-007`, `p6-leg-015`) on legitimate corporate secondary domains and transactional SaaS.

### 3.5 Phase 7: Domain Precision Refinement Study
- **Scientific Objective**: Remediate the 3 Phase 6 false positives using Domain Analyzer V3 while preserving 100% sophisticated phishing recall.
- **Dataset Provenance**:
  - Evaluated on a 240-email adversarial benchmark combining `phase5_regression_160` (160) + `phase6_domain_challenge` (40) + `phase7_precision_challenge` (40).
- **Key Empirical Findings**:
  - Config B (Domain Analyzer V3) successfully eliminated **100% of historical false positives** (3/3) and prevented new precision challenge false positives (3/3).
  - Maintained **100.0% sophisticated phishing recall** (60/60 detected).
  - Overall accuracy reached **99.58%** with $\text{FPR} = 0.77\%$ (1/130).
  - Mean latency reduced by 7.5% (4.09s vs. 4.42s).
- **Known Limitations**:
  - Single remaining false positive on `gen-inj-071` (Stage 2 LLM sensitivity to security advisory vocabulary, unrelated to domain analysis).
  - Benchmark volume ($N=240$) is sufficient for research candidate selection, but requires external Track A real-email validation.
