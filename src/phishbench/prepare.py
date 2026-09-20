"""Prepare frozen PhishFuzzer and reused Nazario+Enron evaluation datasets."""

from __future__ import annotations

import argparse
import json
import random
import shutil
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .attacks import ATTACK_VERSION, TEMPLATES, build_conditions
from .io import read_jsonl, sha256_file, stable_id, write_json, write_jsonl

SOURCE_URLS = {
    "phishfuzzer_repository": "https://github.com/DataPhish/PhishFuzzer",
    "nazario": "https://monkey.org/~jose/phishing/phishing3.mbox",
    "enron": "https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz",
}


def normalized_key(subject: str, body: str) -> str:
    value = unicodedata.normalize("NFKC", subject + "\n" + body).casefold()
    return " ".join(value.split())


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)] if str(value).strip() else []


def load_phishfuzzer(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("PhishFuzzer seed must be a JSON array")
    accepted: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    raw_types = Counter()
    duplicate_counts = Counter()
    empty_counts = Counter()
    for source_index, item in enumerate(raw):
        source_type = str(item.get("Type") or "").strip()
        raw_types[source_type] += 1
        if source_type not in {"Phishing", "Valid"}:
            continue
        label = 1 if source_type == "Phishing" else 0
        subject = str(item.get("Subject") or "").strip()
        body = str(item.get("Body") or "").strip()
        if not normalized_key(subject, body):
            empty_counts[source_type] += 1
            continue
        key = (label, normalized_key(subject, body))
        if key in seen:
            duplicate_counts[source_type] += 1
            continue
        seen.add(key)
        upstream_id = item.get("No.", source_index + 1)
        accepted.append({
            "email_id": stable_id("PhishFuzzer", upstream_id, subject, body),
            "original_id": f"phishfuzzer-seed-{upstream_id}",
            "subject": subject,
            "body": body,
            "sender": str(item.get("Sender") or "").strip() or None,
            "reply_to": None,
            "receiver": None,
            "date": None,
            "urls": _string_list(item.get("URL")),
            "attachments": _string_list(item.get("File")),
            "source_dataset": "PhishFuzzer_original_seed_v1",
            "source_record_id": upstream_id,
            "source_provenance": item.get("Source"),
            "created_by": item.get("Created by"),
            "year": item.get("Year"),
            "language": item.get("Language"),
            "motivation": item.get("Motivation"),
            "variant_type": "clean",
            "has_injected_prompt": False,
            "label": label,
            "label_name": "phishing" if label else "legitimate",
        })
    report = {
        "raw_total": len(raw),
        "raw_type_counts": dict(raw_types),
        "excluded_spam": raw_types["Spam"],
        "empty_removed": dict(empty_counts),
        "within_label_duplicates_removed": dict(duplicate_counts),
        "deduplicated_label_counts": {
            "phishing": sum(r["label"] == 1 for r in accepted),
            "legitimate": sum(r["label"] == 0 for r in accepted),
        },
        "normalization": "Unicode NFKC + casefold + whitespace collapse over subject + newline + body; deduplicate within label",
    }
    return accepted, report


def sample_balanced(rows: list[dict[str, Any]], per_label: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    for label in (0, 1):
        bucket = sorted((row for row in rows if row["label"] == label), key=lambda row: str(row["email_id"]))
        rng.shuffle(bucket)
        take = min(per_label, len(bucket))
        selected.extend(bucket[:take])
    rng.shuffle(selected)
    return selected


def normalize_external(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        item = dict(row)
        item.setdefault("original_id", item["email_id"])
        item.setdefault("has_injected_prompt", False)
        item.setdefault("label_name", "phishing" if int(item["label"]) else "legitimate")
        output.append(item)
    return output


def emit_dataset(name: str, clean: list[dict[str, Any]], output_dir: Path, seed: int) -> dict[str, Any]:
    target = output_dir / name
    attacked, controls, attack_manifest = build_conditions(clean, seed)
    paths = {
        "clean": target / "clean.jsonl",
        "attacked_phishing": target / "attacked_phishing.jsonl",
        "injected_legitimate_control": target / "injected_legitimate_control.jsonl",
        "attack_manifest": target / "attack_manifest.jsonl",
    }
    write_jsonl(paths["clean"], clean)
    write_jsonl(paths["attacked_phishing"], attacked)
    write_jsonl(paths["injected_legitimate_control"], controls)
    write_jsonl(paths["attack_manifest"], attack_manifest)
    (target / "test_ids.txt").write_text("\n".join(sorted(str(r["email_id"]) for r in clean)) + "\n", encoding="utf-8")
    return {
        "dataset": name,
        "seed": seed,
        "counts": {"clean": len(clean), "clean_phishing": sum(r["label"] == 1 for r in clean), "clean_legitimate": sum(r["label"] == 0 for r in clean), "attacked_phishing": len(attacked), "injected_legitimate_control": len(controls)},
        "attack_version": ATTACK_VERSION,
        "attack_families": {family: len(templates) for family, templates in TEMPLATES.items()},
        "files": {key: {"path": str(path), "sha256": sha256_file(path)} for key, path in paths.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phishfuzzer", type=Path, default=Path("data/raw/phishfuzzer/upstream/PhishFuzzer_emails_original_seed_v1.json"))
    parser.add_argument("--phishfuzzer-commit", default="1e21dd4edbe5c64694f156bf5318c97c7c80681c")
    parser.add_argument("--v1-test", type=Path, default=Path("../v1/data/processed/nazario_enron/nazario_enron_test.jsonl"))
    parser.add_argument("--v1-report", type=Path, default=Path("../v1/data/processed/nazario_enron/preparation_report.json"))
    parser.add_argument("--v1-nazario", type=Path, default=Path("../v1/data/raw/nazario/phishing3.mbox"))
    parser.add_argument("--v1-enron", type=Path, default=Path("../v1/data/raw/enron/enron_mail_20150507.tar.gz"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--metadata-dir", type=Path, default=Path("data/metadata"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--per-label", type=int, default=1000)
    args = parser.parse_args()

    pf_rows, audit = load_phishfuzzer(args.phishfuzzer)
    pf_clean = sample_balanced(pf_rows, args.per_label, args.seed)
    pf_report = emit_dataset("phishfuzzer_seed_42", pf_clean, args.output_dir, args.seed)
    pf_report["audit"] = audit

    external_raw_hash = sha256_file(args.v1_test)
    external_clean = normalize_external(read_jsonl(args.v1_test))
    external_report = emit_dataset("nazario_enron_reused", external_clean, args.output_dir, args.seed)
    external_report["v1_test_original_sha256"] = external_raw_hash
    # Preserve an exact byte-for-byte v1 copy beside the normalized condition file.
    exact_copy = args.output_dir / "nazario_enron_reused" / "v1_test_exact_copy.jsonl"
    shutil.copy2(args.v1_test, exact_copy)
    external_report["v1_test_exact_copy"] = {"path": str(exact_copy), "sha256": sha256_file(exact_copy)}

    source_manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "phishfuzzer": {
            "repository_url": SOURCE_URLS["phishfuzzer_repository"],
            "commit": args.phishfuzzer_commit,
            "local_path": str(args.phishfuzzer),
            "sha256": sha256_file(args.phishfuzzer),
            "license_status": "No LICENSE/COPYING file found at the pinned upstream commit; public redistribution permission is not established and must be confirmed before release.",
        },
        "nazario_enron": {
            "reuse_policy": "v2 reuses the frozen v1 test; it does not rebuild or resample it",
            "v1_test_path": str(args.v1_test),
            "v1_test_sha256": external_raw_hash,
            "v1_preparation_report_path": str(args.v1_report),
            "v1_preparation_report_sha256": sha256_file(args.v1_report),
            "nazario": {"url": SOURCE_URLS["nazario"], "local_path": str(args.v1_nazario), "sha256": sha256_file(args.v1_nazario)},
            "enron": {"url": SOURCE_URLS["enron"], "local_path": str(args.v1_enron), "sha256": sha256_file(args.v1_enron)},
            "license_status": "Retain upstream terms and attribution; verify redistribution terms before publishing raw email text.",
        },
    }
    write_json(args.metadata_dir / "source_manifest.json", source_manifest)
    write_json(args.metadata_dir / "preparation_report.json", {"seed": args.seed, "phishfuzzer": pf_report, "nazario_enron": external_report})
    print(json.dumps({"phishfuzzer": pf_report["counts"], "nazario_enron": external_report["counts"]}, indent=2))


if __name__ == "__main__":
    main()
