# Phase 8.1C: Statistical Design Review (`800 + 200` vs. Revised `600 + 200` Track A)

## 1. Scope & Generalization Boundary

This review evaluates the statistical precision, hypothesis-testing power, subgroup resolution, and structural limitations of both the Phase 8.1B proposed design (`N_test = 800`, `N_val = 200`) and the Phase 8.1C conservative revised design (`N_test = 600`, `N_val = 200`).

> [!WARNING]
> **Mandatory Generalization Disclaimer**:
> Neither `800` nor `600` emails establish **universal real-world enterprise generalization**. Both designs evaluate generalization solely across their sampled domains and eras (`2007` academic/server mail + `2021–2025` open standards/OSS mailing lists + `2022–2025` honeypot/bait phishing captures) and **do not** measure live private corporate HR/payroll/executive inbox traffic or authentic wire-transfer BEC.

---

## 2. Overall Accuracy, FPR & FNR Confidence Intervals (`N = 800` vs. `N = 600`)

All intervals below are exact two-sided **95% Wilson score confidence intervals** ($z = 1.9600$). Reducing `N_test` from `800` (`400`/`400`) to the conservative `600` (`300`/`300`) floor widens class-level 95% CI half-widths by only **`0.20` to `0.35` percentage points**, while eliminating `175` unverified spam-trap phishing records:

| Metric & Assumed Point Estimate | Phase 8.1B (`N_test = 800`: `400`L / `400`P) | Phase 8.1C Revised (`N_test = 600`: `300`L / `300`P) | Disjoint Validation (`N_val = 200`: `100`L / `100`P) |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy (`95.00%`)** | `760/800` $\rightarrow$ **`[93.26%, 96.31%]`** (`±1.53 pp`) | `570/600` $\rightarrow$ **`[92.95%, 96.48%]`** (`±1.77 pp`) | `190/200` $\rightarrow$ `[91.05%, 97.26%]` |
| **Overall Accuracy (`98.00%`)** | `784/800` $\rightarrow$ **`[96.78%, 98.77%]`** (`±1.00 pp`) | `588/600` $\rightarrow$ **`[96.54%, 98.85%]`** (`±1.16 pp`) | `196/200` $\rightarrow$ `[94.96%, 99.22%]` |
| **Legitimate FPR (`0.00%`)** | `0/400` $\rightarrow$ **`[0.00%, 0.95%]`** | `0/300` $\rightarrow$ **`[0.00%, 1.26%]`** | `0/100` $\rightarrow$ `[0.00%, 3.70%]` |
| **Legitimate FPR (`1.00%`)** | `4/400` $\rightarrow$ **`[0.39%, 2.54%]`** | `3/300` $\rightarrow$ **`[0.34%, 2.90%]`** | `1/100` $\rightarrow$ `[0.18%, 5.45%]` |
| **Legitimate FPR (`2.00%`)** | `8/400` $\rightarrow$ **`[1.02%, 3.90%]`** | `6/300` $\rightarrow$ **`[0.92%, 4.29%]`** | `2/100` $\rightarrow$ `[0.55%, 7.00%]` |
| **Phishing Recall (`95.00%`) / FNR (`5.00%`)** | Recall **`[92.40%, 96.74%]`** / FNR **`[3.26%, 7.60%]`** | Recall **`[91.92%, 96.95%]`** / FNR **`[3.05%, 8.08%]`** | Recall `[88.82%, 97.85%]` / FNR `[2.15%, 11.18%]` |
| **Phishing Recall (`98.00%`) / FNR (`2.00%`)** | Recall **`[96.10%, 98.98%]`** / FNR **`[1.02%, 3.90%]`** | Recall **`[95.71%, 99.08%]`** / FNR **`[0.92%, 4.29%]`** | Recall `[93.00%, 99.45%]` / FNR `[0.55%, 7.00%]` |

