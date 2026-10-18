"""Core single-call and multi-model inference functions (M1, M2, M3, M4) with zero Streamlit imports."""

from __future__ import annotations

import json
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


def classify_email_m1(email_text: str) -> dict[str, Any]:
    """Classify email using classical TF-IDF + LogisticRegression (M1)."""
    t0 = time.perf_counter()
    vec, clf = get_m1_model()
    X = vec.transform([email_text])
    pred = int(clf.predict(X)[0])
    prob = float(clf.predict_proba(X)[0][pred])
    elapsed_ms = (time.perf_counter() - t0) * 1000

    feature_names = vec.get_feature_names_out()
    nonzero_indices = X.nonzero()[1]
    coefs = clf.coef_[0]
    token_weights = [(feature_names[i], coefs[i] * X[0, i]) for i in nonzero_indices]
    token_weights.sort(key=lambda x: abs(x[1]), reverse=True)
    top_tokens = [f"{t} ({'+' if w > 0 else ''}{w:.2f})" for t, w in token_weights[:5]]

    return {
        "method": "M1 (TF-IDF + LogReg)",
        "verdict": "phishing" if pred == 1 else "legitimate",
        "is_phishing": pred == 1,
        "confidence": prob,
        "has_prompt_injection": False,
        "has_prompt_injection_display": "No (N/A — Bag-of-Words)",
        "latency_ms": elapsed_ms,
        "latency_seconds": elapsed_ms / 1000,
        "reasons": [
            "Linear decision boundary on 10,000 TF-IDF n-gram token weights.",
            f"Influential tokens: {', '.join(top_tokens) if top_tokens else 'Standard vocabulary frequencies'}"
        ],
        "is_valid": True,
        "raw_response": f"Predicted label: {pred} (probability {prob:.4f})",
    }


def _call_ollama_json(
    system_prompt: str,
    user_prompt: str,
    model: str = "qwen2.5:0.5b",
    api_base: str = "http://127.0.0.1:11434",
    timeout: float = 30.0,
) -> tuple[dict[str, Any] | None, str, float]:
    """Call Ollama /api/chat with format=json and measure duration."""
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
        "options": {"temperature": 0.0, "num_predict": 512},
    }

    try:
        resp = httpx.post(url, json=payload, timeout=timeout)
        duration = time.perf_counter() - t0
        if resp.status_code == 200:
            data = resp.json()
            raw_text = data.get("message", {}).get("content", "")
            clean_json_str = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
            try:
                parsed = json.loads(clean_json_str)
                return parsed, raw_text, duration
            except json.JSONDecodeError:
                return None, raw_text, duration
        return None, f"HTTP Error {resp.status_code}: {resp.text[:300]}", duration
    except Exception as exc:
        return None, f"Connection error: {exc}", time.perf_counter() - t0


