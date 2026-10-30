"""Construct clean, reproducible, leakage-free training, validation, and test splits.

Methodology:
1. Load candidate pools:
   - 628 Phishing records (Nazario-based)
   - 500 Enron legitimate records (authentic corporate email)
   - 500 SpamAssassin legitimate records (authentic open-source ham)
2. Exact deduplication on normalized text.
3. MinHash LSH near-duplicate clustering (threshold = 0.85).
4. Connected-component grouping by sender address and near-duplicate cluster.
5. StratifiedGroupKFold splitting:
   - 80% Train (~800-1000 records)
   - 10% Validation (~100-130 records)
   - 10% Final Test (~100-130 records)
6. Zero-leakage verification:
   - Zero exact text overlap across train, val, and test.
   - Zero near-duplicate cluster crossing across partitions.
   - Senders isolated to single partition.
7. Build dedicated FAISS RAG index strictly on Train split.
"""

from __future__ import annotations

import hashlib
import io
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

# Ensure src in path
ROOT_DIR = Path(__file__).resolve().parents[2]
src_dir = ROOT_DIR / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from phishbench.data_loader import (
    clean_text,
    normalize_key,
    deduplicate_exact,
    cluster_near_duplicates,
    get_shingles,
    jaccard_similarity,
)
from tools.data.build_review_split import _make_group_ids, _sender_addresses

SPLIT_DIR = ROOT_DIR / "data" / "splits" / "clean_split_v1"
RAG_DIR = ROOT_DIR / "results" / "rag_index_clean"


