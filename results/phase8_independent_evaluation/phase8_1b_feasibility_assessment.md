# Phase 8.1B: Track A `2,000`-Message Feasibility Assessment & Statistical Power Analysis

## 1. Executive Conclusion

A `2,000`-message real-email Track A benchmark (`1,000` Legitimate + `1,000` Phishing) **cannot currently be assembled without silently violating at least one binding scientific or legal requirement** established in [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml), [`docs/V2_RESEARCH_SPEC_ZH.md`](file:///d:/Project/IFSI-for-phishing-email-detection/docs/V2_RESEARCH_SPEC_ZH.md), [`PUBLIC_RELEASE.md`](file:///d:/Project/IFSI-for-phishing-email-detection/PUBLIC_RELEASE.md), or Phase 8.1A.

By contrast, a **smaller `N = 800` Track A Evaluation Corpus (`400` Legitimate + `400` Phishing)**—supported by a disjoint **`N = 200` Validation/Confounding-Audit Partition (`100` Legitimate + `100` Phishing)** across **five genuinely independent raw RFC 822 sources**—satisfies every dataset gate without relaxation, preserves the `40%` per-source cap (`max = 30.0%`), exceeds `minimum_test_records_per_class: 300` by **`+33.3%`**, and delivers high statistical precision for paired McNemar testing between Config A and Config B.

---

## 2. Four Structural Bottlenecks Preventing a Defensible `2,000`-Message Track A Today

### Bottleneck 1 — Absence of Free, Legally Clear, Modern Enterprise Mailbox Corpora
- With **Enron** (`369` active vectors in [`results/rag_index_clean/index.faiss`](file:///d:/Project/IFSI-for-phishing-email-detection/results/rag_index_clean/index.faiss)) and **SpamAssassin** (`4,150` ham consumed in `review_split_seed42`) excluded, **zero open-access, contemporary private corporate mailbox corpora exist in the public domain**.
- **Avocado (`LDC2015T03`)** contains genuine corporate finance/HR/vendor mail (`279` accounts), **but** requires a paid institutional Linguistic Data Consortium membership or `~$2,000–$3,000` license fee, dates to `1999–2002`, and lacks SMTP/DKIM gateway headers because it was extracted from Outlook PSTs.
- **NIST TREC W3C** requires bilateral institutional NIST agreements and dates to `2004`; **FOIA Reading Room** releases are flattened, redacted PDFs without RFC 822 headers.
- Consequently, contemporary open legitimate email with authentic `SPF/DKIM/ARC` headers comes primarily from **public organizational mailing lists** (`IETF`, `ASF`). Scaling `IETF` + `ASF` from `280` (`160 + 120`) up to `700–1,000` messages would flood Track A with technical/standards discussion mail rather than diverse enterprise workflows, degrading **construct validity** for phishing false-positive evaluation.

### Bottleneck 2 — Severe `<5%` True-Phishing Yield Inside Raw Sinkhole Spam & Campaign Deduplication Attrition
- [`docs/V2_RESEARCH_SPEC_ZH.md`](file:///d:/Project/IFSI-for-phishing-email-detection/docs/V2_RESEARCH_SPEC_ZH.md) (§2.2) and [`spamassassin_ham.json`](file:///d:/Project/IFSI-for-phishing-email-detection/data/manifests/spamassassin_ham.json) strictly forbid equating generic spam with phishing (`phishing != spam`).
- In raw live-server and bait sinkhole corpora (`trecc07p` `50,199` spam; `untroubled.org` monthly `.7z` archives), `>95%` of malicious traffic consists of unsolicited bulk commercial spam (pharmaceuticals, SEO, adult/gambling ads, penny stocks) lacking deceptive identity spoofing or credential/financial social engineering.
- Even after isolating candidate phishing lures via automated pre-screening, **phish-kit campaign bursts** typically collapse by `5x–15x` under IFSI's `0.70` 3-shingle/5-shingle Jaccard deduplication gate (max `2` messages per campaign cluster).
- **Operational Calculation**:
  - Assembling `400` test + `100` validation = **`500` unique-campaign, dual-human-verified phishing emails** (`150` from `trecc07p`, `225` from `phishing_pot`, `125` from `untroubled_phish`) already requires inspecting **`~6,000–10,000` raw sinkhole messages** after keyword/structure pre-filtering.
  - Scaling to `1,000` test + `250` validation = **`1,250` unique-campaign phishing emails** without Nazario (`phishing3.mbox` exhausted), `PhishFuzzer` (exhausted & headerless), or composite CSVs (`Zenodo 8339691` / `MeAJOR` contaminated) would require inspecting **`~20,000–30,000+` raw spam captures** or relaxing campaign deduplication—directly violating Phase 8 independence standards.

### Bottleneck 3 — Zero Open Raw-`.eml` Business Email Compromise (BEC) Corpora
- Phase 8.1B investigated academic and industry BEC sources (`APWG eCX`, `MalwareBazaar`, Kaggle/LLM BEC repositories, `IWSPA`).
- Authentic corporate wire-transfer, payroll-diversion, and executive-impersonation BEC emails contain acute victim PII, banking routing details, and active legal privilege; enterprises never release raw `.eml` BEC captures publicly outside closed NDAs (`APWG eCX`). All public "BEC datasets" are LLM-generated or headerless CSVs, which belong strictly in **Track B1**, never Track A.

### Bottleneck 4 — Mathematical Confounding Ceiling When Scaling Single-Class Sources
- As proven in [`phase8_1b_independence_risk_matrix.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1b_independence_risk_matrix.md), if a fraction $\alpha$ of a balanced corpus comes from single-class archives, the Bayes-optimal within-corpus `source_only` balanced accuracy is $\text{BA}^*_{\text{source-only}} = 0.5 + 0.5\alpha$.
- `trecc07p` (`2007`) is the **only** shortlisted open raw RFC 822 corpus containing both classes on the exact same receiving MTA ($\text{BA}_{\text{source-only}} = 0.50$), capped at `<= 40%` (`30.0%` in our design) by [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml). Inflating single-class sources to reach `2,000` messages would not improve de-confounded statistical power; instead, it would widen mailing-list vs. honeypot domain/era skew while multiplying manual annotation risk.

---

## 3. Head-to-Head Comparison: `N = 2,000` Target vs. Recommended `N = 800` Track A Design

| Evaluation Dimension | Naive `N = 2,000` Target (`1,000`L / `1,000`P) | Recommended `N = 800` Track A (`400`L / `400`P + `200` Val) | Gate Requirement (`config/dataset_gates.yaml`) |
| :--- | :--- | :--- | :--- |
| **Legitimate Test Count** | `1,000` *(requires over-sampling OSS mailing lists or paid LDC DUA)* | **`400`** (`120` `trecc07p` + `160` `ietf` + `120` `asf`) | `minimum_test_records_per_class: 300` (**PASS: `+33.3%` margin**) |
| **Phishing Test Count** | `1,000` *(requires relaxing phish-kit dedup or spam boundary)* | **`400`** (`120` `trecc07p` + `180` `phishing_pot` + `100` `untroubled`) | `minimum_test_records_per_class: 300` (**PASS: `+33.3%` margin**) |
| **Disjoint Validation Slice** | `200+` (`100+` per class) | **`200`** (`100` Legitimate + `100` Phishing) | `minimum_validation_records_per_class: 100` (**PASS**) |
| **Max Single-Source Fraction** | Would push `phishing_pot` or `ietf` toward `>40%` | **`30.0%`** (`trecc07p_dual`: `240 / 800`) | `maximum_source_fraction: 0.40` (**PASS: `10 pp` headroom**) |
| **Class Balance** | `50.0% / 50.0%` | **`50.0% / 50.0%`** | `minimum_minority_fraction: 0.20` (**PASS**) |
| **Prior IFSI / RAG Contamination** | High risk if composite/legacy sources added to hit `2,000` | **`0.0%`** (Zero prior IFSI usage across all 5 sources) | Zero training / `rag_index_clean` leakage (**PASS**) |
| **Raw Spam Inspection Burden** | `~20,000–30,000+` raw messages to isolate `1,250` non-spam phish | **`~6,000–10,000` pre-screened messages** (`1,000` final dual-annotated) | Dual human review ($\kappa \ge 0.85$) (**FEASIBLE**) |

---

## 4. Exact Statistical Power & Precision of the `N = 800` Track A Design

### 4.1 95% Wilson Score Confidence Intervals on Proportion Metrics
Using the exact Wilson score interval ($z = 1.9600$):

1. **Pooled Track A Legitimate FPR (`n = 400` Legitimate)**:
   - Observed `0 / 400` (`0.00%` FPR) $\rightarrow$ 95% Wilson CI **`[0.00%, 0.95%]`** (Rule-of-Three one-sided 95% upper bound: **`0.75%`**).
   - Observed `4 / 400` (`1.00%` FPR) $\rightarrow$ 95% Wilson CI **`[0.39%, 2.54%]`** (half-width `~1.08 pp`).
   - Observed `8 / 400` (`2.00%` FPR) $\rightarrow$ 95% Wilson CI **`[1.02%, 3.90%]`**.
2. **Pooled Track A Phishing Recall (`n = 400` Phishing)**:
   - Observed `392 / 400` (`98.00%` Recall) $\rightarrow$ 95% Wilson CI **`[96.10%, 98.98%]`** (half-width `~1.44 pp`).
   - Observed `380 / 400` (`95.00%` Recall) $\rightarrow$ 95% Wilson CI **`[92.40%, 96.74%]`** (half-width `~2.17 pp`).
3. **Unconfounded Dual-Class Anchor (`trecc07p_dual`, `N = 240`: `120` Legit + `120` Phish)**:
   - `0 / 120` (`0.00%` FPR) $\rightarrow$ 95% Wilson CI **`[0.00%, 3.10%]`**; `2 / 120` (`1.67%` FPR) $\rightarrow$ **`[0.46%, 5.87%]`**.
   - `115 / 120` (`95.83%` Recall) $\rightarrow$ 95% Wilson CI **`[90.62%, 98.21%]`**.

### 4.2 Paired McNemar Power (Config B vs. Config A on Identical Emails)
Because frozen Config A (Phase 5 A1-Opt without domain evidence) and frozen Config B (Phase 7 Engine V4 + Domain Analyzer V3) are evaluated on the **exact same `800` Track A messages**, statistical power is governed by **paired discordant predictions $(b, c)$** rather than independent-sample variance:
- If Config B newly detects **`8` sophisticated domain-spoofing phishing emails** missed by Config A with **`0` regressions** ($b = 8, c = 0$), the exact two-sided McNemar test achieves **$p = 2 / 2^8 = 0.0078 < 0.01$** (`+2.00 pp` recall gain on `n = 400`).
- If Config B newly detects **`12` phishing emails** while regressing on **`1`** ($b = 12, c = 1$), exact two-sided McNemar achieves **$p = 0.0034 < 0.01$** (`+2.75 pp` net recall gain).
- Simultaneously, on `n = 400` legitimate emails, non-inferiority within a **`2.0 pp` FPR margin** ([`docs/V2_RESEARCH_SPEC_ZH.md`](file:///d:/Project/IFSI-for-phishing-email-detection/docs/V2_RESEARCH_SPEC_ZH.md) H2) is testable with `>85%` paired power whenever discordant legitimate flips remain $\le 3$.

---

## 5. Inference Runtime & Staged Phase 8.1C Preflight Workload

1. **Inference Compute Feasibility**:
   - Evaluating both Config A and Config B on `N = 800` Track A messages (`1,600` two-stage local Ollama evaluations at `~3–5s` per evaluation) requires **`~1.5–2.2` GPU hours**, making full deterministic single-run execution with zero sampling shortcuts completely practical once preflight passes.
2. **Mandatory Staged Gate Before Any Email Download (Phase 8.1C)**:
   - **Step 1 (Metadata & License Text Only)**: Fetch and SHA-256 hash *only* the plain-text license/policy pages for `rf-peixoto/phishing_pot` (`LICENSE`), `untroubled.org/spam/` (permission notice), `plg.uwaterloo.ca/~gvcormac/treccorpus07/` (TREC usage agreement), `mailarchive.ietf.org` (Note Well / rsync ToS), and `lists.apache.org` (Public Forum Archive Policy).
   - **Step 2 (`25`-Record/Source Dry-Run Pilot)**: Only after Step 1 human legal sign-off, inspect `25` messages per source (`125` total) to validate RFC 822 header completeness, `phishing != spam` yield rates, symmetric `List-*` / `<REDACTED_RECIPIENT>` canonicalization, and `confounding_audit.py` gates before assembling the `200`-record validation and `800`-record test splits.

