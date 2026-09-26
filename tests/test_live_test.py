"""Tests for Live Test page utilities, unmarked injection synthesis, and disagreement highlighting."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is on path
src_dir = Path(__file__).resolve().parents[1] / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import pytest
from streamlit.testing.v1 import AppTest

from ui_utils import (
    apply_unmarked_injection,
    evaluate_method_disagreements,
    get_random_unmarked_injection,
    load_unmarked_injection_templates,
)


def test_load_unmarked_injection_templates() -> None:
    """Test that authentic unmarked injection templates load correctly from data/injections."""
    templates = load_unmarked_injection_templates()
    assert len(templates) >= 40, f"Expected at least 40 templates, got {len(templates)}"

    for tmpl in templates:
        assert "attack_family" in tmpl
        assert "injection_style" in tmpl
        assert "attack_position" in tmpl
        assert "injected_text" in tmpl
        assert len(tmpl["injected_text"].strip()) > 0


def test_get_random_unmarked_injection() -> None:
    """Test random unmarked injection sampling with deterministic seed."""
    t1 = get_random_unmarked_injection(seed=42)
    t2 = get_random_unmarked_injection(seed=42)
    assert t1 == t2
    assert "injected_text" in t1


def test_apply_unmarked_injection_positions() -> None:
    """Test injection blending into email body across body_start, body_end, and body_middle."""
    body = "Line 1: Account alert.\nLine 2: Please log in.\nLine 3: Thank you."
    payload = "--- INJECTION PAYLOAD ---"

    # Start
    tmpl_start = {"attack_position": "body_start", "injected_text": payload}
    res_start = apply_unmarked_injection(body, tmpl_start)
    assert res_start.startswith(payload)
    assert body in res_start

    # End
    tmpl_end = {"attack_position": "body_end", "injected_text": payload}
    res_end = apply_unmarked_injection(body, tmpl_end)
    assert res_end.endswith(payload)
    assert body in res_end

    # Middle
    tmpl_mid = {"attack_position": "body_middle", "injected_text": payload}
    res_mid = apply_unmarked_injection(body, tmpl_mid)
    assert payload in res_mid


def test_evaluate_method_disagreements_full_consensus_phishing() -> None:
    """Test consensus when all 4 methods predict phishing."""
    results = {
        "M1": {"is_phishing": True, "confidence": 0.95},
        "M2": {"is_phishing": True, "confidence": 0.88},
        "M3": {"is_phishing": True, "confidence": 0.92},
        "M4": {"is_phishing": True, "confidence": 0.99},
    }
    summary = evaluate_method_disagreements(results)
    assert summary["has_disagreement"] is False
    assert summary["majority_verdict"] == "phishing"
    for m in results:
        assert summary["method_styles"][m]["card_class"] == "card-consensus"
        assert "Consensus" in summary["method_styles"][m]["status_label"]


def test_evaluate_method_disagreements_full_consensus_legitimate() -> None:
    """Test consensus when all 4 methods predict legitimate."""
    results = {
        "M1": {"is_phishing": False, "confidence": 0.90},
        "M2": {"is_phishing": False, "confidence": 0.85},
        "M3": {"is_phishing": False, "confidence": 0.93},
        "M4": {"is_phishing": False, "confidence": 0.91},
    }
    summary = evaluate_method_disagreements(results)
    assert summary["has_disagreement"] is False
    assert summary["majority_verdict"] == "legitimate"


def test_evaluate_method_disagreements_m3_fooled() -> None:
    """Test 3 Phishing vs 1 Legitimate (M3 fooled by prompt injection)."""
    results = {
        "M1": {"is_phishing": True, "confidence": 0.95},
        "M2": {"is_phishing": True, "confidence": 0.88},
        "M3": {"is_phishing": False, "confidence": 0.90},  # Fooled!
        "M4": {"is_phishing": True, "confidence": 0.99},
    }
    summary = evaluate_method_disagreements(results)
    assert summary["has_disagreement"] is True
    assert summary["num_phishing"] == 3
    assert summary["num_legitimate"] == 1
    assert summary["majority_verdict"] == "phishing"

    # M3 should be flagged in danger / warning disagreement style
    assert summary["method_styles"]["M3"]["card_class"] == "card-disagreement-danger"
    assert "FOOLED" in summary["method_styles"]["M3"]["badge_html"]

    # Majority methods should have consensus style
    assert summary["method_styles"]["M1"]["card_class"] == "card-consensus"
    assert summary["method_styles"]["M4"]["card_class"] == "card-consensus"


def test_evaluate_method_disagreements_m4_false_alarm() -> None:
    """Test 1 Phishing vs 3 Legitimate (M4 false alarm on compliance text)."""
    results = {
        "M1": {"is_phishing": False, "confidence": 0.95},
        "M2": {"is_phishing": False, "confidence": 0.88},
        "M3": {"is_phishing": False, "confidence": 0.90},
        "M4": {"is_phishing": True, "confidence": 0.95},  # False Alarm
    }
    summary = evaluate_method_disagreements(results)
    assert summary["has_disagreement"] is True
    assert summary["num_phishing"] == 1
    assert summary["num_legitimate"] == 3
    assert summary["majority_verdict"] == "legitimate"

    assert summary["method_styles"]["M4"]["card_class"] == "card-disagreement-warning"
    assert "DISSENTING" in summary["method_styles"]["M4"]["badge_html"]


def test_evaluate_method_disagreements_split_decision() -> None:
    """Test 2 Phishing vs 2 Legitimate (Split decision)."""
    results = {
        "M1": {"is_phishing": True, "confidence": 0.95},
        "M2": {"is_phishing": False, "confidence": 0.88},
        "M3": {"is_phishing": False, "confidence": 0.90},
        "M4": {"is_phishing": True, "confidence": 0.95},
    }
    summary = evaluate_method_disagreements(results)
    assert summary["has_disagreement"] is True
    assert summary["majority_verdict"] == "split"
    assert summary["method_styles"]["M1"]["card_class"] == "card-disagreement-danger"
    assert summary["method_styles"]["M2"]["card_class"] == "card-disagreement-warning"


def test_app_test_live_test_page_loads() -> None:
    """Test that pages/1_Live_Test.py loads without error and renders widgets."""
    page_path = Path(__file__).resolve().parents[1] / "pages" / "1_Live_Test.py"
    at = AppTest.from_file(str(page_path))
    at.run()
    assert not at.exception, f"Live Test page threw exception: {at.exception}"
    assert len(at.title) >= 1
    assert len(at.toggle) >= 1

    # Toggle unmarked injection
    at.toggle[0].set_value(True).run()
    assert not at.exception, f"Live Test page threw exception after toggle: {at.exception}"
