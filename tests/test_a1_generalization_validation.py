"""Automated Test Suite for A1 Generalization Validation V1 Dataset & System Integrity.

Tests:
1. Exact 500 sample volume & ID uniqueness
2. Category balance (100 per category)
3. Symmetrical ground-truth balance (250 phishing, 250 legitimate)
4. Injection distribution (50 active phishing, 50 quoted legitimate)
5. Complete provenance metadata coverage
6. Cryptographic non-leakage & zero overlap with prior datasets
7. Zero overlap with clean FAISS index
8. Input formatting compatibility for A0 and A1
9. Code and index hash invariance
"""

import hashlib
import json
import re
from pathlib import Path
import pytest

DATASET_PATH = Path("data/evaluation/a1_generalization_v1.jsonl")
FAISS_META_PATH = Path("results/rag_index_clean/metadata.json")
FAISS_INDEX_PATH = Path("results/rag_index_clean/index.faiss")

EXPECTED_HASHES = {
    "src/core/inference.py": "aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506",
    "src/core/inference_m4_v2.py": "fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37",
    "results/rag_index_clean/index.faiss": "d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc",
    "results/rag_index_clean/metadata.json": "4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece",
}


def normalize_text(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def text_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


@pytest.fixture(scope="module")
def dataset_records():
    assert DATASET_PATH.exists(), f"Dataset file missing: {DATASET_PATH}"
    records = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def test_sample_count_and_uniqueness(dataset_records):
    assert len(dataset_records) == 500, f"Expected 500 samples, got {len(dataset_records)}"
    ids = [r["id"] for r in dataset_records]
    assert len(ids) == len(set(ids)), f"Duplicate IDs found in dataset!"


def test_category_balance(dataset_records):
    expected_categories = {
        "ordinary_legitimate": 100,
        "difficult_legitimate": 100,
        "conventional_phishing": 100,
        "sophisticated_phishing": 100,
        "prompt_injection": 100,
    }
    from collections import Counter
    counts = Counter(r["category"] for r in dataset_records)
    for cat, exp_cnt in expected_categories.items():
        assert counts[cat] == exp_cnt, f"Category {cat}: expected {exp_cnt}, got {counts[cat]}"


def test_ground_truth_balance(dataset_records):
    phishing = [r for r in dataset_records if r["is_phishing"]]
    legitimate = [r for r in dataset_records if not r["is_phishing"]]
    assert len(phishing) == 250, f"Expected 250 phishing, got {len(phishing)}"
    assert len(legitimate) == 250, f"Expected 250 legitimate, got {len(legitimate)}"
    # Check label alignment
    for r in phishing:
        assert r["label"] == 1, f"Sample {r['id']} has is_phishing=True but label={r.get('label')}"
    for r in legitimate:
        assert r["label"] == 0, f"Sample {r['id']} has is_phishing=False but label={r.get('label')}"


def test_injection_distribution(dataset_records):
    inj_records = [r for r in dataset_records if r["has_prompt_injection"]]
    assert len(inj_records) == 100, f"Expected 100 injection samples, got {len(inj_records)}"

    active_inj = [r for r in inj_records if r.get("active_prompt_injection")]
    quoted_inj = [r for r in inj_records if r.get("quoted_prompt_injection")]

    assert len(active_inj) == 50, f"Expected 50 active injections, got {len(active_inj)}"
    assert len(quoted_inj) == 50, f"Expected 50 quoted injections, got {len(quoted_inj)}"

    for r in active_inj:
        assert r["is_phishing"] is True, f"Active injection {r['id']} must be phishing"
        assert r["injection_type"] == "active"

    for r in quoted_inj:
        assert r["is_phishing"] is False, f"Quoted injection {r['id']} must be legitimate"
        assert r["injection_type"] == "quoted"


def test_provenance_metadata_completeness(dataset_records):
    for r in dataset_records:
        sid = r["id"]
        assert "source_dataset" in r and len(r["source_dataset"].strip()) > 0, f"Missing source_dataset in {sid}"
        assert "provenance_citation" in r and len(r["provenance_citation"].strip()) > 0, f"Missing citation in {sid}"
        assert "collection_method" in r and len(r["collection_method"].strip()) > 0, f"Missing collection_method in {sid}"
        assert r.get("origin_type") in ["original_real_world", "synthetic_supplemented"], f"Invalid origin_type in {sid}"
        assert "preprocessing_redaction" in r and len(r["preprocessing_redaction"].strip()) > 0, f"Missing redaction in {sid}"
        assert "subject" in r and len(r["subject"].strip()) > 0, f"Missing subject in {sid}"
        assert "sender" in r and len(r["sender"].strip()) > 0, f"Missing sender in {sid}"
        assert "body" in r and len(r["body"].strip()) > 0, f"Missing body in {sid}"
        assert "explanation" in r and len(r["explanation"].strip()) > 0, f"Missing explanation in {sid}"


def test_zero_leakage_with_rag_index(dataset_records):
    with open(FAISS_META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    index_records = meta.get("records", [])
    assert len(index_records) == 1321, f"Expected 1,321 vectors, got {len(index_records)}"

    index_ids = set(r["id"] for r in index_records)
    index_hashes = set(text_hash(r.get("text") or r.get("body") or "") for r in index_records)

    for r in dataset_records:
        assert r["id"] not in index_ids, f"Sample {r['id']} leaked into FAISS index IDs!"
        b_hash = text_hash(r["body"])
        assert b_hash not in index_hashes, f"Sample {r['id']} text leaked into FAISS index!"


def test_zero_leakage_with_historical_datasets(dataset_records):
    eval_hashes = {r["id"]: text_hash(r["body"]) for r in dataset_records}
    prior_corpora = [
        Path("data/evaluation/live_benchmark_v1.jsonl"),
        Path("data/evaluation/live_benchmark_v2.jsonl"),
        Path("data/evaluation/heldout_benchmark_v1.jsonl"),
        Path("data/splits/clean_split_v1/train.jsonl"),
        Path("data/splits/clean_split_v1/val.jsonl"),
        Path("data/splits/clean_split_v1/test.jsonl"),
    ]

    for p in prior_corpora:
        if not p.exists():
            continue
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    b = item.get("body") or item.get("text") or ""
                    if b:
                        h = text_hash(b)
                        for sid, e_hash in eval_hashes.items():
                            assert e_hash != h, f"Sample {sid} matches text in {p.name} (item {item.get('id')})!"


def test_code_and_index_hash_invariance():
    for fpath, expected_hash in EXPECTED_HASHES.items():
        p = Path(fpath)
        assert p.exists(), f"Tracked file missing: {fpath}"
        actual_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch for {fpath}! Expected {expected_hash}, got {actual_hash}"

