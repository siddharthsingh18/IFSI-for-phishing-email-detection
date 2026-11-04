# Phase 8.1C — Conditional Revised Allocation

## Decision rule

The Phase 8.1B quotas that are unsupported are rejected. The table below is a **conditional planning envelope**, not authorization and not evidence that the sources can supply the counts. It is the smallest retained design considered here that preserves the repository’s class-size gates while keeping every source at or below `0.40` in both partitions.

## Conditional `600 + 200` envelope

| Source | Test legitimate | Test phishing | Test total | Test fraction | Validation legitimate | Validation phishing | Validation total | Validation fraction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `phishing_pot` | 0 | 225 | 225 | 37.50% | 0 | 75 | 75 | 37.50% |
| TREC 2007 | 105 | 45 | 150 | 25.00% | 35 | 15 | 50 | 25.00% |
| IETF | 105 | 0 | 105 | 17.50% | 35 | 0 | 35 | 17.50% |
| ASF | 90 | 0 | 90 | 15.00% | 30 | 0 | 30 | 15.00% |
| Untroubled.org | 0 | 30 | 30 | 5.00% | 0 | 10 | 10 | 5.00% |
| **Total** | **300** | **300** | **600** | **100%** | **100** | **100** | **200** | **100%** |

Arithmetic checks:

- test: `300 + 300 = 600`; validation: `100 + 100 = 200`;
- maximum source fraction is `37.50%`, below `maximum_source_fraction: 0.40`;
- both classes meet the configured minimums only if every conditional phishing quota is actually accepted;
- test and validation are disjoint only after campaign/thread/domain grouping and a frozen split;
- the allocation is not perfectly source/class-confounded because TREC contains both classes, but the source-only balanced accuracy remains high (approximately `0.925` under a TREC-majority source rule), so pooled results require source-stratified reporting.

## Why this is not yet feasible

The `225 + 75` Phishing Pot counts are estimates because no commit or inventory was pinned. The `45 + 15` TREC counts have no native phishing support. The `30 + 10` Untroubled counts are also unsupported because the source is an unlabeled spam archive. The legitimate quotas from IETF and ASF are plausible from their public archive mechanisms but are not measured after list/thread/domain filters. The conditional table therefore cannot be promoted to an approved acquisition plan.

## Hard stop and no-inflation rule

After approval, if any source fails its accepted quota, do not reclassify `C3`, `C4`, or `C6` as phishing; do not relax the `0.40` source cap; do not merge validation into test; and do not substitute historical IFSI data. Reduce the benchmark to the accepted counts or stop acquisition and seek a new separately licensed source. Any resulting class or source imbalance must be reported exactly.

## Required split protocol

Validation is sampled independently before the test set is frozen. Group by exact hash, normalized near-duplicate shingles, campaign/URL infrastructure, mailing-list thread identifiers, and sender/domain clusters where applicable. The split must be disjoint at the message, thread, and campaign levels, and the final manifest must record source member IDs and hashes without publishing message text.
