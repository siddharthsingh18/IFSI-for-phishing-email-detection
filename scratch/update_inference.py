from pathlib import Path

inference_path = Path("src/core/inference.py")
content = inference_path.read_text(encoding="utf-8")

# 1. Update _call_ollama_json
old_call = """def _call_ollama_json(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_LIVE_MODEL,
    api_base: str = "http://127.0.0.1:11434",
    timeout: float = 30.0,
) -> tuple[dict[str, Any] | None, str, float, str | None]:
    \"\"\"Call Ollama /api/chat with format=json and measure duration.\"\"\"
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
"""

new_call = """def _call_ollama_json(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_LIVE_MODEL,
    api_base: str = "http://127.0.0.1:11434",
    timeout: float = 60.0,
) -> tuple[dict[str, Any] | None, str, float, str | None]:
    \"\"\"Call Ollama /api/chat with format=json, think=False, and measure duration.\"\"\"
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
"""

content = content.replace(old_call.replace("\r\n", "\n"), new_call.replace("\r\n", "\n"))

# 2. Update M2 error returns
old_m2_unsupported = """        if verdict not in {"phishing", "legitimate"}:
            return {
                "method": "M2 (Zero-Shot LLM)",
                "verdict": "legitimate",
                "is_phishing": False,
                "confidence": 0.0,
                "has_prompt_injection": False,
                "has_prompt_injection_display": "NOT FLAGGED (Unsupported Verdict)",
                "latency_ms": duration * 1000,
                "latency_seconds": duration,
                "reasons": ["Error: Model returned an unsupported verdict."],
                "is_valid": False,
                "raw_response": raw_text,
                "failure_type": "unsupported_verdict",
                "failure_message": f"Unsupported verdict: {verdict}",
                "attempts": 1,
            }"""

new_m2_unsupported = """        if verdict not in {"phishing", "legitimate"}:
            return {
                "method": "M2 (Zero-Shot LLM)",
                "verdict": "error",
                "is_phishing": False,
                "confidence": 0.0,
                "has_prompt_injection": False,
                "has_prompt_injection_display": "ERROR (Unsupported Verdict)",
                "latency_ms": duration * 1000,
                "latency_seconds": duration,
                "reasons": [f"Error: Model returned an unsupported verdict '{verdict}'."],
                "is_valid": False,
                "raw_response": raw_text,
                "failure_type": "unsupported_verdict",
                "failure_message": f"Unsupported verdict: {verdict}",
                "attempts": 1,
            }"""

content = content.replace(old_m2_unsupported.replace("\r\n", "\n"), new_m2_unsupported.replace("\r\n", "\n"))

old_m2_failure = """    return {
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
        "failure_type": failure_type or ("schema_error" if parsed else "invalid_json"),
        "failure_message": raw_text,
        "attempts": 1,
    }"""

new_m2_failure = """    return {
        "method": "M2 (Zero-Shot LLM)",
        "verdict": "error",
        "is_phishing": False,
        "confidence": 0.0,
        "has_prompt_injection": False,
        "has_prompt_injection_display": "ERROR (Inference Failure)",
        "latency_ms": duration * 1000,
        "latency_seconds": duration,
        "reasons": [f"Error: {raw_text or 'Model failed to emit valid JSON conforming to target schema.'}"],
        "is_valid": False,
        "raw_response": raw_text,
        "failure_type": failure_type or ("schema_error" if parsed else "invalid_json"),
        "failure_message": raw_text,
        "attempts": 1,
    }"""

content = content.replace(old_m2_failure.replace("\r\n", "\n"), new_m2_failure.replace("\r\n", "\n"))

