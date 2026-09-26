"""Tests for Injection Lab utilities, attack family examples, and AppTest page loading."""

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
    load_attack_family_examples,
    load_benchmark_summary,
)


def test_load_attack_family_examples() -> None:
    """Test that all 5 attack families load both marked and unmarked authentic templates."""
    fam_examples = load_attack_family_examples()
    expected_families = [
        "label_override",
        "false_authority",
        "output_hijack",
        "rule_redefinition",
        "light_obfuscation",
    ]

    for fam in expected_families:
        assert fam in fam_examples, f"Missing attack family: {fam}"
        fam_data = fam_examples[fam]

        # Marked template checks
        marked = fam_data.get("marked", {})
        assert "injected_text" in marked
        assert "[BEGIN EMBEDDED CLASSIFIER MESSAGE]" in marked["injected_text"]
        assert len(marked.get("base_instruction", "")) > 0

        # Unmarked styles checks
        unmarked_styles = fam_data.get("unmarked_by_style", {})
        assert len(unmarked_styles) >= 2, f"Expected multiple disguise styles for {fam}, got {len(unmarked_styles)}"
        for style_name, variants in unmarked_styles.items():
            assert len(variants) > 0
            assert "[BEGIN EMBEDDED CLASSIFIER MESSAGE]" not in variants[0]["injected_text"]
            assert len(variants[0]["injected_text"]) > 0


def test_prompt_8_benchmark_cells_present() -> None:
    """Verify that Prompt 8 marked and unmarked cells for M1-M4 exist in full benchmark summary."""
    summary = load_benchmark_summary()
    cells = summary.get("cells", {})

    for m in ("M1", "M2", "M3", "M4"):
        for c in ("marked", "unmarked"):
            cell_key = f"{m}_{c}"
            assert cell_key in cells, f"Missing cell {cell_key} in benchmark summary"
            metrics = cells[cell_key].get("metrics", {})
            assert "recall" in metrics
            assert "fpr" in metrics
            assert 0.0 <= metrics["recall"] <= 1.0
            assert 0.0 <= metrics["fpr"] <= 1.0


def test_injection_lab_apptest_loads_and_changes_family() -> None:
    """Test that pages/3_Injection_Lab.py loads cleanly and allows family selection."""
    lab_path = Path(__file__).resolve().parents[1] / "pages" / "3_Injection_Lab.py"
    at = AppTest.from_file(str(lab_path))
    at.run(timeout=15)
    assert not at.exception, f"Injection Lab threw exception on initial load: {at.exception}"

    # Select another family
    at.selectbox[0].set_value("false_authority").run(timeout=15)
    assert not at.exception, f"Injection Lab threw exception after selecting false_authority: {at.exception}"

    # Select another family
    at.selectbox[0].set_value("output_hijack").run(timeout=15)
    assert not at.exception, f"Injection Lab threw exception after selecting output_hijack: {at.exception}"
