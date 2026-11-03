# Phase 8.1C: Final Shortlisted Source Readiness & Track A Preflight Decision

## 1. Separate Four-Axis Readiness Assessment (Per Shortlisted Source)

Per Phase 8.1C governance rules, **legal clearance**, **technical suitability**, **independence**, and **usable sample yield** are assessed independently for every shortlisted candidate. **Zero files or archives have been downloaded.**

| Shortlisted Source | 1. Legal Clearance | 2. Technical Suitability | 3. Independence Status | 4. Usable Sample Yield (`Revised 600+200`) | **Final Per-Source Readiness Decision** |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **`rf-peixoto/phishing_pot`** (https://github.com/rf-peixoto/phishing_pot) | **UNCLEARED PENDING APPROVAL** — `CC BY-NC 4.0` documented; must hash pinned `LICENSE`, confirm `NC` scope, and keep bodies local-only (`redistribution_allowed: false`). | **SUITABLE** — Raw `.eml` wire format (`SPF`/`DKIM`/`DMARC`, MIME, URLs); must normalize `To: phishing@pot` to `<REDACTED_RECIPIENT>` & strip attachments. | **INDEPENDENT** — `0%` prior IFSI overlap; run SHA-256 + `0.70` shingle dedup at ingestion. | **PLAUSIBLE (`225` test + `75` val = `300` phish)** — `<2.5%` of `12,000+` `.eml` files; requires 6-class human filter (`C1/C2` vs `C4`) + campaign dedup. | **`READY FOR A SEPARATE ACQUISITION APPROVAL`** |
| **IETF Public Mail Archive** (https://mailarchive.ietf.org/) | **UNCLEARED PENDING APPROVAL** — Public under `BCP 78` (`RFC 5378`) & TLP; author prose copyright retained (`redistribution_allowed: false`); hash `rsync`/TLP terms first. | **SUITABLE** — Official `.mbox`/`rsync` (`rsync.ietf.org`, no scraping) with `DKIM`/`ARC`; strip `List-*` & mask `<REDACTED_RECIPIENT>` + signature PII. | **INDEPENDENT** — `0%` prior IFSI overlap on `2021–2025` slice. | **EVIDENCE-BASED (`105` test + `35` val = `140` legit)** — `<0.15%` of `>100k` `2021–2025` messages (`1`/thread, max `3`/domain). | **`READY FOR A SEPARATE ACQUISITION APPROVAL`** |
| **ASF Public Mail Archives** (https://lists.apache.org/) | **UNCLEARED PENDING APPROVAL** — ASF Public Forum Archive Policy (`public-archives.html`); author prose copyright retained (`redistribution_allowed: false`); hash policy first. | **SUITABLE** — `.mbox` with `SPF`/`DKIM`; exclude `jira@`/`gitbox@`/CI bots, strip `List-*`, and scrub PII. | **INDEPENDENT** — `0%` prior IFSI overlap on `2021–2025` slice (`spamassassin_ham` is `2002–2003`). | **EVIDENCE-BASED (`90` test + `30` val = `120` legit)** — `<0.15%` of human governance/security/ops threads. | **`READY FOR A SEPARATE ACQUISITION APPROVAL`** |
| **NIST / Waterloo `TREC 2007` (`trec07p`)** (https://plg.uwaterloo.ca/~gvcormac/treccorpus07/) | **UNCLEARED PENDING APPROVAL** — Waterloo TREC Spam Usage Agreement (`NC` research, no redistribution); must capture/hash gateway agreement & confirm institutional sign-off. | **CONDITIONAL** — Raw RFC 2822 (`inmail.*`), single MTA, **but** `2007` pre-DMARC era, heavy `2007` image/PDF spam, and disused/honeypot `spam` accounts requiring `<REDACTED_RECIPIENT>`. | **INDEPENDENT** — `0%` prior IFSI overlap. | **MIXED**: `ham` (`105+35=140`) **evidence-based** (`25,220` `ham`); `phish` (`120+30` **rejected**; revised `45+15=60` **conditional estimate** requiring `0.12%` yield across `50,199` `spam` via 6-class dual human review). | **`CONDITIONALLY SUITABLE`** |
| **`Untroubled.org` Bait Archive** (http://untroubled.org/spam/) | **UNCLEARED PENDING APPROVAL** — Informal R&D permission notice over plain `http://` (no SPDX; third-party sender copyright/PII uncleared; `redistribution_allowed: false`). | **CONDITIONAL** — Raw RFC 822 in `.7z` archives; `>95%` ordinary bulk spam (`C4`) + live malware payloads requiring isolated sandbox & attachment stripping. | **INDEPENDENT** — `0%` prior IFSI overlap; must cross-deduplicate `2022–2025` waves against `phishing_pot`. | **CONDITIONAL ESTIMATE** — Phase 8.1B `100+25=125` phish **rejected**; revised `30` test + `10` val = `40` verified phish (`<0.04%` of `2022–2025` bait volume) requires manual 6-class extraction. | **`CONDITIONALLY SUITABLE`** |

---

## 2. Formal Overall Phase 8.1C Preflight Decision

Out of the three permitted overall decisions:
- *The 800 + 200 design is feasible.*
- *A smaller source-diverse design is feasible.*
- *No defensible acquisition design is currently feasible.*

**Selected Overall Decision:**

> **`A smaller source-diverse design is feasible.`**

### Why `The 800 + 200 design is feasible` Was Rejected
1. Phase 8.1B's `800 + 200` design required **`120 + 30 = 150` unique phishing records from `TREC 2007`** and **`100 + 25 = 125` unique phishing records from `Untroubled.org`** (`275 / 500 = 55.0%` of all phishing across Test + Validation) from two general spam corpora with **`0` native phishing labels** and no published phishing counts.
2. Presenting `TREC 2007` as a `120 / 120` balanced phishing benchmark misrepresented an `Apr–Jul 2007` general spam dataset dominated by commercial/image/PDF spam.

### Why `A smaller source-diverse design is feasible` (`600` Test + `200` Disjoint Validation) Is Justified
1. Down-scoping Test to **`N_test = 600` (`300` Legitimate + `300` Phishing)** alongside **`N_val = 200` (`100` Legitimate + `100` Phishing)** satisfies **every bound in [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml)** without relaxing `maximum_source_fraction: 0.40` (`max = 37.50%` in both Test and Validation).
2. Unverified spam-archive phishing reliance is cut by **`63.6%`** (`275 -> 100` total: `45 + 15 = 60` conditional from `50,199` `TREC` spam [`0.12%`] and `30 + 10 = 40` conditional from `>100,000` `Untroubled.org` spam [`<0.04%`]), while `TREC 2007` is restored to a legitimate-majority (`70%` `ham` / `30%` verified phishing) server slice.
3. Paired McNemar power (`A0` vs `A1` and `Config A` vs `Config B`) remains high (`>= 6` zero-loss discordant flips significant at $p = 0.031 < 0.05$; class-level 95% Wilson CIs widen by only `0.20–0.35 pp` relative to `N = 800`).

---

## 3. Preserved Protections & Mandatory Pre-Acquisition Authorization Gate

1. **Zero Downloads Executed**: Nothing has been downloaded, scraped, or ingested in Phase 8.1C.
2. **Prior Decisions Preserved**: All Phase 8.1A (`phase8_1a_*.md`) and Phase 8.1B (`phase8_1b_*.md`) deliverables remain intact; **Enron** and **Jose Nazario** remain on acquisition hold; **Track B1** and **Track B2** remain strictly separated from Track A.
3. **Mandatory Separate Acquisition Approval Checklist (Before Any Bytes Are Fetched)**:
   - Obtain human legal/PI sign-off after capturing verbatim texts + SHA-256 hashes of all five upstream license/policy documents (`phishing_pot` `LICENSE` at pinned commit; Waterloo `trec07p` Usage Agreement; `untroubled.org/spam/` R&D notice; IETF TLP/`rsync` terms; ASF `public-archives.html`).
   - Execute dual-analyst 6-class blind annotation (`C1`–`C6`, $\kappa_{\text{binary}} \ge 0.85$) and enforce the **Hard Stop Contingency Rule** in [`phase8_1c_revised_allocation.md`](file:///d:/Project/IFSI-for-phishing-email-detection/results/phase8_independent_evaluation/phase8_1c_revised_allocation.md) if `TREC 2007` or `Untroubled.org` falls short of its reduced conditional phishing ceiling (`60` and `40` records).

