"""Modular Configuration-Driven Ablation Engine for M4 Phishing Detection.

Provides strict, controlled component activation across all primary cumulative
configurations (A0-A4) and isolated leave-one-out configurations (ISO-1 to ISO-4).
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Sequence

from core.balanced_retriever import (
    format_balanced_reference_block,
    get_balanced_rag_retriever,
)
from core.domain_analyzer import (
    analyze_email_domains,
    format_domain_evidence_block,
)
from core.inference import _call_ollama_json
from core.model_config import DEFAULT_LIVE_MODEL
from core.models import get_rag_retriever
from core.sanitizer import sanitize_stage2_input
from phishbench.rag import format_reference_block

from .prompts import (
    BASELINE_STAGE1_PROMPT,
    EXPERIMENTAL_STAGE1_PROMPT,
    STAGE2_BASELINE,
    STAGE2_CANONICAL_V2,
    STAGE2_WITH_DOMAIN_ONLY,
    STAGE2_WITH_SANITIZATION_AND_DOMAIN,
    STAGE2_WITH_SANITIZATION_ONLY,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AblationConfig:
    """Explicit declarative specification of an ablation configuration."""

    config_id: str
    name: str
    description: str
    injection_detector_version: str  # "baseline_v1" | "experimental_v2"
    sanitization_enabled: bool
    domain_analysis_enabled: bool
    rag_mode: str  # "standard" | "balanced"
    stage2_prompt_mode: str  # "baseline" | "sanitization_only" | "domain_only" | "sanitization_and_domain" | "canonical_v2"
    k_standard: int = 3
    k_phish: int = 2
    k_legit: int = 2
    model: str = DEFAULT_LIVE_MODEL
    temperature: float = 0.0
    num_predict: int = 512
    timeout: float = 60.0


# =============================================================================
# EXPLICIT CONFIGURATION REGISTRY
# =============================================================================

CONFIGURATIONS: dict[str, AblationConfig] = {
    # -------------------------------------------------------------------------
    # Cumulative Configurations (A-Series)
    # -------------------------------------------------------------------------
    "A0": AblationConfig(
        config_id="A0",
        name="Production M4 Baseline",
        description="Original production M4: binary injection detector, no sanitization, no domain analysis, standard top-3 RAG.",
        injection_detector_version="baseline_v1",
        sanitization_enabled=False,
        domain_analysis_enabled=False,
        rag_mode="standard",
        stage2_prompt_mode="baseline",
        k_standard=3,
    ),
    "ISO-4": AblationConfig(
        config_id="ISO-4",
        name="Baseline + Injection Classifier Only",
        description="Isolates Stage 1 active-vs-quoted disambiguation without Stage 1.5 sanitization, domain analysis, or balanced RAG.",
        injection_detector_version="experimental_v2",
        sanitization_enabled=False,
        domain_analysis_enabled=False,
        rag_mode="standard",
        stage2_prompt_mode="baseline",
        k_standard=3,
    ),
    "A1": AblationConfig(
        config_id="A1",
        name="Baseline + Injection Disambiguation & Sanitizer",
        description="A0 plus experimental active-vs-quoted injection classifier and Stage 1.5 span redaction.",
        injection_detector_version="experimental_v2",
        sanitization_enabled=True,
        domain_analysis_enabled=False,
        rag_mode="standard",
        stage2_prompt_mode="sanitization_only",
        k_standard=3,
    ),
    "A2": AblationConfig(
        config_id="A2",
        name="A1 + Structured Domain Analysis",
        description="A1 plus structured sender and link domain telemetry extraction with domain scrutiny directives.",
        injection_detector_version="experimental_v2",
        sanitization_enabled=True,
        domain_analysis_enabled=True,
        rag_mode="standard",
        stage2_prompt_mode="sanitization_and_domain",
        k_standard=3,
    ),
    "A3": AblationConfig(
        config_id="A3",
        name="A2 + Balanced RAG Retrieval",
        description="A2 plus balanced RAG retrieval (2 phishing + 2 legitimate exemplars). Modular assembly of full components.",
        injection_detector_version="experimental_v2",
        sanitization_enabled=True,
        domain_analysis_enabled=True,
        rag_mode="balanced",
        stage2_prompt_mode="canonical_v2",
        k_phish=2,
        k_legit=2,
    ),
    "A4": AblationConfig(
        config_id="A4",
        name="Full Experimental M4 Architecture",
        description="Canonical full experimental M4 pipeline for validation parity against standalone classify_email_m4_v2.",
        injection_detector_version="experimental_v2",
        sanitization_enabled=True,
        domain_analysis_enabled=True,
        rag_mode="balanced",
        stage2_prompt_mode="canonical_v2",
        k_phish=2,
        k_legit=2,
    ),
    # -------------------------------------------------------------------------
    # Isolated Leave-One-Out Configurations (ISO-Series)
    # -------------------------------------------------------------------------
    "ISO-1": AblationConfig(
        config_id="ISO-1",
        name="Full Experimental WITHOUT Sanitization",
        description="Full experimental pipeline with Stage 1.5 sanitization disabled (raw text passed to Stage 2).",
        injection_detector_version="experimental_v2",
        sanitization_enabled=False,
        domain_analysis_enabled=True,
        rag_mode="balanced",
        stage2_prompt_mode="domain_only",
        k_phish=2,
        k_legit=2,
    ),
    "ISO-2": AblationConfig(
        config_id="ISO-2",
        name="Full Experimental WITHOUT Domain Analysis",
        description="Full experimental pipeline with structured sender/domain telemetry disabled.",
        injection_detector_version="experimental_v2",
        sanitization_enabled=True,
        domain_analysis_enabled=False,
        rag_mode="balanced",
        stage2_prompt_mode="sanitization_only",
        k_phish=2,
        k_legit=2,
    ),
    "ISO-3": AblationConfig(
        config_id="ISO-3",
        name="Full Experimental WITHOUT Balanced RAG",
        description="Full experimental pipeline with standard top-3 global RAG instead of balanced RAG.",
        injection_detector_version="experimental_v2",
        sanitization_enabled=True,
        domain_analysis_enabled=True,
        rag_mode="standard",
        stage2_prompt_mode="sanitization_and_domain",
        k_standard=3,
    ),
}


def _resolve_stage2_prompt(mode: str) -> str:
    if mode == "baseline":
        return STAGE2_BASELINE
    if mode == "sanitization_only":
        return STAGE2_WITH_SANITIZATION_ONLY
    if mode == "domain_only":
        return STAGE2_WITH_DOMAIN_ONLY
    if mode == "sanitization_and_domain":
        return STAGE2_WITH_SANITIZATION_AND_DOMAIN
    if mode == "canonical_v2":
        return STAGE2_CANONICAL_V2
    raise ValueError(f"Unknown stage2_prompt_mode: {mode}")


def classify_email_ablation(
    email_text: str,
    config: AblationConfig,
    subject: str = "",
    sender: str = "",
    api_base: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    """Execute email classification under a strictly declared ablation configuration."""
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

    # =========================================================================
    # COMPONENT 2: DOMAIN & SENDER TELEMETRY
    # =========================================================================
    domain_analysis: dict[str, Any] | None = None
    domain_evidence_block: str = ""
    domain_evidence_present: bool = False

    if config.domain_analysis_enabled:
        domain_analysis = analyze_email_domains(subject, sender, email_text)
        domain_evidence_block = format_domain_evidence_block(domain_analysis)
        domain_evidence_present = True

    # =========================================================================
    # COMPONENT 3: RAG RETRIEVAL (STANDARD vs. BALANCED)
    # =========================================================================
    retrieved_samples: list[dict[str, Any]] = []
    rag_reference_block: str = "No reference exemplars available."

    if config.rag_mode == "standard":
        retriever = get_rag_retriever()
        if retriever is not None:
            try:
                retrieved_samples = retriever.retrieve(email_text, top_k=config.k_standard)
                rag_reference_block = format_reference_block(retrieved_samples)
            except Exception as exc:
                logger.warning("[%s] Standard RAG retrieval error: %s", config.config_id, exc)
                rag_reference_block = f"Retrieval error: {exc}"
    elif config.rag_mode == "balanced":
        balanced_retriever = get_balanced_rag_retriever()
        if balanced_retriever is not None:
            try:
                retrieved_samples = balanced_retriever.retrieve_balanced(
                    email_text,
                    k_phish=config.k_phish,
                    k_legit=config.k_legit,
                )
                rag_reference_block = format_balanced_reference_block(retrieved_samples)
            except Exception as exc:
                logger.warning("[%s] Balanced RAG retrieval error: %s", config.config_id, exc)
                rag_reference_block = f"Retrieval error: {exc}"
    else:
        raise ValueError(f"Unknown rag_mode: {config.rag_mode}")

    retrieved_exemplar_ids = [str(s.get("id")) for s in retrieved_samples]
    retrieved_exemplar_labels = [str(s.get("label_name") or s.get("label")) for s in retrieved_samples]

    # =========================================================================
    # COMPONENT 1 (STAGE 1): INJECTION DETECTOR
    # =========================================================================
    user_prompt_c1 = f"Inspect this untrusted email for prompt injection:\n\n{email_text}"

    if config.injection_detector_version == "baseline_v1":
        p1, raw1, dur1, failure1 = _call_ollama_json(
            BASELINE_STAGE1_PROMPT,
            user_prompt_c1,
            model=config.model,
            api_base=api_base,
            timeout=config.timeout,
        )
        s1_ok = p1 is not None and "has_prompt_injection" in p1
        has_injection = bool(p1.get("has_prompt_injection", False)) if s1_ok else False
        active_injection = has_injection
        quoted_injection = False
        injection_span = ""
        reasoning_s1 = "Baseline binary detector evaluated injection." if s1_ok else (failure1 or "Parse error")
    elif config.injection_detector_version == "experimental_v2":
        p1, raw1, dur1, failure1 = _call_ollama_json(
            EXPERIMENTAL_STAGE1_PROMPT,
            user_prompt_c1,
            model=config.model,
            api_base=api_base,
            timeout=config.timeout,
        )
        s1_ok = p1 is not None and ("active_prompt_injection" in p1 or "has_prompt_injection" in p1)
        if s1_ok:
            active_injection = bool(p1.get("active_prompt_injection", p1.get("has_prompt_injection", False)))
            quoted_injection = bool(p1.get("quoted_prompt_injection", False))
            injection_span = str(p1.get("injection_span", "")).strip()
            reasoning_s1 = str(p1.get("reasoning", "")).strip()
            has_injection = active_injection or quoted_injection
        else:
            active_injection = False
            quoted_injection = False
            injection_span = ""
            has_injection = False
            reasoning_s1 = failure1 or "Stage 1 parsing failed"
    else:
        raise ValueError(f"Unknown injection_detector_version: {config.injection_detector_version}")

    # Injection verdict categorization
    if active_injection:
        injection_type = "active"
        injection_verdict = "active_injection_detected"
    elif quoted_injection:
        injection_type = "quoted"
        injection_verdict = "quoted_injection_detected"
    else:
        injection_type = "none"
        injection_verdict = "clean"

    # =========================================================================
    # COMPONENT 1.5: INPUT SANITIZATION
    # =========================================================================
    if config.sanitization_enabled:
        sanitization_result = sanitize_stage2_input(
            email_text=email_text,
            active_prompt_injection=active_injection,
            candidate_span=injection_span,
        )
        stage2_email_body = sanitization_result["sanitized_text"]
        is_sanitized = sanitization_result["is_sanitized"]
    else:
        sanitization_result = {
            "sanitized_text": email_text,
            "is_sanitized": False,
            "redacted_span": None,
            "safe_fallback_triggered": False,
            "requires_manual_review": False,
        }
        stage2_email_body = email_text
        is_sanitized = False

    # =========================================================================
    # STAGE 2: PHISHING CLASSIFICATION
    # =========================================================================
    stage2_system_prompt = _resolve_stage2_prompt(config.stage2_prompt_mode)

    # Assemble user prompt based on component availability
    if domain_evidence_present:
        user_prompt_c2 = (
            f"{rag_reference_block}\n\n"
            f"{domain_evidence_block}\n\n"
            f"--- CANDIDATE EMAIL TO EVALUATE ---\n"
            f"{stage2_email_body}\n"
            f"--- END CANDIDATE EMAIL ---"
        )
    else:
        user_prompt_c2 = f"{rag_reference_block}\n\nEmail to evaluate:\n{stage2_email_body}"

    p2, raw2, dur2, failure2 = _call_ollama_json(
        stage2_system_prompt,
        user_prompt_c2,
        model=config.model,
        api_base=api_base,
        timeout=config.timeout,
    )

    s2_ok = p2 is not None and "is_phishing" in p2
    total_duration = time.perf_counter() - t_start

    if s2_ok:
        is_phishing_pred = bool(p2.get("is_phishing", False))
        conf_val = p2.get("confidence")
        confidence = float(conf_val) if conf_val is not None else (0.95 if is_phishing_pred else 0.90)
        reasons_s2 = p2.get("reasons", [])
        if not isinstance(reasons_s2, list):
            reasons_s2 = [str(reasons_s2)]
    else:
        is_phishing_pred = False
        confidence = 0.0
        reasons_s2 = [failure2 or "Stage 2 parsing failed"]

    # =========================================================================
    # STAGE FAILURE / MANUAL REVIEW FALLBACK
    # =========================================================================
    if not s1_ok or not s2_ok or sanitization_result.get("requires_manual_review"):
        failed_stages = []
        if not s1_ok:
            failed_stages.append("Stage 1 (Injection Detector)")
        if not s2_ok:
            failed_stages.append("Stage 2 (Phishing Classifier)")
        if sanitization_result.get("requires_manual_review"):
            failed_stages.append("Sanitizer (Unresolved Injection Span)")

        return {
            "configuration_id": config.config_id,
            "config_id": config.config_id,
            "configuration_name": config.name,
            "method": f"M4 Ablation ({config.config_id})",
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
            "domain_evidence_present": domain_evidence_present,
            "rag_mode": config.rag_mode,
            "is_valid": False,
            "failure_type": failure1 or failure2 or "sanitization_fallback",
            "failure_message": f"Failure in {', '.join(failed_stages)}",
            "reasons": [f"Error: Pipeline failure in {', '.join(failed_stages)}. Security action: MANUAL_REVIEW."],
            "raw_response_call1": raw1,
            "raw_response_call2": raw2,
            "domain_analysis": domain_analysis,
            "sanitization_info": sanitization_result,
        }

    # =========================================================================
    # SECURITY ACTION POLICY MAPPING
    # =========================================================================
    if config.injection_detector_version == "baseline_v1":
        # Baseline Option B Mapping (does not distinguish active vs quoted)
        if has_injection and is_phishing_pred:
            security_action = "block"
        elif has_injection and not is_phishing_pred:
            security_action = "quarantine_review"
        elif not has_injection and is_phishing_pred:
            security_action = "block"
        else:
            security_action = "allow"
    else:
        # Enhanced Option B Mapping (disambiguates active vs quoted)
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
        reasons_list.append(f"🚨 [Stage 1 Alert] Active prompt injection detected ({reasoning_s1}).")
        if is_sanitized:
            reasons_list.append("🛡️ [Sanitizer] Instruction span redacted prior to Stage 2 classification.")
    elif quoted_injection:
        reasons_list.append(f"ℹ️ [Stage 1 Note] Quoted/discussed injection payload detected ({reasoning_s1}). Non-adversarial.")
    else:
        reasons_list.append("✅ [Stage 1] Clean: No prompt injection detected.")

    if is_phishing_pred:
        reasons_list.append(f"🚨 [Stage 2 Alert] Email classified as phishing ({'; '.join(reasons_s2[:2]) if reasons_s2 else 'Phishing indicators detected'}).")
    else:
        reasons_list.append(f"✅ [Stage 2] Email evaluated as legitimate ({'; '.join(reasons_s2[:2]) if reasons_s2 else 'Standard corporate correspondence'}).")

    phishing_verdict = "phishing" if is_phishing_pred else "legitimate"

    return {
        "configuration_id": config.config_id,
        "config_id": config.config_id,
        "configuration_name": config.name,
        "method": f"M4 Ablation ({config.config_id})",
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
        "domain_evidence_present": domain_evidence_present,
        "rag_mode": config.rag_mode,
        "is_valid": True,
        "failure_type": None,
        "failure_message": None,
        "reasons": reasons_list,
        "raw_response_call1": raw1,
        "raw_response_call2": raw2,
        "domain_analysis": domain_analysis,
        "sanitization_info": sanitization_result,
    }

