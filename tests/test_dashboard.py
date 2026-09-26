"""Unit and AppTest integration tests for the Benchmark Dashboard and Worst Mistakes analysis."""

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
    get_worst_mistakes,
    load_benchmark_summary,
    load_email_text_lookup,
    load_pilot_summary,
)


def test_load_email_text_lookup() -> None:
    """Test that email text lookup successfully maps email IDs from test split and injections."""
    lookup = load_email_text_lookup()
    assert len(lookup) >= 1500, f"Expected >=1500 indexed email texts, found {len(lookup)}"
    # Verify clean test ID
    assert "email-04377" in lookup
    assert len(lookup["email-04377"]) > 0


def test_load_pilot_summary() -> None:
    """Test loading llama3.2:3b pilot benchmark summary."""
    pilot = load_pilot_summary()
    assert "methods" in pilot
    assert "M2" in pilot["methods"]
    assert "M3" in pilot["methods"]
    assert "M4" in pilot["methods"]


def test_get_worst_mistakes_structure_and_constraints() -> None:
    """Test that worst mistakes extraction satisfies all user requirements:
    - 10 highest-confidence wrong predictions per method
    - Truncated snippets <= 203 chars (200 + '...')
    - Fields: snippet, true label, predicted label, confidence
    - Sorted descending by confidence per method
    """
    mistakes = get_worst_mistakes(methods=("M1", "M2", "M3", "M4"), top_n_per_method=10)
    assert len(mistakes) > 0

    by_method: dict[str, list[dict]] = {}
    for m in mistakes:
        by_method.setdefault(m["method"], []).append(m)

        # Check required fields
        assert "snippet" in m
        assert "true_label" in m
        assert "predicted_label" in m
        assert "confidence" in m
        assert "method" in m
        assert "condition" in m
        assert "model" in m

        # Check snippet truncation (200 chars max + optional '...' ellipses)
        assert len(m["snippet"]) <= 205, f"Snippet exceeded length constraint: {len(m['snippet'])}"

        # Check that it is an actual wrong prediction
        assert m["predicted_label"] != m["true_label"], f"Expected mistake, but labels matched: {m}"

    # Check top 10 limit per method
    for method_name, m_list in by_method.items():
        assert len(m_list) <= 10, f"Expected <= 10 mistakes for {method_name}, got {len(m_list)}"

        # Check sorted descending by confidence
        confidences = [item["confidence"] for item in m_list]
        assert confidences == sorted(confidences, reverse=True), f"Mistakes not sorted descending for {method_name}: {confidences}"


def test_get_worst_mistakes_filtered_by_method_and_condition() -> None:
    """Test filtering worst mistakes to a single method and condition."""
    m3_unmarked = get_worst_mistakes(methods=("M3",), conditions=("unmarked",), top_n_per_method=10)
    for item in m3_unmarked:
        assert item["method"] == "M3"
        assert item["condition"] == "Unmarked"


def test_dashboard_apptest_loads_and_filters() -> None:
    """Test that Dashboard page loads without error and responds to filter modifications."""
    dashboard_path = Path(__file__).resolve().parents[1] / "pages" / "2_Dashboard.py"
    at = AppTest.from_file(str(dashboard_path))
    at.run(timeout=15)
    assert not at.exception, f"Dashboard threw exception on load: {at.exception}"

    # Filter methods to M1 and M3
    at.sidebar.multiselect[0].set_value(["M1", "M3"]).run(timeout=15)
    assert not at.exception, f"Dashboard threw exception on method filter: {at.exception}"

    # Filter condition to unmarked
    at.sidebar.multiselect[1].set_value(["unmarked"]).run(timeout=15)
    assert not at.exception, f"Dashboard threw exception on condition filter: {at.exception}"
