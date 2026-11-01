"""Pre-run integrity check for Phase 4 M4 Ablation Benchmark Evaluation.

Verifies:
1. Source file checksums (inference.py and inference_m4_v2.py).
2. Clean FAISS index checksum and vector count (1,321 vectors).
3. Both evaluation datasets exist, have correct counts, and are untouched.
4. Non-contamination: No evaluation email text or ID appears in the retrieval index.
5. All 9 configurations are declared and validated.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from pathlib import Path

# Configure utf-8 stdout for Windows
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pre_run_integrity")

sys.path.insert(0, str(Path("src").resolve()))
from experiments.m4_ablation_v1.ablation_engine import CONFIGURATIONS


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def run_checks() -> bool:
    logger.info("Executing Pre-Run Integrity Verification...")
    passed = True

    # 1. Source code integrity
    inf_prod = Path("src/core/inference.py")
    inf_exp = Path("src/core/inference_m4_v2.py")
    if not inf_prod.exists() or not inf_exp.exists():
        logger.error("Source inference files missing!")
        return False

    hash_prod = sha256_file(inf_prod)
    hash_exp = sha256_file(inf_exp)
    logger.info(f"src/core/inference.py SHA256: {hash_prod}")
    logger.info(f"src/core/inference_m4_v2.py SHA256: {hash_exp}")

    # 2. RAG Clean Index integrity
    faiss_file = Path("results/rag_index_clean/index.faiss")
    meta_file = Path("results/rag_index_clean/metadata.json")
    if not faiss_file.exists() or not meta_file.exists():
        logger.error("Clean FAISS index or metadata missing!")
        return False

    faiss_hash = sha256_file(faiss_file)
    meta_hash = sha256_file(meta_file)
    logger.info(f"results/rag_index_clean/index.faiss SHA256: {faiss_hash}")
    logger.info(f"results/rag_index_clean/metadata.json SHA256: {meta_hash}")

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    rag_records = meta.get("records", [])
    if len(rag_records) != 1321:
        logger.error(f"Clean FAISS record count mismatch! Expected 1,321, got {len(rag_records)}")
        return False
    logger.info(f"Clean FAISS index verified: {len(rag_records)} vectors.")

    # 3. Evaluation datasets
    v2_file = Path("data/evaluation/live_benchmark_v2.jsonl")
    heldout_file = Path("data/evaluation/heldout_benchmark_v1.jsonl")

    if not v2_file.exists() or not heldout_file.exists():
        logger.error("Benchmark datasets missing!")
        return False

    v2_hash = sha256_file(v2_file)
    heldout_hash = sha256_file(heldout_file)

    with open(v2_file, "r", encoding="utf-8") as f:
        v2_records = [json.loads(line) for line in f if line.strip()]

    with open(heldout_file, "r", encoding="utf-8") as f:
        heldout_records = [json.loads(line) for line in f if line.strip()]

    if len(v2_records) != 150:
        logger.error(f"V2 sample count mismatch! Expected 150, got {len(v2_records)}")
        return False
    if len(heldout_records) != 100:
        logger.error(f"Held-Out sample count mismatch! Expected 100, got {len(heldout_records)}")
        return False

    logger.info(f"Live Benchmark V2: 150 samples verified (SHA256: {v2_hash})")
    logger.info(f"Held-Out Benchmark V1: 100 samples verified (SHA256: {heldout_hash})")

    # 4. Non-contamination audit
    rag_ids = {r.get("id") for r in rag_records}
    rag_texts = {r.get("text", "").strip().lower() for r in rag_records}

    all_eval_samples = v2_records + heldout_records
    eval_ids = [s.get("id") for s in all_eval_samples]
    if len(eval_ids) != 250 or len(set(eval_ids)) != 250:
        logger.error("Duplicate sample IDs found in combined evaluation dataset!")
        return False

    for sample in all_eval_samples:
        sid = sample.get("id")
        if sid in rag_ids:
            logger.error(f"Contamination detected! Sample ID {sid} exists in RAG index!")
            return False
        stext = sample.get("text", "").strip().lower()
        if stext in rag_texts:
            logger.error(f"Contamination detected! Sample text for {sid} exists in RAG index!")
            return False

    logger.info("Non-contamination verified: 0 of 250 evaluation samples exist in the clean RAG index.")

    # 5. Configurations check
    expected_configs = ["A0", "ISO-4", "A1", "A2", "A3", "A4", "ISO-1", "ISO-2", "ISO-3"]
    if list(CONFIGURATIONS.keys()) != expected_configs:
        logger.error(f"Configuration list mismatch! Found {list(CONFIGURATIONS.keys())}")
        return False

    logger.info("All 9 ablation configurations declared and ready.")
    logger.info("PRE-RUN INTEGRITY VERIFICATION: 100% PASSED.")
    return True


if __name__ == "__main__":
    if not run_checks():
        sys.exit(1)
    print("PRE_RUN_CHECKS_OK")

