"""Controlled Phase 5 Regression Benchmark Runner.

Evaluates:
- Baseline: Frozen A1 (from historical evaluation records for the 160 samples)
- Candidate: Optimized A1 (A1-Opt: Compact Stage 1 + Sanitizer V2)

Outputs:
- results/phase5_a1_sanitizer_latency/predictions.jsonl (320 records total)
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Setup paths
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.experiments.phase5_a1_optimization.engine_v2 import classify_email_a1_optimized

BENCHMARK_FILE = Path("data/evaluation/phase5_regression_160.jsonl")
HISTORICAL_PREDS_FILE = Path("results/a1_generalization_v1/predictions.jsonl")
OUT_DIR = Path("results/phase5_a1_sanitizer_latency")
OUT_PREDS_FILE = OUT_DIR / "predictions.jsonl"


def load_completed_keys(pred_file: Path) -> set[tuple[str, str]]:
    completed = set()
    if pred_file.exists():
        with open(pred_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    completed.add((row["config_id"], row["sample_id"]))
                except Exception:
                    pass
    return completed


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("PHASE 5: CONTROLLED REGRESSION BENCHMARK")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    # 1. Load benchmark dataset
    samples = []
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    print(f"Loaded {len(samples)} evaluation samples from {BENCHMARK_FILE}")

    completed_keys = load_completed_keys(OUT_PREDS_FILE)
    print(f"Already completed predictions in output file: {len(completed_keys)}")

    # 2. Write Frozen A1 historical baseline predictions for these 160 samples (if not already written)
    a1_hist_map = {}
    with open(HISTORICAL_PREDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if r.get("config_id") == "A1":
                    a1_hist_map[r["sample_id"]] = r

    a1_baseline_written = 0
    with open(OUT_PREDS_FILE, "a", encoding="utf-8") as out_f:
        for s in samples:
            sid = s["sample_id"]
            if ("A1", sid) not in completed_keys:
                if sid in a1_hist_map:
                    hist_row = a1_hist_map[sid]
                    # Ensure standard schema fields
                    hist_row["config_id"] = "A1"
                    hist_row["config_name"] = "Frozen A1 Baseline"
                    out_f.write(json.dumps(hist_row, ensure_ascii=False) + "\n")
                    out_f.flush()
                    completed_keys.add(("A1", sid))
                    a1_baseline_written += 1
                else:
                    print(f"Warning: Missing historical A1 record for {sid}")

    print(f"Frozen A1 records in output file: {len([k for k in completed_keys if k[0] == 'A1'])} (+{a1_baseline_written} newly synced)")

    # 3. Run Optimized A1 (A1-Opt)
    a1_opt_pending = [s for s in samples if ("A1-Opt", s["sample_id"]) not in completed_keys]
    print(f"Optimized A1 (A1-Opt) pending evaluations: {len(a1_opt_pending)} / {len(samples)}")

    if not a1_opt_pending:
        print("All A1-Opt predictions already completed.")
        return

    print("\nStarting sequential evaluation for A1-Opt...")
    t0_all = time.perf_counter()

    for idx, s in enumerate(a1_opt_pending, 1):
        sid = s["sample_id"]
        subj = s.get("subject", "")
        sender = s.get("sender", "")
        body = s.get("body", "")
        cat = s.get("category", "")
        subcat = s.get("subcategory", "")

        # Format full email text
        email_text = f"From: {sender}\nSubject: {subj}\n\n{body}"

        # Ground truth values
        gt_is_phish = bool(s.get("label", 0) == 1 or s.get("is_phishing", False) or s.get("ground_truth_is_phishing", False))
        gt_has_inj = bool(s.get("has_prompt_injection", False) or s.get("ground_truth_has_injection", False))
        gt_active_inj = bool(subcat.startswith("active_") or s.get("ground_truth_active_injection", False))
        gt_quoted_inj = bool(subcat.startswith("quoted_") or s.get("ground_truth_quoted_injection", False))

        t0_sample = time.perf_counter()
        pred = classify_email_a1_optimized(
            email_text=email_text,
            subject=subj,
            sender=sender,
        )
        sample_wall_ms = round((time.perf_counter() - t0_sample) * 1000, 2)

        record = {
            "config_id": "A1-Opt",
            "configuration_id": "A1-Opt",
            "config_name": "A1 Optimized (Compact Stage 1 + Sanitizer V2)",
            "dataset": "phase5_regression_160",
            "sample_id": sid,
            "subject": subj,
            "sender": sender,
            "category": cat,
            "subcategory": subcat,
            "origin_type": s.get("origin_type", "synthetic"),
            "source_dataset": s.get("source_dataset", "a1_generalization_v1"),
            "ground_truth_is_phishing": gt_is_phish,
            "ground_truth_has_injection": gt_has_inj,
            "ground_truth_active_injection": gt_active_inj,
            "ground_truth_quoted_injection": gt_quoted_inj,
            "ground_truth_injection_type": "active" if gt_active_inj else ("quoted" if gt_quoted_inj else "none"),
            "is_phishing": pred["is_phishing"],
            "phishing_verdict": pred["phishing_verdict"],
            "has_prompt_injection": pred["has_prompt_injection"],
            "active_prompt_injection": pred["active_prompt_injection"],
            "quoted_prompt_injection": pred["quoted_prompt_injection"],
            "injection_verdict": pred["injection_verdict"],
            "injection_type": pred["injection_type"],
            "security_action": pred["security_action"],
            "confidence": pred["confidence"],
            "reasons": pred["reasons"],
            "is_valid": pred["is_valid"],
            "failure_type": pred.get("failure_type"),
            "failure_message": pred.get("failure_message"),
            "is_sanitized": pred.get("is_sanitized", False),
            "match_method": pred.get("sanitization_info", {}).get("match_method", "none"),
            "sanitization_info": pred.get("sanitization_info"),
            "stage1_latency_ms": pred.get("stage1_latency_ms", 0.0),
            "stage2_latency_ms": pred.get("stage2_latency_ms", 0.0),
            "total_latency_ms": pred.get("total_latency_ms", 0.0),
            "wall_clock_ms": sample_wall_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        with open(OUT_PREDS_FILE, "a", encoding="utf-8") as out_f:
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()

        completed_keys.add(("A1-Opt", sid))

        print(
            f"[{idx:03d}/{len(a1_opt_pending):03d}] {sid} ({subcat}) | "
            f"Pred Phish: {record['is_phishing']} (GT: {gt_is_phish}) | "
            f"Inj: {record['injection_type']} | "
            f"Sanitized: {record['is_sanitized']} ({record['match_method']}) | "
            f"Action: {record['security_action']} | "
            f"S1: {record['stage1_latency_ms']:.0f}ms | Tot: {record['total_latency_ms']:.0f}ms"
        )

    elapsed_all = time.perf_counter() - t0_all
    print(f"\nA1-Opt evaluation complete! Processed {len(a1_opt_pending)} samples in {elapsed_all:.1f}s ({elapsed_all/len(a1_opt_pending):.2f}s/sample).")


if __name__ == "__main__":
    main()

