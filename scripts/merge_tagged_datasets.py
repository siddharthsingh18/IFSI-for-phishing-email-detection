"""Merge tagged email sources, deduplicate globally, and create v2 splits.

This script intentionally leaves the existing data/splits directory untouched.
It reads the user-provided source files in Downloads and writes local,
gitignored artifacts under data/combined_v2 and data/splits_v2.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any, Iterable

from phishbench.data_loader import (
    clean_text,
    deduplicate_exact,
    deduplicate_near_duplicates,
    normalize_key,
    stratified_split,
    validate_splits,
)


EPVME_CANONICAL_DIRS = ("1", "1 3", "2", "2 2", "3", "3 2", "4", "5")


def _stable_id(source: str, key: str) -> str:
    digest = hashlib.sha256(f"{source}\0{key}".encode("utf-8")).hexdigest()[:20]
    return f"{source}-{digest}"


def parse_iwspa_csv(path: Path, source: str) -> list[dict[str, Any]]:
    """Parse an IWSPA CSV with text and binary label columns."""
    records: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        for index, row in enumerate(csv.DictReader(handle), start=1):
            text = clean_text(row.get("text") or row.get("body") or "")
            if not text:
                continue
            label_raw = str(row.get("label", "")).strip().casefold()
            if label_raw in {"1", "phishing", "spam", "true"}:
                label = "phishing"
            elif label_raw in {"0", "legit", "legitimate", "ham", "false"}:
                label = "legit"
            else:
                raise ValueError(f"Unknown {source} label {row.get('label')!r} at row {index}")
            records.append(
                {
                    "id": _stable_id(source, str(index)),
                    "text": text,
                    "label": label,
                    "source": source,
                }
            )
    return records


def _message_text(message: Any) -> str:
    """Return headers plus the best available decoded body for an .eml file."""
    headers = "\n".join(f"{key}: {value}" for key, value in message.items())
    if message.is_multipart():
        parts = list(message.walk())
        candidates = [
            part
            for part in parts
            if part.get_content_maintype() == "text"
            and not part.is_multipart()
            and part.get_content_disposition() != "attachment"
        ]
        preferred = next(
            (part for part in candidates if part.get_content_type() == "text/plain"),
            candidates[0] if candidates else None,
        )
    else:
        preferred = message if message.get_content_maintype() == "text" else None
    body = ""
    if preferred is not None:
        try:
            body = str(preferred.get_content())
        except (LookupError, UnicodeError):
            payload = preferred.get_payload(decode=True) or b""
            body = payload.decode("utf-8", errors="replace")
    return clean_text(f"{headers}\n\n{body}")


def parse_epvme(root: Path) -> list[dict[str, Any]]:
    """Parse one copy of each EPVME package as phishing."""
    records: list[dict[str, Any]] = []
    seen_content: set[str] = set()
    for directory_name in EPVME_CANONICAL_DIRS:
        directory = root / directory_name
        if not directory.is_dir():
            raise FileNotFoundError(f"Missing EPVME directory: {directory}")
        for path in sorted(directory.glob("*.eml")):
            raw = path.read_bytes()
            content_hash = hashlib.sha256(raw).hexdigest()
            if content_hash in seen_content:
                continue
            seen_content.add(content_hash)
            message = BytesParser(policy=policy.default).parsebytes(raw)
            text = _message_text(message)
            if text:
                records.append(
                    {
                        "id": _stable_id("epvme", path.name),
                        "text": text,
                        "label": "phishing",
                        "source": "epvme",
                    }
                )
    return records


def _as_numeric_label(record: dict[str, Any]) -> dict[str, Any]:
    result = dict(record)
    result["label"] = (
        int(record["label"])
        if isinstance(record["label"], int)
        else 1
        if record["label"] == "phishing"
        else 0
    )
    return result


def _write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _source_counts(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: Counter[tuple[str, str]] = Counter(
        (str(record["source"]), str(record["label"])) for record in records
    )
    sources = sorted({source for source, _ in counts})
    return {
        source: {
            "total": counts[(source, "phishing")] + counts[(source, "legit")],
            "phishing": counts[(source, "phishing")],
            "legit": counts[(source, "legit")],
        }
        for source in sources
    }


def _source_mix(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: Counter[tuple[str, int]] = Counter(
        (str(record["source"]), int(record["label"])) for record in records
    )
    return {
        source: {
            "total": counts[(source, 0)] + counts[(source, 1)],
            "phishing": counts[(source, 1)],
            "legit": counts[(source, 0)],
        }
        for source in sorted({source for source, _ in counts})
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iwspa-root",
        type=Path,
        default=Path.home() / "Downloads/IWSPA-2023-Adversarial-Synthetic-Dataset-main",
    )
    parser.add_argument(
        "--epvme-root",
        type=Path,
        default=Path.home() / "Downloads/EPVME-Dataset-main",
    )
    parser.add_argument("--combined-dir", type=Path, default=Path("data/combined_v2"))
    parser.add_argument("--splits-dir", type=Path, default=Path("data/splits_v2"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--near-dedup-threshold", type=float, default=0.85)
    args = parser.parse_args()

    parsed = [
        *parse_iwspa_csv(
            args.iwspa_root / "Synthetic/synthetic_phish.csv",
            "iwspa_synthetic",
        ),
        *parse_iwspa_csv(
            args.iwspa_root / "Adversarial/adversarial_dataset.csv",
            "iwspa_adversarial",
        ),
        *parse_epvme(args.epvme_root),
    ]
    before = len(parsed)
    cleaned = [dict(record, text=clean_text(str(record["text"]))) for record in parsed]
    cleaned = [record for record in cleaned if record["text"]]
    exact, exact_stats = deduplicate_exact(
        [_as_numeric_label(record) for record in cleaned]
    )
    after_near, near_removed = deduplicate_near_duplicates(
        exact,
        threshold=args.near_dedup_threshold,
    )
    # Restore the source field after the shared helper has preserved it.
    deduped = [
        {**record, "label": "phishing" if int(record["label"]) else "legit"}
        for record in after_near
    ]
    numeric_deduped = [
        {**record, "label": 1 if record["label"] == "phishing" else 0}
        for record in deduped
    ]
    source_by_id = {str(record["id"]): str(record["source"]) for record in deduped}
    splits = stratified_split(
        numeric_deduped,
        seed=args.seed,
    )
    split_records = {
        name: [
            {
                **record,
                "source": source_by_id[str(record["id"])],
            }
            for record in rows
        ]
        for name, rows in splits.items()
    }

    for name, rows in split_records.items():
        _write_jsonl(args.splits_dir / f"{name}.jsonl", rows)
    validation = validate_splits(
        args.splits_dir / "train.jsonl",
        args.splits_dir / "val.jsonl",
        args.splits_dir / "test.jsonl",
    )
    _write_jsonl(args.combined_dir / "combined_deduped.jsonl", deduped)
    report = {
        "seed": args.seed,
        "near_dedup_threshold": args.near_dedup_threshold,
        "inputs": {
            "iwspa_synthetic": str(args.iwspa_root / "Synthetic/synthetic_phish.csv"),
            "iwspa_adversarial": str(args.iwspa_root / "Adversarial/adversarial_dataset.csv"),
            "epvme": str(args.epvme_root),
        },
        "counts": {
            "before": before,
            "after_clean": len(cleaned),
            "after_exact": len(exact),
            "after_near": len(deduped),
            "exact_stats": exact_stats,
            "near_duplicates_removed": near_removed,
        },
        "source_contribution_before": _source_counts(parsed),
        "source_contribution_after": _source_counts(deduped),
        "source_label_distribution_after": _source_mix(deduped),
        "splits": {
            name: {
                "total": len(rows),
                "phishing": sum(int(row["label"]) == 1 for row in rows),
                "legit": sum(int(row["label"]) == 0 for row in rows),
                "source_mix": _source_mix(rows),
            }
            for name, rows in split_records.items()
        },
        "validation": validation,
        "schema": "intermediate pool uses id,text,label,source; split files use id,text,label",
    }
    (args.combined_dir / "merge_report.json").parent.mkdir(parents=True, exist_ok=True)
    (args.combined_dir / "merge_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
