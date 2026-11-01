# Domain Analyzer V3 Architectural & Design Specification

**Project:** IFSI Phishing Email Detection  
**Experiment:** Phase 7 — Domain Evidence Precision Refinement  
**Date:** November 2026  
**Status:** Approved & Implemented  

---

## 1. Architectural Motivation

Phase 6 demonstrated that structured domain evidence successfully resolved the 0.0% sophisticated phishing blind spot, catching 100% of spear-phishing attacks. However, Domain Analyzer V2 recorded 3 False Positives due to:
1. Unawareness of legitimate B2B secondary domains (`amazon-business.com`).
2. Blind identity mismatch rules that flagged internal corporate employees (`@enterprise-corp.com`) when referencing enterprise software tools ("SAP Concur") in the subject line.
3. Inability to recognize multi-domain SaaS tenant portals (`myworkday.com` vs. `workday.com`).

Domain Analyzer V3 introduces **Precision-Tiered Domain Context Modeling**, distinguishing verified enterprise relationships from deceptive lookalike patterns while maintaining zero false reassurances.

---

## 2. Structural Comparison: V2 vs. V3

| Capability | Domain Analyzer V2 (Phase 6) | Domain Analyzer V3 (Phase 7) |
| :--- | :--- | :--- |
| **Secondary Domain Support** | Single primary string per brand (e.g. `amazon.com`) | Explicit auditable registry mapping primary + secondary domains (e.g. `amazon-business.com`) |
| **Multi-Domain Tenant Portals** | Treated cross-domain portal links as deceptive lookalikes | Differentiates outbound transactional senders from customer-facing application tenant domains (`myworkday.com`, `concursolutions.com`) |
| **Internal Sender Handling** | Flagged any brand mention in subject as an "Identity Mismatch" | Contextual check: internal corporate senders (`@enterprise-corp.com`) referencing tools are classified as `Internal Corporate Tool References` |
| **Evidence Categorization** | Single flat observation list mixing facts and warnings | Categorized semantic groupings: `Verified Organizational Relationships`, `Observable Structural Facts`, and `Observed Structural Anomalies` |
| **Reputation Semantics** | Factual observables without safety claims | Explicit notice: absence of anomalies does not prove safety; unknown external domains remain unverified |

---

## 3. Auditable Multi-Domain Registry Specification

The verified enterprise mapping registry (`VERIFIED_ENTERPRISE_RELATIONSHIPS`) explicitly declares the authorized sender domains, tenant/link domains, and documentation scope for major corporate services:

```python
VERIFIED_ENTERPRISE_RELATIONSHIPS = {
    "amazon": {
        "authorized_sender_domains": {"amazon.com", "aws.amazon.com", "amazon-business.com"},
        "authorized_link_domains": {"amazon.com", "aws.amazon.com", "amazon-business.com"},
        "description": "Amazon Corporate & B2B Procurement Infrastructure",
        "evidence_source": "Enterprise B2B Purchasing Portals & AWS Public Registry",
    },
    "workday": {
        "authorized_sender_domains": {"workday.com", "myworkday.com"},
        "authorized_link_domains": {"workday.com", "myworkday.com"},
        "description": "Workday HCM & Multi-Tenant Application Portal",
        "evidence_source": "Workday Customer Tenant Architecture Documentation",
    },
    "concur": {
        "authorized_sender_domains": {"concur.com", "concursolutions.com"},
        "authorized_link_domains": {"concur.com", "concursolutions.com"},
        "description": "SAP Concur Corporate Travel & Solutions Portal",
        "evidence_source": "SAP Concur Architecture & Enterprise Integration Guide",
    },
    "docusign": {
        "authorized_sender_domains": {"docusign.com", "docusign.net"},
        "authorized_link_domains": {"docusign.com", "docusign.net"},
        "description": "DocuSign e-Signature Platform & Secondary Processing",
        "evidence_source": "DocuSign API & Infrastructure Routing Documentation",
    },
    ...
}
```

---

## 4. Contextual Discrepancy & Anomaly Classification

### 4.1 Internal Corporate Tool Reference vs. External Impersonation
Given an email with sender domain $D_{\text{sender}}$, subject $Sub$, display name $Disp$, and extracted destination URLs $\mathcal{U}$:

$$\text{InternalAligned}(\mathcal{U}, D_{\text{sender}}) = \forall u \in \mathcal{U}, \text{Reg}(u) = \text{Reg}(D_{\text{sender}}) \lor \text{Host}(u) \text{ ends with } D_{\text{sender}}$$

If a brand $b$ appears in $Sub$, the analyzer applies the following branching logic:
1. **Case 1: Display Name Impersonation (External)**  
   If $b \in Disp$ and $\text{Reg}(D_{\text{sender}}) \notin \text{AuthSenders}(b)$, emit:  
   `Display Identity Mismatch: Display Name claims identity '{Disp}' but email is sent from unaffiliated domain '@{D_sender}'.`
2. **Case 2: Internal Tool Reference**  
   If $b \in Sub$, $\text{Reg}(D_{\text{sender}}) \notin \text{AuthSenders}(b)$, but $\text{InternalAligned}(\mathcal{U}, D_{\text{sender}}) = \text{True}$, emit:  
   `Internal Corporate Tool Reference: Subject references '{b.title()}' while email originates from internal corporate domain '@{D_sender}'; destination links point to verified internal subdomains.`
3. **Case 3: Authorized Secondary Domain**  
   If $\text{Reg}(D_{\text{sender}}) \in \text{AuthSenders}(b)$, emit:  
   `Verified Enterprise Domain: Sender domain '{D_sender}' is an authorized domain for {Description}.`

---

## 5. Output Representation Format

```
[STRUCTURED SENDER & DOMAIN EVIDENCE]
- Sender Address: {sender_address}
- Sender Domain: {sender_domain}
- Display Name: {display_name}
- Extracted Destination Links:
  * {url} (Host: {host})
- Verified Organizational Relationships:
  * {relationship_fact}
- Observable Structural Facts:
  * {structural_fact}
- Observed Structural Anomalies:
  * {anomaly_fact}
- Reputation Notice: Absence of structural anomalies does not prove safety; unknown external domains remain unverified.
```

