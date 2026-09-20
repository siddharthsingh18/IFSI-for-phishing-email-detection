"""Build a balanced, deduplicated Nazario+Enron test set without empty bodies."""

from __future__ import annotations

import argparse
import json
import random
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

from .attacks import ATTACK_VERSION, build_conditions
from .io import read_jsonl, sha256_file, write_json, write_jsonl


CONDITIONS = ("clean", "attacked_phishing", "injected_legitimate_control")
MIME_PLACEHOLDER_RE = re.compile(r"^html(?: file)? (?:is )?required(?: for this (?:letter|message))?\.?$", re.IGNORECASE)


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or "")).casefold()).strip()


def original_id(row: dict[str, Any]) -> str:
    return str(row.get("original_id") or row["email_id"])


def content_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return normalize(row.get("subject")), normalize(row.get("sender")), normalize(row.get("body"))


def deduplicate(rows: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[content_key(row)].append(row)
    kept: list[dict[str, Any]] = []
    for group in groups.values():
        ordered = sorted(group, key=original_id)
        keeper = ordered[0]
        kept.append(keeper)
        for duplicate in ordered[1:]:
            decisions.append(
                {
                    "original_id": original_id(duplicate),
                    "label": int(duplicate["label"]),
                    "decision": "exclude",
                    "reason": "normalized_exact_duplicate",
                    "duplicate_of": original_id(keeper),
                }
            )
    return kept


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path("data/processed/nazario_enron_reused"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/nazario_enron_quality_seed_42"))
    parser.add_argument("--audit-output", type=Path, default=Path("experiments/config/nazario_enron_quality_manifest.json"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    clean = read_jsonl(args.source_dir / "clean.jsonl")
    decisions: list[dict[str, Any]] = []
    nonempty: list[dict[str, Any]] = []
    for row in clean:
        normalized_body = normalize(row.get("body"))
        issue_reason = None
        if not normalized_body:
            issue_reason = "empty_body_after_legacy_mime_parse"
        elif MIME_PLACEHOLDER_RE.fullmatch(normalized_body):
            issue_reason = "mime_html_placeholder_without_extracted_html"
        if issue_reason:
            decisions.append(
                {
                    "original_id": original_id(row),
                    "label": int(row["label"]),
                    "decision": "exclude",
                    "reason": issue_reason,
                    "source_dataset": row.get("source_dataset"),
                }
            )
        else:
            nonempty.append(row)

    unique_by_label = {
        label: deduplicate([row for row in nonempty if int(row["label"]) == label], decisions)
        for label in (0, 1)
    }
    target_per_label = min(len(unique_by_label[0]), len(unique_by_label[1]))
    phishing = sorted(unique_by_label[1], key=original_id)
    if len(phishing) != target_per_label:
        raise RuntimeError("quality filtering unexpectedly leaves fewer legitimate than phishing records")

    legitimate = sorted(unique_by_label[0], key=original_id)
    rng = random.Random(args.seed)
    rng.shuffle(legitimate)
    selected_legitimate = legitimate[:target_per_label]
    for row in legitimate[target_per_label:]:
        decisions.append(
            {
                "original_id": original_id(row),
                "label": 0,
                "decision": "exclude",
                "reason": "deterministic_balance_downsample",
                "seed": args.seed,
            }
        )

    selected_clean = sorted(phishing + selected_legitimate, key=original_id)
    selected_ids = {int(label): {original_id(row) for row in rows} for label, rows in ((0, selected_legitimate), (1, phishing))}
    attacked, controls, attack_manifest = build_conditions(selected_clean, args.seed)
    condition_rows: dict[str, list[dict[str, Any]]] = {
        "clean": selected_clean,
        "attacked_phishing": attacked,
        "injected_legitimate_control": controls,
    }
    if len(attack_manifest) != target_per_label * 2:
        raise RuntimeError("filtered attack manifest is not fully paired")

    files: dict[str, dict[str, Any]] = {}
    for condition in CONDITIONS:
        path = args.output_dir / f"{condition}.jsonl"
        write_jsonl(path, condition_rows[condition])
        files[condition] = {"path": str(path), "count": len(condition_rows[condition]), "sha256": sha256_file(path)}
    attack_manifest_path = args.output_dir / "attack_manifest.jsonl"
    write_jsonl(attack_manifest_path, attack_manifest)
    files["attack_manifest"] = {"path": str(attack_manifest_path), "count": len(attack_manifest), "sha256": sha256_file(attack_manifest_path)}
    decisions_path = args.output_dir / "quality_decisions.jsonl"
    write_jsonl(decisions_path, sorted(decisions, key=lambda row: (str(row["reason"]), str(row["original_id"]))))
    files["quality_decisions"] = {"path": str(decisions_path), "count": len(decisions), "sha256": sha256_file(decisions_path)}
    ids_path = args.output_dir / "selected_original_ids.json"
    write_json(ids_path, {"legitimate": sorted(selected_ids[0]), "phishing": sorted(selected_ids[1])})
    files["selected_original_ids"] = {"path": str(ids_path), "count": target_per_label * 2, "sha256": sha256_file(ids_path)}

    reason_counts: dict[str, int] = defaultdict(int)
    for row in decisions:
        reason_counts[str(row["reason"])] += 1
    manifest = {
        "dataset_version": "nazario-enron-quality-v1",
        "dataset_id": args.output_dir.name,
        "created_from": "frozen V1 Nazario+Enron test exact copy; attacks rebuilt after quality filtering",
        "seed": args.seed,
        "quality_policy": {
            "exclude_empty_body": True,
            "exclude_known_mime_placeholder": MIME_PLACEHOLDER_RE.pattern,
            "empty_body_reason": "Legacy parser retained only text/plain parts; many Nazario messages contain HTML-only bodies.",
            "deduplication_key": "NFKC+casefold+collapsed-whitespace(subject, sender, body)",
            "duplicate_keeper": "lexicographically smallest original_id",
            "class_balance": "retain all unique usable phishing; seeded shuffle and downsample unique usable legitimate to the same count",
            "attack_rebuild": f"{ATTACK_VERSION}, seed={args.seed}; phishing and legitimate control receive index-matched family/template/position assignments",
        },
        "source_files": {
            name: {"path": str(args.source_dir / f"{name}.jsonl"), "sha256": sha256_file(args.source_dir / f"{name}.jsonl")}
            for name in (*CONDITIONS, "attack_manifest")
        },
        "counts": {
            "source_clean_total": len(clean),
            "source_by_label": {str(label): sum(int(row["label"]) == label for row in clean) for label in (0, 1)},
            "nonempty_by_label": {str(label): sum(int(row["label"]) == label for row in nonempty) for label in (0, 1)},
            "unique_nonempty_by_label": {str(label): len(unique_by_label[label]) for label in (0, 1)},
            "selected_per_label": target_per_label,
            "selected_clean_total": len(selected_clean),
            "attacked_phishing": len(condition_rows["attacked_phishing"]),
            "injected_legitimate_control": len(condition_rows["injected_legitimate_control"]),
            "exclusions_by_reason": dict(sorted(reason_counts.items())),
        },
        "files": files,
    }
    write_json(args.output_dir / "quality_manifest.json", manifest)
    write_json(args.audit_output, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
