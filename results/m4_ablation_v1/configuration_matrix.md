# Configuration Matrix & Experimental Design: M4 Ablation Study

**Experiment:** IFSI Phishing Email Detection — M4 Modular Component Ablation Study  
**Version:** V1  
**Date:** 2026-10-31  
**Status:** Approved & Implemented  
**Code Reference:** `src/experiments/m4_ablation_v1/ablation_engine.py`  

---

## 1. Full Ablation Configuration Matrix

The following matrix formally specifies all 9 configurations under evaluation. Every component state is strictly declared and enforced by `AblationConfig`.

| Config ID | Category | Name / Description | Stage 1 Injection Detector | Stage 1.5 Sanitizer | Feature: Domain Analysis | Stage 2 RAG Mode | Stage 2 Prompt Mode | Model & Inference Params |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **A0** | Baseline | **Production M4 Baseline**<br>Standard production two-stage RAG | `baseline_v1`<br>(Binary detector) | **Disabled**<br>(Raw body) | **Disabled**<br>(No domain block) | `standard`<br>(Top-3 cosine) | `baseline`<br>(No new directives) | `qwen3.5:4b`<br>temp=0.0, max=512 |
| **ISO-4** | Isolated Classifier | **Baseline + Injection Classifier Only**<br>Decouples detection from redaction | `experimental_v2`<br>(Active vs. Quoted) | **Disabled**<br>(Raw body) | **Disabled**<br>(No domain block) | `standard`<br>(Top-3 cosine) | `baseline`<br>(No new directives) | `qwen3.5:4b`<br>temp=0.0, max=512 |
| **A1** | Cumulative Step 1 | **Baseline + Classifier + Sanitizer**<br>Active injection redaction added | `experimental_v2`<br>(Active vs. Quoted) | **Enabled**<br>(Redacts spans) | **Disabled**<br>(No domain block) | `standard`<br>(Top-3 cosine) | `sanitization_only`<br>(Redaction aware) | `qwen3.5:4b`<br>temp=0.0, max=512 |
| **A2** | Cumulative Step 2 | **A1 + Structured Domain Analysis**<br>Domain & sender telemetry added | `experimental_v2`<br>(Active vs. Quoted) | **Enabled**<br>(Redacts spans) | **Enabled**<br>(Telemetry block) | `standard`<br>(Top-3 cosine) | `sanitization_and_domain`<br>(Domain + Redaction) | `qwen3.5:4b`<br>temp=0.0, max=512 |
| **A3** | Cumulative Step 3 | **A2 + Balanced RAG Retrieval**<br>Balanced exemplar retrieval added | `experimental_v2`<br>(Active vs. Quoted) | **Enabled**<br>(Redacts spans) | **Enabled**<br>(Telemetry block) | **`balanced`**<br>(2 Phish + 2 Legit) | `canonical_v2`<br>(Full instructions) | `qwen3.5:4b`<br>temp=0.0, max=512 |
| **A4** | Parity Verification | **Full Canonical Experimental M4**<br>Independent execution of full system | `experimental_v2`<br>(Active vs. Quoted) | **Enabled**<br>(Redacts spans) | **Enabled**<br>(Telemetry block) | **`balanced`**<br>(2 Phish + 2 Legit) | `canonical_v2`<br>(Full instructions) | `qwen3.5:4b`<br>temp=0.0, max=512 |
| **ISO-1** | Leave-One-Out | **Full Experimental WITHOUT Sanitization**<br>Removes Stage 1.5 redaction | `experimental_v2`<br>(Active vs. Quoted) | **Disabled**<br>(Raw body) | **Enabled**<br>(Telemetry block) | **`balanced`**<br>(2 Phish + 2 Legit) | `domain_only`<br>(Domain instructions) | `qwen3.5:4b`<br>temp=0.0, max=512 |
| **ISO-2** | Leave-One-Out | **Full Experimental WITHOUT Domain Analysis**<br>Removes domain telemetry | `experimental_v2`<br>(Active vs. Quoted) | **Enabled**<br>(Redacts spans) | **Disabled**<br>(No domain block) | **`balanced`**<br>(2 Phish + 2 Legit) | `sanitization_only`<br>(Redaction aware) | `qwen3.5:4b`<br>temp=0.0, max=512 |
| **ISO-3** | Leave-One-Out | **Full Experimental WITHOUT Balanced RAG**<br>Replaces balanced with top-3 RAG | `experimental_v2`<br>(Active vs. Quoted) | **Enabled**<br>(Redacts spans) | **Enabled**<br>(Telemetry block) | `standard`<br>(Top-3 cosine) | `sanitization_and_domain`<br>(Domain + Redaction) | `qwen3.5:4b`<br>temp=0.0, max=512 |

---

## 2. Hypothesis & Pairwise Contrast Schema

To attribute causal performance shifts strictly to individual architectural components without confounding variables, the ablation study defines 8 specific paired contrasts:

