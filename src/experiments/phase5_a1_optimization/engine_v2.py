"""Optimized A1 Architecture Execution Engine (Phase 5).

Combines:
1. Compact Stage 1 Prompt (minimizing prefill tokens and eliminating verbose reasoning).
2. Multilingual Robust Sanitizer V2 (boundary-tolerant, CJK/Punctuation resilient).
3. Frozen A1 Stage 2 Phishing Classifier with standard top-3 RAG.
4. Separate tracking of classification verdict vs. operational security action.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from core.inference import _call_ollama_json
from core.model_config import DEFAULT_LIVE_MODEL
from core.models import get_rag_retriever
from phishbench.rag import format_reference_block

from .prompts_v2 import STAGE1_COMPACT_PROMPT, STAGE2_A1_PROMPT
from .sanitizer_v2 import sanitize_stage2_input

logger = logging.getLogger(__name__)


def classify_email_a1_optimized(
    email_text: str,
    subject: str = "",
    sender: str = "",
    model: str = DEFAULT_LIVE_MODEL,
    k_standard: int = 3,
    api_base: str = "http://127.0.0.1:11434",
    timeout: float = 60.0,
) -> dict[str, Any]:
    """Execute the Optimized A1 (A1-Opt) two-stage detection pipeline."""
    t_start = time.perf_counter()

    # Step 1: Standard RAG Retrieval (top-k standard, identical to A1)
    retrieved_samples: list[dict[str, Any]] = []
    rag_reference_block = "No reference exemplars available."
    retriever = get_rag_retriever()
    if retriever is not None:
        try:
            retrieved_samples = retriever.retrieve(email_text, top_k=k_standard)
            rag_reference_block = format_reference_block(retrieved_samples)
        except Exception as exc:
            logger.warning("[A1-Opt] RAG retrieval error: %s", exc)
            rag_reference_block = f"Retrieval error: {exc}"

    retrieved_exemplar_ids = [str(s.get("id")) for s in retrieved_samples]
    retrieved_exemplar_labels = [str(s.get("label_name") or s.get("label")) for s in retrieved_samples]

    # Step 2: Stage 1 Injection Detection with Compact Prompt
    user_prompt_c1 = f"Inspect this untrusted email for prompt injection:\n\n{email_text}"
    p1, raw1, dur1, failure1 = _call_ollama_json(
        STAGE1_COMPACT_PROMPT,
        user_prompt_c1,
        model=model,
        api_base=api_base,
        timeout=timeout,
    )

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

    # Step 3: Stage 1.5 Sanitization with Sanitizer V2
    sanitization_result = sanitize_stage2_input(
        email_text=email_text,
        active_prompt_injection=active_injection,
        candidate_span=injection_span,
    )
    stage2_email_body = sanitization_result["sanitized_text"]
    is_sanitized = sanitization_result["is_sanitized"]

    # Step 4: Stage 2 Phishing Classifier (Frozen A1 prompt)
    user_prompt_c2 = f"{rag_reference_block}\n\nEmail to evaluate:\n{stage2_email_body}"
    p2, raw2, dur2, failure2 = _call_ollama_json(
        STAGE2_A1_PROMPT,
        user_prompt_c2,
        model=model,
        api_base=api_base,
        timeout=timeout,
    )

    s2_ok = p2 is not None and "is_phishing" in p2
    total_duration = time.perf_counter() - t_start

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

    # Step 5: Defensive Fail-Safe & Manual Review Check
    if not s1_ok or not s2_ok or sanitization_result.get("requires_manual_review"):
        failed_stages = []
        if not s1_ok:
            failed_stages.append("Stage 1 (Injection Detector)")
        if not s2_ok:
            failed_stages.append("Stage 2 (Phishing Classifier)")
        if sanitization_result.get("requires_manual_review"):
            failed_stages.append("Sanitizer (Unresolved Injection Span)")

        return {
            "configuration_id": "A1-Opt",
            "config_id": "A1-Opt",
            "configuration_name": "A1 Optimized (Compact Stage 1 + Sanitizer V2)",
            "method": "A1 Optimized (Phase 5)",
            "verdict": "error",
            "phishing_verdict": "error" if not s2_ok else ("phishing" if is_phishing_pred else "legitimate"),
            "is_phishing": False,
            "confidence": 0.0,
            "has_prompt_injection": has_injection,
            "active_prompt_injection": active_injection,
            "quoted_prompt_injection": quoted_injection,
            "injection_type": injection_type,
            "injection_verdict": injection_verdict,
            "security_action": "manual_review",
            "latency_stage1_seconds": round(dur1, 4),
            "latency_stage2_seconds": round(dur2, 4),
            "total_latency_seconds": round(total_duration, 4),
            "stage1_latency_ms": round(dur1 * 1000, 2),
            "stage2_latency_ms": round(dur2 * 1000, 2),
            "total_latency_ms": round(total_duration * 1000, 2),
            "retrieved_exemplar_ids": retrieved_exemplar_ids,
            "retrieved_exemplar_labels": retrieved_exemplar_labels,
            "is_sanitized": is_sanitized,
            "domain_evidence_present": False,
            "rag_mode": "standard",
            "is_valid": False,
            "failure_type": failure1 or failure2 or "sanitization_fallback",
            "failure_message": f"Failure in {', '.join(failed_stages)}",
            "reasons": [f"Error: Pipeline failure in {', '.join(failed_stages)}. Security action: MANUAL_REVIEW."],
            "raw_response_call1": raw1,
            "raw_response_call2": raw2,
            "sanitization_info": sanitization_result,
        }

    # Step 6: Operational Security Action Mapping
    if is_phishing_pred:
        security_action = "block"
    elif active_injection and not is_phishing_pred:
        security_action = "quarantine_review"
    elif quoted_injection and not is_phishing_pred:
        security_action = "allow"
    else:
        security_action = "allow"

    reasons_list: list[str] = []
    if active_injection:
        reasons_list.append("🚨 [Stage 1 Alert] Active prompt injection detected.")
        if is_sanitized:
            reasons_list.append(f"🛡️ [Sanitizer V2] Instruction span redacted (method: {sanitization_result.get('match_method')}).")
    elif quoted_injection:
        reasons_list.append("ℹ️ [Stage 1 Note] Quoted/discussed injection payload detected. Non-adversarial.")
    else:
        reasons_list.append("✅ [Stage 1] Clean: No prompt injection detected.")

    phishing_verdict = "phishing" if is_phishing_pred else "legitimate"
    if is_phishing_pred:
        reasons_list.append("🚨 [Stage 2 Alert] Email classified as phishing.")
    else:
        reasons_list.append("✅ [Stage 2] Email evaluated as legitimate.")

    return {
        "configuration_id": "A1-Opt",
        "config_id": "A1-Opt",
        "configuration_name": "A1 Optimized (Compact Stage 1 + Sanitizer V2)",
        "method": "A1 Optimized (Phase 5)",
        "verdict": phishing_verdict,
        "phishing_verdict": phishing_verdict,
        "is_phishing": is_phishing_pred,
        "confidence": confidence,
        "has_prompt_injection": has_injection,
        "active_prompt_injection": active_injection,
        "quoted_prompt_injection": quoted_injection,
        "injection_type": injection_type,
        "injection_verdict": injection_verdict,
        "security_action": security_action,
        "latency_stage1_seconds": round(dur1, 4),
        "latency_stage2_seconds": round(dur2, 4),
        "total_latency_seconds": round(total_duration, 4),
        "stage1_latency_ms": round(dur1 * 1000, 2),
        "stage2_latency_ms": round(dur2 * 1000, 2),
        "total_latency_ms": round(total_duration * 1000, 2),
        "retrieved_exemplar_ids": retrieved_exemplar_ids,
        "retrieved_exemplar_labels": retrieved_exemplar_labels,
        "is_sanitized": is_sanitized,
        "domain_evidence_present": False,
        "rag_mode": "standard",
        "is_valid": True,
        "failure_type": None,
        "failure_message": None,
        "reasons": reasons_list,
        "raw_response_call1": raw1,
        "raw_response_call2": raw2,
        "sanitization_info": sanitization_result,
    }

