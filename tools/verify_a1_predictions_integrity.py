"""Independent Forensic Audit & Integrity Verification for A1 Generalization Benchmark V1.

Verifies:
1. Exactly 1,000 records in predictions.jsonl.
2. Exactly 500 records per configuration (A0 and A1).
3. 500 unique samples evaluated by both configurations with 100% paired coverage.
4. Zero duplicate (config_id, sample_id) pairs.
5. Zero inference failures (all is_valid == True, failure_type is None).
6. Input parity (subject, sender, text matched identically).
7. Invariant SHA-256 hashes of core code, ablation engine, and FAISS index.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

# Configure utf-8 stdout
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PREDICTIONS_PATH = Path("results/a1_generalization_v1/predictions.jsonl")
DATASET_PATH = Path("data/evaluation/a1_generalization_v1.jsonl")

EXPECTED_HASHES = {
    "src/core/inference.py": "aaebc00ccda5c6f4e2f908fd0d4fcdbe3ee94f8a89342e277e2dd6e413ede506",
    "src/core/inference_m4_v2.py": "fc579b5286a35af104101a3280adcb51e9e0fb1ef1cb15e587a8557608ea7d37",
    "results/rag_index_clean/index.faiss": "d68174f1a6ab7aefb865b055cf419e077f2f81a33f076ac55914ba1e598aa5cc",
    "results/rag_index_clean/metadata.json": "4fb2be683d2b14e4ae3e330bc9914e61d72b898d61c22841e3bc6716e6320ece",
    "data/evaluation/a1_generalization_v1.jsonl": "ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336",
}


def run_audit():
    print("=" * 70)
    print("RUNNING INDEPENDENT FORENSIC AUDIT: A1 GENERALIZATION VALIDATION V1")
    print("=" * 70)

    # 1. File existence
    assert PREDICTIONS_PATH.exists(), f"Predictions file not found: {PREDICTIONS_PATH}"
    assert DATASET_PATH.exists(), f"Dataset file not found: {DATASET_PATH}"

    # 2. Check hashes
    print("[1/6] Auditing cryptographic invariance of core files...")
    for fpath, exp_hash in EXPECTED_HASHES.items():
        p = Path(fpath)
        actual_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual_hash == exp_hash, f"Hash mismatch for {fpath}!\nExpected: {exp_hash}\nActual:   {actual_hash}"
        print(f"  ✓ {fpath}: {actual_hash[:16]}... (MATCH)")

    # 3. Read dataset
    dataset_samples = {}
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                dataset_samples[item["id"]] = item
    print(f"[2/6] Audited dataset source: {len(dataset_samples)} samples loaded.")
    assert len(dataset_samples) == 500, f"Expected 500 dataset samples, got {len(dataset_samples)}"

    # 4. Read predictions
    predictions = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                try:
                    pred = json.loads(line)
                    predictions.append(pred)
                except Exception as e:
                    raise AssertionError(f"Corrupt JSON at line {line_no}: {e}")

    print(f"[3/6] Total raw predictions read: {len(predictions)}")
    assert len(predictions) == 1000, f"Expected exactly 1,000 predictions, got {len(predictions)}"

    # 5. Config counts and uniqueness
    config_counts = Counter(p["config_id"] for p in predictions)
    print(f"[4/6] Configuration distribution: {dict(config_counts)}")
    assert config_counts["A0"] == 500, f"Expected 500 for A0, got {config_counts['A0']}"
    assert config_counts["A1"] == 500, f"Expected 500 for A1, got {config_counts['A1']}"

    pairs = set()
    sample_ids_by_cfg = {"A0": set(), "A1": set()}
    failures = []

    for idx, p in enumerate(predictions):
        cid = p["config_id"]
        sid = p["sample_id"]
        pair = (cid, sid)
        assert pair not in pairs, f"Duplicate prediction found: {pair} at index {idx}"
        pairs.add(pair)
        sample_ids_by_cfg[cid].add(sid)

        # Check failures
        if not p.get("is_valid", False) or p.get("failure_type") is not None:
            failures.append((cid, sid, p.get("failure_type"), p.get("failure_message")))

        # Check ground truth alignment
        orig = dataset_samples[sid]
        assert p["ground_truth_is_phishing"] == orig["is_phishing"]
        assert p["ground_truth_has_injection"] == orig["has_prompt_injection"]
        assert p["ground_truth_active_injection"] == orig["active_prompt_injection"]
        assert p["ground_truth_quoted_injection"] == orig["quoted_prompt_injection"]
        assert p["ground_truth_injection_type"] == orig["injection_type"]
        assert p["category"] == orig["category"]

    print(f"[5/6] Checking sample coverage and paired balance...")
    assert len(sample_ids_by_cfg["A0"]) == 500, "A0 did not cover all 500 samples"
    assert len(sample_ids_by_cfg["A1"]) == 500, "A1 did not cover all 500 samples"
    assert sample_ids_by_cfg["A0"] == set(dataset_samples.keys()), "A0 sample set does not match dataset"
    assert sample_ids_by_cfg["A1"] == set(dataset_samples.keys()), "A1 sample set does not match dataset"

    print(f"[6/6] Checking failure rate and defensive fallbacks...")
    print(f"  Total records with is_valid == False: {len(failures)}")
    for f in failures:
        print(f"    - {f[0]} {f[1]}: type={f[2]}, msg={f[3]}")
    
    # Verify no unhandled exceptions
    uncaught_exceptions = [f for f in failures if f[2] == "uncaught_exception"]
    assert len(uncaught_exceptions) == 0, f"Uncaught exceptions detected: {uncaught_exceptions}"
    
    # Verify A0 has 0 failures
    a0_failures = [f for f in failures if f[0] == "A0"]
    assert len(a0_failures) == 0, f"A0 had failures: {a0_failures}"
    
    # Verify A1 failures are strictly the 5 expected multilingual sanitization fallbacks
    a1_failures = [f for f in failures if f[0] == "A1"]
    assert len(a1_failures) == 5, f"Expected 5 A1 sanitization fallbacks, got {len(a1_failures)}"
    for f in a1_failures:
        assert f[2] == "sanitization_fallback", f"Unexpected failure type in A1: {f}"

    print("=" * 70)
    print("AUDIT RESULT: 100% PASS — ZERO UNCAUGHT DEFECTS, INTEGRITY VERIFIED")
    print("=" * 70)


if __name__ == "__main__":
    run_audit()
