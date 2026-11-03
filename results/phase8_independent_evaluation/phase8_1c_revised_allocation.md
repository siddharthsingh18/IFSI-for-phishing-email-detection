# Phase 8.1C: Audit of Phase 8.1B Allocation & Revised Conservative Track A Design (`600 + 200`)

## 1. Preflight Audit of the Phase 8.1B Proposed Allocation (`800` Test + `200` Validation)

### 1.1 Exact Source Fractions in Phase 8.1B (Calculated Separately for Test and Validation)

| Source | 8.1B Test Legit | 8.1B Test Phish | 8.1B Test Total (`N=800`) | **8.1B Test Fraction** | 8.1B Val Legit | 8.1B Val Phish | 8.1B Val Total (`N=200`) | **8.1B Val Fraction** | Quota Evidence Audit |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **`TREC 2007`** | 120 | 120 | 240 | **`30.00%`** | 30 | 30 | 60 | **`30.00%`** | `ham` (`120+30`) supported; **`phish` (`120+30`) UNSUPPORTED** |
| **`phishing_pot`** | 0 | 180 | 180 | **`22.50%`** | 0 | 45 | 45 | **`22.50%`** | Supported by `12,000+` `.eml` capacity |
| **`IETF Archives`** | 160 | 0 | 160 | **`20.00%`** | 40 | 0 | 40 | **`20.00%`** | Supported (`>100k` `2021–2025` `.mbox`) |
| **`ASF Archives`** | 120 | 0 | 120 | **`15.00%`** | 30 | 0 | 30 | **`15.00%`** | Supported (`>100k` `2021–2025` `.mbox`) |
| **`Untroubled.org`** | 0 | 100 | 100 | **`12.50%`** | 0 | 25 | 25 | **`12.50%`** | **`phish` (`100+25`) UNSUPPORTED** |
| **TOTAL** | **400** | **400** | **800** | **`100.00%`** | **100** | **100** | **200** | **`100.00%`** | **`275 / 500` (`55%`) phish from unlabeled spam** |

### 1.2 Seven-Point Gate Audit of the Phase 8.1B `800 + 200` Allocation
1. **Total test `N = 800`**: Arithmetically satisfied (`400 + 400 = 800`), **but empirically unsupported** because `220 / 400` (`55.0%`) of test phishing relies on unverified spam-trap extraction.
2. **Total validation `N = 200`**: Arithmetically satisfied (`100 + 100 = 200`), **but `55 / 100` (`55.0%`)** of validation phishing relies on unverified spam-trap extraction.
3. **Both test classes `>= 300`**: Arithmetically `400 >= 300`, **but fails conservative yield verification** on phishing (`only 180` test phishing come from a dedicated phishing repository).
4. **No source exceeds `40%` of test set**: Satisfied (`max = 30.00% <= 40.00%`).
5. **Validation independently sampled & disjoint from test**: Satisfied in protocol via cluster-grouped splitting (`0.70` shingle Jaccard + `Subject:` stem + sender domain/campaign grouping before split).
6. **Source and class not perfectly confounded**: Arithmetically $\text{BA}^*_{\text{source-only}} = 0.8500 < 1.0000$ (`MI = 0.4852`, `NMI = 0.4661`), **only because** `TREC` was assumed `120 / 120`.
7. **Dual-class `TREC` core not misrepresented as a phishing corpus**: **FAILS**. Native `trec07p` contains `25,220` `ham` and `50,199` `spam` (`0` native phishing labels) dominated by `2007` commercial/image/PDF spam. Presenting `TREC 2007` as a `50/50` (`120` legit / `120` phish) balanced phishing core misstates its empirical composition and risks forcing marginal spam into the phishing label.

---

## 2. Phase 8.1C Revised Conservative Allocation (`N_test = 600` + `N_val = 200`)

