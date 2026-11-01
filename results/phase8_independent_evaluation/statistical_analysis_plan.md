# Phase 8.0: Statistical Analysis & Hypothesis Testing Plan

## 1. Executive Summary & Epistemic Rationale

Evaluating security classification systems requires rigorous statistical methodologies that extend far beyond raw point-estimate accuracy. In enterprise email security:
1. **Accuracy is an Insufficient Metric**: An email gateway operating on a 95% legitimate / 5% phishing distribution can achieve 95% accuracy by classifying every message as legitimate, completely failing its operational security function.
2. **Asymmetric Operational Costs**: A false positive (blocking legitimate executive or business payroll communication) disrupts corporate operations and incurs immediate user friction. A false negative (delivering a sophisticated BEC wire-fraud email or active prompt injection) exposes the enterprise to catastrophic financial theft or infrastructure compromise.
3. **Paired Design Efficiency**: Evaluating Config A and Config B on identical $N = 3,000$ inputs removes inter-sample variance, enabling high-powered paired statistical significance testing.

---

## 2. Formal Research Hypotheses

Phase 8 formulates three primary two-tailed hypotheses:

### Hypothesis 1: Classification Superiority (False Positive Reduction)
- **Null Hypothesis ($H_{0,1}$)**: The probability of correct classification under Config B equals that of Config A ($P(\text{Correct}_B) = P(\text{Correct}_A)$).
- **Alternative Hypothesis ($H_{1,1}$)**: Config B achieves a statistically significant reduction in discordant false positive errors compared to Config A ($P(\text{Correct}_B) > P(\text{Correct}_A)$), driven by Domain Analyzer V3's precision improvements.
- **Test**: Two-sided **McNemar's Test with continuity correction** ($\alpha = 0.01$).

### Hypothesis 2: Non-Inferiority of Phishing Recall
- **Null Hypothesis ($H_{0,2}$)**: Config B's recall on sophisticated phishing is inferior to Config A by more than a non-inferiority margin $\delta = 0.01$ ($R_A - R_B \ge 0.01$).
- **Alternative Hypothesis ($H_{1,2}$)**: Config B preserves non-inferior recall on sophisticated phishing ($R_A - R_B < 0.01$).
- **Test**: One-sided **Farrington-Manning non-inferiority test** ($\alpha = 0.01$).

### Hypothesis 3: End-to-End Latency Acceleration
- **Null Hypothesis ($H_{0,3}$)**: The median paired latency difference between Config A and Config B is zero ($\tilde{D} = 0$).
- **Alternative Hypothesis ($H_{1,3}$)**: Config B exhibits lower latency due to concise Stage 2 reasoning traces ($\tilde{D} < 0$).
- **Test**: Two-sided **Wilcoxon Signed-Rank Test** ($\alpha = 0.01$).

---

## 3. Statistical Testing Methodology

### 3.1 McNemar's Test for Paired Binary Classifications
For the $2 \times 2$ contingency table of paired predictions:

```
                  Config B Correct    Config B Incorrect
Config A Correct         n_11                n_10
Config A Incorrect       n_01                n_00
```

Where:
- $n_{11}$: Both configurations correct.
- $n_{00}$: Both configurations incorrect.
- $n_{01}$: Config B correct, Config A incorrect (Config B improvement).
- $n_{10}$: Config A correct, Config B incorrect (Config B regression).

The continuity-corrected McNemar test statistic is:
$$\chi^2 = \frac{(|n_{01} - n_{10}| - 1)^2}{n_{01} + n_{10}} \sim \chi^2(1)$$
A significance threshold of $p < 0.01$ is enforced.

---

### 3.2 Confidence Interval Estimation (Wilson Score Interval)
Point estimates for Accuracy, Precision, Recall, FPR, and FNR must be accompanied by **95% Wilson Score Confidence Intervals**, which maintain statistical validity near the boundaries ($p \approx 0$ or $p \approx 1$):
$$w = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
Where $z = 1.95996$ for a 95% two-sided confidence interval.

---

### 3.3 Statistical Power & Sample Size Justification ($N = 3,000$)

| Sub-Cohort | Sample Count ($N$) | Target Effect Size | Significance Level ($\alpha$) | Statistical Power ($1 - \beta$) | Audit Feasibility |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Entire Benchmark Suite** | **3,000** | $\Delta \text{Acc} \ge 1.0\%$ | $\alpha = 0.01$ | **$> 0.999$** | High statistical resolution across full traffic. |
| **Difficult Legitimate Sub-Cohort**| **600** | $\Delta \text{FPR} \ge 2.5\%$ | $\alpha = 0.01$ | **$> 0.995$** | Fully powered to validate false positive elimination. |
| **Sophisticated Phishing Sub-Cohort**| **450** | Non-inferiority $\delta = 1.0\%$ | $\alpha = 0.01$ | **$> 0.960$** | High power to confirm zero degradation of attack detection. |
| **Prompt Injection Sub-Cohort** | **300** | $\Delta \text{Containment} \ge 2.0\%$ | $\alpha = 0.01$ | **$> 0.920$** | Sufficient power to verify active injection defense. |

---

## 4. Mandatory Disaggregated Reporting Protocol

All Phase 8 evaluation metrics must be reported along four orthogonal axes:

1. **By Attack / Legitimate Category**:
   - Ordinary Legitimate ($N=900$)
   - Difficult Legitimate ($N=600$)
   - Conventional Phishing ($N=750$)
   - Sophisticated Phishing ($N=450$)
   - Active Prompt Injection ($N=150$)
   - Quoted Benign Injection ($N=150$)
2. **By Industry Sector**:
   - Technology vs Financial Services vs Healthcare vs Higher Ed vs Manufacturing.
3. **By Origin Type**:
   - `real_world_unmodified` vs `real_world_anonymized` vs `adapted_template` vs `synthetic_adversarial`.
4. **By Message Formatting**:
   - Plain text RFC822 vs Multipart MIME (HTML/Text).