### Proper Statistical Role of the `N_val = 200` Validation Set
With `100` records per class, `N_val = 200` has wide 95% CIs (`±3.2` to `±4.5 pp` around `2%–5%` error rates) and **must NOT be used for confirmatory accuracy claims or post-hoc threshold fishing**. Its sole permitted functions are:
1. Running [`confounding_audit.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/tools/diagnostics/confounding_audit.py) (`format_only_balanced_accuracy <= 0.85`, `full_minus_format_balanced_accuracy >= 0.05`).
2. Verifying MIME parsing, attachment stripping, and symmetric `List-*` / `<REDACTED_RECIPIENT>` canonicalization before touching `N_test = 600`.
3. Confirming JSON schema validity (`>= 99%`) and runtime latency prior to freezing test execution.

---

## 3. Source-Stratified & Phishing-Subtype Statistical Resolution (`N_test = 600`)

### 3.1 Per-Source Confidence Intervals
| Source Stratum | Class & `n` (`N_test = 600`) | Metric Policy | Illustrative Estimate & Exact 95% Wilson CI | Adequacy Assessment |
| :--- | :---: | :---: | :--- | :--- |
| **`phishing_pot`** | `225` Phishing | `Recall` / `FNR` | `214/225` (`95.11%`) $\rightarrow$ **`[91.46%, 97.25%]`** | **Adequate** for primary contemporary phishing recall (`±2.9 pp`). |
| **`trecc07p` (`ham`)** | `105` Legitimate | `FPR` (+ dual-class MCC) | `0/105` (`0.00%`) $\rightarrow$ **`[0.00%, 3.53%]`**; `2/105` (`1.90%`) $\rightarrow$ **`[0.52%, 6.68%]`** | **Moderate** (`<= 3.5%` zero-error upper bound). |
| **`trecc07p` (`phish`)** | `45` Phishing | `Recall` (+ dual-class MCC) | `42/45` (`93.33%`) $\rightarrow$ **`[82.14%, 97.71%]`** | **Exploratory width (`~15.6 pp` span)** — report exact CI; do not over-claim fine differences on `n = 45` alone. |
| **`ietf_mailarchive`** | `105` Legitimate | `FPR` | `0/105` (`0.00%`) $\rightarrow$ **`[0.00%, 3.53%]`**; `2/105` (`1.90%`) $\rightarrow$ **`[0.52%, 6.68%]`** | **Moderate** (`n = 105`). |
| **`asf_lists_mbox`** | `90` Legitimate | `FPR` | `0/90` (`0.00%`) $\rightarrow$ **`[0.00%, 4.09%]`**; `2/90` (`2.22%`) $\rightarrow$ **`[0.61%, 7.74%]`** | **Moderate**; combined contemporary legit (`IETF`+`ASF`, `n = 195`) achieves `[0.00%, 1.93%]` at `0` FP. |
| **`untroubled_phish`** | `30` Phishing | `Recall` | `28/30` (`93.33%`) $\rightarrow$ **`[78.68%, 98.15%]`** | **Exploratory (`n = 30`)** — acts as cross-sinkhole sanity check, not standalone headline test. |

### 3.2 Phishing Subtype Recall Resolution (`n_phish = 300`)
Across `300` phishing test messages stratified by the Phase 8.1C taxonomy (`C1` vs. `C2` and lure mechanism):
- **`C1: Credential theft / phishing`** (expected `n ≈ 180–210`): At `95.0%` (`171/180`), 95% Wilson CI is **`[90.77%, 97.35%]`** (`±3.3 pp` — **well-powered**).
- **`C2: Financial fraud / impersonation`** (expected `n ≈ 60–90`): At `90.0%` (`81/90`), 95% Wilson CI is **`[82.08%, 94.65%]`** (`±6.3 pp` — **descriptive only**, insufficient power for `<5 pp` sub-genre differences).
- **Rare sub-strata (`n <= 30`)**: E.g., `27/30` (`90.0%`) spans **`[74.38%, 96.54%]`** (`>22 pp` width) — must be labeled **descriptive/exploratory**.

---

## 4. Paired Comparison Requirements: `A0` vs. `A1` (and Frozen `Config A` vs. `Config B`)

Because every candidate architecture—**`A0`** ([`src/core/inference.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/core/inference.py) production M4), **`A1`** ([`src/core/inference_m4_v2.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/core/inference_m4_v2.py) frozen A1), **`Config A`** (Phase 5 A1-Opt), and **`Config B`** ([`engine_v4.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/experiments/phase7_domain_precision/engine_v4.py) + [`domain_analyzer_v3.py`](file:///d:/Project/IFSI-for-phishing-email-detection/src/experiments/phase7_domain_precision/domain_analyzer_v3.py))—must be evaluated deterministically on the **exact same `600` email IDs**:

1. **Exact Two-Sided Paired McNemar Test**:
   - Let $b$ be messages classified **correctly by Candidate (`A1` or `Config B`) and wrongly by Baseline (`A0` or `Config A`)**, and $c$ the reverse ($D = b + c$ total discordant pairs).
   - Exact binomial McNemar significance ($\alpha = 0.05$, two-sided) depends solely on $(b, c)$:
     - Zero regressions ($c = 0$): requires **$b \ge 6$ discordant wins** ($p = 2 / 64 = 0.03125 < 0.05$; `+2.00 pp` net recall gain on `n = 300`, or `+1.00 pp` overall accuracy gain on `N = 600`).
     - One regression ($c = 1$): requires **$b \ge 9$ discordant wins** ($p = 20 / 1024 = 0.0195 < 0.05$; `+2.67 pp` net recall gain on `n = 300`).
     - For **80% unconditional power** at two-sided $\alpha = 0.05$ when the true win/loss ratio among discordant pairs is `4 : 1` ($p_{\text{win}} = 0.80$), **`D >= 22` discordant pairs** suffice (e.g., `18` wins vs. `4` losses = `+4.67 pp` net shift on `n = 300` or `+2.33 pp` on `N = 600`).
2. **Paired Cluster-Bootstrap 95% Confidence Intervals (`10,000` Resamples)**:
   - Report paired differences $\Delta \text{Recall}$, $\Delta \text{FPR}$, $\Delta \text{FNR}$, and $\Delta \text{MCC}$ resampled by **campaign/thread cluster ID** so residual intra-cluster correlation (`max 2` msgs/campaign) never understates standard errors.
3. **Pre-Specified Non-Inferiority & Multiplicity Rules**:
   - Co-primary comparisons (`A1` vs `A0`, and `Config B` vs `Config A` on Phishing Recall and Legitimate FPR) must apply **Holm-Bonferroni** family-wise error control ($\alpha = 0.05$).
   - Legitimate FPR non-inferiority holds only if the upper bound of the paired two-sided 95% CI on $\Delta \text{FPR} = \text{FPR}_{\text{candidate}} - \text{FPR}_{\text{baseline}}$ is **`<= +2.00` percentage points** ([docs/V2_RESEARCH_SPEC_ZH.md](file:///d:/Project/IFSI-for-phishing-email-detection/docs/V2_RESEARCH_SPEC_ZH.md) H2).
   - **Zero Silent Dropouts**: Any LLM JSON parse failure or timeout must remain in the denominator with its fail-safe verdict recorded explicitly.

---

## 5. Structural Limitations Caused by Source & Time-Period Differences

1. **Bimodal `15-Year` Temporal Split (`2007` vs. `2021–2025`)**: `trecc07p` captures `2007` server traffic (pre-`DMARC`, pre-modern cloud SaaS), whereas `phishing_pot`, `Untroubled.org`, `IETF`, and `ASF` span `2021–2025`. Pooled summaries mix eras; era-separated reporting (`2007` vs. `2021–2025`) is mandatory.
2. **Public Mailing-List vs. Private Enterprise Inbox Gap**: `IETF` and `ASF` legitimate emails (`65.0%` of Track A legitimate mail) are public engineering/governance discussions rather than private corporate HR, payroll, legal, or vendor-payment correspondence (which are probed instead via controlled synthetic/adapted envelopes in **Track B1**, never merged into Track A).
3. **Residual Within-Track-A Source-Class Asymmetry (`BA_source = 0.9250`)**: Because `85.0%` of Track A phishing (`255 / 300`) originates from contemporary phishing/spam-trap repositories (`phishing_pot` + `Untroubled.org`) while `65.0%` of legitimate mail (`195 / 300`) originates from public `.mbox` lists (`IETF` + `ASF`), **pooled accuracy/MCC/F1 must never be cited without source-stratified FPR and Recall tables**.
4. **Absence of Naturalistic In-the-Wild Prompt Injections**: Real `2007` and `2022–2025` archives rarely contain LLM-targeted prompt injections; injection robustness of `A1` vs `A0` continues to rely on **Track B1** paired clean/injected controls and **Track B2** stress tests rather than natural Track A prevalence.
