# Phase 8.1C — Final Acquisition-Readiness Decision

## Overall decision

> **No defensible acquisition design is currently feasible.**

This is a preflight decision, not a rejection of every source forever. The `800 + 200` arithmetic works and respects the `0.40` source cap, but its class counts depend on unsupported phishing extraction from TREC and Untroubled.org and on unmeasured post-deduplication yields elsewhere. The conditional `600 + 200` envelope is retained as a planning fallback only; it is not approved or feasible until the acquisition gates pass.

## Per-source decisions

| Source | Legal assessment | Technical assessment | Independence assessment | Usable-yield assessment | Decision |
|---|---|---|---|---|---|
| TREC 2007 | Usage agreement not captured or hashed | Public email corpus documented; exact current fields unverified | No source-byte comparison performed | Ham capacity-plausible; phishing unknown | **UNVERIFIED** |
| `phishing_pot` | CC BY-NC 4.0 visible; third-party rights and institutional scope unresolved | `.eml` format and mixed real-mail content documented | Requires hash/near-duplicate audit after approval | Quota is an estimate | **CONDITIONALLY SUITABLE** |
| Untroubled.org | Informal research permission; third-party rights unresolved | p7zip spam archive documented; exact members/headers unverified | Requires cross-source deduplication | Phishing quota unsupported | **CONDITIONALLY SUITABLE** |
| IETF archive | Public-record and Trust framework; exact reuse scope unresolved | Public archive/rsync path documented | Requires source-byte comparison | Legitimate quota is an estimate | **CONDITIONALLY SUITABLE** |
| ASF archive | Public Forum Archive Policy; no blanket message license established | Public mbox path documented | Requires source-byte comparison | Legitimate quota is an estimate | **CONDITIONALLY SUITABLE** |

No source is `READY FOR A SEPARATE ACQUISITION APPROVAL` yet because the required exact legal text, pinned version, and yield evidence are incomplete.

## Allocation audit

### Phase 8.1B proposal

| Source | Test | Test fraction | Validation | Validation fraction |
|---|---:|---:|---:|---:|
| TREC 2007 | 240 | 30.00% | 60 | 30.00% |
| `phishing_pot` | 180 | 22.50% | 45 | 22.50% |
| IETF | 160 | 20.00% | 40 | 20.00% |
| ASF | 120 | 15.00% | 30 | 15.00% |
| Untroubled.org | 100 | 12.50% | 25 | 12.50% |
| **Total** | **800** | **100%** | **200** | **100%** |

The class arithmetic was `400` test / `400` test and `100` validation / `100` validation, but those are assumed counts, not verified accepted labels. The largest source is `30%`, and the allocation is not perfectly confounded because TREC is dual-class. It remains highly source/class-confounded: `70%` of each partition is from single-class sources, with an approximate source-only balanced accuracy of `0.85` under a majority rule. Validation disjointness and independent sampling are **not demonstrated** before acquisition.

### Conditional fallback

The retained fallback is `600` test (`300` legitimate, `300` phishing) plus `200` validation (`100` legitimate, `100` phishing): Phishing Pot `225/75` phishing; TREC `105/35` legitimate plus `45/15` conditional phishing; IETF `105/35` legitimate; ASF `90/30` legitimate; and Untroubled `30/10` conditional phishing. Test and validation source fractions are respectively `37.50%`, `25.00%`, `17.50%`, `15.00%`, and `5.00%` for those five rows. This satisfies the arithmetic source cap, but every conditional phishing count and every live-archive yield still requires evidence.

## Unresolved licensing and governance questions

- TREC: exact Waterloo agreement text, acceptance mechanism, institutional requirements, and redistribution language must be captured and hashed.
- Phishing Pot: pin a commit; verify the exact license at that commit; confirm that non-commercial institutional evaluation is authorized; assess third-party privacy, trademark, and malware risks.
- Untroubled: preserve the permission-page text and hash; determine whether the informal notice covers the intended institution and derived processing; assess third-party rights and PII.
- IETF: freeze the applicable TLP/Note Well version, list/date scope, archive export terms, and the institution’s right to create and retain derived data.
- ASF: establish the legal scope of the Public Forum Archive Policy and mbox export for research processing; do not apply Apache-2.0 to email prose.
- For every source: define local-only storage, retention, deletion, redaction, and whether any message text may be published. Until resolved, set `redistribution_allowed: false`.

## Exact label requirements

No accepted Phase 8.1C message counts exist yet. The required classes are `C1` credential theft/phishing, `C2` financial fraud/impersonation, `C3` malware delivery, `C4` ordinary unsolicited commercial spam, `C5` legitimate email, and `C6` ambiguous. Only `C1/C2` count as phishing; `C3/C4` are not backfill; `C6` is quarantined. Two independent blind annotators and a third adjudicator for disagreements are required, with binary Cohen’s `κ ≥ 0.85`.

