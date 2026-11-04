# Phase 8.1C — Sample-Yield Feasibility

## Preflight boundary

This report uses metadata and policy pages only. It does not count downloaded messages, inspect members, scrape archives, or infer phishing from a source name. A “plausible” quota means that the public service appears large enough in principle; it is not a measured post-deduplication yield.

## Phase 8.1B allocation audit

| Source | Test quota | Test fraction | Validation quota | Validation fraction | Quota status |
|---|---:|---:|---:|---:|---|
| TREC 2007 | 240 | 30.00% | 60 | 30.00% | 120/30 phish unsupported; 120/30 ham capacity-plausible |
| `phishing_pot` | 180 | 22.50% | 45 | 22.50% | Phishing repository, but rolling version and usable count unverified |
| IETF | 160 | 20.00% | 40 | 20.00% | Plausible from public archive scale; selected-pool yield estimated |
| ASF | 120 | 15.00% | 30 | 15.00% | Plausible from public archive scale; selected-pool yield estimated |
| Untroubled.org | 100 | 12.50% | 25 | 12.50% | Unlabeled spam archive; phishing quota unsupported |
| **Total** | **800** | **100%** | **200** | **100%** | **Arithmetic only** |

The proposed counts sum correctly to `800` test and `200` validation. No source exceeds the required `0.40` test or validation fraction. However, the proposed phishing counts from TREC and Untroubled.org have no message-level support, and the Phishing Pot, IETF, and ASF counts have no frozen post-deduplication inventory. The proposed class totals (`400`/`400` and `100`/`100`) are therefore not verified.

The allocation is not perfectly source/class-confounded because TREC is assigned both classes. It is nevertheless highly confounded: `560 / 800 = 70%` of test records and `140 / 200 = 70%` of validation records come from single-class sources. A source-only majority rule can obtain approximately `0.85` balanced accuracy on the proposed test allocation (tie handling for TREC stated explicitly), far above the repository’s `0.65` confounding ceiling. This allocation must not be treated as a pooled, source-independent benchmark.

## Source-by-source yield status

| Source | Expected usable volume | Proposed quota | Evidence classification | Blocking condition |
|---|---|---:|---|---|
| TREC ham | `25,220` native ham reported by NIST | 150 ham | Capacity-plausible, not yet sampled | Agreement, deduplication, human legitimacy review |
| TREC phishing | No native count | 150 phish | Unsupported | Dual-human message review must establish actual `C1/C2` yield |
| Phishing Pot | Rolling repository; no pinned count captured | 225 phish | Estimate only | Pin commit, inventory `.eml`, deduplicate campaigns, annotate mixed spam/malware |
| Untroubled | Live bait archive; no frozen count captured | 125 phish | Unsupported | Select archive months, inspect safely, and establish actual `C1/C2` yield |
| IETF | Live archive; exact list/date pool not frozen | 200 legitimate | Estimate only | Freeze lists/dates and review public-list noise, threads, and PII |
| ASF | Live archive; exact list/month pool not frozen | 150 legitimate | Estimate only | Freeze lists/months and exclude bots, spam, and duplicate threads |

## Acquisition-gated yield test

After a separate approval, the minimum pilot should be source-specific and non-destructive: capture only policy/license text first; then, if approved, use a sandboxed small sample sufficient to measure format, empty-body rate, PII exposure, duplicate/campaign clustering, `C1/C2` yield, and `C5` yield. The pilot must record a source member ID and cryptographic hash for every inspected message and must not execute attachments or render URLs.

The acceptance rule is count-based, not wish-based:

1. count only records with an adjudicated `C1`/`C2` or `C5` label;
2. remove exact and near duplicates, repeated campaigns, and cross-source overlaps;
3. split validation before test use, at the campaign/thread/domain grouping level;
4. report `C3`, `C4`, and `C6` counts separately;
5. stop if the accepted count is below the allocation; never backfill by relabeling ordinary spam.

## Yield conclusion

The `800 + 200` design is **not currently feasible as a defensible acquisition target**. A smaller design can be written as a conditional planning envelope, but it cannot be called feasible until the same unresolved license, pinning, independence, and label-yield gates pass.