```
[A0: Baseline]
      │
      ├──────────────── ISO-4 vs A0 ───────────────► Hyp 1: Injection Classifier Value
      │                                                     (Does active/quoted classification reduce false alarms?)
      ▼
   [ISO-4]
      │
      ├──────────────── A1 vs ISO-4 ───────────────► Hyp 2: Sanitizer Redaction Value
      │                                                     (Does redacting text prevent Stage 2 jailbreaking?)
      ▼
    [A1]
      │
      ├──────────────── A2 vs A1 ──────────────────► Hyp 3: Structured Domain Telemetry Value
      │                                                     (Does domain mismatch evidence catch spoofed emails?)
      ▼
    [A2]
      │
      ├──────────────── A3 vs A2 ──────────────────► Hyp 4: Balanced RAG Retrieval Value
      │                                                     (Does guaranteed class symmetry prevent classification bias?)
      ▼
    [A3]
      │
      ├──────────────── A4 vs A3 ──────────────────► Hyp 5: Canonical Experimental Parity Check
      │                                                     (Does modular engine match canonical M4 V2 exactly?)
      ▼
[A4: Full System]
      │
      ├──────────────── A4 vs ISO-1 ───────────────► Hyp 6: Leave-One-Out Sanitization Impact
      │                                                     (What is lost when redaction is disabled from full system?)
      │
      ├──────────────── A4 vs ISO-2 ───────────────► Hyp 7: Leave-One-Out Domain Analysis Impact
      │                                                     (What is lost when domain telemetry is removed?)
      │
      └──────────────── A4 vs ISO-3 ───────────────► Hyp 8: Leave-One-Out Balanced RAG Impact
                                                            (What is lost when standard RAG replaces balanced retrieval?)
```

### Detailed Contrast Definitions

#### Hypothesis 1: Isolated Value of Stage 1 Active-vs-Quoted Classifier (`ISO-4` vs `A0`)
- **Independent Variable:** Stage 1 detector: `experimental_v2` vs `baseline_v1`.
- **Controlled Constants:** Sanitization=False, Domain Analysis=False, RAG=standard (top-3), Stage 2 Prompt=`baseline`.
- **Target Measurement:** Injection precision, injection recall, quarantine_review accuracy, false positive reduction on quoted SOC reports.

#### Hypothesis 2: Isolated Value of Stage 1.5 Text Sanitization (`A1` vs `ISO-4`)
- **Independent Variable:** Text sanitization: Enabled vs Disabled.
- **Controlled Constants:** Stage 1=`experimental_v2`, Domain Analysis=False, RAG=standard (top-3).
- **Target Measurement:** Phishing classification robustness against prompt injection payloads that attempt to force `is_phishing=false`.

#### Hypothesis 3: Incremental Value of Structured Domain Telemetry (`A2` vs `A1`)
- **Independent Variable:** Domain analysis: Enabled vs Disabled.
- **Controlled Constants:** Stage 1=`experimental_v2`, Sanitization=True, RAG=standard (top-3).
- **Target Measurement:** Detection recall on sophisticated spear-phishing, domain spoofing, and lookalike domains.

#### Hypothesis 4: Incremental Value of Balanced RAG Retrieval (`A3` vs `A2`)
- **Independent Variable:** RAG Retrieval: Balanced (2 phish + 2 legit) vs Standard (top-3 nearest neighbors).
- **Controlled Constants:** Stage 1=`experimental_v2`, Sanitization=True, Domain Analysis=True.
- **Target Measurement:** Overall accuracy, false negative rate, exemplar class balance impact on borderline legitimate emails.

#### Hypothesis 5: Canonical System Parity Verification (`A4` vs `A3`)
- **Independent Variable:** None (Identical component specifications).
- **Purpose:** Verifies that the modular configuration engine (`A3`) reproduces the identical behavior of canonical experimental M4 (`A4`). Expected variance $\Delta \approx 0.0\%$.

#### Hypothesis 6: Total Contribution of Sanitization (`A4` vs `ISO-1`)
- **Independent Variable:** Sanitization in full multi-component setting.
- **Target Measurement:** Quantifies system vulnerability to adversarial injection bypasses when domain analysis and balanced RAG are both active.

#### Hypothesis 7: Total Contribution of Domain Telemetry (`A4` vs `ISO-2`)
- **Independent Variable:** Domain telemetry in full multi-component setting.
- **Target Measurement:** Quantifies detection drop for deceptive lures when active injection defense and balanced RAG remain active.

#### Hypothesis 8: Total Contribution of Balanced RAG (`A4` vs `ISO-3`)
- **Independent Variable:** Balanced retrieval in full multi-component setting.
- **Target Measurement:** Quantifies retrieval bias and borderline classification stability in the presence of domain telemetry and sanitization.

---

## 3. Evaluation Corpus & Execution Plan

All 9 configurations will be evaluated across the complete combined benchmark corpus:
- **Corpus Size:** Exactly 250 unique emails.
  - 150 emails from Live Benchmark V2 (`results/live_benchmark_v2/test_dataset_v2.jsonl`).
  - 100 emails from Held-Out Benchmark V1 (`results/m4_experiment_v1/heldout_dataset_v1.jsonl`).
- **Total Inferences:** $9 \times 250 = 2,250$ total evaluations.
- **Evaluation Order:** Sequential execution across configurations (`A0`, `ISO-4`, `A1`, `A2`, `A3`, `A4`, `ISO-1`, `ISO-2`, `ISO-3`) to guarantee identical cache and system conditions.
- **Artifact Isolation:** All predictions stored exclusively in `results/m4_ablation_v1/predictions/` with zero mutation of historical benchmark files.

