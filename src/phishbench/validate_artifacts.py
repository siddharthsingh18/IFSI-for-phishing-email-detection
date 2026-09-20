"""Fail-fast integrity checks for frozen datasets and prompt fairness."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from .attacks import TEMPLATES
from .io import read_jsonl, sha256_file
from .prompts import prompt_snapshot


def normalized_content_key(row: dict[str, object]) -> tuple[str, str, str]:
    def normalize(value: object) -> str:
        return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or "")).casefold()).strip()

    return normalize(row.get("subject")), normalize(row.get("sender")), normalize(row.get("body"))


def validate_dataset(base: Path, expected_per_label: int, require_quality: bool = False) -> dict[str, object]:
    clean = read_jsonl(base / "clean.jsonl")
    by_id = {str(r.get("original_id") or r["email_id"]): r for r in clean}
    labels = Counter(int(r["label"]) for r in clean)
    if labels != {0: expected_per_label, 1: expected_per_label}:
        raise AssertionError(f"unexpected clean labels for {base}: {labels}")
    if require_quality:
        if any(not str(row.get("body") or "").strip() for row in clean):
            raise AssertionError(f"empty clean body remains in quality dataset {base}")
        if len({normalized_content_key(row) for row in clean}) != len(clean):
            raise AssertionError(f"normalized duplicate remains in quality dataset {base}")
    details: dict[str, object] = {"clean": len(clean), "labels": dict(labels)}
    assignment_signatures: dict[str, list[tuple[str, str, str]]] = {}
    for condition, label in (("attacked_phishing", 1), ("injected_legitimate_control", 0)):
        rows = read_jsonl(base / f"{condition}.jsonl")
        expected_ids = {key for key, row in by_id.items() if int(row["label"]) == label}
        actual_ids = {str(row["original_id"]) for row in rows}
        if actual_ids != expected_ids or len(rows) != expected_per_label:
            raise AssertionError(f"pairing failure for {base}/{condition}")
        for row in rows:
            original = by_id[str(row["original_id"])]
            _, family, template_index = str(row["attack_template_id"]).split(":")
            payload = TEMPLATES[family][int(template_index)]
            marker = f"\n\n[BEGIN EMBEDDED CLASSIFIER MESSAGE]\n{payload}\n[END EMBEDDED CLASSIFIER MESSAGE]\n\n"
            restored = str(row.get("body") or "").replace(marker, "", 1)
            if restored != str(original.get("body") or ""):
                raise AssertionError(f"attack deleted/changed original body: {row['email_id']}")
            if int(row["label"]) != label:
                raise AssertionError(f"attack changed label: {row['email_id']}")
        assignment_signatures[condition] = [
            (str(row["attack_family"]), str(row["attack_template_id"]), str(row["attack_position"]))
            for row in rows
        ]
        details[condition] = {"count": len(rows), "families": dict(Counter(r["attack_family"] for r in rows)), "positions": dict(Counter(r["attack_position"] for r in rows))}
    if assignment_signatures["attacked_phishing"] != assignment_signatures["injected_legitimate_control"]:
        raise AssertionError(f"attack family/template/position assignments are not index-matched for {base}")
    return details


def validate_prompts() -> dict[str, str]:
    methods = prompt_snapshot()["methods"]
    for block in ("common_task", "common_input_rules", "common_format"):
        hashes = {methods[method]["block_hashes"][block] for method in methods}
        if len(hashes) != 1:
            raise AssertionError(f"shared prompt block differs: {block}")
    if methods["robust"]["block_hashes"]["robust_defense"] != methods["ours"]["block_hashes"]["robust_defense"]:
        raise AssertionError("Robust/Ours defense block differs")
    if methods["direct"]["block_hashes"]["output"] != methods["robust"]["block_hashes"]["output"]:
        raise AssertionError("Direct/Robust output block differs")
    return {block: methods["direct"]["block_hashes"][block] for block in ("common_task", "common_input_rules", "common_format")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--v1-test", type=Path, default=Path("../v1/data/processed/nazario_enron/nazario_enron_test.jsonl"))
    args = parser.parse_args()
    exact_copy = args.processed_dir / "nazario_enron_reused/v1_test_exact_copy.jsonl"
    if sha256_file(args.v1_test) != sha256_file(exact_copy):
        raise AssertionError("Nazario+Enron exact copy hash differs from v1")
    report = {
        "phishfuzzer_seed_42": validate_dataset(args.processed_dir / "phishfuzzer_seed_42", 1000),
        "nazario_enron_reused_legacy_audit_only": validate_dataset(args.processed_dir / "nazario_enron_reused", 441),
        "nazario_enron_quality_seed_42": validate_dataset(args.processed_dir / "nazario_enron_quality_seed_42", 239, require_quality=True),
        "nazario_enron_v1_sha256": sha256_file(args.v1_test),
        "prompt_common_block_hashes": validate_prompts(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