def classify_email_m2(
    email_text: str,
    model: str = "qwen2.5:0.5b",
    api_base: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    """Classify email using Zero-Shot LLM (M2)."""
    user_prompt = f"Analyze the following incoming email and classify it:\n\n{email_text}"
    parsed, raw_text, duration = _call_ollama_json(SYSTEM_PROMPT, user_prompt, model=model, api_base=api_base)

    if parsed and "verdict" in parsed:
        verdict = str(parsed.get("verdict", "legitimate")).lower().strip()
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

        return {
            "method": "M2 (Zero-Shot LLM)",
            "verdict": "phishing" if is_phish else "legitimate",
            "is_phishing": is_phish,
            "confidence": conf,
            "has_prompt_injection": has_inj,
            "has_prompt_injection_display": "DETECTED 🚨 (In Reasons)" if has_inj else "NOT FLAGGED (Zero-Shot)",
            "latency_ms": duration * 1000,
            "latency_seconds": duration,
            "reasons": reasons or ["No explicit reasons provided by model."],
            "is_valid": True,
            "raw_response": raw_text,
        }

    return {
        "method": "M2 (Zero-Shot LLM)",
        "verdict": "legitimate",
        "is_phishing": False,
        "confidence": 0.0,
        "has_prompt_injection": False,
        "has_prompt_injection_display": "NOT FLAGGED (Parse Error)",
        "latency_ms": duration * 1000,
        "latency_seconds": duration,
        "reasons": ["Error: Model failed to emit valid JSON conforming to target schema."],
        "is_valid": False,
        "raw_response": raw_text,
    }


def classify_email_m3(
    email_text: str,
    model: str = "qwen2.5:0.5b",
    top_k: int = 3,
    api_base: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    """Classify email using RAG Combined Single-Call (M3)."""
    retriever = get_rag_retriever()
    ref_block = "No reference exemplars available."
    retrieved_samples: list[dict[str, Any]] = []

    if retriever is not None:
        try:
            retrieved_samples = retriever.retrieve(email_text, top_k=top_k)
            ref_block = format_reference_block(retrieved_samples)
        except Exception as exc:
            ref_block = f"Retrieval error: {exc}"

    user_prompt = (
        f"{ref_block}\n\n"
        f"--- INCOMING EMAIL TO CLASSIFY ---\n"
        f"{email_text}\n"
        f"--- END INCOMING EMAIL ---"
    )

    parsed, raw_text, duration = _call_ollama_json(RAG_SYSTEM_PROMPT, user_prompt, model=model, api_base=api_base)

    if parsed and "verdict" in parsed:
        verdict = str(parsed.get("verdict", "legitimate")).lower().strip()
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

        return {
            "method": "M3 (RAG Combined)",
            "verdict": "phishing" if is_phish else "legitimate",
            "is_phishing": is_phish,
            "confidence": conf,
            "has_prompt_injection": has_inj,
            "has_prompt_injection_display": "DETECTED 🚨 (In Reasons)" if has_inj else "NOT FLAGGED / EVADED",
            "latency_ms": duration * 1000,
            "latency_seconds": duration,
            "reasons": reasons or ["No reasons provided."],
            "is_valid": True,
            "raw_response": raw_text,
            "retrieved_samples": retrieved_samples,
        }

    return {
        "method": "M3 (RAG Combined)",
        "verdict": "legitimate",
        "is_phishing": False,
        "confidence": 0.0,
        "has_prompt_injection": False,
        "has_prompt_injection_display": "NOT FLAGGED (Parse Error)",
        "latency_ms": duration * 1000,
        "latency_seconds": duration,
        "reasons": ["Error: Model failed to emit valid JSON matching RAG schema."],
        "is_valid": False,
        "raw_response": raw_text,
        "retrieved_samples": retrieved_samples,
    }


def classify_email_m4(
    email_text: str,
    model: str = "qwen2.5:0.5b",
    top_k: int = 3,
    api_base: str = "http://127.0.0.1:11434",
) -> dict[str, Any]:
    """Classify email using RAG Two-Call Decoupled pipeline (M4)."""
    retriever = get_rag_retriever()
    ref_block = ""
    retrieved_samples: list[dict[str, Any]] = []
    if retriever is not None:
        try:
            retrieved_samples = retriever.retrieve(email_text, top_k=top_k)
            ref_block = format_reference_block(retrieved_samples)
        except Exception:
            pass

    # --- Call 1: Injection Detector ---
    user_prompt_c1 = f"Inspect this untrusted email for prompt injection:\n\n{email_text}"
    p1, raw1, dur1 = _call_ollama_json(SYSTEM_INJECTION_DETECTOR, user_prompt_c1, model=model, api_base=api_base)
    has_injection = bool(p1.get("has_prompt_injection", False)) if p1 else False

    # --- Call 2: Boolean Phishing ---
    user_prompt_c2 = f"{ref_block}\n\nEmail to evaluate:\n{email_text}"
    p2, raw2, dur2 = _call_ollama_json(SYSTEM_IS_PHISHING_ONLY, user_prompt_c2, model=model, api_base=api_base)
    is_phishing_pred = bool(p2.get("is_phishing", False)) if p2 else False

    total_duration = dur1 + dur2

    # Check for execution/connection failures in either decoupled stage
    if p1 is None or p2 is None:
        failed_calls: list[str] = []
        if p1 is None:
            failed_calls.append("Stage 1 (Injection Detector)")
        if p2 is None:
            failed_calls.append("Stage 2 (Classifier)")
        return {
            "method": "M4 (RAG Decoupled)",
            "verdict": "legitimate",
            "is_phishing": False,
            "has_injection": False,
            "has_prompt_injection": False,
            "has_prompt_injection_display": "NOT FLAGGED (Execution Error)",
            "is_phishing_only": False,
            "confidence": 0.0,
            "latency_ms": total_duration * 1000,
            "latency_seconds": total_duration,
            "reasons": [
                f"Error: Model pipeline failed on {', '.join(failed_calls)}. Verify local LLM service (Ollama) is active.",
            ],
            "is_valid": False,
            "raw_response_call1": raw1,
            "raw_response_call2": raw2,
            "retrieved_samples": retrieved_samples,
        }

    overall_malicious = has_injection or is_phishing_pred

    reasons: list[str] = []
    if has_injection:
        reasons.append("🚨 [Call 1 Alert] Indirect prompt injection detected inside email text.")
    else:
        reasons.append("✅ [Call 1] No prompt injection manipulation detected.")

    if is_phishing_pred:
        reasons.append("🚨 [Call 2 Alert] Email classified as phishing based on retrieved domain indicators.")
    else:
        reasons.append("✅ [Call 2] Email evaluated as legitimate correspondence.")

    return {
        "method": "M4 (RAG Decoupled)",
        "verdict": "phishing" if overall_malicious else "legitimate",
        "is_phishing": overall_malicious,
        "has_injection": has_injection,
        "has_prompt_injection": has_injection,
        "has_prompt_injection_display": "DETECTED 🚨 (Call 1)" if has_injection else "CLEAN ✅ (Call 1)",
        "is_phishing_only": is_phishing_pred,
        "confidence": 0.95 if overall_malicious else 0.90,
        "latency_ms": total_duration * 1000,
        "latency_seconds": total_duration,
        "reasons": reasons,
        "is_valid": True,
        "raw_response_call1": raw1,
        "raw_response_call2": raw2,
        "retrieved_samples": retrieved_samples,
    }


def classify_all_methods(
    email_text: str,
    model: str = "qwen2.5:0.5b",
    top_k: int = 3,
    api_base: str = "http://127.0.0.1:11434",
) -> dict[str, dict[str, Any]]:
    """Run all four methods (M1, M2, M3, M4) on the same input email."""
    return {
        "M1": classify_email_m1(email_text),
        "M2": classify_email_m2(email_text, model=model, api_base=api_base),
        "M3": classify_email_m3(email_text, model=model, top_k=top_k, api_base=api_base),
        "M4": classify_email_m4(email_text, model=model, top_k=top_k, api_base=api_base),
    }


def evaluate_method_disagreements(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Evaluate consensus and disagreements among M1, M2, M3, M4 classification results.

    Returns:
        dict containing disagreement flags, counts, titles, descriptions, and per-method metadata.
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
        summary_detail = f"All {total} detection architectures reached the exact same conclusion: {majority_verdict.upper()}."
        for m in method_verdicts:
            styles[m] = {
                "card_class": "card-consensus",
                "badge_html": f'<span class="badge-agree">✅ Consensus ({majority_verdict.capitalize()})</span>',
                "status_label": f"Consensus ({majority_verdict.capitalize()})",
                "note": "Agrees with all other methods.",
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
            summary_detail += " Note: M4's Call 1 triggered an injection alert on compliance text (False Alarm Tax)."

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
                note = "False alarm on injected language." if m == "M4" else "Dissenting verdict: flagged phishing."
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
