"""Analyze candidate records across all sources for clean split construction."""
import json
import sys
from pathlib import Path
from collections import Counter

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

# 1. Load Enron legitimate emails
enron_path = Path("data/processed/enron_ingested/enron_clean_500.jsonl")
enron_records = []
if enron_path.exists():
    with open(enron_path, "r", encoding="utf-8") as f:
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

# 2. Load phishing records from review_seed42 train and test
phish_records = []
for p in [Path("data/splits/review_seed42/train.jsonl"), Path("data/splits/review_seed42/test.jsonl")]:
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if item.get("label") in (1, "1", "phishing"):
                        phish_records.append({
                            "id": item["id"],
                            "text": item.get("text", item.get("body", "")),
                            "label": 1,
                            "source": "nazario",
                            "sender": item.get("sender", ""),
                            "subject": item.get("subject", ""),
                        })

# 3. Load SpamAssassin ham records from review_seed42
ham_records = []
for p in [Path("data/splits/review_seed42/train.jsonl"), Path("data/splits/review_seed42/test.jsonl")]:
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
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

print(f"Loaded {len(enron_records)} Enron records, {len(ham_records)} SpamAssassin ham records, {len(phish_records)} Phishing records.")

# Check exact deduplication on phish_records
phish_kept, p_stats = deduplicate_exact(phish_records)
print(f"Phishing exact deduplication: {len(phish_records)} -> {len(phish_kept)} (removed {p_stats['total_exact_duplicates_removed']})")

# Cluster near duplicates
phish_clustered, pc_stats = cluster_near_duplicates(phish_kept, threshold=0.85)
print(f"Phishing near-duplicate clusters: {pc_stats['cluster_count']} clusters from {len(phish_kept)} records")

enron_clustered, ec_stats = cluster_near_duplicates(enron_records, threshold=0.85)
print(f"Enron near-duplicate clusters: {ec_stats['cluster_count']} clusters from {len(enron_records)} records")
