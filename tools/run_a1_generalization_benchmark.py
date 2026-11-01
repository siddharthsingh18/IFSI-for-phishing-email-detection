"""A1 Generalization Validation V1: Controlled A0 vs. A1 Evaluation Runner.

Evaluates two frozen configurations (A0 and A1) across 500 synthetic challenge samples
(total 1,000 predictions). Runs sequentially, checkpoints progress after each prediction,
and supports safe resume without duplicates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from pathlib import Path

# Configure utf-8 stdout for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
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
logger = logging.getLogger("a1_generalization_runner")

sys.path.insert(0, str(Path("src").resolve()))
from experiments.m4_ablation_v1.ablation_engine import (
    CONFIGURATIONS,
    classify_email_ablation,
)

EXPECTED_DATASET_SHA256 = "ab602982e7406d700a23e075b5c820a3bf70f02ec8b7cda10e9b05340cbc1336"
DATASET_PATH = Path("data/evaluation/a1_generalization_v1.jsonl")
OUT_DIR = Path("results/a1_generalization_v1")
PREDICTIONS_PATH = OUT_DIR / "predictions.jsonl"
PROGRESS_PATH = OUT_DIR / "evaluation_progress.json"

CONFIG_ORDER = ["A0", "A1"]


def verify_dataset_sha256() -> None:
    """Verifies that data/evaluation/a1_generalization_v1.jsonl is authentic and untampered."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at: {DATASET_PATH}")
    hasher = hashlib.sha256()
    with open(DATASET_PATH, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest()
    if actual_hash != EXPECTED_DATASET_SHA256:
        raise ValueError(
            f"Dataset SHA-256 mismatch!\nExpected: {EXPECTED_DATASET_SHA256}\nActual:   {actual_hash}"
        )
    logger.info(f"Verified dataset integrity: {DATASET_PATH} (SHA-256: {actual_hash})")


def load_dataset() -> list[dict]:
    """Loads all 500 samples from the benchmark dataset."""
    samples = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            samples.append(item)
    logger.info(f"Loaded {len(samples)} samples from {DATASET_PATH}")
    return samples


def load_existing_progress() -> tuple[set[tuple[str, str]], dict[str, int]]:
    """Loads already recorded (config_id, sample_id) pairs to support safe resumption."""
    completed_pairs = set()
    config_counts = {cid: 0 for cid in CONFIG_ORDER}

    if PREDICTIONS_PATH.exists():
        with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
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
                    logger.warning(f"Error parsing existing prediction line: {e}")

    logger.info(
        f"Resume state: {len(completed_pairs)} completed predictions found. "
        f"A0: {config_counts.get('A0', 0)}, A1: {config_counts.get('A1', 0)}"
    )
    return completed_pairs, config_counts


def write_progress(
    completed_count: int,
    total_expected: int,
    current_config: str,
    config_counts: dict[str, int],
    t0: float,
) -> None:
    """Updates evaluation_progress.json with live statistics and ETA."""
    now = time.time()
    elapsed = now - t0
    rate = completed_count / elapsed if elapsed > 0 else 0
    rem_count = total_expected - completed_count
    eta_sec = rem_count / rate if rate > 0 else 0

    progress_data = {
        "total_expected": total_expected,
        "completed_count": completed_count,
        "percent_complete": round((completed_count / total_expected) * 100, 2) if total_expected > 0 else 0.0,
        "current_config": current_config,
        "config_counts": config_counts,
        "elapsed_seconds": round(elapsed, 1),
        "estimated_remaining_seconds": round(eta_sec, 1),
        "estimated_remaining_minutes": round(eta_sec / 60, 1),
        "rate_predictions_per_sec": round(rate, 3),
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    PROGRESS_PATH.write_text(json.dumps(progress_data, indent=2), encoding="utf-8")


def run_benchmark(target_configs: list[str] | None = None, limit_per_config: int | None = None) -> None:
    """Main execution loop for A0 and A1 benchmark inference."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    verify_dataset_sha256()

    configs_to_run = target_configs or CONFIG_ORDER
    for cid in configs_to_run:
        if cid not in CONFIGURATIONS:
            raise KeyError(f"Configuration '{cid}' not found in registry.")

    samples = load_dataset()
    if limit_per_config:
        samples = samples[:limit_per_config]

    total_expected = len(configs_to_run) * len(samples)
    completed_pairs, config_counts = load_existing_progress()

    logger.info(
        f"Total benchmark workload: {total_expected} predictions across {len(configs_to_run)} configurations "
        f"({len(completed_pairs)} already completed)."
    )

    t0 = time.time()
    # Adjust t0 if resuming to avoid skewed ETA
    completed_before_run = len(completed_pairs)

    with open(PREDICTIONS_PATH, "a", encoding="utf-8") as out_f:
        for cid in configs_to_run:
            config = CONFIGURATIONS[cid]
            logger.info("=" * 70)
            logger.info(f"STARTING CONFIGURATION: {cid} ({config.name})")
            logger.info(f"Config Description: {config.description}")
            logger.info(f"Current Progress for {cid}: {config_counts[cid]} / {len(samples)}")
            logger.info("=" * 70)

            for idx, sample in enumerate(samples, 1):
                sid = sample["id"]
                pair = (cid, sid)
                if pair in completed_pairs:
                    continue

                t_start = time.time()
                try:
                    result = classify_email_ablation(
                        email_text=sample["body"],
                        config=config,
                        subject=sample.get("subject", ""),
                        sender=sample.get("sender", ""),
                    )
                    wall_ms = round((time.time() - t_start) * 1000, 1)

                    prediction_record = {
                        "config_id": cid,
                        "configuration_id": cid,
                        "config_name": config.name,
                        "dataset": "a1_generalization_v1",
                        "sample_id": sid,
                        "subject": sample.get("subject", ""),
                        "sender": sample.get("sender", ""),
                        "category": sample.get("category", "unknown"),
                        "subcategory": sample.get("subcategory", "unknown"),
                        "origin_type": sample.get("origin_type", "unknown"),
                        "source_dataset": sample.get("source_dataset", "unknown"),
                        "ground_truth_is_phishing": sample.get("is_phishing", False),
                        "ground_truth_has_injection": sample.get("has_prompt_injection", False),
                        "ground_truth_active_injection": sample.get("active_prompt_injection", False),
                        "ground_truth_quoted_injection": sample.get("quoted_prompt_injection", False),
                        "ground_truth_injection_type": sample.get("injection_type", "none"),
                        # Inferred verdicts & telemetry
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
                        "is_sanitized": result.get("is_sanitized", False),
                        "domain_evidence_present": result.get("domain_evidence_present", False),
                        "rag_mode": result.get("rag_mode", "standard"),
                        "retrieved_exemplar_ids": result.get("retrieved_exemplar_ids", []),
                        "retrieved_exemplar_labels": result.get("retrieved_exemplar_labels", []),
                        "stage1_latency_ms": result.get("stage1_latency_ms", 0.0),
                        "stage2_latency_ms": result.get("stage2_latency_ms", 0.0),
                        "total_latency_ms": result.get("total_latency_ms", 0.0),
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
                        "dataset": "a1_generalization_v1",
                        "sample_id": sid,
                        "subject": sample.get("subject", ""),
                        "sender": sample.get("sender", ""),
                        "category": sample.get("category", "unknown"),
                        "subcategory": sample.get("subcategory", "unknown"),
                        "origin_type": sample.get("origin_type", "unknown"),
                        "source_dataset": sample.get("source_dataset", "unknown"),
                        "ground_truth_is_phishing": sample.get("is_phishing", False),
                        "ground_truth_has_injection": sample.get("has_prompt_injection", False),
                        "ground_truth_active_injection": sample.get("active_prompt_injection", False),
                        "ground_truth_quoted_injection": sample.get("quoted_prompt_injection", False),
                        "ground_truth_injection_type": sample.get("injection_type", "none"),
                        "is_phishing": False,
                        "phishing_verdict": "unknown",
                        "has_prompt_injection": False,
                        "active_prompt_injection": False,
                        "quoted_prompt_injection": False,
                        "injection_verdict": "unknown",
                        "injection_type": "none",
                        "security_action": "manual_review",
                        "confidence": 0.0,
                        "reasons": [f"Uncaught exception during pipeline execution: {str(e)}"],
                        "is_valid": False,
                        "failure_type": "uncaught_exception",
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

                # Write immediately and flush
                out_f.write(json.dumps(prediction_record, ensure_ascii=False) + "\n")
                out_f.flush()

                completed_pairs.add(pair)
                config_counts[cid] += 1

                # Progress updates
                current_total_done = len(completed_pairs)
                if current_total_done % 10 == 0 or idx == len(samples):
                    run_done = current_total_done - completed_before_run
                    run_elapsed = time.time() - t0
                    cur_rate = run_done / run_elapsed if run_elapsed > 0 else 0
                    rem = total_expected - current_total_done
                    eta_min = (rem / cur_rate) / 60.0 if cur_rate > 0 else 0.0

                    logger.info(
                        f"[{cid}] Sample {idx:3d}/{len(samples)} ({sid}) | "
                        f"Overall: {current_total_done}/{total_expected} ({current_total_done/total_expected*100:.1f}%) | "
                        f"Rate: {cur_rate:.2f} it/s | ETA: {eta_min:.1f} min | "
                        f"Verdict: {prediction_record['phishing_verdict']} | "
                        f"Action: {prediction_record['security_action']} | "
                        f"Latency: {wall_ms:.0f}ms"
                    )

                write_progress(current_total_done, total_expected, cid, config_counts, t0)

    logger.info("=" * 70)
    logger.info("ALL BENCHMARK INFERENCE COMPLETED SUCCESSFULLY!")
    logger.info(f"Final Count: {len(completed_pairs)} / {total_expected}")
    logger.info(f"Predictions stored at: {PREDICTIONS_PATH}")
    logger.info("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A1 Generalization Validation Benchmark Runner")
    parser.add_argument("--configs", nargs="+", default=CONFIG_ORDER, help="Configurations to evaluate (e.g. A0 A1)")
    parser.add_argument("--limit", type=int, default=None, help="Limit samples per configuration (for testing)")
    args = parser.parse_args()

    run_benchmark(target_configs=args.configs, limit_per_config=args.limit)
