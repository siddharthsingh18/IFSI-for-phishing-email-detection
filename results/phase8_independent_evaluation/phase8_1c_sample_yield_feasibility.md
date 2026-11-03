# Phase 8.1C: Sample-Yield Feasibility & Quota Verification Audit

## 1. Analytical Principle: Confirmed Capacity vs. Estimated Post-Filter Yield

Because Phase 8.1C strictly prohibits downloading archives or inspecting raw messages, every proposed sample quota must be audited across **four sequential attrition stages**:
1. **Stage A — Confirmed Upstream Raw Volume**: Verified from primary-source documentation or published benchmark papers.
2. **Stage B — Format & Parseability Attrition**: Losses from empty/image-only/PDF-only bodies (`2007` image spam), automated bot traffic (`ASF` Jira/GitHub notifications), or binary-only malspam.
3. **Stage C — Class-Purity Attrition (`Phishing != Spam`)**: Losses when separating genuine deceptive phishing (`C1` Credential Theft + `C2` Financial Fraud/Impersonation) from ordinary unsolicited commercial spam (`C4`), malware-only delivery (`C3`), and `Ambiguous` items (`C6`).
4. **Stage D — Deduplication & Thread/Domain Cap Attrition**: Losses under IFSI's `0.70` 3-shingle/5-shingle Jaccard near-duplicate clustering (max `2` messages per phishing campaign cluster; max `1` message per mailing-list reply thread; max `3` legitimate messages per sender domain).

> [!IMPORTANT]
> **Conservative Decision Rule**: If a source's proposed quota relies on an unverified assumption about Stage C (`phishing` yield inside general `spam`) or Stage D (unique phishing campaigns), **that quota is classified as `MERELY ESTIMATED` and rejected if aggressive**.

---

## 2. Source-by-Source Sample-Yield Audit

### 2.1 `TREC 2007 Public Corpus` (`trec07p`)
- **Confirmed Raw Volume**: `75,419` messages (`25,220` `ham` + `50,199` `spam`, `Apr 8 – Jul 6, 2007`).
- **Legitimate (`ham`) Yield Assessment (`Phase 8.1B: 120 test + 30 val = 150`)**:
  - *Classification*: **EVIDENCE-BASED**.
  - *Math*: `25,220` messages carry human-adjudicated `ham` labels in `full/index`. Even if `80%` of `ham` is removed by thread deduplication (max `1`/thread), mailing-list filtering, and empty-body checks, `~5,000+` distinct legitimate messages remain—over **`33x`** the required `140–150` messages (`<0.6%` of raw `ham`).
- **Phishing (from `spam`) Yield Assessment (`Phase 8.1B: 120 test + 30 val = 150`)**:
  - *Classification*: **MERELY ESTIMATED — PHASE 8.1B QUOTA (`150`) REJECTED**.
  - *Math & Risk*: `full/index` contains **zero** phishing labels. Mid-2007 botnet spam (`50,199` messages on one server over 89 days) was heavily dominated by inline GIF/PNG image spam (unparseable as text) and penny-stock/pharma bulk campaigns. Suppose raw text-parseable phishing is `1.0%–2.0%` (`500–1,000` raw messages), **but** single-server 2007 bank/PayPal/eBay waves exhibit `10x–20x` template repetition (`50–100` unique clusters, yielding at most `50–100` usable records after `Ambiguous` dead-link exclusions). Counting on `150` high-confidence unique phishing emails risks exhausting genuine phishing and pressuring annotators to stretch `C4`/`C6` boundaries.
  - *Conservative Ceiling*: Slashed by **`60%`** to **`45` Test + `15` Validation = `60` verified phishing** (requiring only **`0.12%`** usable yield across `50,199` spam—`30` unique campaign clusters at max `2`/cluster), and marked **strictly conditional** on post-approval manual audit.

---

### 2.2 `rf-peixoto/phishing_pot`
- **Confirmed Raw Volume**: `12,000+` sequential `.eml` files in `email/sample-*.eml` (`~7,900+` already present by 2024; rolling `2022–2025/2026`).
- **Phishing Yield Assessment (`Phase 8.1B: 180 test + 45 val = 225` $\rightarrow$ `Phase 8.1C: 225 test + 75 val = 300`)**:
  - *Classification*: **EVIDENCE-SUPPORTED CAPACITY / PLAUSIBLE POST-DEDUP ESTIMATE** (requires message-level campaign-cluster confirmation after approval).
  - *Math*: Unlike `trec07p` and `Untroubled.org`, `phishing_pot` is a **purpose-built phishing `.eml` corpus**. Even under a highly conservative attrition cascade:
    - Raw `.eml` files (`2022–2025`): `10,000+`
    - Minus `25%` residual non-phishing spam (`C4`), malspam-only (`C3`), or empty/corrupt MIME: `7,500` true phishing `.eml` files (`C1`/`C2`)
    - Minus `10x` phish-kit campaign deduplication (`0.70` shingle Jaccard, max `2`/cluster) + `Ambiguous` (`C6`) quarantine: **`~750–1,500` usable phishing records**—providing **`2.5x–5.0x` safety margin** over the revised **`300`-record (`225` test + `75` val, `37.50%` of Track A)** quota (`<3.0%` of raw corpus).

---