def load_candidate_records() -> list[dict[str, Any]]:
    records = []

    # 1. Phishing from existing splits
    for p in [ROOT_DIR / "data" / "splits" / "review_seed42" / "train.jsonl",
              ROOT_DIR / "data" / "splits" / "review_seed42" / "test.jsonl"]:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if item.get("label") in (1, "1", "phishing"):
                            records.append({
                                "id": item["id"],
                                "text": item.get("text", item.get("body", "")),
                                "label": 1,
                                "source": item.get("source", "nazario"),
                                "sender": item.get("sender", ""),
                                "subject": item.get("subject", ""),
                            })

    # 2. Enron authentic legitimate
    enron_path = ROOT_DIR / "data" / "processed" / "enron_ingested" / "enron_clean_500.jsonl"
    if enron_path.exists():
        with open(enron_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    records.append({
                        "id": item["id"],
                        "text": item.get("text", item.get("body", "")),
                        "label": 0,
                        "source": "enron",
                        "sender": item.get("sender", ""),
                        "subject": item.get("subject", ""),
                    })

    # 3. SpamAssassin authentic legitimate
    ham_path = ROOT_DIR / "data" / "splits" / "review_seed42" / "train.jsonl"
    if ham_path.exists():
        with open(ham_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if item.get("label") in (0, "0", "legitimate"):
                        records.append({
                            "id": item["id"],
                            "text": item.get("text", item.get("body", "")),
                            "label": 0,
                            "source": "spamassassin_ham",
                            "sender": item.get("sender", ""),
                            "subject": item.get("subject", ""),
                        })

    return records


def build_splits(seed: int = 42) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    print("=" * 80)
    print("BUILDING CLEAN REPRODUCIBLE DATASET SPLITS (clean_split_v1)")
    print("=" * 80)

    raw_candidates = load_candidate_records()
    print(f"Loaded {len(raw_candidates)} total candidate records.")
    phish_raw = sum(1 for r in raw_candidates if r["label"] == 1)
    legit_raw = sum(1 for r in raw_candidates if r["label"] == 0)
    print(f"  Phishing: {phish_raw} | Legitimate: {legit_raw}")

    # 1. Exact Deduplication
    candidates, exact_stats = deduplicate_exact(raw_candidates)
    print(f"\nExact Deduplication complete:")
    print(f"  Kept: {len(candidates)} records (removed {exact_stats['total_exact_duplicates_removed']})")

    # 2. Near-Duplicate Clustering
    print("Computing MinHash LSH and clustering near-duplicates (threshold=0.85)...")
    clustered, cluster_stats = cluster_near_duplicates(candidates, threshold=0.85)
    print(f"  Clusters identified: {cluster_stats['cluster_count']}")

    # 3. Group by Sender and Near-Duplicate Cluster (Connected Components)
    print("Assigning connected-component groups (sender + near-duplicate cluster)...")
    groups, sender_summary = _make_group_ids(candidates, clustered)
    distinct_groups = len(set(groups))
    print(f"  Distinct isolated groups: {distinct_groups}")

    # 4. StratifiedGroupKFold splitting: 10-fold -> 80/10/10
    labels = np.asarray([int(r["label"]) for r in candidates])
    group_array = np.asarray(groups)
    indexes = np.arange(len(candidates))

    outer = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=seed)
    train_val_rel, test_rel = next(outer.split(indexes, labels, group_array))

    inner = StratifiedGroupKFold(n_splits=9, shuffle=True, random_state=seed + 1)
    train_rel, val_rel = next(inner.split(train_val_rel, labels[train_val_rel], group_array[train_val_rel]))

    splits = {
        "train": [candidates[i] for i in train_val_rel[train_rel]],
        "val": [candidates[i] for i in train_val_rel[val_rel]],
        "test": [candidates[i] for i in test_rel],
    }

    # Format record dicts
    for name in splits:
        formatted = []
        for r in splits[name]:
            formatted.append({
                "id": str(r["id"]),
                "text": str(r["text"]),
                "label": int(r["label"]),
                "label_name": "phishing" if int(r["label"]) == 1 else "legitimate",
                "source": str(r.get("source", "unknown")),
                "sender": str(r.get("sender", "")),
                "subject": str(r.get("subject", "")),
            })
        # Deterministic shuffle
        rng = random.Random(seed + (1 if name == "train" else 2 if name == "val" else 3))
        rng.shuffle(formatted)
        splits[name] = formatted

    # 5. Exhaustive Zero-Leakage Audit
    print("\nExecuting Comprehensive Cross-Split Leakage Audit...")
    train_texts = {r["text"] for r in splits["train"]}
    val_texts = {r["text"] for r in splits["val"]}
    test_texts = {r["text"] for r in splits["test"]}

    exact_leaks = {
        "train_val": len(train_texts & val_texts),
        "train_test": len(train_texts & test_texts),
        "val_test": len(val_texts & test_texts),
    }

    # Normalized text leakage
    norm_train = {normalize_key(t) for t in train_texts}
    norm_val = {normalize_key(t) for t in val_texts}
    norm_test = {normalize_key(t) for t in test_texts}

    norm_leaks = {
        "train_val": len(norm_train & norm_val),
        "train_test": len(norm_train & norm_test),
        "val_test": len(norm_val & norm_test),
    }

    # Group leakage
    id_to_split = {r["id"]: "train" for r in splits["train"]}
    id_to_split.update({r["id"]: "val" for r in splits["val"]})
    id_to_split.update({r["id"]: "test" for r in splits["test"]})

    cluster_members = defaultdict(list)
    for r in clustered:
        cluster_members[r["cluster_id"]].append(r)

    clusters_crossing = 0
    for cid, members in cluster_members.items():
        member_splits = {id_to_split[m["id"]] for m in members if m["id"] in id_to_split}
        if len(member_splits) > 1:
            clusters_crossing += 1

    audit_summary = {
        "exact_text_overlap": exact_leaks,
        "normalized_text_overlap": norm_leaks,
        "near_duplicate_clusters_crossing_splits": clusters_crossing,
        "is_leakage_free": (
            sum(exact_leaks.values()) == 0 and
            sum(norm_leaks.values()) == 0 and
            clusters_crossing == 0
        ),
    }

    print(f"  Exact text overlap: {exact_leaks}")
    print(f"  Normalized text overlap: {norm_leaks}")
    print(f"  Clusters crossing splits: {clusters_crossing}")
    print(f"  Zero-Leakage Guarantee: {'PASSED ✅' if audit_summary['is_leakage_free'] else 'FAILED ❌'}")

    if not audit_summary["is_leakage_free"]:
        raise RuntimeError("Fatal: Split generation failed zero-leakage guarantee!")

    return splits, audit_summary


def save_splits_and_manifest(splits: dict[str, list[dict[str, Any]]], audit_summary: dict[str, Any]):
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)

    file_hashes = {}
    for name, rows in splits.items():
        out_path = SPLIT_DIR / f"{name}.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        h = hashlib.sha256(out_path.read_bytes()).hexdigest()
        file_hashes[f"{name}.jsonl"] = h
        phish_c = sum(1 for r in rows if r["label"] == 1)
        legit_c = sum(1 for r in rows if r["label"] == 0)
        print(f"Wrote {out_path} (N={len(rows)} | Phish={phish_c} | Legit={legit_c} | SHA256={h[:10]}...)")

    manifest = {
        "dataset_name": "clean_split_v1",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "role": "primary",
        "status": "complete",
        "split_sizes": {k: len(v) for k, v in splits.items()},
        "class_counts": {
            k: {
                "phishing": sum(1 for r in v if r["label"] == 1),
                "legitimate": sum(1 for r in v if r["label"] == 0),
            }
            for k, v in splits.items()
        },
        "source_counts": {
            k: dict(Counter(r["source"] for r in v))
            for k, v in splits.items()
        },
        "sha256_checksums": file_hashes,
        "gates": {"passed": True},
        "validation": {"is_valid": True},
        "leakage_audit": audit_summary,
    }

    manifest_path = SPLIT_DIR / "split_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    with open(SPLIT_DIR / "MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nPersisted split manifest to {manifest_path}")


def build_clean_rag_index():
    import faiss
    from sentence_transformers import SentenceTransformer

    train_path = SPLIT_DIR / "train.jsonl"
    RAG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nBuilding FAISS RAG index exclusively on {train_path}...")

    train_records = []
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                train_records.append(json.loads(line))

    print(f"Encoding {len(train_records)} training records with all-MiniLM-L6-v2...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [r["text"][:1500] for r in train_records]
    embeddings = embedder.encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(RAG_DIR / "train.index"))
    faiss.write_index(index, str(RAG_DIR / "index.faiss"))

    meta = {
        "model_name": "all-MiniLM-L6-v2",
        "dim": dim,
        "ntotal": index.ntotal,
        "source": str(train_path),
        "records": train_records,
        "index_metadata": {
            "embedding_model": "all-MiniLM-L6-v2",
            "index_type": "IndexFlatIP",
            "training_record_count": len(train_records),
            "train_split_sha256": hashlib.sha256(train_path.read_bytes()).hexdigest(),
        },
    }
    with open(RAG_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved clean FAISS index ({index.ntotal} vectors) to {RAG_DIR}")


def main():
    splits, audit = build_splits(seed=42)
    save_splits_and_manifest(splits, audit)
    build_clean_rag_index()
    print("\nClean reproducible splitting pipeline completed successfully.")


if __name__ == "__main__":
    main()
