#!/usr/bin/env python3
"""Combine per-run portable evaluations into one traceable matrix artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from phishbench.io import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        metavar="RUN_ID,MEMBER,METRICS_JSON",
        help="Repeat once per model/mode run.",
    )
    args = parser.parse_args()

    runs: dict[str, dict[str, Any]] = {}
    prompt_hashes: set[str] = set()
    for specification in args.run:
        run_id, member, metrics_path_text = specification.split(",", 2)
        metrics_path = Path(metrics_path_text)
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        prompt_hashes.add(str(metrics["inputs"]["prompts_sha256"]))
        metrics["inputs"]["results"] = member
        runs[run_id] = metrics
    if len(prompt_hashes) != 1:
        raise RuntimeError(f"runs do not share one frozen prompt export: {sorted(prompt_hashes)}")

    report = {
        "format": "phishbench-portable-model-mode-matrix-v1",
        "source_manifest": str(args.source_manifest),
        "source_manifest_sha256": sha256_file(args.source_manifest),
        "frozen_prompts_sha256": next(iter(prompt_hashes)),
        "run_count": len(runs),
        "runs": runs,
    }
    write_json(args.output, report)
    print(json.dumps({"runs": len(runs), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
