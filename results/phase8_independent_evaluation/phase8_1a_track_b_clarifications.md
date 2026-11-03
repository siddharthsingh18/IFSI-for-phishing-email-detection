# Phase 8.1A: Track B Taxonomy, Schema & Metric Boundary Clarifications

## 1. Purpose & Governance Invariants

Earlier Phase 8 planning documents grouped heterogeneous adversarial test artifacts under **Track B (Controlled Challenge Corpus)** while imposing a blanket Gate 1 rule requiring *"all 3,000 candidate records to possess complete, syntactically valid RFC 822 header envelopes"* and pooling Track B denominators.

This document establishes **three binding Track B invariants** for Phase 8:
1. **Explicit Provenance & Medium Separation**: Track B must schema-tag and separate **synthetic email envelopes**, **adapted email examples**, and **standalone non-email documents** (research papers, vulnerability advisories, OWASP documentation).
2. **Absolute Ban on Fabricated Email Headers**: Standalone research papers, CVE advisories, and threat bulletins **must never have fabricated `From:` / `Subject:` / `Received:` headers prepended** and **must never be described as emails**.
3. **Metric Segregation**: Standalone non-email documents **must remain strictly outside all email classification metrics** (phishing recall, legitimate FPR, email accuracy, McNemar email classification tests).

---

## 2. Explicit Four-Part Track B Taxonomy

### 2.1 Medium & Provenance Classes (`provenance_class`)

| Provenance Class | `is_email` | `header_origin` | Exact Definition | Permitted Usage & Claim Scope |
| :--- | :---: | :--- | :--- | :--- |
| **1. Synthetic Email Envelope** (`synthetic_email_envelope`) | `true` | `"synthetic_constructed"` | A purpose-built test email authored from scratch (envelope headers + body) to model a specific threat or enterprise pattern (e.g., synthetic Okta/Workday SaaS notice, synthetic zero-link CFO wire-transfer BEC, or synthetic email carrying an active/quoted injection). | Evaluated in **Track B1 (Controlled Email Challenge Metrics)**. Must be explicitly labeled synthetic; never described as real-world email traffic. |
| **2. Adapted Email Example** (`adapted_email_example`) | `true` | `"adapted_from_source"` | An item derived from a documented real email specimen or disclosed phishing lure where domains, PII, or payload spans were deterministically modified or augmented, with full lineage recorded (`base_specimen_citation`, `adaptation_ops`). | Evaluated in **Track B1 (Controlled Email Challenge Metrics)**, reported in a separate provenance breakdown from purely synthetic envelopes. |
| **3. Standalone Non-Email Document** (`standalone_non_email_document`) | **`false`** | **`"none"`** | A genuine non-email text artifact—such as an arXiv prompt-injection research paper excerpt, NVD/CISA CVE vulnerability advisory, OWASP LLM01 markdown entry, or SIEM log snippet—retained in its native document format **without email headers**. | Evaluated **exclusively in Track B2 (Standalone Parser & Sanitizer Stress Metrics)**. **Strictly excluded** from all email phishing/legitimate classification tables. |

### 2.2 Orthogonal Injection Payload Dimension (`injection_status`)

Across Track B1 and Track B2, prompt injection status is recorded independently of medium and phishing intent:

| `injection_status` | Exact Operational Definition | Expected Stage 1 / Sanitizer V2 Behavior | Expected Stage 2 Behavior (Track B1 Emails Only) |
| :--- | :--- | :--- | :--- |
| **`no_injection`** | Contains zero instructions targeting an LLM/classifier, system prompt, output schema, or policy rules. | `injection_detected = false`; body passes unchanged. | Classify email normally (`phishing` vs `legitimate`). |
| **`active_injection`** | Contains unquoted/adversarial meta-instructions attempting to override system instructions, force a `"legitimate"` verdict, poison JSON output, or evade detection (including Unicode/CJK/homoglyph variants). | **Containment Mandatory**: detect span (`injection_detected = true`), neutralize via Sanitizer V2 (`[REDACTED_INJECTION]`), or trigger fail-safe quarantine if span extraction fails. | Classify sanitized email without obeying the injected directive (or hold in fail-safe quarantine). |
| **`quoted_injection`** | Discusses, cites, or quotes prompt-injection payloads inside an educational, defensive, academic, or incident-response context (e.g., SOC advisory quoting an attacker string inside code fences/blockquotes, or a standalone security paper). | Distinguish quoted analytical context or safely sanitize quoted span **without** triggering false-positive fail-safe quarantine. | For Track B1 emails: classify underlying email on its actual sender/intent (`legitimate` for genuine SOC advisories; `phishing` if an attacker wraps a lure in fake advisory framing). For Track B2 standalone docs: **no email verdict scored**. |

