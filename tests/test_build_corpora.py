from __future__ import annotations

import json
from pathlib import Path

from tools.data.build_corpora import build_corpora


def test_corpus_build_is_deterministic_and_respects_roles(tmp_path: Path) -> None:
    pool = tmp_path / "pool.jsonl"
    rows = []
    for index in range(12):
        rows.append({"id": f"l{index}", "text": f"legit message {index}", "label": "legit", "source": "enron"})
        rows.append({"id": f"p{index}", "text": f"phishing message {index}", "label": "phishing", "source": "nazario"})
    for index in range(12):
        rows.extend([
            {"id": f"cross-l{index}", "text": f"legit cross-source message {index}", "label": "legit", "source": "nazario"},
            {"id": f"cross-p{index}", "text": f"phishing cross-source message {index}", "label": "phishing", "source": "enron"},
        ])
    for index in range(4):
        rows.append({"id": f"e{index}", "text": f"attack message {index}", "label": "phishing", "source": "epvme", "family": "1"})
    pool.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    config = tmp_path / "corpora.yaml"
    config.write_text(
        json.dumps({
            "sources": {
                "enron": {"role": "legit"},
                "nazario": {"role": "phishing"},
                "epvme": {"role": "malicious"},
            },
            "corpora": {
                "primary_balanced": {
                    "include_roles": ["legit", "phishing"],
                    "exclude_sources": ["epvme"],
                    "target_phishing_share": [0.4, 0.6],
                    "max_source_share": 1.0,
                },
                "adversarial_robustness": {
                    "include_sources": ["epvme"],
                    "metrics_policy": "recall_only",
                },
                "legit_controls": {"include_roles": ["legit"]},
            },
        }),
        encoding="utf-8",
    )
    first = build_corpora(pool, config, tmp_path / "out1", 42)
    second = build_corpora(pool, config, tmp_path / "out2", 42)
    assert first["primary_balanced"]["class_balance"] == second["primary_balanced"]["class_balance"]
    assert (tmp_path / "out1/primary_balanced/split_manifest.json").exists()


def test_primary_corpus_reports_missing_legitimate_sources(tmp_path: Path) -> None:
    pool = tmp_path / "pool.jsonl"
    pool.write_text(json.dumps({"id": "p", "text": "phish", "label": "phishing", "source": "nazario"}) + "\n")
    config = tmp_path / "corpora.yaml"
    config.write_text(json.dumps({
        "sources": {"enron": {"role": "legit"}, "nazario": {"role": "phishing"}},
        "corpora": {"primary_balanced": {"include_roles": ["legit", "phishing"], "target_phishing_share": [0.4, 0.6]}},
    }))
    try:
        build_corpora(pool, config, tmp_path / "out", 42)
    except ValueError as exc:
        assert "enron" in str(exc)
    else:
        raise AssertionError("expected missing legitimate source failure")
