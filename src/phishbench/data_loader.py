"""Data loading, cleaning, deduplication (exact + near-duplicate), stratified splitting, and validation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence


def clean_text(text: str) -> str:
    """Clean text by applying Unicode NFKC normalization and stripping whitespace."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKC", text)
    return normalized.strip()


def normalize_key(text: str) -> str:
    """Normalize text for exact/near matching (NFKC + casefold + collapsed whitespace)."""
    norm = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(norm.split())


def deduplicate_exact(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Deduplicate records based on exact text and normalized whitespace/case text.

    Args:
        records: List of email record dicts containing at least 'text'.

    Returns:
        tuple of (kept_records, stats_dict)
    """
    seen_raw: set[str] = set()
    exact_raw_dupes = 0
    after_raw: list[dict[str, Any]] = []

    for r in records:
        raw_text = r["text"]
        if raw_text in seen_raw:
            exact_raw_dupes += 1
            continue
        seen_raw.add(raw_text)
        after_raw.append(r)

    seen_norm: set[str] = set()
    norm_dupes = 0
    kept: list[dict[str, Any]] = []

    for r in after_raw:
        key = normalize_key(r["text"])
        if key in seen_norm:
            norm_dupes += 1
            continue
        seen_norm.add(key)
        kept.append(r)

    stats = {
        "exact_raw_duplicates_removed": exact_raw_dupes,
        "normalized_whitespace_duplicates_removed": norm_dupes,
        "total_exact_duplicates_removed": exact_raw_dupes + norm_dupes,
    }
    return kept, stats


def get_shingles(text: str, k: int = 3) -> set[str]:
    """Extract word k-shingles from text."""
    words = re.findall(r"\b\w+\b", text.casefold())
    if not words:
        return set()
    if len(words) < k:
        return set(words)
    return set(" ".join(words[i : i + k]) for i in range(len(words) - k + 1))


def compute_minhash_signature(shingles: set[str], num_perm: int = 64) -> list[int]:
    """Compute deterministic MinHash signature for a set of shingles."""
    if not shingles:
        return [0] * num_perm
    hashes = [int(hashlib.md5(s.encode("utf-8")).hexdigest()[:16], 16) for s in shingles]
    sig = []
    for i in range(num_perm):
        a = (i * 10007 + 104729) & 0xFFFFFFFF
        b = (i * 31337 + 7919) & 0xFFFFFFFF
        min_val = min((a * h + b) & 0xFFFFFFFF for h in hashes)
        sig.append(min_val)
    return sig


def jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def deduplicate_near_duplicates(
    records: list[dict[str, Any]],
    threshold: float = 0.85,
    num_perm: int = 64,
    num_bands: int = 8,
) -> tuple[list[dict[str, Any]], int]:
    """Deduplicate records based on word 3-gram MinHash LSH and Jaccard similarity.

    When two documents have Jaccard similarity >= threshold, the later occurrence
    is excluded as a near-duplicate.
    """
    if len(records) <= 1:
        return records, 0

    rows_per_band = num_perm // num_bands
    shingle_cache = [get_shingles(r["text"]) for r in records]
    signatures = [compute_minhash_signature(s, num_perm=num_perm) for s in shingle_cache]

    # Index into LSH buckets
    buckets: dict[tuple[int, tuple[int, ...]], list[int]] = defaultdict(list)
    for idx, sig in enumerate(signatures):
        for b in range(num_bands):
            band = tuple(sig[b * rows_per_band : (b + 1) * rows_per_band])
            buckets[(b, band)].append(idx)

    dropped_indices: set[int] = set()
    for bucket in buckets.values():
        if len(bucket) <= 1:
            continue
        for i in range(len(bucket)):
            idx1 = bucket[i]
            if idx1 in dropped_indices:
                continue
            for j in range(i + 1, len(bucket)):
                idx2 = bucket[j]
                if idx2 in dropped_indices:
                    continue
                s1 = shingle_cache[idx1]
                s2 = shingle_cache[idx2]
                if not s1 or not s2:
                    continue
                sim = jaccard_similarity(s1, s2)
                if sim >= threshold:
                    dropped_indices.add(idx2)

    kept = [r for idx, r in enumerate(records) if idx not in dropped_indices]
    return kept, len(dropped_indices)


def stratified_split(
    records: list[dict[str, Any]],
    train_ratio: float = 0.80,
    val_ratio: float = 0.10,
    test_ratio: float = 0.10,
    seed: int = 42,
) -> dict[str, list[dict[str, Any]]]:
    """Perform a stratified 80/10/10 train/val/test split with seed 42.

    Returns:
        dict with keys "train", "val", "test", where each item is {id, text, label}.
    """
    if not (0.999 <= train_ratio + val_ratio + test_ratio <= 1.001):
        raise ValueError("Split ratios must sum to 1.0")

    by_label: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        by_label[int(r["label"])].append(r)

    train: list[dict[str, Any]] = []
    val: list[dict[str, Any]] = []
    test: list[dict[str, Any]] = []

    for label in sorted(by_label.keys()):
        group = list(by_label[label])
        group.sort(key=lambda x: str(x["id"]))
        rng = random.Random(seed)
        rng.shuffle(group)

        n_total = len(group)
        n_train = int(round(n_total * train_ratio))
        n_val = int(round(n_total * val_ratio))

        train.extend(group[:n_train])
        val.extend(group[n_train : n_train + n_val])
        test.extend(group[n_train + n_val :])

    rng_train = random.Random(seed)
    rng_val = random.Random(seed + 1)
    rng_test = random.Random(seed + 2)

    rng_train.shuffle(train)
    rng_val.shuffle(val)
    rng_test.shuffle(test)

    def _format(r: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(r["id"]),
            "text": str(r["text"]),
            "label": int(r["label"]),
        }

    return {
        "train": [_format(r) for r in train],
        "val": [_format(r) for r in val],
        "test": [_format(r) for r in test],
    }


def save_splits_to_jsonl(
    splits: dict[str, list[dict[str, Any]]],
    output_dir: Path,
) -> dict[str, Path]:
    """Save split records to JSONL files with strictly {id, text, label} format."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name in ("train", "val", "test"):
        path = output_dir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for item in splits[name]:
                record = {
                    "id": str(item["id"]),
                    "text": str(item["text"]),
                    "label": int(item["label"]),
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        paths[name] = path
    return paths


def validate_splits(
    train_path: Path,
    val_path: Path,
    test_path: Path,
) -> dict[str, Any]:
    """Validate that train, val, and test splits conform to requirements:

    1. Valid JSONL format with exact keys: {id, text, label}.
    2. IDs are unique within each split and across splits.
    3. NO email appears in more than one split (checks both ID and text).
    4. Labels are integers in {0, 1}.
    5. Returns statistics on class distribution per split.
    """
    splits_data: dict[str, list[dict[str, Any]]] = {}
    split_ids: dict[str, set[str]] = {}
    split_texts: dict[str, set[str]] = {}
    split_norm_texts: dict[str, set[str]] = {}

    paths = {"train": train_path, "val": val_path, "test": test_path}

    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Split file does not exist: {path}")

        records: list[dict[str, Any]] = []
        ids: set[str] = set()
        texts: set[str] = set()
        norm_texts: set[str] = set()

        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as err:
                    raise ValueError(f"{name}:{line_no}: Invalid JSON: {err}") from err

                if not isinstance(obj, dict):
                    raise ValueError(f"{name}:{line_no}: Row is not a JSON object")

                required_keys = {"id", "text", "label"}
                if set(obj.keys()) != required_keys:
                    raise ValueError(
                        f"{name}:{line_no}: Expected keys {required_keys}, got {set(obj.keys())}"
                    )

                item_id = str(obj["id"]).strip()
                if not item_id:
                    raise ValueError(f"{name}:{line_no}: 'id' cannot be empty")

                if item_id in ids:
                    raise ValueError(f"{name}:{line_no}: Duplicate ID '{item_id}' within {name} split")
                ids.add(item_id)

                text = str(obj["text"]).strip()
                if not text:
                    raise ValueError(f"{name}:{line_no}: 'text' cannot be empty")
                texts.add(text)

                norm_key = normalize_key(text)
                norm_texts.add(norm_key)

                label = obj["label"]
                if not isinstance(label, int) or label not in (0, 1):
                    raise ValueError(f"{name}:{line_no}: 'label' must be 0 or 1, got {label!r}")

                records.append(obj)

        splits_data[name] = records
        split_ids[name] = ids
        split_texts[name] = texts
        split_norm_texts[name] = norm_texts

    # Check cross-split isolation (no email appears in two splits)
    pairs = [("train", "val"), ("train", "test"), ("val", "test")]
    for s1, s2 in pairs:
        shared_ids = split_ids[s1] & split_ids[s2]
        if shared_ids:
            raise AssertionError(
                f"Data leakage detected! {len(shared_ids)} ID(s) appear in both {s1} and {s2}: {list(shared_ids)[:5]}"
            )

        shared_texts = split_texts[s1] & split_texts[s2]
        if shared_texts:
            raise AssertionError(
                f"Data leakage detected! {len(shared_texts)} exact email text(s) appear in both {s1} and {s2}"
            )

        shared_norm = split_norm_texts[s1] & split_norm_texts[s2]
        if shared_norm:
            raise AssertionError(
                f"Data leakage detected! {len(shared_norm)} normalized email(s) appear in both {s1} and {s2}"
            )

    report: dict[str, Any] = {
        "is_valid": True,
        "total_emails": sum(len(r) for r in splits_data.values()),
        "splits": {},
    }
    for name, records in splits_data.items():
        label_counts = Counter(r["label"] for r in records)
        n = len(records)
        report["splits"][name] = {
            "total": n,
            "legitimate_count": label_counts[0],
            "phishing_count": label_counts[1],
            "phishing_ratio": label_counts[1] / n if n > 0 else 0.0,
            "legitimate_ratio": label_counts[0] / n if n > 0 else 0.0,
        }

    return report


def load_raw_records(input_path: Path) -> list[dict[str, Any]]:
    """Load raw records from CSV or JSONL."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    records: list[dict[str, Any]] = []

    if input_path.suffix.lower() == ".csv":
        with input_path.open("r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                text = row.get("text") or row.get("content") or row.get("body") or ""
                label_raw = row.get("spam") or row.get("label") or row.get("email_type") or 0
                if str(label_raw).lower() in ("1", "phishing", "spam", "true"):
                    label = 1
                else:
                    label = 0
                records.append({
                    "id": f"email-{idx+1:05d}",
                    "text": text,
                    "label": label,
                })
    elif input_path.suffix.lower() in (".jsonl", ".json"):
        with input_path.open("r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                text = row.get("text") or row.get("content") or row.get("body") or ""
                label_raw = row.get("spam") or row.get("label") or row.get("email_type") or 0
                if str(label_raw).lower() in ("1", "phishing", "spam", "true"):
                    label = 1
                else:
                    label = 0
                row_id = row.get("id") or row.get("email_id") or f"email-{idx+1:05d}"
                records.append({
                    "id": str(row_id),
                    "text": text,
                    "label": label,
                })
    else:
        raise ValueError(f"Unsupported file extension: {input_path.suffix}")

    return records


def run_pipeline(
    input_path: Path,
    output_dir: Path,
    seed: int = 42,
    near_dedup_threshold: float = 0.85,
) -> dict[str, Any]:
    """Execute end-to-end data pipeline: load, clean, dedupe, stratified split, save, and validate."""
    # 1. Load
    raw_records = load_raw_records(input_path)
    raw_total = len(raw_records)
    raw_balance = Counter(r["label"] for r in raw_records)

    # 2. Clean
    cleaned: list[dict[str, Any]] = []
    empty_count = 0
    for r in raw_records:
        t = clean_text(r["text"])
        if not t:
            empty_count += 1
            continue
        cleaned.append({
            "id": r["id"],
            "text": t,
            "label": r["label"],
        })

    # 3. Exact Deduplication
    after_exact, exact_stats = deduplicate_exact(cleaned)

    # 4. Near-Duplicate Deduplication
    after_near, near_dupes_removed = deduplicate_near_duplicates(
        after_exact,
        threshold=near_dedup_threshold,
    )

    total_dupes_removed = exact_stats["total_exact_duplicates_removed"] + near_dupes_removed
    post_dedup_balance = Counter(r["label"] for r in after_near)

    # 5. Stratified 80/10/10 Split
    splits = stratified_split(after_near, train_ratio=0.80, val_ratio=0.10, test_ratio=0.10, seed=seed)

    # 6. Save JSONL
    saved_paths = save_splits_to_jsonl(splits, output_dir)

    # 7. Validate
    validation_report = validate_splits(
        saved_paths["train"],
        saved_paths["val"],
        saved_paths["test"],
    )

    report = {
        "raw_total": raw_total,
        "raw_class_balance": {
            "legitimate (0)": raw_balance[0],
            "phishing (1)": raw_balance[1],
        },
        "empty_removed": empty_count,
        "duplicates_removed": {
            "exact_raw": exact_stats["exact_raw_duplicates_removed"],
            "normalized_whitespace_case": exact_stats["normalized_whitespace_duplicates_removed"],
            "near_duplicates_minhash_jaccard": near_dupes_removed,
            "total_duplicates_removed": total_dupes_removed,
        },
        "final_clean_total": len(after_near),
        "final_class_balance": {
            "legitimate (0)": post_dedup_balance[0],
            "phishing (1)": post_dedup_balance[1],
            "phishing_percentage": round(post_dedup_balance[1] / len(after_near) * 100, 2),
            "legitimate_percentage": round(post_dedup_balance[0] / len(after_near) * 100, 2),
        },
        "splits": validation_report["splits"],
        "paths": {k: str(v) for k, v in saved_paths.items()},
        "validation_passed": validation_report["is_valid"],
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/emails.csv"), help="Path to input raw data file")
    parser.add_argument("--output-dir", type=Path, default=Path("data/splits"), help="Path to output splits directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for stratified split")
    parser.add_argument("--near-threshold", type=float, default=0.85, help="Jaccard threshold for near-duplicate deduplication")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing splits without rebuilding")
    args = parser.parse_args()

    if args.validate_only:
        report = validate_splits(
            args.output_dir / "train.jsonl",
            args.output_dir / "val.jsonl",
            args.output_dir / "test.jsonl",
        )
        print(json.dumps(report, indent=2))
        return

    report = run_pipeline(
        input_path=args.input,
        output_dir=args.output_dir,
        seed=args.seed,
        near_dedup_threshold=args.near_threshold,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
