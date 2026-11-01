"""Controlled Benchmark Runner for Phase 6: A1-Opt Domain Evidence Integration Study.

Evaluates:
- Config A: A1-Opt Baseline (Compact Stage 1 + Sanitizer V2 + Frozen Stage 2 + Standard RAG, NO Domain Evidence)
- Config B: A1-Opt + Domain Evidence (Domain Analyzer V2 Enabled)
- Config C: Domain Evidence Ablation (B without domain block, strictly verifying identity with A)

Datasets:
1. data/evaluation/phase5_regression_160.jsonl (160 samples)
2. data/evaluation/phase6_domain_challenge.jsonl (40 samples)

Output:
- results/phase6_domain_evidence/predictions.jsonl
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

from src.experiments.phase6_domain_evidence.engine_v3 import classify_email_phase6

REGRESSION_FILE = Path("data/evaluation/phase5_regression_160.jsonl")
CHALLENGE_FILE = Path("data/evaluation/phase6_domain_challenge.jsonl")
HISTORICAL_A1_OPT_FILE = Path("results/phase5_a1_sanitizer_latency/predictions.jsonl")

OUT_DIR = Path("results/phase6_domain_evidence")
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
    print("PHASE 6: DOMAIN EVIDENCE INTEGRATION BENCHMARK RUNNER")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    # 1. Load Datasets
    regression_samples = []
    with open(REGRESSION_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                regression_samples.append(json.loads(line))

    challenge_samples = []
    with open(CHALLENGE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                challenge_samples.append(json.loads(line))

    all_samples = regression_samples + challenge_samples
    print(f"Loaded {len(regression_samples)} regression samples and {len(challenge_samples)} challenge samples.")
    print(f"Total unique evaluation samples: {len(all_samples)}")

    completed_keys = load_completed_keys(OUT_PREDS_FILE)
    print(f"Already completed predictions in output file: {len(completed_keys)}")

    # 2. Sync Config A baseline from Phase 5 for the 160 regression samples
    a1_opt_hist_map = {}
    if HISTORICAL_A1_OPT_FILE.exists():
        with open(HISTORICAL_A1_OPT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    if r.get("config_id") == "A1-Opt":
                        a1_opt_hist_map[r["sample_id"]] = r

    synced_a = 0
    with open(OUT_PREDS_FILE, "a", encoding="utf-8") as out_f:
        for s in regression_samples:
            sid = s["sample_id"]
            if ("A", sid) not in completed_keys and sid in a1_opt_hist_map:
                h = a1_opt_hist_map[sid].copy()
                h["config_id"] = "A"
                h["configuration_id"] = "A"
                h["config_name"] = "A1-Opt Baseline"
                h["method"] = "A1-Opt Baseline (No Domain Evidence)"
                out_f.write(json.dumps(h, ensure_ascii=False) + "\n")
                out_f.flush()
                completed_keys.add(("A", sid))
                synced_a += 1

    print(f"Synced {synced_a} historical Config A predictions on regression suite.")

    # 3. Plan Runs
    # Config A on challenge_samples (40)
    # Config B on all_samples (200)
    # Config C on challenge_samples (40) to verify invariance with Config A
    runs_to_do = []

    # Config A pending
    for s in challenge_samples:
        if ("A", s["sample_id"]) not in completed_keys:
            runs_to_do.append(("A", s, "phase6_domain_challenge"))

    # Config B pending
    for s in regression_samples:
        if ("B", s["sample_id"]) not in completed_keys:
            runs_to_do.append(("B", s, "phase5_regression_160"))
    for s in challenge_samples:
        if ("B", s["sample_id"]) not in completed_keys:
            runs_to_do.append(("B", s, "phase6_domain_challenge"))

    # Config C pending (challenge suite)
    for s in challenge_samples:
        if ("C", s["sample_id"]) not in completed_keys:
            runs_to_do.append(("C", s, "phase6_domain_challenge"))

    print(f"\nTotal pending inference runs: {len(runs_to_do)}")
    if not runs_to_do:
        print("All Phase 6 benchmark runs are complete!")
        return

    # Execute Sequential Inference
    t0_all = time.perf_counter()
    with open(OUT_PREDS_FILE, "a", encoding="utf-8") as out_f:
        for idx, (cfg_id, s, dset_name) in enumerate(runs_to_do, 1):
            sid = s["sample_id"]
            subj = s.get("subject", "")
            sender = s.get("sender", "")
            body = s.get("body", "")
            cat = s.get("category", "")
            subcat = s.get("subcategory", "")

            email_text = f"From: {sender}\nSubject: {subj}\n\n{body}"

            gt_is_phish = bool(s.get("label", 0) == 1 or s.get("is_phishing", False) or s.get("ground_truth_is_phishing", False))
            gt_has_inj = bool(s.get("has_prompt_injection", False) or s.get("ground_truth_has_injection", False))
            gt_active_inj = bool(subcat.startswith("active_") or s.get("ground_truth_active_injection", False))
            gt_quoted_inj = bool(subcat.startswith("quoted_") or s.get("ground_truth_quoted_injection", False))

            t0_sample = time.perf_counter()
            pred = classify_email_phase6(
                email_text=email_text,
                config_id=cfg_id,
                subject=subj,
                sender=sender,
            )
            sample_wall_ms = round((time.perf_counter() - t0_sample) * 1000, 2)

            cfg_names = {
                "A": "A1-Opt Baseline",
                "B": "A1-Opt + Domain Evidence",
                "C": "Domain Evidence Ablation",
            }

            record = {
                "config_id": cfg_id,
                "configuration_id": cfg_id,
                "config_name": cfg_names[cfg_id],
                "dataset": dset_name,
                "sample_id": sid,
                "subject": subj,
                "sender": sender,
                "category": cat,
                "subcategory": subcat,
                "origin_type": s.get("origin_type", "synthetic"),
                "source_dataset": s.get("source_dataset", dset_name),
                "ground_truth_is_phishing": gt_is_phish,
                "ground_truth_has_injection": gt_has_inj,
                "ground_truth_active_injection": gt_active_inj,
                "ground_truth_quoted_injection": gt_quoted_inj,
                "ground_truth_injection_type": s.get("injection_type", "none"),
                "is_phishing": pred["is_phishing"],
                "phishing_verdict": pred["phishing_verdict"],
                "has_prompt_injection": pred["has_prompt_injection"],
                "active_prompt_injection": pred["active_prompt_injection"],
                "quoted_prompt_injection": pred["quoted_prompt_injection"],
                "injection_verdict": pred["injection_verdict"],
                "injection_type": pred["injection_type"],
                "security_action": pred["security_action"],
                "verdict": pred["verdict"],
                "confidence": pred["confidence"],
                "reasons": pred["reasons"],
                "is_valid": pred["is_valid"],
                "is_sanitized": pred["is_sanitized"],
                "domain_evidence_present": pred["domain_evidence_present"],
                "domain_telemetry": pred["domain_telemetry"],
                "retrieved_exemplar_ids": pred["retrieved_exemplar_ids"],
                "retrieved_exemplar_labels": pred["retrieved_exemplar_labels"],
                "stage1_latency_ms": pred["stage1_latency_ms"],
                "stage2_latency_ms": pred["stage2_latency_ms"],
                "total_latency_ms": pred["total_latency_ms"],
                "wall_clock_ms": sample_wall_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()
            completed_keys.add((cfg_id, sid))

            # Progress log every 10 samples
            if idx % 10 == 0 or idx == len(runs_to_do):
                elapsed = time.perf_counter() - t0_all
                rate = idx / elapsed if elapsed > 0 else 0
                remaining = (len(runs_to_do) - idx) / rate if rate > 0 else 0
                print(
                    f"[{idx}/{len(runs_to_do)}] Config {cfg_id} | Sample {sid} ({cat}) | "
                    f"Pred: phish={pred['is_phishing']}, act={pred['security_action']} | "
                    f"Time: {sample_wall_ms}ms | ETA: {remaining:.1f}s"
                )

    total_time = time.perf_counter() - t0_all
    print(f"\nAll Phase 6 inference completed in {total_time:.2f}s ({total_time/60:.2f} min).")


if __name__ == "__main__":
    main()

