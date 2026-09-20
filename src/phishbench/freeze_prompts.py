"""Write the immutable expanded prompt snapshot and experiment matrix."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from .io import sha256_text, write_json
from .prompts import PROMPT_VERSION, prompt_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-output", type=Path, default=Path(f"experiments/inputs/prompt_snapshot_{PROMPT_VERSION}.json"))
    parser.add_argument("--matrix-output", type=Path, default=Path("experiments/config/main_matrix.json"))
    args = parser.parse_args()
    snapshot = prompt_snapshot()
    canonical = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    snapshot["snapshot_sha256"] = sha256_text(canonical)
    write_json(args.prompt_output, snapshot)
    cells = [
        {"dataset": dataset, "model": model, "thinking": thinking, "method": method, "condition": condition}
        for dataset, model, thinking, method, condition in itertools.product(
            ("phishfuzzer_seed_42", "nazario_enron_quality_seed_42"),
            ("deepseek-v4-flash", "deepseek-v4-pro"),
            ("off", "on"),
            ("direct", "robust", "ours"),
            ("clean", "attacked_phishing", "injected_legitimate_control"),
        )
    ]
    write_json(args.matrix_output, {"matrix_version": "main-v2-quality-filtered", "prompt_version": PROMPT_VERSION, "cell_count": len(cells), "cells": cells, "ablation": {"dataset": "phishfuzzer_seed_42", "model": "deepseek-v4-flash", "thinking": "off", "method": "ours_no_summary", "conditions": ["clean", "attacked_phishing", "injected_legitimate_control"]}})
    print(f"wrote {args.prompt_output} and {len(cells)} main cells to {args.matrix_output}")


if __name__ == "__main__":
    main()
