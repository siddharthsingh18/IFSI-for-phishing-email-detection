"""Core single-call and multi-model inference functions (M1, M2, M3, M4) with zero Streamlit imports.

Primary Architecture: M4 (Decoupled Two-Stage RAG)
Lightweight Baseline: M1 (TF-IDF + Logistic Regression, calibrated tau=0.29)
Archived Baselines: M2 (Zero-Shot LLM), M3 (RAG Combined)
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

import httpx

from phishbench.ollama_client import SYSTEM_PROMPT
from phishbench.rag import RAG_SYSTEM_PROMPT, format_reference_block
from phishbench.evaluate_decoupled_rag import (
    SYSTEM_INJECTION_DETECTOR,
    SYSTEM_IS_PHISHING_ONLY,
)
from .models import get_m1_model, get_rag_retriever
from .model_config import DEFAULT_LIVE_MODEL

logger = logging.getLogger(__name__)


def classify_email_m1(email_text: str) -> dict[str, Any]:
    """Classify email using classical TF-IDF + LogisticRegression baseline (M1).

    Validation-calibrated decision threshold: tau = 0.29.
    Retained strictly as a lightweight local baseline and feature explainer.
    """
    t0 = time.perf_counter()
    vec, clf = get_m1_model()
    X = vec.transform([email_text])
    prob_phish = float(clf.predict_proba(X)[0][1])

    # Validation-calibrated decision threshold (tau = 0.29)
    M1_CALIBRATED_THRESHOLD = 0.29
    is_phish = prob_phish >= M1_CALIBRATED_THRESHOLD
    pred = 1 if is_phish else 0
    confidence = prob_phish if is_phish else (1.0 - prob_phish)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    feature_names = vec.get_feature_names_out()
    nonzero_indices = X.nonzero()[1]
    coefs = clf.coef_[0]
    token_weights = [(feature_names[i], coefs[i] * X[0, i]) for i in nonzero_indices]
    token_weights.sort(key=lambda x: abs(x[1]), reverse=True)
    top_tokens = [f"{t} ({'+' if w > 0 else ''}{w:.2f})" for t, w in token_weights[:5]]

    phishing_verdict = "phishing" if is_phish else "legitimate"
    injection_verdict = "clean"
    security_action = "block" if is_phish else "allow"

    return {
        "method": "M1 (TF-IDF + LogReg)",
        "verdict": phishing_verdict,
        "phishing_verdict": phishing_verdict,
        "is_phishing": is_phish,
        "has_prompt_injection": False,
        "injection_verdict": injection_verdict,
        "security_action": security_action,
        "confidence": confidence,
        "has_prompt_injection_display": "No (N/A — Classical ML)",
        "latency_ms": elapsed_ms,
        "latency_seconds": elapsed_ms / 1000,
        "reasons": [
            f"Classical baseline threshold decision (calibrated tau={M1_CALIBRATED_THRESHOLD:.2f}, p_phish={prob_phish:.4f}).",
            f"Influential tokens: {', '.join(top_tokens) if top_tokens else 'Standard vocabulary frequencies'}"
        ],
        "is_valid": True,
        "raw_response": f"Predicted label: {pred} (probability {prob_phish:.4f})",
        "failure_type": None,
        "failure_message": None,
        "attempts": 1,
    }


def _call_ollama_json(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_LIVE_MODEL,
    api_base: str = "http://127.0.0.1:11434",
    timeout: float = 60.0,
) -> tuple[dict[str, Any] | None, str, float, str | None]:
    """Call Ollama /api/chat with format=json, think=False, and measure duration."""
    t0 = time.perf_counter()
    url = f"{api_base.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "format": "json",
        "stream": False,
        "think": False,
        "options": {"temperature": 0.0, "num_predict": 512},
    }

    try:
        resp = httpx.post(url, json=payload, timeout=timeout)
        duration = time.perf_counter() - t0
        if resp.status_code == 200:
            data = resp.json()
            raw_text = data.get("message", {}).get("content", "").strip()
            clean_json_str = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()
            if not clean_json_str.startswith("{"):
                match = re.search(r"(\{.*\})", clean_json_str, re.DOTALL)
                if match:
                    clean_json_str = match.group(1)
            try:
                parsed = json.loads(clean_json_str)
                return parsed, raw_text, duration, None
            except json.JSONDecodeError:
                return None, raw_text, duration, "invalid_json"
        return None, f"HTTP Error {resp.status_code}: {resp.text[:300]}", duration, "unavailable"
    except httpx.TimeoutException as exc:
        return None, f"Timeout: {exc}", time.perf_counter() - t0, "timeout"
    except (httpx.ConnectError, httpx.NetworkError) as exc:
        return None, f"Connection error: {exc}", time.perf_counter() - t0, "unavailable"
    except (ValueError, RuntimeError, KeyError) as exc:
        return None, f"Response error: {exc}", time.perf_counter() - t0, "schema_error"


def classify_email_m2(
    email_text: str,
    model: str = DEFAULT_LIVE_MODEL,
    api_base: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    """Archived Baseline: Classify email using Zero-Shot LLM (M2).

    Note: Removed from active production detection workflow due to excessive false positives.
    """
    user_prompt = f"Analyze the following incoming email and classify it:\n\n{email_text}"
    parsed, raw_text, duration, failure_type = _call_ollama_json(SYSTEM_PROMPT, user_prompt, model=model, api_base=api_base)

    if parsed and "verdict" in parsed:
        verdict = str(parsed.get("verdict", "legitimate")).lower().strip()
        if verdict not in {"phishing", "legitimate"}:
            return {
                "method": "M2 (Zero-Shot LLM)",
                "verdict": "error",
                "phishing_verdict": "error",
                "is_phishing": False,
                "confidence": 0.0,
                "has_prompt_injection": False,
                "injection_verdict": "error",
                "security_action": "manual_review",
                "has_prompt_injection_display": "ERROR (Unsupported Verdict)",
                "latency_ms": duration * 1000,
                "latency_seconds": duration,
                "reasons": [f"Error: Model returned an unsupported verdict '{verdict}'."],
                "is_valid": False,
                "raw_response": raw_text,
                "failure_type": "unsupported_verdict",
                "failure_message": f"Unsupported verdict: {verdict}",
                "attempts": 1,
            }
        is_phish = "phish" in verdict
        conf = float(parsed.get("confidence", 0.5))
        reasons = parsed.get("reasons", [])
        if isinstance(reasons, str):
            reasons = [reasons]

        has_inj = any(
            term in r.lower()
            for r in (reasons or [])
            for term in ["prompt injection", "system override", "injection", "hijack", "disregard instructions"]
        )

        injection_verdict = "detected" if has_inj else "clean"
        phishing_verdict = "phishing" if is_phish else "legitimate"
        security_action = "block" if is_phish else ("quarantine_review" if has_inj else "allow")

        return {
            "method": "M2 (Zero-Shot LLM)",
            "verdict": phishing_verdict,
            "phishing_verdict": phishing_verdict,
            "is_phishing": is_phish,
            "confidence": conf,
            "has_prompt_injection": has_inj,
            "injection_verdict": injection_verdict,
            "security_action": security_action,
            "has_prompt_injection_display": "DETECTED 🚨 (In Reasons)" if has_inj else "NOT FLAGGED (Zero-Shot)",
            "latency_ms": duration * 1000,
            "latency_seconds": duration,
            "reasons": reasons or ["No explicit reasons provided by model."],
            "is_valid": True,
            "raw_response": raw_text,
            "failure_type": None,
            "failure_message": None,
            "attempts": 1,
        }

    return {
        "method": "M2 (Zero-Shot LLM)",
        "verdict": "error",
        "phishing_verdict": "error",
        "is_phishing": False,
        "confidence": 0.0,
        "has_prompt_injection": False,
        "injection_verdict": "error",
        "security_action": "manual_review",
        "has_prompt_injection_display": "ERROR (Inference Failure)",
        "latency_ms": duration * 1000,
        "latency_seconds": duration,
        "reasons": [f"Error: {raw_text or 'Model failed to emit valid JSON conforming to target schema.'}"],
        "is_valid": False,
        "raw_response": raw_text,
        "failure_type": failure_type or ("schema_error" if parsed else "invalid_json"),
        "failure_message": raw_text,
        "attempts": 1,
    }


def classify_email_m3(
    email_text: str,
    model: str = DEFAULT_LIVE_MODEL,
    top_k: int = 3,
    api_base: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    """Archived Baseline: Classify email using RAG Combined Single-Call (M3).

    Note: Removed from active production detection workflow due to prompt hijacking vulnerabilities.
    """
    retriever = get_rag_retriever()
    ref_block = "No reference exemplars available."
    retrieved_samples: list[dict[str, Any]] = []

    if retriever is not None:
        try:
            retrieved_samples = retriever.retrieve(email_text, top_k=top_k)
            ref_block = format_reference_block(retrieved_samples)
        except (ValueError, RuntimeError, KeyError) as exc:
            ref_block = f"Retrieval error: {exc}"

    user_prompt = (
        f"{ref_block}\n\n"
        f"--- INCOMING EMAIL TO CLASSIFY ---\n"
        f"{email_text}\n"
        f"--- END INCOMING EMAIL ---"
    )

    parsed, raw_text, duration, failure_type = _call_ollama_json(RAG_SYSTEM_PROMPT, user_prompt, model=model, api_base=api_base)

    if parsed and "verdict" in parsed:
        verdict = str(parsed.get("verdict", "legitimate")).lower().strip()
        if verdict not in {"phishing", "legitimate"}:
            return {
                "method": "M3 (RAG Combined)",
                "verdict": "error",
                "phishing_verdict": "error",
                "is_phishing": False,
                "confidence": 0.0,
                "has_prompt_injection": False,
                "injection_verdict": "error",
                "security_action": "manual_review",
                "has_prompt_injection_display": "ERROR (Unsupported Verdict)",
                "latency_ms": duration * 1000,
                "latency_seconds": duration,
                "reasons": [f"Error: Model returned an unsupported verdict '{verdict}'."],
                "is_valid": False,
                "raw_response": raw_text,
                "retrieved_samples": retrieved_samples,
                "failure_type": "unsupported_verdict",
                "failure_message": f"Unsupported verdict: {verdict}",
                "attempts": 1,
            }
        is_phish = "phish" in verdict
        conf = float(parsed.get("confidence", 0.5))
        reasons = parsed.get("reasons", [])
        if isinstance(reasons, str):
            reasons = [reasons]

        has_inj = any(
            term in r.lower()
            for r in (reasons or [])
            for term in ["prompt injection", "system override", "injection", "hijack", "disregard instructions"]
        )

        injection_verdict = "detected" if has_inj else "clean"
        phishing_verdict = "phishing" if is_phish else "legitimate"
        security_action = "block" if is_phish else ("quarantine_review" if has_inj else "allow")

        return {
            "method": "M3 (RAG Combined)",
            "verdict": phishing_verdict,
            "phishing_verdict": phishing_verdict,
            "is_phishing": is_phish,
            "confidence": conf,
            "has_prompt_injection": has_inj,
            "injection_verdict": injection_verdict,
            "security_action": security_action,
            "has_prompt_injection_display": "DETECTED 🚨 (In Reasons)" if has_inj else "NOT FLAGGED / EVADED",
            "latency_ms": duration * 1000,
            "latency_seconds": duration,
            "reasons": reasons or ["No reasons provided."],
            "is_valid": True,
            "raw_response": raw_text,
            "retrieved_samples": retrieved_samples,
            "failure_type": None,
            "failure_message": None,
            "attempts": 1,
        }

    return {
        "method": "M3 (RAG Combined)",
        "verdict": "error",
        "phishing_verdict": "error",
        "is_phishing": False,
        "confidence": 0.0,
        "has_prompt_injection": False,
        "injection_verdict": "error",
        "security_action": "manual_review",
        "has_prompt_injection_display": "ERROR (Inference Failure)",
        "latency_ms": duration * 1000,
        "latency_seconds": duration,
        "reasons": [f"Error: {raw_text or 'Model failed to emit valid JSON matching RAG schema.'}"],
        "is_valid": False,
        "raw_response": raw_text,
        "retrieved_samples": retrieved_samples,
        "failure_type": failure_type or ("retrieval_error" if retriever is None else "invalid_json"),
        "failure_message": raw_text,
        "attempts": 1,
    }


def classify_email_m4(
    email_text: str,
    model: str = DEFAULT_LIVE_MODEL,
    top_k: int = 3,
    api_base: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    """Primary Production Architecture: RAG Decoupled Two-Stage pipeline (M4).

    Stage 1: Indirect prompt injection detector.
    Stage 2: Phishing intent classification with clean RAG exemplars.
    Decision 2 (Option B): Independent classification statuses with security_action policy.
    """
    retriever = get_rag_retriever()
    ref_block = ""
    retrieved_samples: list[dict[str, Any]] = []
    if retriever is not None:
        try:
            retrieved_samples = retriever.retrieve(email_text, top_k=top_k)
            ref_block = format_reference_block(retrieved_samples)
        except Exception as exc:
            ref_block = f"Retrieval error: {exc}"

    # --- Stage 1: Injection Detector ---
    user_prompt_c1 = f"Inspect this untrusted email for prompt injection:\n\n{email_text}"
    p1, raw1, dur1, failure1 = _call_ollama_json(SYSTEM_INJECTION_DETECTOR, user_prompt_c1, model=model, api_base=api_base)
    s1_ok = p1 is not None and "has_prompt_injection" in p1
    has_injection = bool(p1.get("has_prompt_injection", False)) if s1_ok else False

    # --- Stage 2: Pure Phishing Classifier ---
    user_prompt_c2 = f"{ref_block}\n\nEmail to evaluate:\n{email_text}"
    p2, raw2, dur2, failure2 = _call_ollama_json(SYSTEM_IS_PHISHING_ONLY, user_prompt_c2, model=model, api_base=api_base)
    s2_ok = p2 is not None and "is_phishing" in p2
    is_phishing_pred = bool(p2.get("is_phishing", False)) if s2_ok else False

    total_duration = dur1 + dur2

    # Check for execution/connection failures in either stage
    if not s1_ok or not s2_ok:
        failed_calls: list[str] = []
        if not s1_ok:
            failed_calls.append("Stage 1 (Injection Detector)")
        if not s2_ok:
            failed_calls.append("Stage 2 (Phishing Classifier)")

        # Independent stage reporting on partial or total failure
        injection_verdict = ("detected" if has_injection else "clean") if s1_ok else "error"
        phishing_verdict = ("phishing" if is_phishing_pred else "legitimate") if s2_ok else "error"
        primary_failure = failure1 if not s1_ok else failure2

        return {
            "method": "M4 (RAG Decoupled)",
            "verdict": "error",
            "phishing_verdict": phishing_verdict,
            "is_phishing": False,
            "has_injection": has_injection,
            "has_prompt_injection": has_injection,
            "injection_verdict": injection_verdict,
            "security_action": "manual_review",
            "has_prompt_injection_display": "ERROR (Stage Failure)" if not s1_ok else ("DETECTED 🚨 (Stage 1)" if has_injection else "CLEAN ✅ (Stage 1)"),
            "is_phishing_only": is_phishing_pred if s2_ok else False,
            "confidence": 0.0,
            "latency_ms": total_duration * 1000,
            "latency_seconds": total_duration,
            "reasons": [
                f"Error: Pipeline failure on {', '.join(failed_calls)}. Required security action: MANUAL_REVIEW.",
                f"Stage 1 status: {'OK' if s1_ok else (failure1 or 'parse_failure')}, Stage 2 status: {'OK' if s2_ok else (failure2 or 'parse_failure')}"
            ],
            "is_valid": False,
            "raw_response_call1": raw1,
            "raw_response_call2": raw2,
            "retrieved_samples": retrieved_samples,
            "failure_type": primary_failure or "inference_failure",
            "failure_message": f"Failure in {', '.join(failed_calls)}",
            "attempts": 1,
        }

    # Decision 2 (Option B): Independent Status Calculation
    injection_verdict = "detected" if has_injection else "clean"
    phishing_verdict = "phishing" if is_phishing_pred else "legitimate"

    # Documented Policy for security_action:
    # 1. Clean Legitimate: allow
    # 2. Conventional Phishing: block
    # 3. Legitimate Injected: quarantine_review (flagged for prompt injection review without false phishing labeling)
    # 4. Attacked Phishing: block (phishing intent + injection attack)
    if has_injection and is_phishing_pred:
        security_action = "block"
        sec_desc = "Blocked: High-risk email with both phishing indicators and adversarial prompt injection."
    elif has_injection and not is_phishing_pred:
        security_action = "quarantine_review"
        sec_desc = "Quarantined for Review: Email content is non-phishing, but active prompt injection was detected."
    elif not has_injection and is_phishing_pred:
        security_action = "block"
        sec_desc = "Blocked: Classified as phishing correspondence."
    else:
        security_action = "allow"
        sec_desc = "Allowed: Legitimate correspondence with no prompt injection."

    reasons: list[str] = []
    if has_injection:
        reasons.append("🚨 [Stage 1 Alert] Indirect prompt injection detected inside email text.")
    else:
        reasons.append("✅ [Stage 1] Clean: No prompt injection manipulation detected.")

    if is_phishing_pred:
        reasons.append("🚨 [Stage 2 Alert] Email classified as phishing based on domain and intent indicators.")
    else:
        reasons.append("✅ [Stage 2] Email evaluated as legitimate correspondence.")

    reasons.append(f"🛡️ [Security Action] {sec_desc}")

    conf = 0.95 if is_phishing_pred else 0.90

    return {
        "method": "M4 (RAG Decoupled)",
        "verdict": phishing_verdict,
        "phishing_verdict": phishing_verdict,
        "is_phishing": is_phishing_pred,
        "has_injection": has_injection,
        "has_prompt_injection": has_injection,
        "injection_verdict": injection_verdict,
        "security_action": security_action,
        "has_prompt_injection_display": "DETECTED 🚨 (Stage 1)" if has_injection else "CLEAN ✅ (Stage 1)",
        "is_phishing_only": is_phishing_pred,
        "confidence": conf,
        "latency_ms": total_duration * 1000,
        "latency_seconds": total_duration,
        "reasons": reasons,
        "is_valid": True,
        "raw_response_call1": raw1,
        "raw_response_call2": raw2,
        "retrieved_samples": retrieved_samples,
        "failure_type": None,
        "failure_message": None,
        "attempts": 1,
    }


def classify_all_methods(
    email_text: str,
    model: str = DEFAULT_LIVE_MODEL,
    top_k: int = 3,
    api_base: str = "http://127.0.0.1:11434",
    include_archived: bool = True,
) -> dict[str, dict[str, Any]]:
    """Run detection architectures on input email.
    
    Active Production:
        M4: Decoupled Two-Stage RAG (Primary)
        M1: TF-IDF + Logistic Regression (Lightweight Baseline)
    Archived Research Baselines (if include_archived=True):
        M2: Zero-Shot LLM
        M3: RAG Combined
    """
    results = {
        "M1": classify_email_m1(email_text),
        "M4": classify_email_m4(email_text, model=model, top_k=top_k, api_base=api_base),
    }
    if include_archived:
        results["M2"] = classify_email_m2(email_text, model=model, api_base=api_base)
        results["M3"] = classify_email_m3(email_text, model=model, top_k=top_k, api_base=api_base)

    return results


def evaluate_method_disagreements(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Evaluate consensus and disagreements among classification results.

    Supports both active primary/baseline (M4 vs M1) and full 4-method comparison.
    """
    method_verdicts = {k: v.get("is_phishing", False) for k, v in results.items()}
    num_phishing = sum(1 for is_p in method_verdicts.values() if is_p)
    num_legitimate = len(method_verdicts) - num_phishing
    total = len(method_verdicts)

    has_disagreement = 0 < num_phishing < total
    styles: dict[str, dict[str, str]] = {}

    if not has_disagreement:
        majority_verdict = "phishing" if num_phishing == total else "legitimate"
        summary_title = f"🎯 Full Consensus ({num_phishing}/{total} {majority_verdict.capitalize()})"
        summary_detail = f"All {total} evaluated architectures reached the exact same conclusion: {majority_verdict.upper()}."
        for m in method_verdicts:
            styles[m] = {
                "card_class": "card-consensus",
                "badge_html": f'<span class="badge-agree">✅ Consensus ({majority_verdict.capitalize()})</span>',
                "status_label": f"Consensus ({majority_verdict.capitalize()})",
                "note": "Agrees with all other evaluated methods.",
            }
    elif total == 2 and "M4" in results and "M1" in results:
        # Comparison between Primary (M4) and Baseline (M1)
        m4_phish = results["M4"].get("is_phishing", False)
        m1_phish = results["M1"].get("is_phishing", False)
        majority_verdict = "phishing" if m4_phish else "legitimate"
        summary_title = f"⚡ Architectural Divergence: Primary M4 ({results['M4']['verdict'].upper()}) vs Baseline M1 ({results['M1']['verdict'].upper()})"
        summary_detail = (
            f"Primary Engine (M4) evaluated as {results['M4']['verdict'].upper()} (Security Action: {results['M4'].get('security_action', 'N/A').upper()}), "
            f"while Classical Baseline (M1) evaluated as {results['M1']['verdict'].upper()}."
        )
        styles["M4"] = {
            "card_class": "card-consensus",
            "badge_html": f'<span class="badge-agree">🛡️ Primary Verdict ({results["M4"]["verdict"].capitalize()})</span>',
            "status_label": f"Primary M4 ({results['M4']['verdict'].capitalize()})",
            "note": f"Authoritative verdict. Security action: {results['M4'].get('security_action', 'N/A').upper()}.",
        }
        styles["M1"] = {
            "card_class": "card-disagreement-warning",
            "badge_html": f'<span class="badge-disagree-warning">📊 Baseline Reference ({results["M1"]["verdict"].capitalize()})</span>',
            "status_label": f"Baseline M1 ({results['M1']['verdict'].capitalize()})",
            "note": "Lightweight token frequency baseline. Does not override M4.",
        }
    elif num_phishing >= 3:
        # Majority is Phishing (3-1)
        majority_verdict = "phishing"
        dissenting = [m for m, is_p in method_verdicts.items() if not is_p]
        dissent_str = ", ".join(dissenting)
        summary_title = "⚡ Disagreement Detected (3 Phishing vs 1 Legitimate)"
        summary_detail = (
            f"Majority of methods flagged this email as Phishing, but {dissent_str} predicted Legitimate."
        )
        if "M3" in dissenting:
            summary_detail += " Notice that M3 (RAG Combined) was deceived by the prompt injection into marking it legitimate!"

        for m, is_p in method_verdicts.items():
            if is_p:
                styles[m] = {
                    "card_class": "card-consensus",
                    "badge_html": '<span class="badge-agree">✅ Majority (Phishing)</span>',
                    "status_label": "Majority Consensus",
                    "note": "Aligned with majority detection.",
                }
            else:
                card_cls = "card-disagreement-danger" if m == "M3" else "card-disagreement-warning"
                badge = (
                    '<span class="badge-disagree-danger">🚨 FOOLED BY INJECTION</span>'
                    if m == "M3"
                    else '<span class="badge-disagree-warning">⚠️ DISSENTING (LEGITIMATE)</span>'
                )
                note = "Tricked by prompt injection!" if m == "M3" else "Dissenting verdict: predicted legitimate."
                styles[m] = {
                    "card_class": card_cls,
                    "badge_html": badge,
                    "status_label": "Dissenting Verdict",
                    "note": note,
                }
    elif num_legitimate >= 3:
        # Majority is Legitimate (1-3)
        majority_verdict = "legitimate"
        dissenting = [m for m, is_p in method_verdicts.items() if is_p]
        dissent_str = ", ".join(dissenting)
        summary_title = "⚡ Disagreement Detected (1 Phishing vs 3 Legitimate)"
        summary_detail = (
            f"Majority of methods evaluated this email as Legitimate, but {dissent_str} flagged it as Phishing."
        )
        if "M4" in dissenting:
            summary_detail += " Note: M4 Stage 1 detected prompt injection, isolating it from benign intent."

        for m, is_p in method_verdicts.items():
            if not is_p:
                styles[m] = {
                    "card_class": "card-consensus",
                    "badge_html": '<span class="badge-agree">✅ Majority (Legitimate)</span>',
                    "status_label": "Majority Consensus",
                    "note": "Aligned with majority evaluation.",
                }
            else:
                card_cls = "card-disagreement-warning"
                badge = '<span class="badge-disagree-warning">⚠️ DISSENTING (PHISHING)</span>'
                note = "Flagged phishing intent." if m != "M4" else "Flagged on intent indicators."
                styles[m] = {
                    "card_class": card_cls,
                    "badge_html": badge,
                    "status_label": "Dissenting Verdict",
                    "note": note,
                }
    else:
        # 2-2 Split Decision
        majority_verdict = "split"
        phish_methods = [m for m, is_p in method_verdicts.items() if is_p]
        legit_methods = [m for m, is_p in method_verdicts.items() if not is_p]
        summary_title = "⚡ Split Decision (2 Phishing vs 2 Legitimate)"
        summary_detail = (
            f"Classifiers are evenly split: {', '.join(phish_methods)} flagged Phishing, "
            f"while {', '.join(legit_methods)} evaluated Legitimate."
        )
        for m, is_p in method_verdicts.items():
            if is_p:
                styles[m] = {
                    "card_class": "card-disagreement-danger",
                    "badge_html": '<span class="badge-agree">🚨 Split: PHISHING</span>',
                    "status_label": "Split: Phishing",
                    "note": "Classified as Phishing in split decision.",
                }
            else:
                styles[m] = {
                    "card_class": "card-disagreement-warning",
                    "badge_html": '<span class="badge-disagree-warning">⚠️ Split: LEGITIMATE</span>',
                    "status_label": "Split: Legitimate",
                    "note": "Evaluated as Legitimate in split decision.",
                }

    return {
        "has_disagreement": has_disagreement,
        "num_phishing": num_phishing,
        "num_legitimate": num_legitimate,
        "majority_verdict": majority_verdict,
        "summary_title": summary_title,
        "summary_detail": summary_detail,
        "method_styles": styles,
    }
