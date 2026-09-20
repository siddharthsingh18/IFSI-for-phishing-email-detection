#!/usr/bin/env python3
"""Create per-file checksums and row counts for unpacked raw result directories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from phishbench.io import sha256_file, write_json


def line_count(path: Path) -> int:
    with path.open("rb") as handle:
        return sum(1 for _ in handle)


def file_entry(path: Path, root: Path, include_rows: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path.relative_to(root)),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if include_rows:
        result["records"] = line_count(path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deepseek-dir", type=Path, required=True)
    parser.add_argument("--qwen-dir", type=Path, required=True)
    args = parser.parse_args()

    deepseek_results = sorted(args.deepseek_dir.glob("cells/*/results.jsonl"))
    deepseek_manifests = sorted(args.deepseek_dir.glob("cells/*/manifest.json"))
    if len(deepseek_results) != 72 or len(deepseek_manifests) != 72:
        raise RuntimeError(
            f"expected 72 DeepSeek result/manifest pairs, got "
            f"{len(deepseek_results)}/{len(deepseek_manifests)}"
        )
    deepseek_entries = [file_entry(path, args.deepseek_dir, True) for path in deepseek_results]
    write_json(
        args.deepseek_dir / "MANIFEST.json",
        {
            "format": "phishbench-unpacked-deepseek-results-v1",
            "cell_count": len(deepseek_entries),
            "result_records": sum(entry["records"] for entry in deepseek_entries),
            "results": deepseek_entries,
            "cell_manifests": [
                file_entry(path, args.deepseek_dir) for path in deepseek_manifests
            ],
        },
    )

    qwen_results = sorted(args.qwen_dir.glob("*.jsonl"))
    if len(qwen_results) != 4:
        raise RuntimeError(f"expected 4 Qwen result files, got {len(qwen_results)}")
    qwen_entries = [file_entry(path, args.qwen_dir, True) for path in qwen_results]
    write_json(
        args.qwen_dir / "MANIFEST.json",
        {
            "format": "phishbench-unpacked-qwen-results-v1",
            "run_count": len(qwen_entries),
            "result_records": sum(entry["records"] for entry in qwen_entries),
            "results": qwen_entries,
        },
    )
    print(
        json.dumps(
            {
                "deepseek_cells": len(deepseek_entries),
                "deepseek_records": sum(entry["records"] for entry in deepseek_entries),
                "qwen_runs": len(qwen_entries),
                "qwen_records": sum(entry["records"] for entry in qwen_entries),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
