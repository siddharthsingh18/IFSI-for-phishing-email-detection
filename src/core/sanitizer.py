"""Input Sanitization Layer for Stage 2 Phishing Classifier.

When Stage 1 detects an active indirect prompt injection, this module extracts
the untrusted instruction span and substitutes a neutral placeholder, preventing
the adversarial instruction from reaching or manipulating Stage 2's context window.
"""

from __future__ import annotations

import re
from typing import Any

INJECTION_PLACEHOLDER = "[UNTRUSTED_INSTRUCTION_REDACTED]"

# Common injection bounding patterns used as secondary extraction heuristics
HEURISTIC_PATTERNS = [
    r"<!--\s*\[?AI AGENT INSTRUCTION\]?.*?-->",
    r"<!--\s*System note:.*?-->",
    r"\[SYSTEM DIRECTIVE\]:.*?(?:\n\n|\Z)",
    r"---\s*SYSTEM:\s*OVERRIDE INSTRUCTION\s*---.*?---\s*(?:END SYSTEM|END OVERRIDE)\s*---",
    r"---\s*SYSTEM:\s*OVERRIDE INSTRUCTION\s*---.*?(?:\n\n|\Z)",
    r"```json\s*\{\s*\"(?:override|system_override|override_model_output)\".*?\}\s*```",
    r"\{\s*\"system_override\":\s*true.*?\}",
    r"CONFIDENTIALITY & SECURITY COMPLIANCE DISCLAIMER:.*?(?:\n\n|\Z)",
    r"POLICY OVERRIDE EXEMPTION ID:.*?(?:\n\n|\Z)",
    r"\*\*\*\s*Special AI instruction token:.*?\*\*\*",
    r"(?i)ignore\s+(?:all\s+)?previous\s+instructions.*?(?:\n\n|\Z)",
    r"(?i)disregard\s+(?:all\s+)?prior\s+instructions.*?(?:\n\n|\Z)",
    r"(?i)system\s*directive:.*?(?:\n\n|\Z)",
]


def _find_normalized_span_indices(text: str, span: str) -> tuple[int, int] | None:
    """Find start and end indices of span in text using normalized whitespace matching."""
    if not span or not text:
        return None

    # 1. Exact match
    idx = text.find(span)
    if idx != -1:
        return idx, idx + len(span)

    # 2. Case-insensitive exact match
    text_lower = text.lower()
    span_lower = span.lower()
    idx = text_lower.find(span_lower)
    if idx != -1:
        return idx, idx + len(span)

    # 3. Normalized whitespace regex match
    escaped_tokens = [re.escape(token) for token in span.split() if token]
    if escaped_tokens:
        flexible_pattern = r"\s+".join(escaped_tokens)
        match = re.search(flexible_pattern, text, re.IGNORECASE)
        if match:
            return match.start(), match.end()

    return None


def sanitize_stage2_input(
    email_text: str,
    active_prompt_injection: bool,
    candidate_span: str | None = None,
) -> dict[str, Any]:
    """Sanitize email text before forwarding to Stage 2 phishing classifier.

    Args:
        email_text: Complete formatted email text.
        active_prompt_injection: Whether Stage 1 detected active injection.
        candidate_span: Substring identified by Stage 1 as the instruction span.

    Returns:
        Dict containing:
            - sanitized_text: Sanitized text safe for Stage 2.
            - is_sanitized: bool indicating whether redaction took place.
            - redacted_span: Exact string that was redacted.
            - safe_fallback_triggered: bool indicating if span extraction failed
              requiring defensive fallback.
            - requires_manual_review: bool indicating if safe routing is advised.
    """
    if not active_prompt_injection:
        return {
            "sanitized_text": email_text,
            "is_sanitized": False,
            "redacted_span": None,
            "safe_fallback_triggered": False,
            "requires_manual_review": False,
        }

    # 1. Attempt extraction using candidate_span from Stage 1
    if candidate_span and len(candidate_span.strip()) > 5:
        span_loc = _find_normalized_span_indices(email_text, candidate_span.strip())
        if span_loc:
            start, end = span_loc
            original_span = email_text[start:end]
            sanitized = email_text[:start] + INJECTION_PLACEHOLDER + email_text[end:]
            return {
                "sanitized_text": sanitized,
                "is_sanitized": True,
                "redacted_span": original_span,
                "safe_fallback_triggered": False,
                "requires_manual_review": False,
            }

    # 2. Secondary heuristic fallback: scan for known injection pattern blocks
    for pat in HEURISTIC_PATTERNS:
        match = re.search(pat, email_text, re.DOTALL)
        if match:
            start, end = match.start(), match.end()
            original_span = email_text[start:end]
            sanitized = email_text[:start] + INJECTION_PLACEHOLDER + email_text[end:]
            return {
                "sanitized_text": sanitized,
                "is_sanitized": True,
                "redacted_span": original_span,
                "safe_fallback_triggered": True,
                "requires_manual_review": False,
            }

    # 3. Fail-Safe Fallback:
    # Active injection was asserted by Stage 1, but specific span could not be isolated.
    # Rather than passing potentially malicious instructions into Stage 2 unredacted,
    # mark message for manual review and prepend a protective delimiter.
    fallback_text = (
        f"--- CAUTION: UNRESOLVED ADVERSARIAL INSTRUCTION DETECTED IN BODY ---\n"
        f"{INJECTION_PLACEHOLDER}\n"
        f"--- END PROTECTIVE BOUNDARY ---\n\n"
        f"{email_text}"
    )
    return {
        "sanitized_text": fallback_text,
        "is_sanitized": False,
        "redacted_span": None,
        "safe_fallback_triggered": True,
        "requires_manual_review": True,
    }

