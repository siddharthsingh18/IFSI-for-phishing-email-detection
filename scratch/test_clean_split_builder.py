"""Test grouped splitting logic on candidates to ensure zero leakage and proper balance."""
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

sys.path.insert(0, str(Path("src").resolve()))
sys.path.insert(0, str(Path(".").resolve()))

from phishbench.data_loader import (
    clean_text,
    normalize_key,
    deduplicate_exact,
    cluster_near_duplicates,
    get_shingles,
    jaccard_similarity,
)
from tools.data.build_review_split import _make_group_ids, _sender_addresses

def test_split():
    # 1. Load Phishing
    phish_records = []
    for p in [Path("data/splits/review_seed42/train.jsonl"), Path("data/splits/review_seed42/test.jsonl")]:
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if item.get("label") in (1, "1", "phishing"):
                        phish_records.append({
                            "id": item["id"],
                            "text": item.get("text", item.get("body", "")),
                            "label": 1,
                            "source": item.get("source", "nazario"),
                            "sender": item.get("sender", ""),
                            "subject": item.get("subject", ""),
                        })

    # 2. Load Enron legitimate
    enron_records = []
    with open("data/processed/enron_ingested/enron_clean_500.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                enron_records.append({
                    "id": item["id"],
                    "text": item.get("text", item.get("body", "")),
                    "label": 0,
                    "source": "enron",
                    "sender": item.get("sender", ""),
                    "subject": item.get("subject", ""),
                })

    # 3. Load SpamAssassin legitimate to reach balance
    ham_records = []
    with open("data/splits/review_seed42/train.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                if item.get("label") in (0, "0", "legitimate"):
                    ham_records.append({
                        "id": item["id"],
                        "text": item.get("text", item.get("body", "")),
                        "label": 0,
                        "source": "spamassassin_ham",
                        "sender": item.get("sender", ""),
                        "subject": item.get("subject", ""),
                    })

    # Combine into candidate pool
    # Deduplicate exact
    all_raw = phish_records + enron_records + ham_records
    candidates, exact_stats = deduplicate_exact(all_raw)
    print(f"Total candidates after exact deduplication: {len(candidates)}")
    print(f"Exact stats: {exact_stats}")

    # Cluster near duplicates
    clustered, cluster_stats = cluster_near_duplicates(candidates, threshold=0.85)
    print(f"Cluster count: {cluster_stats['cluster_count']}")

    # Form connected component groups
    groups, sender_summary = _make_group_ids(candidates, clustered)
    print(f"Distinct groups: {len(set(groups))}")

    # Run StratifiedGroupKFold 80/10/10
    labels = np.asarray([int(r["label"]) for r in candidates])
    group_array = np.asarray(groups)
    indexes = np.arange(len(candidates))

    # Outer split: 10-fold -> 90% train_val, 10% test
    outer = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=42)
    train_val_idx, test_idx = next(outer.split(indexes, labels, group_array))

    # Inner split: 9-fold on train_val -> 80% train, 10% val
    inner = StratifiedGroupKFold(n_splits=9, shuffle=True, random_state=43)
    train_sub_idx, val_sub_idx = next(inner.split(train_val_idx, labels[train_val_idx], group_array[train_val_idx]))

    train_final = [candidates[i] for i in train_val_idx[train_sub_idx]]
    val_final = [candidates[i] for i in train_val_idx[val_sub_idx]]
    test_final = [candidates[i] for i in test_idx]

    print(f"\nSplit Sizes:")
    print(f"  Train: {len(train_final)} (phish={sum(r['label']==1 for r in train_final)}, legit={sum(r['label']==0 for r in train_final)})")
    print(f"  Val  : {len(val_final)} (phish={sum(r['label']==1 for r in val_final)}, legit={sum(r['label']==0 for r in val_final)})")
    print(f"  Test : {len(test_final)} (phish={sum(r['label']==1 for r in test_final)}, legit={sum(r['label']==0 for r in test_final)})")

    # Check for group leakage
    train_groups = {groups[i] for i in train_val_idx[train_sub_idx]}
    val_groups = {groups[i] for i in train_val_idx[val_sub_idx]}
    test_groups = {groups[i] for i in test_idx}

    print(f"\nLeakage Verification:")
    print(f"  train & val group overlap : {len(train_groups & val_groups)}")
    print(f"  train & test group overlap: {len(train_groups & test_groups)}")
    print(f"  val & test group overlap  : {len(val_groups & test_groups)}")

    # Check exact text overlap
    train_texts = {r["text"] for r in train_final}
    val_texts = {r["text"] for r in val_final}
    test_texts = {r["text"] for r in test_final}
    print(f"  train & val text overlap  : {len(train_texts & val_texts)}")
    print(f"  train & test text overlap : {len(train_texts & test_texts)}")
    print(f"  val & test text overlap   : {len(val_texts & test_texts)}")

    # Check near-duplicate Jaccard overlap
    shingles_map = {r["id"]: get_shingles(r["text"]) for r in candidates}
    id_to_split = {}
    for r in train_final: id_to_split[r["id"]] = "train"
    for r in val_final: id_to_split[r["id"]] = "val"
    for r in test_final: id_to_split[r["id"]] = "test"

    near_dupe_cross_count = 0
    # Check within clusters
    members_by_cluster = defaultdict(list)
    for r in clustered:
        members_by_cluster[r["cluster_id"]].append(r)

    for cid, members in members_by_cluster.items():
        splits_in_cluster = {id_to_split[m["id"]] for m in members if m["id"] in id_to_split}
        if len(splits_in_cluster) > 1:
            near_dupe_cross_count += 1

    print(f"  Clusters crossing splits: {near_dupe_cross_count}")

if __name__ == "__main__":
    test_split()

