from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.diagnostics.confounding_audit import audit_corpus


def _write_split(root: Path, rows: list[dict]) -> None:
    root.mkdir(exist_ok=True)
    for name in ("train", "test"):
        (root / f"{name}.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )


def test_format_and_source_shortcut_fails_gate(tmp_path: Path) -> None:
    rows = [
        {"id": f"p{i}", "text": f"From: attacker@example.com\nSubject: urgent scam {i}", "label": 1, "source": "phish"}
        for i in range(10)
    ] + [
        {"id": f"l{i}", "text": f"From: staff@example.org\nSubject: meeting notes {i}", "label": 0, "source": "legit"}
        for i in range(10)
    ]
    _write_split(tmp_path, rows)
    result = audit_corpus(tmp_path)
    assert result["gate"]["passed"] is False
    assert (tmp_path / "audit.json").exists()
    assert (tmp_path / "audit.md").exists()


def test_balanced_source_corpus_passes_gate(tmp_path: Path) -> None:
    rows = []
    for i in range(40):
        label = i % 2
        source = "a" if i % 4 < 2 else "b"
        word = "credential theft" if label else "project meeting"
        rows.append({
            "id": str(i),
            "text": f"Subject: {word} {i}\nBody: {'please verify account' if label else 'agenda and minutes'}",
            "label": label,
            "source": source,
        })
    _write_split(tmp_path, rows)
    result = audit_corpus(tmp_path)
    assert result["gate"]["passed"] is True
