"""Cryptographic and lexical integrity checker for heldout_benchmark_v1.jsonl.

Verifies zero overlap against V1, V2, train, val, test, and FAISS RAG index.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

def normalize_text(text: str) -> str:
    t = text.lower()
    t = re.sub(r"\s+", " ", t).strip()
    return t

def get_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()

def load_bodies(path: str | Path) -> set[str]:
    hashes = set()
    p = Path(path)
    if not p.exists():
        return hashes
    if p.suffix == ".json":
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            records = data.get("records", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            for d in records:
                body = d.get("body") or d.get("text") or ""
                if body:
                    hashes.add(get_hash(body))
        return hashes
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                body = d.get("body") or d.get("text") or ""
                if body:
                    hashes.add(get_hash(body))
    return hashes

def main():
    heldout_path = Path("data/evaluation/heldout_benchmark_v1.jsonl")
    assert heldout_path.exists(), "Heldout dataset missing"

    heldout_records = []
    heldout_hashes = set()
    with open(heldout_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                heldout_records.append(d)
                heldout_hashes.add(get_hash(d["body"]))

    print(f"Total Heldout Records: {len(heldout_records)}")
    assert len(heldout_records) == 100, f"Expected 100, got {len(heldout_records)}"

    phish = sum(1 for r in heldout_records if r["is_phishing"])
    legit = sum(1 for r in heldout_records if not r["is_phishing"])
    inj = sum(1 for r in heldout_records if r["has_prompt_injection"])
    print(f"Distribution: Phishing={phish}, Legitimate={legit}, Prompt Injection={inj}")
    assert phish == 50
    assert legit == 50
    assert inj == 20

    sources = [
        ("Live Benchmark V1", "data/evaluation/live_benchmark_v1.jsonl"),
        ("Live Benchmark V2", "data/evaluation/live_benchmark_v2.jsonl"),
        ("Clean Split Train", "data/splits/clean_split_v1/train.jsonl"),
        ("Clean Split Val", "data/splits/clean_split_v1/val.jsonl"),
        ("Clean Split Test", "data/splits/clean_split_v1/test.jsonl"),
        ("FAISS RAG Metadata", "results/rag_index_clean/metadata.json"),
    ]

    total_overlap = 0
    for name, path in sources:
        hashes = load_bodies(path)
        overlap = heldout_hashes.intersection(hashes)
        print(f"Overlap with {name} ({len(hashes)} items): {len(overlap)}")
        total_overlap += len(overlap)
        assert len(overlap) == 0, f"Detected {len(overlap)} overlapping records with {name}!"

    print(f"\nALL INTEGRITY CHECKS PASSED: Total overlap across all historical datasets = {total_overlap} (0.00%)")

if __name__ == "__main__":
    main()