## Mandatory next gate — still no download authorization

1. Capture and hash only the five applicable license/policy texts and record their exact URLs and retrieval timestamps.
2. Obtain institutional/legal approval for local processing and non-commercial scope.
3. Pin each source version/list/date window and define the local-only storage boundary.
4. Run an approved, sandboxed, metadata-controlled yield pilot; do not execute or render attachments/URLs.
5. Perform dual annotation, deduplication, cross-source overlap checks, and the independent validation split.
6. Recompute accepted class counts and source fractions. If any quota fails, reduce the design or stop; never relabel ordinary spam.

## Mandatory final audit record

### Files created or modified

The six Phase 8.1C deliverables in this directory were updated:

- `phase8_1c_trec_label_validity_audit.md`
- `phase8_1c_primary_source_legal_verification.md`
- `phase8_1c_sample_yield_feasibility.md`
- `phase8_1c_revised_allocation.md`
- `phase8_1c_statistical_design_review.md`
- `phase8_1c_final_decision.md`

No production implementation, historical dataset, RAG index, or prior Phase 8.1A/8.1B deliverable was modified.

### Source evidence examined

The exact primary URLs are listed in `phase8_1c_primary_source_legal_verification.md`. The key evidence was the NIST TREC 2007 overview; Phishing Pot’s repository/readme/dataset card/license; Untroubled’s archive policy page; IETF open-records, archive, RFC 5378, TLP, and FAQ pages; and ASF’s archive homepage, developer mbox instructions, Public Forum Archive Policy, and Pony Mail documentation.

### Required execution audit

Commands executed and observed exit codes:

| Command | Exit code | Result |
|---|---:|---|
| `python tools/init_phase8.py` | `1` | Not run because Python is unavailable in the shell (`python unavailable`). |
| PowerShell `Get-FileHash -Algorithm SHA256` protected-file audit | `0` | Completed for all listed components. |
| `git status --short` | `0` | Six modified Phase 8.1C reports only; no production/data/index files. |
| `git diff --stat` | `0` | `6 files changed, 329 insertions(+), 371 deletions(-)`. |
| `git diff --check` | `0` | No whitespace errors. |

No dataset was downloaded, scraped, archived, extracted, or ingested. No model inference or benchmark execution was run. No protected file was modified. The primary-source checks used web metadata/policy pages only.

### Protected baseline

The repository’s `tools/init_phase8.py` currently enumerates 13 paths, while the Phase 8 task calls for 12 protected baseline components. The 12 core components required for this audit are listed below; the script’s additional Phase 7 predictions result was also hashed as an extra preservation check. All are present and unchanged:

| Protected component | SHA-256 |
|---|---|
| `src/core/inference.py` | `aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506` |
| `src/core/inference_m4_v2.py` | `fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37` |
| `results/rag_index_clean/index.faiss` | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` |
| `results/rag_index_clean/metadata.json` | `4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece` |
| `src/experiments/phase5_a1_optimization/sanitizer_v2.py` | `b51f938ca3a3b4e2b9f4212d4178b58cd47c3f8b4a48a0ba9a0539be4759aa55` |
| `src/experiments/phase6_domain_evidence/domain_analyzer_v2.py` | `e27aefb062350e758840aedd4ecb5eb29e43ae19b61f228a3c864aa3df59fc44` |
| `src/experiments/phase6_domain_evidence/engine_v3.py` | `dbe5150dc7365b6a560b09f9056129fc24d50e0ebfa13c53719c6336263ae8a8` |
| `src/experiments/phase7_domain_precision/domain_analyzer_v3.py` | `7abde00e3795c7e02504d60ad1f631e101eeefb7b9566c70b73bc02b25f32525` |
| `src/experiments/phase7_domain_precision/engine_v4.py` | `b3c6e9b86d664fc911c82f80e81bff7686cbd2032352fd9326b5e0c40f689b01` |
| `data/evaluation/phase5_regression_160.jsonl` | `325bf42f244120667aa00051ed0e2086b02645958c138699cd3bd32d615fc606` |
| `data/evaluation/phase6_domain_challenge.jsonl` | `02ce51faa1c107e43af3ffee0d2eeff4dcf893b075075ba813896b378556a8a7` |
| `data/evaluation/phase7_precision_challenge.jsonl` | `a6ea7aa12d5bc997939d9cd8c721b728fc6fc22cc2a6aab0ef38912f7fb71c1c` |

Additional protected result audited because it is enumerated by `tools/init_phase8.py`:

`results/phase7_domain_precision/predictions.jsonl` — `2e2efbcacc597afcccd060043618ad33cfc6372d42b23b477c749c804daea724`.
