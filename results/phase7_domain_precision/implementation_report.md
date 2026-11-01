# Phase 7: Domain Evidence Precision Refinement — Implementation Report

## 1. Executive Summary

Phase 7 implements an experimental precision refinement to the domain-evidence telemetry architecture established in Phase 6. While Phase 6 demonstrated complete resolution of the sophisticated phishing blind spot (achieving 100% recall on 20 regression attacks), it introduced three false positives on legitimate emails containing corporate secondary domains, internal corporate references to SaaS tools, and multi-domain SaaS authentication portals (`gen-ord-010`, `p6-leg-007`, `p6-leg-015`).

Domain Analyzer V3 addresses these root causes through:
1. **Auditable Multi-Domain Registry**: Explicit mapping of verified enterprise parent/secondary domain relationships (e.g., `amazon-business.com` $\to$ `amazon.com`, `myworkday.com` $\to$ `workday.com`).
2. **Context-Aware Internal Corporate Sender Evaluation**: Suppressing deceptive lookalike / identity mismatch warnings when an internal employee (`@enterprise-corp.com`) mentions an enterprise tool (e.g., "SAP Concur") in the subject line while hyperlinks remain within internal enterprise subdomains (`concur.internal.enterprise-corp.com`).
3. **Structured Fact Categorization**: Replacing speculative anomaly phrasing with three unambiguous telemetry sections: `Verified Organizational Relationships`, `Observable Structural Facts`, and `Observed Structural Anomalies`, with an explicit reputation notice.

All modifications remain strictly isolated in `src/experiments/phase7_domain_precision/`. Production code, frozen A1 code, Phase 5/6 code, historical datasets, and the clean FAISS index remain completely untouched.

---

## 2. Experimental Configurations

Phase 7 defines three controlled configurations evaluated on identical email inputs:

| Configuration | Stage 1 (Injection) | Stage 1.5 (Sanitizer) | Domain Telemetry | Stage 2 Classifier | RAG Retrieval |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Config A** (Frozen Phase 6 Baseline) | Compact Prompt (Phase 5) | Sanitizer V2 (Phase 5) | Domain Analyzer V2 (Phase 6) | `STAGE2_WITH_DOMAIN_EVIDENCE_PROMPT` | Standard Top-3 Clean FAISS |
| **Config B** (Experimental Precision) | Compact Prompt (Phase 5) | Sanitizer V2 (Phase 5) | **Domain Analyzer V3** (Phase 7) | `STAGE2_WITH_DOMAIN_EVIDENCE_PROMPT` | Standard Top-3 Clean FAISS |
| **Config C** (Evidence Disabled) | Compact Prompt (Phase 5) | Sanitizer V2 (Phase 5) | **DISABLED** | `STAGE2_FROZEN_PROMPT` | Standard Top-3 Clean FAISS |

---

## 3. Core Architectural Changes: Domain Analyzer V3 vs V2

### 3.1 Auditable Secondary & Multi-Domain Registry (`VERIFIED_ENTERPRISE_RELATIONSHIPS`)
Domain Analyzer V2 evaluated links and sender domains against isolated single-domain sets (`AUTHORIZED_BRAND_DOMAINS`). In contrast, V3 defines an explicit, auditable relational graph:

```python
VERIFIED_ENTERPRISE_RELATIONSHIPS: dict[str, dict[str, Any]] = {
    "amazon": {
        "primary_domains": {"amazon.com", "amazon.co.uk", "amazon.de", "amazon.ca", "amazon.co.jp"},
        "secondary_domains": {"amazon-business.com", "aws.amazon.com", "media-amazon.com"},
        "description": "Amazon commercial and cloud service infrastructure",
    },
    "workday": {
        "primary_domains": {"workday.com"},
        "secondary_domains": {"myworkday.com", "myworkdayjobs.com"},
        "description": "Workday HCM portal and customer tenant authentication domains",
    },
    "sap": {
        "primary_domains": {"sap.com"},
        "secondary_domains": {"concursolutions.com", "successfactors.com", "ariba.com"},
        "description": "SAP enterprise software, procurement, and Concur expense ecosystem",
    },
    ...
}
```
**No Wildcard Matching**: Only exact domain names registered in this auditable schema are recognized as secondary relationships. No heuristic wildcard substrings or automated substring matching is permitted.

