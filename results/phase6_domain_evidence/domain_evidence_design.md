# Phase 6: Domain Evidence Architecture & Design Specification

**Project:** IFSI Phishing Email Detection  
**Experiment:** Phase 6 — Domain Evidence Integration Study  
**Author:** AI Research Assistant  
**Date:** November 2026  
**Status:** Approved & Implemented  

---

## 1. Motivation & Forensic Context

In Phase 5, the A1-Opt architecture achieved 100% active prompt-injection containment, 0.0% False Positive Rate on challenging legitimate samples, and reduced Stage 1 latency by 19.2%. However, an independent forensic audit revealed that both Frozen A1 and A1-Opt exhibited a **0.0% recall (20/20 False Negatives)** on sophisticated executive spear-phishing lures.

In M4 Ablation V1, the legacy domain analyzer (`src/core/domain_analyzer.py`) attempted to address domain spoofing, but caused a catastrophic **-14.0% drop in sophisticated phishing recall** (A1: 92.0% vs. A2: 78.0%) due to:
1. Emitting false reassurance (`Clean / Standard corporate naming patterns`) when an attacker used an unlisted lookalike domain.
2. Celebrating link alignment (`Sender domain matches destination link`) when an attacker controlled both the fake sender domain and fake link host.
3. Emitting alarmist `[CRITICAL RISK]` tags on legitimate third-party enterprise integrations.

Phase 6 implements **Domain Analyzer V2**, designed from first principles to provide strictly factual, neutral structural telemetry without evaluative hallucinations.

---

## 2. Architectural Comparison: Legacy vs. V2

| Feature / Behavior | Legacy Domain Analyzer (`src/core/domain_analyzer.py`) | Domain Analyzer V2 (`src/experiments/phase6_domain_evidence/`) |
| :--- | :--- | :--- |
| **Output Epistemology** | Evaluative / Prescriptive (attempts to declare safety or risk) | **Strictly Observational & Factual** (telemetry only) |
| **Absence of Detected Anomaly** | Emits `Clean / Standard corporate naming patterns` (misleads LLM) | **Neutral structural report** (absence of evidence is not proof of safety) |
| **Attacker-Aligned Links** | Emits `Link Alignment: Sender domain matches destination link` | Reports destination points to same unverified domain |
| **Severity Flags** | `[CRITICAL RISK]`, `[HIGH RISK]` (overrides LLM reasoning) | **None**; lets Stage 2 synthesize domain facts with semantics & RAG |
| **Enterprise SaaS Awareness** | Flags third-party links as suspicious mismatches | Recognizes DocuSign, Zoom, Salesforce, Okta, Greenhouse as standard |
| **Brand Recognition** | Single hardcoded primary string mapping | Multi-domain authorized mappings (e.g. `docusign.net` + `docusign.com`) |
| **Lookalike Heuristics** | Naive substring search on 35 brands only | Chained administrative pretexting keyword detection (`portal`, `vdr`, `auth`) |

---

## 3. Mathematical & Algorithmic Specification

### 3.1 Component Architecture
```
                                 [ Inbound Candidate Email ]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             [ Email Headers ]                            [ Email Body Text ]
                       │                                           │
         ┌─────────────┴─────────────┐                             │
         ▼                           ▼                             ▼
  [ Sender Domain ]           [ Reply-To Domain ]           [ Extracted URLs ]
         │                           │                             │
         └─────────────┬─────────────┘                             │
                       ▼                                           ▼
         [ Header Alignment Check ]                      [ Link Destination Check ]
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             ▼
                             [ Domain Analyzer V2 Engine ]
                                             │
                                             ▼
                           [ Structured Neutral Domain Block ]
                                             │
                                             ▼
                            [ Stage 2 Phishing Classifier ]
```

### 3.2 Observable Feature Vector

Given an email with sender $S$, subject $Sub$, body $B$, and reply-to $R$:

1. **Sender Decomposition:**
   $$S \to (\text{Display Name } D_s, \text{ Address } A_s, \text{ Domain } \text{Dom}_s, \text{ Registered Domain } \text{Reg}_s)$$
2. **Reply-To Discrepancy:**
   $$\Delta_{\text{reply}} = \begin{cases} 1 & \text{if } \text{Dom}_r \neq \emptyset \land \text{Dom}_r \neq \text{Dom}_s \\ 0 & \text{otherwise} \end{cases}$$
3. **Synthetic Lookalike & Administrative Keyword Density:**
   Let $K_{\text{admin}} = \{\text{portal, auth, login, verify, vdr, governance, board, exec, billing, invoice, payroll, benefits, security, ...}\}$.
   Let $T_s = \text{tokens}(\text{Dom}_s \setminus \text{TLD})$.
   $$\text{Score}_{\text{admin}}(S) = |T_s \cap K_{\text{admin}}|$$
   If $\text{Score}_{\text{admin}}(S) \ge 2$, emit `Administrative Lookalike Construction`.
4. **Brand Collision & Authorization Verification:**
   For known brand $b \in \mathcal{B}$ with authorized domains $\mathcal{D}(b)$:
   $$\text{Impersonation}(S) = \begin{cases} \text{True} & \text{if } b \in \text{Dom}_s \land \text{Reg}_s \notin \mathcal{D}(b) \\ \text{False} & \text{otherwise} \end{cases}$$
5. **Destination Link Host Alignment:**
   For each extracted URL $u \in \mathcal{U}(B)$ with registered domain $\text{Reg}_u$:
   $$\text{Type}(u) = \begin{cases} \text{Internal Aligned} & \text{if } \text{Reg}_u = \text{Reg}_s \\ \text{Authorized SaaS} & \text{if } \text{Reg}_u \in \mathcal{D}_{\text{saas}} \\ \text{External Unverified} & \text{otherwise} \end{cases}$$

---

## 4. Controlled Experimental Configurations

To isolate the precise contribution of structured domain evidence, Phase 6 defines three configurations:

- **Config A (A1-Opt Baseline):**
  - Stage 1: Compact Prompt (Phase 5).
  - Stage 1.5: Sanitizer V2 (Phase 5).
  - RAG: Standard Top-3 ($k=3$).
  - Domain Evidence: **DISABLED** (Stage 2 receives email body only).
  - Stage 2: `STAGE2_FROZEN_PROMPT`.

- **Config B (A1-Opt + Domain Evidence):**
  - Stage 1: Compact Prompt (Phase 5).
  - Stage 1.5: Sanitizer V2 (Phase 5).
  - RAG: Standard Top-3 ($k=3$).
  - Domain Evidence: **ENABLED** (`domain_analyzer_v2.py`).
  - Stage 2: `STAGE2_WITH_DOMAIN_EVIDENCE_PROMPT` receiving structured domain evidence block.

- **Config C (Domain Evidence Ablation):**
  - Identical pipeline to Config B, but the domain evidence block is stripped from the Stage 2 input and `STAGE2_FROZEN_PROMPT` is used.
  - **Invariance Criterion:** Config C predictions MUST match Config A predictions with 100% agreement, confirming zero side-effects or leakage.