Rather than inflating phishing counts from general spam archives or relaxing [`config/dataset_gates.yaml`](file:///d:/Project/IFSI-for-phishing-email-detection/config/dataset_gates.yaml), Track A is down-scoped by **`25.0%` on Test (`800 -> 600`)** to sit squarely on the exact `minimum_test_records_per_class: 300` and `minimum_validation_records_per_class: 100` gates while **cutting unverified spam-archive phishing quotas by `63.6%` (`275 -> 100` total across Test + Validation)** and preserving **`maximum_source_fraction: 0.40`** (`max = 37.50%`) in **both** Test and Validation.

### 2.1 Revised Allocation Table & Separate Test / Validation Source Fractions

| Source ID | Candidate Corpus | Test Legit (`C5`) | Test Phish (`C1/C2`) | **Test Total (`N=600`)** | **Test Source Fraction ($\le 40\%$)** | Val Legit (`C5`) | Val Phish (`C1/C2`) | **Val Total (`N=200`)** | **Val Source Fraction ($\le 40\%$)** | Quota Basis |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **`phishing_pot`** | `rf-peixoto/phishing_pot` (`.eml`, `2022–2025`) | 0 | **225** | **225** | **`37.50%`** | 0 | **75** | **75** | **`37.50%`** | `<2.5%` of `12,000+` phishing `.eml` |
| **`trecc07p`** | NIST/Waterloo `TREC 2007` (`RFC 2822`, `2007`) | **105** | **45** *(cond.)* | **150** | **`25.00%`** | **35** | **15** *(cond.)* | **50** | **`25.00%`** | `0.56%` of `ham`; `0.12%` of `spam` (`70/30` legit-majority) |
| **`ietf_mailarchive`** | IETF Mail Archive (`.mbox`, `2021–2025`) | **105** | 0 | **105** | **`17.50%`** | **35** | 0 | **35** | **`17.50%`** | `<0.15%` of `2021–2025` lists |
| **`asf_lists_mbox`** | ASF Public Mail Archives (`.mbox`, `2021–2025`) | **90** | 0 | **90** | **`15.00%`** | **30** | 0 | **30** | **`15.00%`** | `<0.15%` of human governance lists |
| **`untroubled_phish`** | `Untroubled.org` Sinkhole (`.7z`, `2022–2025`) | 0 | **30** *(cond.)* | **30** | **`5.00%`** | 0 | **10** *(cond.)* | **10** | **`5.00%`** | `<0.04%` of `2022–2025` bait spam |
| **TOTAL** | **5 Independent Sources** | **300 (`50.0%`)** | **300 (`50.0%`)** | **600** | **`100.00%` (Max `37.50%`)** | **100 (`50.0%`)** | **100 (`50.0%`)** | **200** | **`100.00%` (Max `37.50%`)** | **All `dataset_gates.yaml` bounds met** |

---

## 3. Verification of All `dataset_gates.yaml` & Methodological Requirements

1. **Both Test Classes $\ge 300$ (`minimum_test_records_per_class: 300`)**: **PASS** — `300` Legitimate (`C5`) and `300` Phishing (`C1` + `C2`).
2. **Both Validation Classes $\ge 100$ (`minimum_validation_records_per_class: 100`)**: **PASS** — `100` Legitimate and `100` Phishing (`N_val = 200`).
3. **Maximum Source Cap Preserved (`maximum_source_fraction: 0.40`)**: **PASS** — Largest source (`phishing_pot`) is **`37.50%`** in Test (`225 / 600`) and **`37.50%`** in Validation (`75 / 200`), maintaining a `2.50` percentage-point buffer below `40.00%`.
4. **Disjoint Validation & Test Sampling**:
   - Candidate pools from all 5 sources are first grouped by connected components of (`0.70` 3/5-shingle Jaccard similarity $\cup$ normalized `Subject:` stem $\cup$ `In-Reply-To:`/`References:` thread ID $\cup$ registrable phishing URL domain) using [`cluster_near_duplicates`](file:///d:/Project/IFSI-for-phishing-email-detection/src/phishbench/data_loader.py#L182-L220) before stratified `3:1` (`Test : Validation`) group assignment (`seed = 42`), guaranteeing **zero campaign, thread, or URL-domain leakage between Validation and Test**.
5. **Honest Representation of `TREC 2007` & Confounding Accounting**:
   - `TREC 2007` is no longer misrepresented as a `50/50` phishing corpus; it is **`70.0%` Legitimate (`105` test, `35` val) and `30.0%` manually verified Phishing (`45` test, `15` val)**, requiring only `60` genuine phishing messages out of `50,199` `spam` (`0.12%`).
   - **Confounding Metrics Disclosed Transparently**:
     - *Against IFSI Training/RAG (`clean_split_v1/train.jsonl` vs. Track A)*: `held_out_source` `source_only_balanced_accuracy = 0.5000 <= 0.65` (`0%` shared sources).
     - *Within `trecc07p` (`N_test = 150`)*: `source_only_balanced_accuracy = 0.5000` (single `source` tag; receiver headers normalized via `<REDACTED_RECIPIENT>`).
     - *Pooled Within-Track-A (`N_test = 600`)*: Not perfectly confounded ($\text{BA}^*_{\text{source-only}} = \mathbf{0.9250} < 1.0000$, `MI = 0.5404` nats, `NMI = 0.5384`), because a pure source-tag classifier misclassifies all `45` `TREC` phishing records (`15.0%` FNR). Because `0.9250 > 0.65`, **pooled Track A metrics may NEVER be reported in isolation without the mandatory source-stratified Recall/FPR table and `trecc07p` dual-class table**.

---

## 4. Binding Fail-Safe Contingency Rule (Zero Quota Inflation Permitted)

Because the `45 + 15 = 60` `TREC 2007` phishing quota and `30 + 10 = 40` `Untroubled.org` phishing quota remain **conditional estimates** until message-level dual annotation ($\kappa_{\text{binary}} \ge 0.85$) is executed after separate acquisition approval:
- **Hard Stop Rule**: If post-approval manual 6-class annotation of `trec07p` (`50,199` spam) yields `< 60` unique-campaign (`< 0.70` Jaccard) parseable `C1`/`C2` phishing records, or `Untroubled.org` yields `< 40`, **annotators are strictly forbidden from reclassifying `C3` (malware-only), `C4` (ordinary spam), or `C6` (ambiguous) records as `phishing`, and engineers are strictly forbidden from pushing `phishing_pot` above `40.0%` (`240 / 600`)**.
- Any shortfall exceeding `15` phishing records (the `225 -> 240` headroom under `phishing_pot`'s `40.0%` cap) halts Track A assembly until either a formally licensed secondary phishing repository (e.g., APWG `eCX` grant) is approved or an explicit governance review updates dataset size targets.