### 2.3 `Untroubled.org` Bait Sinkhole Archive
- **Confirmed Raw Volume**: Multi-year monthly `.7z` spam-trap archives (`1998–2025/2026`; hundreds of thousands of raw spam messages across `2022–2025`).
- **Phishing Yield Assessment (`Phase 8.1B: 100 test + 25 val = 125`)**:
  - *Classification*: **MERELY ESTIMATED — PHASE 8.1B QUOTA (`125`) REJECTED**.
  - *Math & Risk*: Academic studies confirm `untroubled.org/spam` is an **indiscriminate raw spam-trap archive** with `0` native phishing labels and `>95%` ordinary commercial/SEO/lottery/pharma spam (`C4`), plus potential cross-sinkhole campaign overlap with `phishing_pot` over `2022–2025`. Requiring `125` unique-campaign phishing records (disjoint from `phishing_pot`) would demand manual inspection of `~5,000–12,000` raw spam files with high malware-handling overhead.
  - *Conservative Ceiling*: Slashed by **`68%`** to **`30` Test + `10` Validation = `40` verified phishing** (`5.00%` of Track A), serving purely as a secondary contemporary sinkhole diversity slice conditional on sandboxed post-approval inspection.

---

### 2.4 `IETF Public Mail Archive` (`mailarchive.ietf.org` / `rsync.ietf.org`)
- **Confirmed Raw Volume**: `>100,000` `.mbox` messages in `2021–2025` alone across `100+` active working groups and operational/administrative lists.
- **Legitimate Yield Assessment (`Phase 8.1B: 160 test + 40 val = 200` $\rightarrow$ `Phase 8.1C: 105 test + 35 val = 140`)**:
  - *Classification*: **EVIDENCE-BASED** (for public multi-organization technical/administrative correspondence).
  - *Math*: Even after enforcing `1` message per reply thread (`Subject:` stem / `In-Reply-To:` tree), max `3` messages per sender domain (`@google.com`, `@cloudflare.com`, `@microsoft.com`, `@cisco.com`, `@akamai.com`, universities, NICs), and excluding automated secretariat announcements, `>5,000` independent threads remain (`>35x` safety margin over `140` records).

---

### 2.5 `Apache Software Foundation Public Mail Archives` (`lists.apache.org`)
- **Confirmed Raw Volume**: `>100,000` `.mbox` messages across `350+` ASF project, security, incubator, and community governance lists (`2021–2025`).
- **Legitimate Yield Assessment (`Phase 8.1B: 120 test + 30 val = 150` $\rightarrow$ `Phase 8.1C: 90 test + 30 val = 120`)**:
  - *Classification*: **EVIDENCE-BASED** (after deterministic bot filtering).
  - *Math*: Although raw developer lists contain heavy automated traffic (`jira@apache.org`, `gitbox@apache.org`, `dependabot`, CI notifications—often `60%–75%` of raw volume on dev lists), sampling human-authored posts across foundation-wide governance/operations/security/user lists (`community`, `incubator-general`, `security-discuss`, `legal-discuss`, release VOTE/DISCUSS threads) leaves `>10,000` human threads (`>80x` safety margin over `120` records).

---

## 3. Master Sample-Yield & Quota Audit Summary

| Source | Target Class | Confirmed Raw Pool | Phase 8.1B Quota (`Test + Val`) | Quota Evidence Status | Phase 8.1B Quota Decision | Phase 8.1C Revised Quota (`Test + Val`) | Required Effective Yield |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **`TREC 2007` (`ham`)** | Legitimate (`C5`) | `25,220` adjudicated `ham` | `120 + 30 = 150` | **Evidence-Based** | Scaled to `N=600` | **`105 + 35 = 140`** | `0.56%` of `ham` |
| **`TREC 2007` (`spam`)** | Phishing (`C1/C2`) | `50,199` unlabeled `spam` | `120 + 30 = 150` | **Merely Estimated** | **REJECTED** | **`45 + 15 = 60`** *(conditional)* | `0.12%` of `spam` |
| **`phishing_pot`** | Phishing (`C1/C2`) | `12,000+` phishing `.eml` | `180 + 45 = 225` | **Capacity-Confirmed / Dedup Estimated** | **Accepted & Reweighted (`<= 37.5%`)** | **`225 + 75 = 300`** | `<2.50%` of `.eml` pool |
| **`Untroubled.org`** | Phishing (`C1/C2`) | `>100k` `2022–2025` bait `spam` | `100 + 25 = 125` | **Merely Estimated** | **REJECTED** | **`30 + 10 = 40`** *(conditional)* | `<0.04%` of bait pool |
| **`IETF Archives`** | Legitimate (`C5`) | `>100k` `2021–2025` `.mbox` | `160 + 40 = 200` | **Evidence-Based** | Scaled to `N=600` | **`105 + 35 = 140`** | `<0.15%` of `2021–25` |
| **`ASF Archives`** | Legitimate (`C5`) | `>100k` `2021–2025` `.mbox` | `120 + 30 = 150` | **Evidence-Based** | Scaled to `N=600` | **`90 + 30 = 120`** | `<0.15%` of `2021–25` |
| **TOTAL** | **Balanced `50/50`** | **5 Independent Sources** | **`800 + 200 = 1,000`** | **`275` spam-phish unsupported** | **`800+200` Rejected** | **`600 + 200 = 800`** | **Conservative Floor** |

