from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "merge_tagged_datasets.py"
SPEC = importlib.util.spec_from_file_location("merge_tagged_datasets", SCRIPT_PATH)
assert SPEC and SPEC.loader
merge_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(merge_module)


def _inputs(root: Path) -> tuple[Path, Path]:
    iwspa = root / "iwspa"
    (iwspa / "Synthetic").mkdir(parents=True)
    (iwspa / "Adversarial").mkdir(parents=True)
    with (iwspa / "Synthetic" / "synthetic_phish.csv").open("w", encoding="utf-8") as handle:
        handle.write("text,label\n")
        for index in range(20):
            handle.write(f"synthetic unique phishing message {index},1\n")
    with (iwspa / "Adversarial" / "adversarial_dataset.csv").open("w", encoding="utf-8") as handle:
        handle.write("text,label\n")
        for index in range(20):
            handle.write(f"adversarial unique legitimate message {index},0\n")

    epvme = root / "epvme"
    for directory in merge_module.EPVME_CANONICAL_DIRS:
        (epvme / directory).mkdir(parents=True)
    (epvme / "1" / "one.eml").write_text(
        "Subject: unique phishing sample\n\nPlease verify the account.",
        encoding="utf-8",
    )
    return iwspa, epvme


def _run(monkeypatch: pytest.MonkeyPatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["merge_tagged_datasets.py", *args])
    merge_module.main()


def test_gate_failure_leaves_final_directories_untouched(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    iwspa, epvme = _inputs(tmp_path)
    combined = tmp_path / "combined"
    splits = tmp_path / "splits"
    with pytest.raises(ValueError, match="validation gates failed"):
        _run(
            monkeypatch,
            "--iwspa-root", str(iwspa),
            "--epvme-root", str(epvme),
            "--combined-dir", str(combined),
            "--splits-dir", str(splits),
            "--work-root", str(tmp_path / "work"),
            "--role", "primary",
        )
    assert not combined.exists()
    assert not splits.exists()
    failed = list((tmp_path / "work").glob("*/FAILED.json"))
    assert len(failed) == 1


def test_successful_run_writes_complete_manifests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    iwspa, epvme = _inputs(tmp_path)
    combined = tmp_path / "combined"
    splits = tmp_path / "splits"
    _run(
        monkeypatch,
        "--iwspa-root", str(iwspa),
        "--epvme-root", str(epvme),
        "--combined-dir", str(combined),
        "--splits-dir", str(splits),
        "--work-root", str(tmp_path / "work"),
        "--role", "adversarial",
    )
    for directory in (combined, splits):
        manifest = json.loads((directory / "MANIFEST.json").read_text(encoding="utf-8"))
        assert manifest["status"] == "complete"
        assert manifest["outputs"]
        assert manifest["stages"]["counts"]["near_dedup"] > 0
