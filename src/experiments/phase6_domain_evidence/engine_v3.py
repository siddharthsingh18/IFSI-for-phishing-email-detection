"""Phase 6 Domain Evidence Execution Engine.

Implements three experimental configurations:
1. Config A (A1-Opt Baseline):
   - Stage 1: Compact Prompt (Phase 5)
   - Stage 1.5: Multilingual Sanitizer V2 (Phase 5)
   - Stage 2: Frozen A1 Prompt (STAGE2_FROZEN_PROMPT)
   - RAG: Standard Top-3
   - Domain Evidence: DISABLED

2. Config B (A1-Opt + Domain Evidence):
   - Stage 1: Compact Prompt (Phase 5)
   - Stage 1.5: Multilingual Sanitizer V2 (Phase 5)
   - Stage 2: STAGE2_WITH_DOMAIN_EVIDENCE_PROMPT
   - RAG: Standard Top-3
   - Domain Evidence: ENABLED (Domain Analyzer V2)

3. Config C (Domain Evidence Ablation):
   - Identical to Config B pipeline, but domain evidence block is omitted
     and STAGE2_FROZEN_PROMPT is used. Confirms zero side-effects and
     invariance with Config A.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from core.inference import _call_ollama_json
from core.model_config import DEFAULT_LIVE_MODEL
from core.models import get_rag_retriever
from phishbench.rag import format_reference_block

from ..phase5_a1_optimization.sanitizer_v2 import sanitize_stage2_input
from .domain_analyzer_v2 import (
    analyze_email_domains,
    format_domain_evidence_block,
)
from .prompts_v3 import (
    STAGE1_COMPACT_PROMPT,
    STAGE2_FROZEN_PROMPT,
    STAGE2_WITH_DOMAIN_EVIDENCE_PROMPT,
)

logger = logging.getLogger(__name__)


def classify_email_phase6(
    email_text: str,
    config_id: str,  # "A", "B", or "C"
    subject: str = "",
    sender: str = "",
    model: str = DEFAULT_LIVE_MODEL,
    k_standard: int = 3,
    api_base: str = "http://127.0.0.1:11434",
    timeout: float = 60.0,
) -> dict[str, Any]:
    """Execute email classification under a declared Phase 6 configuration."""
    t_start = time.perf_counter()

    # Extract headers if not provided
    if not sender:
        m_from = re.search(r"^From:\s*(.+)$", email_text, re.MULTILINE | re.IGNORECASE)
        if m_from:
            sender = m_from.group(1).strip()
    if not subject:
        m_subj = re.search(r"^Subject:\s*(.+)$", email_text, re.MULTILINE | re.IGNORECASE)
        if m_subj:
            subject = m_subj.group(1).strip()

    # Step 1: Standard RAG Retrieval (top-3, clean FAISS index)
    retrieved_samples: list[dict[str, Any]] = []
    rag_reference_block = "No reference exemplars available."
    retriever = get_rag_retriever()
    if retriever is not None:
        try:
            retrieved_samples = retriever.retrieve(email_text, top_k=k_standard)
            rag_reference_block = format_reference_block(retrieved_samples)
        except Exception as exc:
            logger.warning("[%s] RAG retrieval error: %s", config_id, exc)
            rag_reference_block = f"Retrieval error: {exc}"

    retrieved_exemplar_ids = [str(s.get("id")) for s in retrieved_samples]
    retrieved_exemplar_labels = [str(s.get("label_name") or s.get("label")) for s in retrieved_samples]

    # Step 2: Stage 1 Injection Detection (Compact Prompt)
    user_prompt_c1 = f"Inspect this untrusted email for prompt injection:\n\n{email_text}"
    t0_s1 = time.perf_counter()
    p1, raw1, dur1, failure1 = _call_ollama_json(
        STAGE1_COMPACT_PROMPT,
        user_prompt_c1,
        model=model,
        api_base=api_base,
        timeout=timeout,
    )
    s1_dur_ms = round((time.perf_counter() - t0_s1) * 1000, 2)

    s1_ok = p1 is not None and ("active_prompt_injection" in p1 or "has_prompt_injection" in p1)
    if s1_ok:
        active_injection = bool(p1.get("active_prompt_injection", p1.get("has_prompt_injection", False)))
        quoted_injection = bool(p1.get("quoted_prompt_injection", False))
        injection_span = str(p1.get("injection_span", "")).strip()
        has_injection = active_injection or quoted_injection
    else:
        active_injection = False
        quoted_injection = False
        injection_span = ""
        has_injection = False

    if active_injection:
        injection_type = "active"
        injection_verdict = "active_injection_detected"
    elif quoted_injection:
        injection_type = "quoted"
        injection_verdict = "quoted_injection_detected"
    else:
        injection_type = "none"
        injection_verdict = "clean"

    # Step 3: Stage 1.5 Sanitization (Sanitizer V2)
    sanitization_result = sanitize_stage2_input(
        email_text=email_text,
        active_prompt_injection=active_injection,
        candidate_span=injection_span,
    )
    stage2_email_body = sanitization_result["sanitized_text"]
    is_sanitized = sanitization_result["is_sanitized"]

    # Step 4: Domain Evidence & Stage 2 Preparation
    domain_telemetry = None
    domain_evidence_block = ""
    domain_evidence_present = False

    if config_id == "B":
        domain_telemetry = analyze_email_domains(subject, sender, email_text)
        domain_evidence_block = format_domain_evidence_block(domain_telemetry)
        domain_evidence_present = True
        stage2_system_prompt = STAGE2_WITH_DOMAIN_EVIDENCE_PROMPT
        user_prompt_c2 = (
            f"{rag_reference_block}\n\n"
            f"{domain_evidence_block}\n\n"
            f"--- CANDIDATE EMAIL TO EVALUATE ---\n"
            f"{stage2_email_body}\n"
            f"--- END CANDIDATE EMAIL ---"
        )
    elif config_id in ("A", "C"):
        # Config A (Baseline) and Config C (Ablation) omit domain evidence
        stage2_system_prompt = STAGE2_FROZEN_PROMPT
        user_prompt_c2 = f"{rag_reference_block}\n\nEmail to evaluate:\n{stage2_email_body}"
    else:
        raise ValueError(f"Unknown config_id: {config_id}")

    # Step 5: Stage 2 Phishing Classifier
    t0_s2 = time.perf_counter()
    p2, raw2, dur2, failure2 = _call_ollama_json(
        stage2_system_prompt,
        user_prompt_c2,
        model=model,
        api_base=api_base,
        timeout=timeout,
    )
    s2_dur_ms = round((time.perf_counter() - t0_s2) * 1000, 2)

    s2_ok = p2 is not None and "is_phishing" in p2
    total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)

    if s2_ok:
        is_phishing_pred = bool(p2.get("is_phishing", False))
        confidence = float(p2.get("confidence", 0.95 if is_phishing_pred else 0.90))
        reasons_s2 = p2.get("reasons", [])
        if not isinstance(reasons_s2, list):
            reasons_s2 = [str(reasons_s2)]
    else:
        is_phishing_pred = False
        confidence = 0.0
        reasons_s2 = [failure2 or "Stage 2 parsing failed"]

    # Step 6: Defensive Security Policy Action
    if not s1_ok or not s2_ok or sanitization_result.get("requires_manual_review"):
        security_action = "manual_review"
        verdict = "error"
    elif active_injection:
        security_action = "quarantine_review" if not is_phishing_pred else "block"
        verdict = "phishing" if is_phishing_pred else "prompt_injection"
    elif is_phishing_pred:
        security_action = "block"
        verdict = "phishing"
    else:
        security_action = "allow"
        verdict = "legitimate"

    return {
        "config_id": config_id,
        "is_phishing": is_phishing_pred,
        "phishing_verdict": "phishing" if is_phishing_pred else "legitimate",
        "has_prompt_injection": has_injection,
        "active_prompt_injection": active_injection,
        "quoted_prompt_injection": quoted_injection,
        "injection_type": injection_type,
        "injection_verdict": injection_verdict,
        "security_action": security_action,
        "verdict": verdict,
        "confidence": confidence,
        "reasons": reasons_s2,
        "is_sanitized": is_sanitized,
        "domain_evidence_present": domain_evidence_present,
        "domain_telemetry": domain_telemetry,
        "retrieved_exemplar_ids": retrieved_exemplar_ids,
        "retrieved_exemplar_labels": retrieved_exemplar_labels,
        "stage1_latency_ms": s1_dur_ms,
        "stage2_latency_ms": s2_dur_ms,
        "total_latency_ms": total_duration_ms,
        "is_valid": s1_ok and s2_ok,
    }

