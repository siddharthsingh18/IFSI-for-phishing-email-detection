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
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
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
        (
            str(record["source"]),
            1
            if record["label"] in (1, "1", "phishing")
            else 0,
        )
        for record in records
    )
    return {
        source: {
            "total": counts[(source, 0)] + counts[(source, 1)],
            "phishing": counts[(source, 1)],
            "legit": counts[(source, 0)],
        }
        for source in sorted({source for source, _ in counts})
    }


def _label_conflicts(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find normalized texts that received both labels."""
    labels_by_text: dict[str, set[str]] = {}
    examples: dict[str, list[str]] = {}
    for record in records:
        key = normalize_key(str(record["text"]))
        labels_by_text.setdefault(key, set()).add(str(record["label"]))
        examples.setdefault(key, []).append(str(record["id"]))
    conflicts = []
    for key, labels in labels_by_text.items():
        if len(labels) > 1:
            conflicts.append(
                {
                    "normalized_text_sha256": hashlib.sha256(key.encode("utf-8")).hexdigest(),
                    "labels": sorted(labels),
                    "record_ids": examples[key],
                }
            )
    return conflicts


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    else:
        for child in sorted(path.rglob("*")):
            if child.is_file():
                digest.update(str(child.relative_to(path)).encode())
                with child.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(chunk)
    return digest.hexdigest()


def _record_count(path: Path) -> int:
    if path.is_file():
        with path.open(encoding="utf-8") as handle:
            return sum(bool(line.strip()) for line in handle)
    return sum(_record_count(child) for child in path.rglob("*.jsonl"))


def _load_gate_config(path: Path) -> dict[str, Any]:
    # The file is JSON-compatible YAML so this pipeline has no hidden runtime dependency.
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "roles" not in data:
        raise ValueError(f"Invalid dataset gate config: {path}")
    return data


def _cross_split_near_leakage(
    split_records: dict[str, list[dict[str, Any]]],
    threshold: float,
) -> int:
    """Use LSH candidates to detect near-duplicate records assigned to different splits."""
    from phishbench.data_loader import compute_minhash_signature, get_shingles, jaccard_similarity

    entries = [
        (split, record, get_shingles(str(record["text"])))
        for split, rows in split_records.items()
        for record in rows
    ]
    buckets: dict[tuple[int, tuple[int, ...]], list[int]] = {}
    num_perm, num_bands = 64, 8
    rows_per_band = num_perm // num_bands
    for index, (_, _, shingles) in enumerate(entries):
        signature = compute_minhash_signature(shingles, num_perm=num_perm)
        for band in range(num_bands):
            key = (band, tuple(signature[band * rows_per_band : (band + 1) * rows_per_band]))
            buckets.setdefault(key, []).append(index)
    leaked: set[tuple[str, str]] = set()
    for candidates in buckets.values():
        for left in range(len(candidates)):
            first = candidates[left]
            for right in range(left + 1, len(candidates)):
                second = candidates[right]
                split_a, record_a, shingles_a = entries[first]
                split_b, record_b, shingles_b = entries[second]
                if split_a != split_b and jaccard_similarity(shingles_a, shingles_b) >= threshold:
                    leaked.add((str(record_a["id"]), str(record_b["id"])))
    return len(leaked)


def _quality_gate(
    records: list[dict[str, Any]],
    source_mix: dict[str, dict[str, int]],
    split_records: dict[str, list[dict[str, Any]]],
    role: str,
    thresholds: dict[str, Any],
    near_dedup_threshold: float,
) -> dict[str, Any]:
    total = len(records)
    phishing = sum(record["label"] == "phishing" for record in records)
    legitimate = total - phishing
    phishing_ratio = phishing / total if total else 0.0
    largest_source = max(
        source_mix.items(),
        key=lambda item: item[1]["total"],
        default=(None, {"total": 0}),
    )
    largest_share = largest_source[1]["total"] / total if total else 0.0
    role_config = thresholds["roles"][role]
    failures: list[str] = []
    if role == "primary":
        if min(phishing, legitimate) / total < role_config["minimum_minority_fraction"]:
            failures.append("minority_class_below_threshold")
        if largest_share > role_config["maximum_source_fraction"]:
            failures.append("source_dominance_above_threshold")
        for split_name, minimum in (
            ("test", role_config["minimum_test_records_per_class"]),
            ("val", role_config["minimum_validation_records_per_class"]),
        ):
            counts = Counter(int(row["label"]) for row in split_records[split_name])
            if min(counts[0], counts[1]) < minimum:
                failures.append(f"{split_name}_class_count_below_threshold")
    missing_provenance = any(
        not record.get("source") for record in records
    ) or any(not record.get("source") for rows in split_records.values() for record in rows)
    if missing_provenance:
        failures.append("missing_provenance")
    cross_split_clusters = _cross_split_near_leakage(split_records, near_dedup_threshold)
    if cross_split_clusters:
        failures.append("cross_split_near_duplicate_cluster_leakage")
    return {
        "passed": not failures,
        "role": role,
        "metrics_policy": role_config.get("metrics_policy", "full"),
        "failures": failures,
        "cross_split_near_duplicate_clusters": cross_split_clusters,
        "class_balance": {
            "total": total,
            "phishing": phishing,
            "legit": legitimate,
            "phishing_ratio": phishing_ratio,
            "legit_ratio": legitimate / total if total else 0.0,
        },
        "largest_source": {
            "source": largest_source[0],
            "count": largest_source[1]["total"],
            "share": largest_share,
        },
    }


def _write_manifest(
    directory: Path,
    *,
    args: argparse.Namespace,
    role: str,
    inputs: dict[str, Path],
    outputs: dict[str, Path],
    stage_counts: dict[str, int],
    stage_seconds: dict[str, float],
    gate: dict[str, Any],
) -> None:
    manifest = {
        "status": "complete",
        "git_commit": _git_commit(),
        "python": sys.version,
        "platform": platform.platform(),
        "package": {"name": "phishbench", "version": "0.1.0"},
        "cli_args": vars(args),
        "role": role,
        "seed": args.seed,
        "inputs": {
            name: {
                "path": str(path),
                "sha256": _sha256(path),
                "record_count": _record_count(path),
            }
            for name, path in inputs.items()
        },
        "outputs": {
            name: {
                "path": str(path),
                "sha256": _sha256(path),
                "record_count": _record_count(path),
            }
            for name, path in outputs.items()
        },
        "stages": {"counts": stage_counts, "wall_clock_seconds": stage_seconds},
        "validation": gate,
    }
    (directory / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


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
    parser.add_argument("--work-root", type=Path, default=Path("data/work"))
    parser.add_argument("--pipeline", default="tagged-datasets")
    parser.add_argument("--role", choices=("primary", "adversarial", "controls", "injection"), default="adversarial")
    parser.add_argument("--gates-config", type=Path, default=Path("config/dataset_gates.yaml"))
    parser.add_argument("--log-every", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--near-dedup-threshold", type=float, default=0.85)
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + _git_commit()[:8]
    work_dir = args.work_root / f"{args.pipeline}_{run_id}"
    combined_stage = work_dir / "combined"
    splits_stage = work_dir / "splits"
    try:
        work_dir.mkdir(parents=True, exist_ok=False)
        if args.combined_dir.exists() or args.splits_dir.exists():
            raise FileExistsError("Final output exists; refusing to overwrite it")
        stage_seconds: dict[str, float] = {}
        start = time.perf_counter()
        parsed = [
            *parse_iwspa_csv(args.iwspa_root / "Synthetic/synthetic_phish.csv", "iwspa_synthetic"),
            *parse_iwspa_csv(args.iwspa_root / "Adversarial/adversarial_dataset.csv", "iwspa_adversarial"),
            *parse_epvme(args.epvme_root),
        ]
        before = len(parsed)
        stage_seconds["raw"] = time.perf_counter() - start
        start = time.perf_counter()
        cleaned = [dict(record, text=clean_text(str(record["text"]))) for record in parsed]
        cleaned = [record for record in cleaned if record["text"]]
        stage_seconds["cleaned"] = time.perf_counter() - start
        start = time.perf_counter()
        exact, exact_stats = deduplicate_exact([_as_numeric_label(record) for record in cleaned])
        stage_seconds["exact_dedup"] = time.perf_counter() - start
        start = time.perf_counter()
        after_near, near_stats = deduplicate_near_duplicates(
            exact,
            threshold=args.near_dedup_threshold,
            checkpoint_dir=work_dir / "near_dedupe",
            log_every=args.log_every,
            return_stats=True,
        )
        stage_seconds["near_dedup"] = time.perf_counter() - start
        deduped = [{**record, "label": "phishing" if int(record["label"]) else "legit"} for record in after_near]
        label_conflicts = _label_conflicts(cleaned)
        numeric_deduped = [{**record, "label": 1 if record["label"] == "phishing" else 0} for record in deduped]
        split_records = stratified_split(numeric_deduped, seed=args.seed)
        for name, rows in split_records.items():
            _write_jsonl(splits_stage / f"{name}.jsonl", rows)
        _write_jsonl(combined_stage / "combined_deduped.jsonl", deduped)
        validation = validate_splits(
            splits_stage / "train.jsonl",
            splits_stage / "val.jsonl",
            splits_stage / "test.jsonl",
        )
        gate = _quality_gate(
            deduped,
            _source_mix(deduped),
            split_records,
            args.role,
            _load_gate_config(args.gates_config),
            args.near_dedup_threshold,
        )
        if not gate["passed"]:
            raise ValueError("Dataset validation gates failed: " + ", ".join(gate["failures"]))
        stage_counts = {
            "raw": len(parsed),
            "cleaned": len(cleaned),
            "exact_dedup": len(exact),
            "near_dedup": len(deduped),
        }
        report = {
            "seed": args.seed,
            "role": args.role,
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
                "near_dedup_stats": near_stats,
            },
            "source_contribution_before": _source_counts(parsed),
            "source_contribution_after": _source_counts(deduped),
            "source_label_distribution_after": _source_mix(deduped),
            "quality_gate": gate,
            "label_conflicts": {
                "count": len(label_conflicts),
                "examples": label_conflicts[:20],
            },
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
            "schema": "all outputs use id,text,label,source",
        }
        combined_stage.mkdir(parents=True, exist_ok=True)
        (combined_stage / "merge_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        _write_manifest(
            combined_stage,
            args=args,
            role=args.role,
            inputs={
                "iwspa_synthetic": args.iwspa_root / "Synthetic/synthetic_phish.csv",
                "iwspa_adversarial": args.iwspa_root / "Adversarial/adversarial_dataset.csv",
                "epvme": args.epvme_root,
            },
            outputs={"combined_jsonl": combined_stage / "combined_deduped.jsonl"},
            stage_counts=stage_counts,
            stage_seconds=stage_seconds,
            gate=gate,
        )
        _write_manifest(
            splits_stage,
            args=args,
            role=args.role,
            inputs={"combined": combined_stage / "combined_deduped.jsonl"},
            outputs={name: splits_stage / f"{name}.jsonl" for name in ("train", "val", "test")},
            stage_counts=stage_counts,
            stage_seconds=stage_seconds,
            gate=gate,
        )
        published_combined = False
        try:
            os.replace(combined_stage, args.combined_dir)
            published_combined = True
            os.replace(splits_stage, args.splits_dir)
        except Exception:
            if published_combined and args.combined_dir.exists() and not combined_stage.exists():
                os.replace(args.combined_dir, combined_stage)
            raise
        print(json.dumps(report, indent=2, ensure_ascii=False))
    except Exception as exc:
        work_dir.mkdir(parents=True, exist_ok=True)
        (work_dir / "FAILED.json").write_text(
            json.dumps({"status": "failed", "reason": str(exc)}, indent=2) + "\n",
            encoding="utf-8",
        )
        raise


if __name__ == "__main__":
    main()