---

## 3. Partition of Track B into Track B1 (Emails) and Track B2 (Standalone Documents)

To enforce the prohibition against fabricating headers and mixing non-emails into email classification denominators, Track B (`N = 1,000`) is partitioned into two physically separate files and metric tables:

### Track B1: Controlled Email Challenge Suite (`data/evaluation/phase8/track_b1_email_challenges.jsonl`, `N = 800`)
All `800` records have `is_email = true` and syntactically valid RFC 822 envelopes (`synthetic_email_envelope` or `adapted_email_example`):
- **B1-1: Difficult Legitimate Enterprise Emails (`N = 300`)** — Multi-tenant SaaS authentication (`Workday`, `Okta`, `Microsoft 365`, `DocuSign`), authorized secondary corporate domains, urgent IT maintenance notices (`injection_status = "no_injection"`).
- **B1-2: Sophisticated Phishing & BEC Emails (`N = 300`)** — Executive zero-link BEC, vendor bank-routing changes, lookalike domains, display-name spoofing (`injection_status = "no_injection"`).
- **B1-3: Active Injection in Email Envelopes (`N = 100`)** — `50` phishing emails with active evasion injections + `50` legitimate emails with active benign-override/signature test injections.
- **B1-4: Quoted Injection in Email Envelopes (`N = 100`)** — `80` legitimate SOC/engineering emails quoting injection payloads + `20` phishing emails attempting "fake security advisory" camouflage.

### Track B2: Standalone Non-Email Sanitizer & Parser Stress Suite (`data/evaluation/phase8/track_b2_standalone_documents.jsonl`, `N = 200`)
All `200` records have `is_email = false`, `header_origin = "none"`, `raw_headers = null`, and `email_phishing_status = "not_applicable"`:
- **B2-1: Standalone Vulnerability Advisories & Research Papers Quoting Injections (`N = 100`, `injection_status = "quoted_injection"`)** — Unmodified excerpts from public LLM security papers, CISA/NVD advisories, and OWASP LLM Top 10 documentation (`CC BY-SA 4.0` attributed).
- **B2-2: Standalone Raw Adversarial Payload Documents (`N = 100`, `injection_status = "active_injection"`)** — Unwrapped adversarial prompt-injection documents (multilingual CJK, XML/JSON boundary escapes, delimiter spoofing) testing raw Stage 1 + Sanitizer V2 span neutralization without email scaffolding.

---

## 4. Schema Enforcement & Metric Firewall Rules

1. **Automated Schema Assertion**:
   - If `provenance_class == "standalone_non_email_document"`, the validator **fails hard** if `is_email != false`, `header_origin != "none"`, `email_phishing_status != "not_applicable"`, or if the text begins with fabricated `From:` / `To:` / `Subject:` lines.
   - Gate 1 (RFC 822 Header Integrity Gate) applies **exclusively** to Track A and Track B1 (`is_email == true`).
2. **Metric Firewall**:
   - **Email Classification Metrics** (Accuracy, Phishing Recall, Legitimate FPR, Precision, F1, McNemar's test) may be computed **only** on Track A (separately) and Track B1 (separately).
   - **Track B2 Metrics** are restricted strictly to **Stage 1 / Stage 1.5 Sanitizer Metrics**:
     - `B2 Active Span Containment Rate` (`N = 100` B2-2 documents)
     - `B2 Quoted Document Non-Quarantine / Span Precision` (`N = 100` B2-1 documents)
     - `B2 Stage 1 Latency Distribution` (mean / P95 ms)

