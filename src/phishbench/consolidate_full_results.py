"""Keep exactly one result row for every item in the frozen full matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .io import read_jsonl, sha256_file, stable_id, write_json, write_jsonl
from .prompts import build_prompt


DATASETS = ("phishfuzzer_seed_42", "nazario_enron_quality_seed_42")
MODELS = ("deepseek-v4-flash", "deepseek-v4-pro")
THINKING = ("off", "on")
METHODS = ("direct", "robust", "ours")
CONDITIONS = ("clean", "attacked_phishing", "injected_legitimate_control")


def expected_id(record: dict[str, Any], model: str, thinking: str, method: str, condition: str) -> str:
    prompt = build_prompt(record, method)
    return stable_id(record.get("email_id"), model, thinking, "high", method, condition, prompt.expanded_prompt_sha256)


def choose_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [row for row in rows if row.get("request_success") is True]
    return successful[-1] if successful else rows[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--runs-dir", type=Path, default=Path("experiments/work/deepseek"))
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=Path("experiments/work/deepseek_consolidation_manifest.json"),
    )
    args = parser.parse_args()

    audit: dict[str, Any] = {"policy": "one row per frozen full-input run_item_id; prefer latest request-success row", "cells": {}}
    for dataset in DATASETS:
        for model in MODELS:
            for thinking in THINKING:
                for method in METHODS:
                    for condition in CONDITIONS:
                        input_path = args.processed_dir / dataset / f"{condition}.jsonl"
                        records = read_jsonl(input_path)
                        ordered_ids = [expected_id(record, model, thinking, method, condition) for record in records]
                        expected = set(ordered_ids)
                        run_dir = args.runs_dir / f"{dataset}__{condition}__{method}__{model}__thinking-{thinking}"
                        result_path = run_dir / "results.jsonl"
                        existing = read_jsonl(result_path)
                        candidates: dict[str, list[dict[str, Any]]] = {}
                        for row in existing:
                            candidates.setdefault(str(row["run_item_id"]), []).append(row)
                        missing = [item_id for item_id in ordered_ids if item_id not in candidates]
                        if missing:
                            raise RuntimeError(f"{result_path}: {len(missing)} full-input IDs have no result row")
                        selected = [choose_row(candidates[item_id]) for item_id in ordered_ids]
                        write_jsonl(result_path, selected)
                        cell = f"{dataset}|{model}|{thinking}|{method}|{condition}"
                        audit["cells"][cell] = {
                            "input": str(input_path),
                            "input_sha256": sha256_file(input_path),
                            "result": str(result_path),
                            "result_sha256": sha256_file(result_path),
                            "full_rows": len(selected),
                            "rows_before": len(existing),
                            "obsolete_rows_removed": sum(item_id not in expected for item_id in candidates),
                            "duplicate_rows_removed": len(existing) - len(candidates),
                            "request_failures": sum(row.get("request_success") is not True for row in selected),
                            "parse_failures": sum(row.get("parse_success") is not True for row in selected),
                        }
    audit["cell_count"] = len(audit["cells"])
    audit["totals"] = {
        key: sum(cell[key] for cell in audit["cells"].values())
        for key in ("full_rows", "rows_before", "obsolete_rows_removed", "duplicate_rows_removed", "request_failures", "parse_failures")
    }
    write_json(args.audit_output, audit)
    print(json.dumps(audit["totals"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
