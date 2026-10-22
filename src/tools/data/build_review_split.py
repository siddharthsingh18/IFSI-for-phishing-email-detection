"""Build an audited local-only, sender-grouped split from clean email candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from email import policy
from email.parser import Parser
from email.utils import getaddresses
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

from phishbench.data_loader import (
    cluster_near_duplicates,
    get_shingles,
    jaccard_similarity,
    normalize_key,
)
from tools.data.parsers import parse_mbox

MIME_PLACEHOLDER_RE = re.compile(
    r"^html(?: file)? (?:is )?required(?: for this (?:letter|message))?\.?$",
    re.IGNORECASE,
)
NEAR_DUPLICATE_THRESHOLD = 0.85


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _clean_body_is_usable(text: str) -> bool:
    _, separator, body = text.partition("\n\n")
    normalized_body = " ".join(unicodedata.normalize("NFKC", body).casefold().split())
    return bool(normalized_body) and not MIME_PLACEHOLDER_RE.fullmatch(normalized_body)


def _sender_addresses(text: str) -> list[str]:
    message = Parser(policy=policy.default).parsestr(text)
    for header in ("From", "Sender", "Return-Path"):
        addresses = [
            address.casefold()
            for _, address in getaddresses([message.get(header, "")])
            if address
        ]
        if addresses:
            return addresses
    return []


def _normalized_candidates(
    nazario_path: Path,
    ham_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    phishing = parse_mbox(nazario_path, source="nazario", label="phishing")
    ham = _read_jsonl(ham_path)
    rows = phishing + ham
    exclusions = Counter()
    exact_by_key: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    for row in rows:
        source = str(row.get("source", ""))
        raw_label = str(row.get("label", "")).casefold()
        if (source, raw_label) not in {("nazario", "phishing"), ("spamassassin_ham", "legit")}:
            raise ValueError(f"Unexpected source/label pair: {source}:{raw_label}")
        text = str(row.get("text", "")).strip()
        if not text or not _clean_body_is_usable(text):
            exclusions[f"{source}:empty_or_placeholder_body"] += 1
            continue
        normalized = normalize_key(text)
        if normalized in exact_by_key:
            previous = exact_by_key[normalized]
            if previous["label"] != raw_label:
                raise ValueError("Exact duplicate text has conflicting labels")
            exclusions[f"{source}:normalized_exact_duplicate"] += 1
            continue
        exact_by_key[normalized] = {"label": raw_label, "source": source}
        records.append(
            {
                "id": str(row["id"]),
                "text": text,
                "label": 1 if raw_label == "phishing" else 0,
                "source": source,
            }
        )
    summary = {
        "input_records": len(rows),
        "accepted_records": len(records),
        "excluded": dict(sorted(exclusions.items())),
        "exact_normalized_duplicates_removed": sum(
            count for key, count in exclusions.items() if key.endswith("normalized_exact_duplicate")
        ),
    }
    return records, summary


def _make_group_ids(
    records: list[dict[str, Any]],
    clustered: list[dict[str, Any]],
) -> tuple[list[str], dict[str, Any]]:
    id_to_index = {str(row["id"]): index for index, row in enumerate(records)}
    parent = list(range(len(records)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    sender_first: dict[str, int] = {}
    sender_record_counts = Counter()
    sender_group_counts = Counter()
    sender_missing_counts = Counter()
    for record in records:
        addresses = _sender_addresses(str(record["text"]))
        if not addresses:
            sender_missing_counts[str(record["source"])] += 1
            continue
        sender_key = f"{record['source']}:{addresses[0]}"
        sender_record_counts[str(record["source"])] += 1
        index = id_to_index[str(record["id"])]
        if sender_key in sender_first:
            union(index, sender_first[sender_key])
        else:
            sender_first[sender_key] = index
            sender_group_counts[str(record["source"])] += 1

    cluster_first: dict[str, int] = {}
    for row in clustered:
        index = id_to_index[str(row["id"])]
        cluster_id = str(row["cluster_id"])
        if cluster_id in cluster_first:
            union(index, cluster_first[cluster_id])
        else:
            cluster_first[cluster_id] = index

    groups = [f"group-{find(index)}" for index in range(len(records))]
    return groups, {
        "records_with_sender_by_source": dict(sender_record_counts),
        "distinct_sender_groups_by_source": dict(sender_group_counts),
        "records_without_sender_by_source": dict(sender_missing_counts),
    }


def _stratified_group_splits(
    records: list[dict[str, Any]],
    groups: list[str],
    seed: int,
) -> dict[str, list[dict[str, Any]]]:
    labels = np.asarray([int(row["label"]) for row in records])
    group_array = np.asarray(groups)
    indexes = np.arange(len(records))
    outer = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=seed)
    remaining_relative, test_relative = next(outer.split(indexes, labels, group_array))
    remaining = indexes[remaining_relative]
    inner = StratifiedGroupKFold(n_splits=9, shuffle=True, random_state=seed + 1)
    train_relative, val_relative = next(
        inner.split(remaining, labels[remaining], group_array[remaining])
    )
    index_sets = {
        "train": remaining[train_relative],
        "val": remaining[val_relative],
        "test": indexes[test_relative],
    }
    split_rows = {
        name: [records[int(index)] for index in split_indexes]
        for name, split_indexes in index_sets.items()
    }
    if any(not rows for rows in split_rows.values()):
        raise ValueError("Grouped split produced an empty partition")
    if any({int(row["label"]) for row in rows} != {0, 1} for rows in split_rows.values()):
        raise ValueError("Grouped split did not preserve both labels in every partition")
    return split_rows


def _audit(
    splits: dict[str, list[dict[str, Any]]],
    records: list[dict[str, Any]],
    groups: list[str],
    clustered: list[dict[str, Any]],
    cluster_stats: dict[str, Any],
    exclusions: dict[str, Any],
    sender_summary: dict[str, Any],
    source_hashes: dict[str, str],
    seed: int,
) -> dict[str, Any]:
    split_for_id = {
        str(row["id"]): split for split, rows in splits.items() for row in rows
    }
    groups_by_id = {
        str(record["id"]): group for record, group in zip(records, groups, strict=True)
    }
    label_source = {
        split: {
            str(label): dict(sorted(Counter(
                str(row["source"]) for row in rows if int(row["label"]) == label
            ).items()))
            for label in (0, 1)
        }
        for split, rows in splits.items()
    }
    class_counts = {
        split: {
            str(label): sum(int(row["label"]) == label for row in rows)
            for label in (0, 1)
        }
        for split, rows in splits.items()
    }
    source_label_totals = Counter(
        (str(row["source"]), int(row["label"]))
        for rows in splits.values()
        for row in rows
    )
    sources_by_label = {
        str(label): sorted(
            source for source in {key[0] for key in source_label_totals}
            if source_label_totals[(source, label)]
        )
        for label in (0, 1)
    }

    cluster_members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in clustered:
        cluster_members[str(row["cluster_id"])].append(row)
    shingles = {str(row["id"]): get_shingles(str(row["text"])) for row in clustered}
    near_pairs_by_split = Counter()
    near_pairs_across_splits = 0
    for members in cluster_members.values():
        for left_index, left in enumerate(members):
            for right in members[left_index + 1 :]:
                if jaccard_similarity(
                    shingles[str(left["id"])], shingles[str(right["id"])]
                ) < NEAR_DUPLICATE_THRESHOLD:
                    continue
                left_split = split_for_id[str(left["id"])]
                right_split = split_for_id[str(right["id"])]
                if left_split == right_split:
                    near_pairs_by_split[left_split] += 1
                else:
                    near_pairs_across_splits += 1

    max_source_share = {}
    for label in (0, 1):
        total = sum(count for (source, current_label), count in source_label_totals.items() if current_label == label)
        max_source_share[str(label)] = max(
            (count / total for (source, current_label), count in source_label_totals.items() if current_label == label),
            default=0.0,
        )
    group_splits: dict[str, set[str]] = defaultdict(set)
    for split, rows in splits.items():
        for row in rows:
            group_splits[groups_by_id[str(row["id"])]].add(split)
    group_leakage = any(len(locations) > 1 for locations in group_splits.values())
    if group_leakage or near_pairs_across_splits:
        raise ValueError("Grouped split leaked a sender or near-duplicate group across partitions")
    source_label_confound = set(sources_by_label["0"]).isdisjoint(sources_by_label["1"])
    return {
        "seed": seed,
        "split_method": "StratifiedGroupKFold 10-fold test; then 9-fold validation on remaining records",
        "grouping": "connected components of same-source sender address and 0.85 Jaccard MinHash-LSH near-duplicate clusters",
        "source_hashes": source_hashes,
        "input_quality": exclusions,
        "split_sizes": {name: len(rows) for name, rows in splits.items()},
        "class_counts": class_counts,
        "source_distribution_by_label": label_source,
        "source_label_confound": {
            "present": source_label_confound,
            "sources_by_label": sources_by_label,
            "largest_single_source_share_by_label": max_source_share,
        },
        "review_only": source_label_confound,
        "duplicate_audit": {
            "exact_normalized_duplicates_removed_before_split": exclusions["exact_normalized_duplicates_removed"],
            "exact_normalized_duplicates_within_or_across_splits": 0,
            "near_duplicate_threshold_jaccard": NEAR_DUPLICATE_THRESHOLD,
            "near_duplicate_detection": (
                "MinHash LSH candidate generation followed by exact Jaccard checks; "
                "not exhaustive all-pairs"
            ),
            "near_duplicate_candidate_pairs_compared": cluster_stats["exact_similarity_comparisons"],
            "near_duplicate_pairs_within_splits": dict(sorted(near_pairs_by_split.items())),
            "near_duplicate_pairs_across_splits": near_pairs_across_splits,
            "near_duplicate_clusters_with_multiple_records": sum(
                size > 1 for size in cluster_stats["cluster_sizes"].values()
            ),
            **sender_summary,
        },
        "split_group_leakage": group_leakage,
        "records_schema": ["id", "text", "label", "source"],
        "files": {},
    }


def build_review_split(
    nazario_path: Path,
    ham_path: Path,
    output_dir: Path,
    *,
    seed: int = 42,
) -> dict[str, Any]:
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing split directory: {output_dir}")
    records, quality = _normalized_candidates(nazario_path, ham_path)
    clustered, cluster_stats = cluster_near_duplicates(
        records, threshold=NEAR_DUPLICATE_THRESHOLD
    )
    groups, sender_summary = _make_group_ids(records, clustered)
    splits = _stratified_group_splits(records, groups, seed)
    source_hashes = {
        str(nazario_path): _sha256(nazario_path),
        str(ham_path): _sha256(ham_path),
    }
    audit = _audit(
        splits,
        records,
        groups,
        clustered,
        cluster_stats,
        quality,
        sender_summary,
        source_hashes,
        seed,
    )
    output_dir.mkdir(parents=True)
    for name, rows in splits.items():
        path = output_dir / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(
                    json.dumps(
                        {
                            "id": str(row["id"]),
                            "text": str(row["text"]),
                            "label": int(row["label"]),
                            "source": str(row["source"]),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        audit["files"][name] = {
            "path": str(path),
            "records": len(rows),
            "sha256": _sha256(path),
        }
    audit_path = output_dir / "audit.json"
    with audit_path.open("w", encoding="utf-8") as handle:
        json.dump(audit, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nazario", type=Path, default=Path("data/raw/nazario/phishing3.mbox"))
    parser.add_argument("--ham", type=Path, default=Path("data/processed/spamassassin_ham.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/splits/review_seed42"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(build_review_split(args.nazario, args.ham, args.output_dir, seed=args.seed), indent=2))


if __name__ == "__main__":
    main()
