"""Phase 4: Controlled M4 Ablation Benchmark Evaluation Runner.

Evaluates 9 configurations across 250 emails (150 V2 + 100 Held-Out = 2,250 total predictions).
Sequential execution, persistent JSONL checkpointing, live progress tracking, and full schema capture.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

# Configure utf-8 stdout for Windows
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("ablation_benchmark_runner")

sys.path.insert(0, str(Path("src").resolve()))
from experiments.m4_ablation_v1.ablation_engine import (
    CONFIGURATIONS,
    classify_email_ablation,
)

CONFIG_ORDER = ["A0", "ISO-4", "A1", "A2", "A3", "A4", "ISO-1", "ISO-2", "ISO-3"]
V2_PATH = Path("data/evaluation/live_benchmark_v2.jsonl")
HELDOUT_PATH = Path("data/evaluation/heldout_benchmark_v1.jsonl")
OUT_DIR = Path("results/m4_ablation_v1")
PREDICTIONS_PATH = OUT_DIR / "predictions.jsonl"
PROGRESS_PATH = OUT_DIR / "evaluation_progress.json"


def load_datasets() -> list[dict]:
    """Loads and standardizes V2 and Held-Out samples into a unified list."""
    samples = []

    # 1. Load V2 (150 samples)
    with open(V2_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            # Ensure ground truth fields
            is_phish = bool(item.get("label", 0) == 1 or item.get("is_phishing", False))
            has_inj = bool(item.get("has_prompt_injection", False))
            active_inj = bool(item.get("active_prompt_injection", False))
            quoted_inj = bool(item.get("quoted_prompt_injection", False))
            inj_type = item.get("injection_type", "active" if has_inj else "none")

            samples.append({
                "dataset": "v2",
                "sample_id": item["id"],
                "subject": item.get("subject", ""),
                "sender": item.get("sender", ""),
                "body": item.get("text", item.get("body", "")),
                "category": item.get("category", "unknown"),
                "difficulty": item.get("difficulty", "unknown"),
                "ground_truth_is_phishing": is_phish,
                "ground_truth_has_injection": has_inj,
                "ground_truth_active_injection": active_inj,
                "ground_truth_quoted_injection": quoted_inj,
                "ground_truth_injection_type": inj_type,
            })

    # 2. Load Held-Out (100 samples)
    with open(HELDOUT_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            is_phish = bool(item.get("label", 0) == 1 or item.get("is_phishing", False))
            has_inj = bool(item.get("has_prompt_injection", False))
            active_inj = bool(item.get("active_prompt_injection", False))
            quoted_inj = bool(item.get("quoted_prompt_injection", False))
            inj_type = item.get("injection_type", "active" if has_inj else "none")

            samples.append({
                "dataset": "heldout",
                "sample_id": item["id"],
                "subject": item.get("subject", ""),
                "sender": item.get("sender", ""),
                "body": item.get("text", item.get("body", "")),
                "category": item.get("category", "unknown"),
                "difficulty": item.get("difficulty", "unknown"),
                "ground_truth_is_phishing": is_phish,
                "ground_truth_has_injection": has_inj,
                "ground_truth_active_injection": active_inj,
                "ground_truth_quoted_injection": quoted_inj,
                "ground_truth_injection_type": inj_type,
            })

    logger.info(f"Loaded {len(samples)} total evaluation samples (150 V2 + 100 Held-Out).")
    return samples


def load_existing_progress() -> tuple[set[tuple[str, str]], dict[str, int]]:
    """Loads existing predictions from disk for seamless resume without duplicates."""
    completed_pairs = set()
    config_counts = {cid: 0 for cid in CONFIG_ORDER}

    if PREDICTIONS_PATH.exists():
        with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    cid = record.get("config_id") or record.get("configuration_id")
                    sid = record.get("sample_id")
                    if cid and sid:
                        pair = (cid, sid)
                        if pair not in completed_pairs:
                            completed_pairs.add(pair)
                            if cid in config_counts:
                                config_counts[cid] += 1
                except Exception as e:
                    logger.warning(f"Failed to parse existing prediction line: {e}")

    logger.info(f"Resume state: {len(completed_pairs)} already completed predictions found.")
    return completed_pairs, config_counts


def write_progress(completed_count: int, total_expected: int, current_config: str, config_counts: dict[str, int], t0: float):
    now = time.time()
    elapsed = now - t0
    rate = completed_count / elapsed if elapsed > 0 else 0
    rem_count = total_expected - completed_count
    eta_sec = rem_count / rate if rate > 0 else 0

    progress_data = {
        "total_expected": total_expected,
        "completed_count": completed_count,
        "percent_complete": round((completed_count / total_expected) * 100, 2),
        "current_config": current_config,
        "config_counts": config_counts,
        "elapsed_seconds": round(elapsed, 1),
        "estimated_remaining_seconds": round(eta_sec, 1),
        "estimated_remaining_minutes": round(eta_sec / 60, 1),
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    PROGRESS_PATH.write_text(json.dumps(progress_data, indent=2), encoding="utf-8")


def run_ablation_benchmark():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    samples = load_datasets()
    total_expected = len(CONFIG_ORDER) * len(samples)  # 9 * 250 = 2250
    completed_pairs, config_counts = load_existing_progress()

    logger.info(f"Total benchmark workload: {total_expected} predictions across {len(CONFIG_ORDER)} configurations.")

    t0 = time.time()
    total_completed = len(completed_pairs)

    with open(PREDICTIONS_PATH, "a", encoding="utf-8") as out_f:
        for cid in CONFIG_ORDER:
            config = CONFIGURATIONS[cid]
            logger.info(f"============================================================")
            logger.info(f"STARTING CONFIGURATION: {cid} ({config.name})")
            logger.info(f"Current Config Progress: {config_counts[cid]} / {len(samples)}")
            logger.info(f"============================================================")

            for idx, sample in enumerate(samples, 1):
                pair = (cid, sample["sample_id"])
                if pair in completed_pairs:
                    continue

                t_start = time.time()
                sid = sample["sample_id"]

                try:
                    result = classify_email_ablation(
                        email_text=sample["body"],
                        config=config,
                        subject=sample["subject"],
                        sender=sample["sender"],
                    )
                    wall_ms = round((time.time() - t_start) * 1000, 1)

                    prediction_record = {
                        "config_id": cid,
                        "configuration_id": cid,
                        "config_name": config.name,
                        "dataset": sample["dataset"],
                        "sample_id": sid,
                        "subject": sample["subject"],
                        "sender": sample["sender"],
                        "category": sample["category"],
                        "difficulty": sample["difficulty"],
                        "ground_truth_is_phishing": sample["ground_truth_is_phishing"],
                        "ground_truth_has_injection": sample["ground_truth_has_injection"],
                        "ground_truth_active_injection": sample["ground_truth_active_injection"],
                        "ground_truth_quoted_injection": sample["ground_truth_quoted_injection"],
                        "ground_truth_injection_type": sample["ground_truth_injection_type"],
                        # Inferred fields
                        "is_phishing": result["is_phishing"],
                        "phishing_verdict": result["phishing_verdict"],
                        "has_prompt_injection": result["has_prompt_injection"],
                        "active_prompt_injection": result["active_prompt_injection"],
                        "quoted_prompt_injection": result["quoted_prompt_injection"],
                        "injection_verdict": result["injection_verdict"],
                        "injection_type": result.get("injection_type", "none"),
                        "security_action": result["security_action"],
                        "confidence": result["confidence"],
                        "reasons": result.get("reasons", []),
                        "is_valid": result.get("is_valid", True),
                        "failure_type": result.get("failure_type"),
                        "failure_message": result.get("failure_message"),
                        "is_sanitized": result["is_sanitized"],
                        "domain_evidence_present": result["domain_evidence_present"],
                        "rag_mode": result["rag_mode"],
                        "retrieved_exemplar_ids": result["retrieved_exemplar_ids"],
                        "retrieved_exemplar_labels": result.get("retrieved_exemplar_labels", []),
                        "stage1_latency_ms": result["stage1_latency_ms"],
                        "stage2_latency_ms": result["stage2_latency_ms"],
                        "total_latency_ms": result["total_latency_ms"],
                        "wall_clock_ms": wall_ms,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }

                except Exception as e:
                    logger.error(f"Inference exception on {cid} / {sid}: {e}", exc_info=True)
                    wall_ms = round((time.time() - t_start) * 1000, 1)
                    prediction_record = {
                        "config_id": cid,
                        "configuration_id": cid,
                        "config_name": config.name,
                        "dataset": sample["dataset"],
                        "sample_id": sid,
                        "subject": sample["subject"],
                        "sender": sample["sender"],
                        "category": sample["category"],
                        "difficulty": sample["difficulty"],
                        "ground_truth_is_phishing": sample["ground_truth_is_phishing"],
                        "ground_truth_has_injection": sample["ground_truth_has_injection"],
                        "ground_truth_active_injection": sample["ground_truth_active_injection"],
                        "ground_truth_quoted_injection": sample["ground_truth_quoted_injection"],
                        "ground_truth_injection_type": sample["ground_truth_injection_type"],
                        "is_phishing": False,
                        "phishing_verdict": "error",
                        "has_prompt_injection": False,
                        "active_prompt_injection": False,
                        "quoted_prompt_injection": False,
                        "injection_verdict": "error",
                        "injection_type": "error",
                        "security_action": "manual_review",
                        "confidence": 0.0,
                        "reasons": [f"Pipeline unhandled exception: {str(e)}"],
                        "is_valid": False,
                        "failure_type": "exception",
                        "failure_message": str(e),
                        "is_sanitized": False,
                        "domain_evidence_present": False,
                        "rag_mode": config.rag_mode,
                        "retrieved_exemplar_ids": [],
                        "retrieved_exemplar_labels": [],
                        "stage1_latency_ms": 0.0,
                        "stage2_latency_ms": 0.0,
                        "total_latency_ms": wall_ms,
                        "wall_clock_ms": wall_ms,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }

                out_f.write(json.dumps(prediction_record) + "\n")
                out_f.flush()

                completed_pairs.add(pair)
                config_counts[cid] += 1
                total_completed += 1

                if total_completed % 10 == 0 or idx == len(samples):
                    write_progress(total_completed, total_expected, cid, config_counts, t0)
                    logger.info(
                        f"[{cid}] Sample {idx}/{len(samples)} ({sid}) | "
                        f"Total: {total_completed}/{total_expected} ({round(total_completed/total_expected*100, 1)}%) | "
                        f"Phish: {prediction_record['is_phishing']} | Action: {prediction_record['security_action']} | "
                        f"Latency: {round(prediction_record['total_latency_ms'])}ms"
                    )

            logger.info(f"COMPLETED CONFIGURATION: {cid} ({config_counts[cid]} / {len(samples)} samples)")

    logger.info("============================================================")
    logger.info(f"ALL 2,250 BENCHMARK PREDICTIONS SUCCESSFULLY COMPLETED!")
    logger.info("============================================================")
    write_progress(total_completed, total_expected, "DONE", config_counts, t0)


if __name__ == "__main__":
    run_ablation_benchmark()

