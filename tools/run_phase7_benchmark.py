"""Phase 7 Domain Evidence Precision Benchmark Runner.

Runs:
1. Config A (Frozen Phase 6 Config B):
   - 160 regression samples imported from Phase 6 Config B
   - 40 Phase 6 domain challenge samples imported from Phase 6 Config B
   - 40 Phase 7 precision challenge samples evaluated live with Domain Analyzer V2
2. Config B (Phase 7 Experimental with Domain Analyzer V3):
   - 160 regression samples evaluated live
   - 40 Phase 6 domain challenge samples evaluated live
   - 40 Phase 7 precision challenge samples evaluated live
3. Config C (Domain Evidence Disabled):
   - 40 Phase 7 precision challenge samples evaluated live
   - 40 Phase 6 domain challenge samples imported from Phase 6 Config C
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from experiments.phase7_domain_precision.engine_v4 import classify_email_phase7

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("phase7_benchmark")

BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results" / "phase7_domain_precision"
PREDICTIONS_PATH = RESULTS_DIR / "predictions.jsonl"
P6_PREDICTIONS_PATH = BASE_DIR / "results" / "phase6_domain_evidence" / "predictions.jsonl"

DATASETS = {
    "phase5_regression_160": BASE_DIR / "data" / "evaluation" / "phase5_regression_160.jsonl",
    "phase6_domain_challenge": BASE_DIR / "data" / "evaluation" / "phase6_domain_challenge.jsonl",
    "phase7_precision_challenge": BASE_DIR / "data" / "evaluation" / "phase7_precision_challenge.jsonl",
}


def load_dataset(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_existing_predictions() -> tuple[set[tuple[str, str]], list[dict]]:
    if not PREDICTIONS_PATH.is_file():
        return set(), []
    records = []
    seen = set()
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            key = (rec["config_id"], rec["sample_id"])
            seen.add(key)
            records.append(rec)
    return seen, records


def sync_historical_predictions(existing_seen: set[tuple[str, str]], out_file) -> int:
    """Sync Config A and Config C records from Phase 6 predictions."""
    if not P6_PREDICTIONS_PATH.is_file():
        logger.error("Phase 6 predictions not found at %s", P6_PREDICTIONS_PATH)
        return 0

    p6_records = []
    with open(P6_PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                p6_records.append(json.loads(line))

    synced_count = 0

    # Config A in Phase 7 is Frozen Phase 6 Config B
    for rec in p6_records:
        if rec.get("config_id") == "B":
            sample_id = rec["sample_id"]
            key = ("A", sample_id)
            if key not in existing_seen:
                new_rec = dict(rec)
                new_rec["config_id"] = "A"
                out_file.write(json.dumps(new_rec, ensure_ascii=False) + "\n")
                existing_seen.add(key)
                synced_count += 1

    # Config C in Phase 7 for phase6_domain_challenge
    for rec in p6_records:
        if rec.get("config_id") == "C":
            sample_id = rec["sample_id"]
            key = ("C", sample_id)
            if key not in existing_seen:
                new_rec = dict(rec)
                new_rec["config_id"] = "C"
                out_file.write(json.dumps(new_rec, ensure_ascii=False) + "\n")
                existing_seen.add(key)
                synced_count += 1

    out_file.flush()
    logger.info("Synced %d historical predictions from Phase 6", synced_count)
    return synced_count


def run_benchmark():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    seen_keys, _ = load_existing_predictions()
    logger.info("Starting Phase 7 benchmark. Existing predictions: %d", len(seen_keys))

    # Open output file in append mode
    with open(PREDICTIONS_PATH, "a", encoding="utf-8") as out_f:
        # Step 1: Sync historical predictions
        sync_historical_predictions(seen_keys, out_f)

        # Step 2: Load datasets
        dsets = {name: load_dataset(path) for name, path in DATASETS.items()}
        for name, data in dsets.items():
            logger.info("Loaded dataset '%s' with %d samples", name, len(data))

        # Define evaluation runs:
        # (config_id, dataset_name, sample_list)
        eval_runs = [
            ("A", "phase7_precision_challenge", dsets["phase7_precision_challenge"]),
            ("C", "phase7_precision_challenge", dsets["phase7_precision_challenge"]),
            ("B", "phase5_regression_160", dsets["phase5_regression_160"]),
            ("B", "phase6_domain_challenge", dsets["phase6_domain_challenge"]),
            ("B", "phase7_precision_challenge", dsets["phase7_precision_challenge"]),
        ]

        total_live_items = sum(
            1 for cid, dname, slist in eval_runs for s in slist if (cid, s["id"]) not in seen_keys
        )
        logger.info("Total remaining live inferences to execute: %d", total_live_items)

        completed = 0
        t_all_start = time.perf_counter()

        for config_id, dataset_name, sample_list in eval_runs:
            logger.info("Starting Config %s on %s (%d samples)...", config_id, dataset_name, len(sample_list))
            for idx, sample in enumerate(sample_list, 1):
                sample_id = sample["id"]
                key = (config_id, sample_id)
                if key in seen_keys:
                    continue

                subject = sample.get("subject", "")
                sender = sample.get("sender", "")
                body = sample.get("body", sample.get("text", ""))
                if "From:" in body and "Subject:" in body:
                    email_text = body
                else:
                    email_text = f"From: {sender}\nSubject: {subject}\n\n{body}".strip()

                category = sample.get("category", "")
                ground_truth = sample.get("label", "")
                if isinstance(ground_truth, int):
                    ground_truth = "phishing" if ground_truth == 1 else "legitimate"

                try:
                    result = classify_email_phase7(
                        email_text=email_text,
                        config_id=config_id,
                        subject=subject,
                        sender=sender,
                    )
                except Exception as exc:
                    logger.error("Error evaluating %s on sample %s: %s", config_id, sample_id, exc)
                    result = {
                        "config_id": config_id,
                        "is_phishing": False,
                        "phishing_verdict": "error",
                        "has_prompt_injection": False,
                        "active_prompt_injection": False,
                        "quoted_prompt_injection": False,
                        "injection_type": "none",
                        "injection_verdict": "error",
                        "security_action": "manual_review",
                        "verdict": "error",
                        "confidence": 0.0,
                        "reasons": [str(exc)],
                        "is_sanitized": False,
                        "domain_evidence_present": False,
                        "domain_telemetry": None,
                        "retrieved_exemplar_ids": [],
                        "retrieved_exemplar_labels": [],
                        "stage1_latency_ms": 0.0,
                        "stage2_latency_ms": 0.0,
                        "total_latency_ms": 0.0,
                        "is_valid": False,
                    }

                record = {
                    "config_id": config_id,
                    "sample_id": sample_id,
                    "dataset": dataset_name,
                    "category": category,
                    "ground_truth_label": ground_truth,
                    "is_phishing": result["is_phishing"],
                    "phishing_verdict": result["phishing_verdict"],
                    "has_prompt_injection": result["has_prompt_injection"],
                    "active_prompt_injection": result["active_prompt_injection"],
                    "quoted_prompt_injection": result["quoted_prompt_injection"],
                    "injection_type": result["injection_type"],
                    "injection_verdict": result["injection_verdict"],
                    "security_action": result["security_action"],
                    "verdict": result["verdict"],
                    "confidence": result["confidence"],
                    "reasons": result["reasons"],
                    "is_sanitized": result["is_sanitized"],
                    "domain_evidence_present": result["domain_evidence_present"],
                    "domain_telemetry": result.get("domain_telemetry"),
                    "stage1_latency_ms": result["stage1_latency_ms"],
                    "stage2_latency_ms": result["stage2_latency_ms"],
                    "total_latency_ms": result["total_latency_ms"],
                    "is_valid": result["is_valid"],
                }

                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                out_f.flush()
                seen_keys.add(key)
                completed += 1

                if completed % 10 == 0 or completed == total_live_items:
                    elapsed = time.perf_counter() - t_all_start
                    rate = completed / elapsed if elapsed > 0 else 0
                    rem = (total_live_items - completed) / rate if rate > 0 else 0
                    logger.info(
                        "Progress: %d/%d (%.1f%%) | Elapsed: %.1fs | Est. Remaining: %.1fs | Last: %s [%s] -> %s",
                        completed,
                        total_live_items,
                        (completed / total_live_items) * 100 if total_live_items else 100,
                        elapsed,
                        rem,
                        sample_id,
                        config_id,
                        result["verdict"],
                    )

    logger.info("Phase 7 benchmark evaluation finished successfully!")


if __name__ == "__main__":
    run_benchmark()

