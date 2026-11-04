# Phase 8.1C — Statistical Design Review

## Interpretation boundary

Neither `800` test messages nor the conditional `600` test messages establish universal real-world generalization. The proposed sources mix a single-server 2007 spam corpus, contemporary honeypot/bait captures, and public technical mailing lists. Results must be described as performance on the frozen sampled strata, not as performance on private enterprise inboxes or all phishing.

## Precision of the planned binary metrics

For any accepted binary sample, report accuracy, legitimate false-positive rate (FPR), phishing recall, false-negative rate (FNR), precision, and MCC with two-sided 95% Wilson intervals. The following are design illustrations, not observed results:

| Quantity | `N=800` design | Conditional `N=600` design | `N=200` validation |
|---|---:|---:|---:|
| Balanced classes | 400 / 400 | 300 / 300 | 100 / 100 |
| Accuracy CI half-width near 95% | ~1.5 percentage points | ~1.8 pp | ~3.0 pp |
| Zero-FP upper 95% bound for FPR | ~0.95% (`n=400`) | ~1.26% (`n=300`) | ~3.62% (`n=100`) |
| Recall CI at 95% observed recall | about 92.4–96.7% | about 91.9–97.0% | about 88.8–97.9% |

The validation sample is useful for parser/canonicalization and pre-registered gate checks, but its `n=100` per class is too small for precise confirmatory subgroup claims. Thresholds and prompts must not be tuned on it and then presented as test-set confirmation.

## Source-stratified reporting

Report at least three views:

1. a dual-class TREC slice, if actual `C1/C2` records are established, with accuracy, FPR, recall, MCC, and paired comparisons;
2. per-source legitimate FPR and phishing recall, with exact denominators and Wilson intervals;
3. a pooled summary only alongside the first two tables and an explicit source/time-period confounding warning.

Subtype recall (`C1` credential theft, `C2` financial fraud/impersonation, and any pre-registered finer subtype) is reportable only with the observed subtype counts. No expected subtype proportions may be presented as results. Subgroups below roughly 30 records are exploratory and will have wide intervals.

## Paired A0 versus A1 comparisons

Every candidate must classify the exact same frozen record IDs. Use paired differences, not independent-proportion tests, for A0 versus A1 (and any pre-registered Config A versus Config B comparison). Report the discordant-pair table and exact two-sided McNemar p-value. With zero regressions, six discordant wins give `p = 2 * (1/2)^6 = 0.03125`; this is a minimum-significance illustration, not a power guarantee. Power depends on the number and direction of discordant pairs and is reduced by campaign/thread clustering.

Use a pre-specified multiplicity rule for co-primary endpoints and a cluster-aware bootstrap or other declared resampling method for confidence intervals. Keep parser failures, timeouts, and fail-safe outputs in the denominators. Do not run inference during this phase.

## Limitations that must accompany results

- TREC is 2007 and its native label is spam/ham, not phishing; any phishing subset is human-annotated and potentially selected.
- Public IETF and ASF mail is technical/governance correspondence, not a representative sample of private HR, payroll, procurement, legal, or executive mail.
- Honeypot and bait sources select for address exposure and attacker behavior and may repeat campaigns.
- Header canonicalization can remove useful operational signals while leaving residual source cues; report the exact transformation.
- Source-only performance can be high even when the benchmark is not perfectly confounded. Pooled accuracy is therefore not sufficient evidence of cross-source generalization.
- A balanced test set estimates conditional class performance, not deployment prevalence or population-level precision.

## Statistical verdict

`N=800 + 200` would provide useful aggregate precision only if the source quotas, labels, legal permissions, independence, and disjoint split were first verified. The conditional `600 + 200` envelope is a reasonable planning target with modestly wider intervals, but neither design is currently executable as a defensible acquisition plan because the required source yields and TREC phishing labels remain unverified.