### 3.2 Context-Aware Internal Corporate Sender Handling
In corporate operations, employees frequently discuss enterprise tools in email subjects (e.g., `Subject: SAP Concur Expense Report Submitted`). V2 flagged this as an `Identity Mismatch` because the sender domain `@enterprise-corp.com` did not equal `sap.com` or `concursolutions.com`.

Domain Analyzer V3 introduces subject brand evaluation logic:
- If a brand is mentioned in the subject line, V3 inspects whether the sender domain is an internal enterprise domain.
- If all hyperlinks stay within the sender's own domain or recognized organizational subdomains (`*.enterprise-corp.com`), the brand mention is classified as an **internal enterprise tool reference**, suppressing false identity mismatch flags.
- If the sender domain is external and unfamiliar, the identity mismatch flag is preserved to catch brand impersonation.

### 3.3 Explicit Semantic Evidence Formatting
In Phase 6, V2 output combined facts, inferences, and anomalies into unstructured bullet points. In Phase 7, V3 formats telemetry with explicit epistemic boundaries:

```markdown
=== DOMAIN TELEMETRY (Deterministic Structural Analysis) ===
Verified Organizational Relationships:
  - Domain 'amazon-business.com' is a recognized secondary/infrastructure domain for 'amazon'.
Observable Structural Facts:
  - From Address: 'orders@amazon-business.com' [Domain: 'amazon-business.com']
  - Primary URL Domain: 'amazon-business.com'
  - Domain Alignment: Consistent (Sender matches Destination)
Observed Structural Anomalies:
  - None detected.
Reputation / Safety Notice:
  - Telemetry only observes structural domain properties; it does not represent safety proof.
============================================================
```

---

## 4. Protected Files & Verification

All protected baseline components have been verified via SHA-256 cryptographic hashes:

| Component | Path | SHA-256 Hash | Integrity Status |
| :--- | :--- | :--- | :--- |
| Production Baseline M4 | `src/core/inference.py` | `aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506` | UNTOUCHED |
| Frozen A1 | `src/core/inference_m4_v2.py` | `fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37` | UNTOUCHED |
| Clean FAISS Index | `results/rag_index_clean/index.faiss` | `d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc` | UNTOUCHED |
| Clean FAISS Metadata | `results/rag_index_clean/metadata.json` | `4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece` | UNTOUCHED |
| Phase 5 Sanitizer V2 | `src/experiments/phase5_a1_optimization/sanitizer_v2.py` | `b51f938ca3a3b4e2b9f4212d4178b58cd47c3f8b4a48a0ba9a0539be4759aa55` | UNTOUCHED |
| Phase 6 Domain Analyzer V2 | `src/experiments/phase6_domain_evidence/domain_analyzer_v2.py` | `e27aefb062350e758840aedd4ecb5eb29e43ae19b61f228a3c864aa3df59fc44` | UNTOUCHED |
| Phase 6 Engine V3 | `src/experiments/phase6_domain_evidence/engine_v3.py` | `dbe5150dc7365b6a560b09f9056129fc24d50e0ebfa13c53719c6336263ae8a8` | UNTOUCHED |

---

## 5. Security & Operational Policy

The operational security policy implemented in `src/experiments/phase7_domain_precision/engine_v4.py` strictly upholds all production fail-safe guarantees:
1. **Prompt Injection Containment**: Any email containing active prompt injection is routed to `quarantine_review` (or `block` if also classified as phishing).
2. **Defensive Fail-Safe**: Any unparseable JSON, API failure, or sanitization failure defaults to `manual_review` and `error` status.
3. **Decoupled Classification vs Operational Action**: Ground truth classification metrics evaluate whether `is_phishing` matches the ground truth label, while security actions (`allow`, `block`, `quarantine_review`, `manual_review`) are evaluated as operational risk containment outcomes.

