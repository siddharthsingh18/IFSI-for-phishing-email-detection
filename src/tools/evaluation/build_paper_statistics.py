#!/usr/bin/env python3
"""Build the three-model statistics used by the CoMeSySo manuscript.

The script is deliberately read-only with respect to model outputs.  It reparses
the retained JSONL records, restricts the multiplicity families to the three
models named in the paper, and evaluates attacked-phishing and injected-
legitimate comparisons separately.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from phishbench.evaluate import exact_mcnemar
from phishbench.io import write_json
from tools.evaluation.build_supplementary_statistics import (
    exact_p,
    holm_adjust,
    normalize_deepseek,
    normalize_qwen,
)


CONFIGS = (
    "deepseek-v4-pro_non-thinking",
    "deepseek-v4-pro_thinking",
    "qwen3.5-9b_non-thinking",
    "qwen3.5-9b_thinking",
    "qwen3.5-35b-a3b_non-thinking",
    "qwen3.5-35b-a3b_thinking",
)
DATASETS = ("phishfuzzer_seed_42", "nazario_enron_quality_seed_42")
CONDITIONS = ("attacked_phishing", "injected_legitimate_control")


def build(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["config"] in CONFIGS:
            grouped[(row["config"], row["dataset"], row["method"], row["condition"])].append(row)

    tests: list[dict[str, Any]] = []
    p_families: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for condition in CONDITIONS:
        for config in CONFIGS:
            for dataset in DATASETS:
                robust = grouped[(config, dataset, "robust", condition)]
                ours = grouped[(config, dataset, "ours", condition)]
                result = exact_mcnemar(robust, ours)
                key = f"{condition}|{config}|{dataset}"
                rc_ow = int(result["a_correct_b_wrong"])
                rw_oc = int(result["a_wrong_b_correct"])
                raw_p = exact_p(rc_ow, rw_oc)
                p_families[condition].append((key, raw_p))
                tests.append(
                    {
                        "key": key,
                        "condition": condition,
                        "config": config,
                        "dataset": dataset,
                        "paired_n": int(result["paired_n"]),
                        "robust_correct_ours_wrong": rc_ow,
                        "robust_wrong_ours_correct": rw_oc,
                        "net_ours_correct": rw_oc - rc_ow,
                        "raw_p": raw_p,
                    }
                )

    adjusted = {
        condition: holm_adjust(items) for condition, items in p_families.items()
    }
    for row in tests:
        row["holm_p_12"] = adjusted[row["condition"]][row["key"]]
        row["holm_significant_0_05"] = row["holm_p_12"] < 0.05

    return {
        "format": "comesyso-paper-statistics-v1",
        "scope": {
            "configs": list(CONFIGS),
            "datasets": list(DATASETS),
            "conditions": list(CONDITIONS),
            "multiplicity": "Separate 12-comparison Holm families for each condition",
        },
        "ours_vs_robust_mcnemar": tests,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deepseek-cells", type=Path, required=True)
    parser.add_argument("--qwen-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = normalize_deepseek(sorted(args.deepseek_cells.glob("*/results.jsonl")))
    rows += normalize_qwen(sorted(args.qwen_dir.glob("*.jsonl")))
    report = build(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, report)
    print(json.dumps({"normalized_rows": len(rows), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
