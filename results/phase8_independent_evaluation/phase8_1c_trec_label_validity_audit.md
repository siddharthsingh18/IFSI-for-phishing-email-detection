# Phase 8.1C — TREC 2007 Label-Validity Audit

## Scope and evidence boundary

This is a metadata-only preflight. No corpus archive, message file, index, attachment, or email body was downloaded or ingested. The official Waterloo page was examined as the requested source, but its current redirect to `cormack.uwaterloo.ca` was not retrievable in this environment. The corpus facts below therefore use the primary TREC 2007 overview published by NIST and the Waterloo source URL; they do not substitute a downloaded corpus inspection.

Primary evidence examined:

- <https://plg.uwaterloo.ca/~gvcormac/treccorpus07/>
- <https://trec.nist.gov/pubs/trec16/papers/SPAM.OVERVIEW16.pdf>
- <https://pages.nist.gov/trec-browser/trec16/spam/proceedings/>

## Confirmed native composition

The NIST overview reports that `trec07p` is a public corpus of `75,419` chronologically ordered messages delivered to one server from 8 April through 6 July 2007:

| Native class | Count | Fraction | Meaning in the source |
|---|---:|---:|---|
| `ham` | 25,220 | 33.44% | Non-spam / ham |
| `spam` | 50,199 | 66.56% | Spam |
| **Total** | **75,419** | **100%** | **TREC public corpus** |

The source is a spam-filtering benchmark. Its native gold standard is binary `ham` versus `spam`; it has no native `phishing` class and no published message-level phishing count. The overview says that the public corpus contains messages delivered to a particular server, includes disused accounts and web-published honeypot accounts, and was unaltered except for a few systematic name substitutions. The same overview says that messages and an index of their gold-standard judgments were supplied to participants.

What remains unconfirmed without an authorized acquisition is the exact current archive layout, exact header set in every message, and whether any local packaging has changed. The overview is consistent with original message files and headers, but that is not a license to claim that every RFC 5322 field is present or intact.

## Phishing cannot be inferred from `spam`

`spam` is not synonymous with phishing. A `spam` record may be ordinary advertising, pharmaceutical or adult promotion, SEO spam, image spam, stock promotion, malware delivery, or an actual credential or financial lure. The native label does not distinguish these cases. Therefore:

- every `spam` record is **unverified for phishing** until a message-level review establishes deceptive identity or financial impersonation and the relevant action request;
- ordinary unsolicited commercial spam must not be relabeled as phishing or legitimate;
- malware delivery is not automatically phishing; it is phishing only if independent message evidence also satisfies the phishing definition;
- the proposed `120` TREC phishing test messages plus `30` validation messages are not supported by the native corpus metadata and are rejected as a quota;
- the proposed `120` TREC legitimate test messages plus `30` validation messages are a capacity-plausible ham draw (`150 / 25,220 = 0.595%`), subject to deduplication and review.

The number of actual, unique-campaign phishing messages in `trec07p` is **unknown** until an approved acquisition and manual review. No percentage, lower bound, or substitute quota is asserted here.

## Required six-class annotation taxonomy

The taxonomy is applied to the message and available headers, not to the native TREC label alone.

| Code | Class | Positive evidence / disposition |
|---|---|---|
| `C1` | Credential theft / phishing | Deceptive identity or trusted-brand impersonation plus a request for credentials, login, password, PIN, account verification, or session information through a link, form, or reply path. Include as binary phishing. |
| `C2` | Financial fraud / impersonation | Deceptive identity, authority, or relationship used to induce payment, wire transfer, invoice diversion, card/bank disclosure, tax/escrow payment, or advance-fee action. Include as binary phishing. |
| `C3` | Malware delivery | Malicious attachment, exploit, or payload delivery without independently demonstrated `C1`/`C2` evidence. Exclude from the binary benchmark; never promote by default. |
| `C4` | Ordinary unsolicited commercial spam | Bulk ads, newsletters, pharmaceuticals, adult/SEO, casino, stock promotion, or similar mail without deceptive credential or financial action. Exclude; never map to phishing or legitimate. |
| `C5` | Legitimate email | Benign personal, administrative, academic, or operational correspondence; must also pass the independent review and contamination checks. Include as legitimate. |
| `C6` | Ambiguous | Evidence is incomplete, image-only, truncated, unavailable, or the reviewers cannot establish intent. Quarantine and exclude from binary denominators. |

`C1` and `C2` are the only positive phishing classes. `C3` and `C4` are retained in the audit log so that the source’s spam composition is not hidden.

## Two-annotator and adjudication protocol

1. Two trained annotators independently label every candidate using the six classes and record short evidence codes (identity target, action requested, URL/form/reply evidence, and uncertainty). They do not see one another’s labels or any A0/A1/model output. Link rendering, active attachment execution, and external network access are prohibited.
2. Report six-class agreement and binary agreement (`C1/C2` versus `C5` after exclusions). The hard binary gate is Cohen’s `κ ≥ 0.85`; a failure pauses allocation.
3. `C1`/`C1`, `C2`/`C2`, or `C1`/`C2` becomes phishing, with subtype resolved by a senior adjudicator. `C5`/`C5` becomes legitimate. `C3`/`C3` and `C4`/`C4` are excluded. `C6`/`C6` is quarantined.
4. Any disagreement crossing binary polarity (`C1/C2` versus `C5`) is reviewed by a third adjudicator. Without explicit message-level evidence, the result defaults to `C6` or an exclusion, never to phishing.
5. Campaign, thread, and near-duplicate controls are applied before the test/validation split. A shortfall is reported as a shortfall; it is not filled with `C3`, `C4`, synthetic mail, or a relaxed deduplication rule.

## TREC verdict

TREC 2007 is technically useful as a same-server historical spam/ham source and as a possible legitimate-mail stratum. It is **not a verified phishing source**. The proposed dual-class TREC core is not currently defensible as `120` phishing plus `120` legitimate. The phishing side remains **UNVERIFIED** pending authorized acquisition and message-level annotation.