# 3. Update M3 error returns
old_m3_unsupported = """        if verdict not in {"phishing", "legitimate"}:
            return {
                "method": "M3 (RAG Combined)",
                "verdict": "legitimate",
                "is_phishing": False,
                "confidence": 0.0,
                "has_prompt_injection": False,
                "has_prompt_injection_display": "NOT FLAGGED (Unsupported Verdict)",
                "latency_ms": duration * 1000,
                "latency_seconds": duration,
                "reasons": ["Error: Model returned an unsupported verdict."],
                "is_valid": False,
                "raw_response": raw_text,
                "retrieved_samples": retrieved_samples,
                "failure_type": "unsupported_verdict",
                "failure_message": f"Unsupported verdict: {verdict}",
                "attempts": 1,
            }"""

new_m3_unsupported = """        if verdict not in {"phishing", "legitimate"}:
            return {
                "method": "M3 (RAG Combined)",
                "verdict": "error",
                "is_phishing": False,
                "confidence": 0.0,
                "has_prompt_injection": False,
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
            }"""

content = content.replace(old_m3_unsupported.replace("\r\n", "\n"), new_m3_unsupported.replace("\r\n", "\n"))

old_m3_failure = """    return {
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
        "failure_type": None,
        "failure_message": None,
        "attempts": 2,
        "failure_type": failure_type or ("retrieval_error" if retriever is None else "invalid_json"),
        "failure_message": raw_text,
        "attempts": 1,
    }"""

new_m3_failure = """    return {
        "method": "M3 (RAG Combined)",
        "verdict": "error",
        "is_phishing": False,
        "confidence": 0.0,
        "has_prompt_injection": False,
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
    }"""

content = content.replace(old_m3_failure.replace("\r\n", "\n"), new_m3_failure.replace("\r\n", "\n"))

# 4. Update M4 Decoupled classification and error handling
old_m4_logic = """    # Check for execution/connection failures in either decoupled stage
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
            "failure_type": failure1 or failure2 or "unavailable",
            "failure_message": "One or more pipeline calls failed.",
            "attempts": 1,
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
    }"""

new_m4_logic = """    # Check for execution/connection failures in either decoupled stage
    if p1 is None or p2 is None:
        failed_calls: list[str] = []
        if p1 is None:
            failed_calls.append("Stage 1 (Injection Detector)")
        if p2 is None:
            failed_calls.append("Stage 2 (Classifier)")
        return {
            "method": "M4 (RAG Decoupled)",
            "verdict": "error",
            "is_phishing": False,
            "has_injection": False,
            "has_prompt_injection": False,
            "has_prompt_injection_display": "ERROR (Execution Error)",
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
            "failure_type": failure1 or failure2 or "unavailable",
            "failure_message": "One or more pipeline calls failed.",
            "attempts": 1,
        }

    # CRITICAL: Separate injection detection from phishing classification verdict.
    # Call 2 decides whether the email itself is phishing; Call 1 detects injection presence.
    verdict = "phishing" if is_phishing_pred else "legitimate"

    reasons: list[str] = []
    if has_injection:
        reasons.append("🚨 [Call 1 Alert] Indirect prompt injection detected inside email text.")
    else:
        reasons.append("✅ [Call 1] No prompt injection manipulation detected.")

    if is_phishing_pred:
        reasons.append("🚨 [Call 2 Alert] Email classified as phishing based on retrieved domain indicators.")
    else:
        reasons.append("✅ [Call 2] Email evaluated as legitimate correspondence.")

    conf = 0.95 if is_phishing_pred else 0.90

    return {
        "method": "M4 (RAG Decoupled)",
        "verdict": verdict,
        "is_phishing": is_phishing_pred,
        "has_injection": has_injection,
        "has_prompt_injection": has_injection,
        "has_prompt_injection_display": "DETECTED 🚨 (Call 1)" if has_injection else "CLEAN ✅ (Call 1)",
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
    }"""

content = content.replace(old_m4_logic.replace("\r\n", "\n"), new_m4_logic.replace("\r\n", "\n"))
inference_path.write_text(content, encoding="utf-8")
print("Updated src/core/inference.py")

