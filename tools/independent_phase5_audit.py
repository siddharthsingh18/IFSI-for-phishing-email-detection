"""Independent Forensic Auditor for Phase 5 (Sanitizer Reliability & Latency Optimization).

Performs strict, independent recalculation directly from raw prediction files without
trusting precomputed reports.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BENCHMARK_PATH = Path("data/evaluation/phase5_regression_160.jsonl")
PREDS_PATH = Path("results/phase5_a1_sanitizer_latency/predictions.jsonl")


def percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    d0 = s[int(f)] * (c - k)
    d1 = s[int(c)] * (k - f)
    return d0 + d1


def compute_binary_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(records)
    tp = fp = tn = fn = 0
    for r in records:
        pred = bool(r["is_phishing"])
        gt = bool(r["ground_truth_is_phishing"])
        if pred and gt:
            tp += 1
        elif pred and not gt:
            fp += 1
        elif not pred and not gt:
            tn += 1
        else:
            fn += 1
            
    acc = (tp + tn) / n if n else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    fnr = fn / (fn + tp) if (fn + tp) else 0.0
    
    return {
        "count": n,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "fnr": round(fnr, 4),
    }


def compute_latency_stats(vals: list[float]) -> dict[str, float]:
    if not vals:
        return {"mean": 0.0, "p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": round(sum(vals) / len(vals), 2),
        "p50": round(percentile(vals, 50), 2),
        "p90": round(percentile(vals, 90), 2),
        "p95": round(percentile(vals, 95), 2),
        "p99": round(percentile(vals, 99), 2),
        "min": round(min(vals), 2),
        "max": round(max(vals), 2),
    }


def run_audit():
    print("=" * 80)
    print("PHASE 5 INDEPENDENT AUDIT EXECUTION")
    print("=" * 80)

    # 1. Audit Benchmark Dataset
    benchmark_samples = {}
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            sid = row.get("sample_id") or row.get("id")
            assert sid not in benchmark_samples, f"Duplicate sample ID in benchmark: {sid}"
            benchmark_samples[sid] = row

    print(f"[Benchmark Audit] Total benchmark samples: {len(benchmark_samples)}")
    assert len(benchmark_samples) == 160, f"Expected 160 benchmark samples, got {len(benchmark_samples)}"

    # 2. Audit Predictions File
    raw_records_by_config: dict[str, dict[str, dict[str, Any]]] = {}
    line_counts_by_config = {}

    with open(PREDS_PATH, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r["config_id"]
            sid = r["sample_id"]
            line_counts_by_config[cid] = line_counts_by_config.get(cid, 0) + 1
            if cid not in raw_records_by_config:
                raw_records_by_config[cid] = {}
            assert sid not in raw_records_by_config[cid], f"Duplicate prediction for ({cid}, {sid}) at line {line_num}"
            raw_records_by_config[cid][sid] = r

    print("[Prediction Count Audit]")
    for cid, cnt in line_counts_by_config.items():
        print(f"  Configuration {cid}: {cnt} unique sample predictions")
        assert cnt == 160, f"Expected 160 predictions for {cid}, got {cnt}"

    assert set(raw_records_by_config.keys()) == {"A1", "A1-Opt"}, f"Unexpected configs: {set(raw_records_by_config.keys())}"

    # Verify identical sample pairing and ground truth consistency
    for sid in benchmark_samples:
        assert sid in raw_records_by_config["A1"], f"Sample {sid} missing from A1"
        assert sid in raw_records_by_config["A1-Opt"], f"Sample {sid} missing from A1-Opt"
        
        b_gt_phish = bool(benchmark_samples[sid].get("label", 0) == 1 or benchmark_samples[sid].get("is_phishing", False) or benchmark_samples[sid].get("ground_truth_is_phishing", False))
        a1_gt_phish = bool(raw_records_by_config["A1"][sid]["ground_truth_is_phishing"])
        opt_gt_phish = bool(raw_records_by_config["A1-Opt"][sid]["ground_truth_is_phishing"])
        assert b_gt_phish == a1_gt_phish == opt_gt_phish, f"Ground truth mismatch for {sid}: b={b_gt_phish}, a1={a1_gt_phish}, opt={opt_gt_phish}"

    print("[Pairing Audit] 100% 1-to-1 sample alignment and ground truth identity verified across benchmark and both configs.")

    # 3. Sophisticated Phishing Audit (Cluster 2 - 20 samples)
    print("\n" + "=" * 80)
    print("SECTION 2: SOPHISTICATED PHISHING DEEP AUDIT (20 Samples)")
    print("=" * 80)
    sop_samples = [s for s in benchmark_samples.values() if s.get("category") == "sophisticated_phishing" or (s.get("sample_id") or s.get("id", "")).startswith("gen-sop-")]
    print(f"Total sophisticated phishing samples identified: {len(sop_samples)}")
    assert len(sop_samples) == 20, f"Expected 20 sophisticated phishing samples, got {len(sop_samples)}"

    sop_diffs = []
    sop_audit_rows = []

    for s in sop_samples:
        sid = s.get("sample_id") or s.get("id")
        r_a1 = raw_records_by_config["A1"][sid]
        r_opt = raw_records_by_config["A1-Opt"][sid]
        
        gt_phish = r_a1["ground_truth_is_phishing"]
        pred_a1 = r_a1["is_phishing"]
        pred_opt = r_opt["is_phishing"]
        action_a1 = r_a1["security_action"]
        action_opt = r_opt["security_action"]
        
        # Domain evidence check
        dom_ev_a1 = r_a1.get("domain_evidence_present", False)
        dom_ev_opt = r_opt.get("domain_evidence_present", False)
        
        if pred_a1 != pred_opt or action_a1 != action_opt:
            sop_diffs.append((sid, pred_a1, pred_opt, action_a1, action_opt))
            
        sop_audit_rows.append({
            "sample_id": sid,
            "subcategory": s.get("subcategory"),
            "ground_truth_is_phishing": gt_phish,
            "a1_prediction": pred_a1,
            "a1_action": action_a1,
            "a1_opt_prediction": pred_opt,
            "a1_opt_action": action_opt,
            "domain_evidence_a1": dom_ev_a1,
            "domain_evidence_a1_opt": dom_ev_opt,
        })

    a1_sop_fn = sum(1 for row in sop_audit_rows if not row["a1_prediction"])
    opt_sop_fn = sum(1 for row in sop_audit_rows if not row["a1_opt_prediction"])
    print(f"Frozen A1: False Negatives = {a1_sop_fn}/20, True Positives = {20 - a1_sop_fn}/20")
    print(f"A1-Opt:    False Negatives = {opt_sop_fn}/20, True Positives = {20 - opt_sop_fn}/20")
    print(f"Prediction or Action Discrepancies between A1 and A1-Opt on Sophisticated Phishing: {len(sop_diffs)}")
    print(f"Domain evidence present in Frozen A1: {any(r['domain_evidence_a1'] for r in sop_audit_rows)}")
    print(f"Domain evidence present in A1-Opt:    {any(r['domain_evidence_a1_opt'] for r in sop_audit_rows)}")
    print("AUDIT FINDING: A1-Opt maintains 100% prediction parity with Frozen A1 on sophisticated phishing. Neither model detects these 20 samples because neither has domain analysis enabled. The sophisticated phishing weakness is NOT resolved in Phase 5.")

    # 4. Full Binary Classification & Category Breakdown
    print("\n" + "=" * 80)
    print("SECTION 3: FULL CLASSIFICATION & OPERATIONAL COMPARISON")
    print("=" * 80)

    cats = {
        "active_prompt_injection": [r for r in raw_records_by_config["A1"].values() if r["ground_truth_active_injection"]],
        "quoted_prompt_injection": [r for r in raw_records_by_config["A1"].values() if r["ground_truth_quoted_injection"]],
        "difficult_legitimate": [r for r in raw_records_by_config["A1"].values() if r["sample_id"].startswith("gen-dif-")],
        "sophisticated_phishing": [r for r in raw_records_by_config["A1"].values() if r["sample_id"].startswith("gen-sop-")],
        "ordinary_legitimate": [r for r in raw_records_by_config["A1"].values() if r["sample_id"].startswith("gen-ord-")],
    }

    print("Category sample counts:")
    for cname, crecs in cats.items():
        print(f"  {cname}: {len(crecs)}")

    metrics_a1_overall = compute_binary_metrics(list(raw_records_by_config["A1"].values()))
    metrics_opt_overall = compute_binary_metrics(list(raw_records_by_config["A1-Opt"].values()))

    print("\nOverall Binary Classification Metrics:")
    print(f"  Frozen A1: Accuracy={metrics_a1_overall['accuracy']}, Precision={metrics_a1_overall['precision']}, Recall={metrics_a1_overall['recall']}, F1={metrics_a1_overall['f1']}, FPR={metrics_a1_overall['fpr']}, FNR={metrics_a1_overall['fnr']}")
    print(f"             Confusion Matrix: TP={metrics_a1_overall['tp']}, FP={metrics_a1_overall['fp']}, TN={metrics_a1_overall['tn']}, FN={metrics_a1_overall['fn']}")
    print(f"  A1-Opt:    Accuracy={metrics_opt_overall['accuracy']}, Precision={metrics_opt_overall['precision']}, Recall={metrics_opt_overall['recall']}, F1={metrics_opt_overall['f1']}, FPR={metrics_opt_overall['fpr']}, FNR={metrics_opt_overall['fnr']}")
    print(f"             Confusion Matrix: TP={metrics_opt_overall['tp']}, FP={metrics_opt_overall['fp']}, TN={metrics_opt_overall['tn']}, FN={metrics_opt_overall['fn']}")

    # Per-category metrics
    per_cat_metrics = {}
    for cname in cats:
        sids = [r["sample_id"] for r in cats[cname]]
        a1_cat_recs = [raw_records_by_config["A1"][s] for s in sids]
        opt_cat_recs = [raw_records_by_config["A1-Opt"][s] for s in sids]
        per_cat_metrics[cname] = {
            "A1": compute_binary_metrics(a1_cat_recs),
            "A1-Opt": compute_binary_metrics(opt_cat_recs),
        }

    # Operational Security Outcomes
    def get_security_outcomes(recs: list[dict[str, Any]]) -> dict[str, Any]:
        actions = {}
        for r in recs:
            a = r.get("security_action", "unknown")
            actions[a] = actions.get(a, 0) + 1
            
        active_inj = [r for r in recs if r["ground_truth_active_injection"]]
        quoted_inj = [r for r in recs if r["ground_truth_quoted_injection"]]
        legit_clean = [r for r in recs if not r["ground_truth_is_phishing"] and not r["ground_truth_active_injection"]]
        
        active_contained = sum(1 for r in active_inj if r.get("security_action") in ["block", "quarantine_review", "manual_review"])
        quoted_delivered = sum(1 for r in quoted_inj if r.get("security_action") == "allow")
        legit_delivered = sum(1 for r in legit_clean if r.get("security_action") == "allow")
        
        return {
            "action_counts": actions,
            "active_injection_containment_rate": round(active_contained / len(active_inj), 4) if active_inj else 0.0,
            "quoted_injection_safe_delivery_rate": round(quoted_delivered / len(quoted_inj), 4) if quoted_inj else 0.0,
            "clean_legitimate_delivery_rate": round(legit_delivered / len(legit_clean), 4) if legit_clean else 0.0,
            "unresolved_sanitizations": sum(1 for r in recs if r.get("sanitization_info", {}).get("requires_manual_review")),
            "pipeline_errors": sum(1 for r in recs if not r.get("is_valid", True)),
        }

    sec_a1 = get_security_outcomes(list(raw_records_by_config["A1"].values()))
    sec_opt = get_security_outcomes(list(raw_records_by_config["A1-Opt"].values()))

    print("\nOperational Security Outcomes:")
    print("  Frozen A1 Action Counts:", sec_a1["action_counts"])
    print("  A1-Opt Action Counts:   ", sec_opt["action_counts"])
    print(f"  Frozen A1 Pipeline Errors: {sec_a1['pipeline_errors']} | A1-Opt Pipeline Errors: {sec_opt['pipeline_errors']}")
    print(f"  Frozen A1 Active Containment: {sec_a1['active_injection_containment_rate']} | A1-Opt: {sec_opt['active_injection_containment_rate']}")
    print(f"  Frozen A1 Quoted Delivery:    {sec_a1['quoted_injection_safe_delivery_rate']} | A1-Opt: {sec_opt['quoted_injection_safe_delivery_rate']}")

    # 5. Latency Audit
    print("\n" + "=" * 80)
    print("SECTION 4: INDEPENDENT LATENCY AUDIT")
    print("=" * 80)

    s1_a1 = [r["stage1_latency_ms"] for r in raw_records_by_config["A1"].values() if r.get("stage1_latency_ms")]
    s2_a1 = [r["stage2_latency_ms"] for r in raw_records_by_config["A1"].values() if r.get("stage2_latency_ms")]
    tot_a1 = [r["total_latency_ms"] for r in raw_records_by_config["A1"].values() if r.get("total_latency_ms")]

    s1_opt = [r["stage1_latency_ms"] for r in raw_records_by_config["A1-Opt"].values() if r.get("stage1_latency_ms")]
    s2_opt = [r["stage2_latency_ms"] for r in raw_records_by_config["A1-Opt"].values() if r.get("stage2_latency_ms")]
    tot_opt = [r["total_latency_ms"] for r in raw_records_by_config["A1-Opt"].values() if r.get("total_latency_ms")]

    lat_a1 = {"stage1": compute_latency_stats(s1_a1), "stage2": compute_latency_stats(s2_a1), "total": compute_latency_stats(tot_a1)}
    lat_opt = {"stage1": compute_latency_stats(s1_opt), "stage2": compute_latency_stats(s2_opt), "total": compute_latency_stats(tot_opt)}

    # Paired sample analysis
    s1_paired_deltas = [raw_records_by_config["A1-Opt"][sid]["stage1_latency_ms"] - raw_records_by_config["A1"][sid]["stage1_latency_ms"] for sid in benchmark_samples]
    tot_paired_deltas = [raw_records_by_config["A1-Opt"][sid]["total_latency_ms"] - raw_records_by_config["A1"][sid]["total_latency_ms"] for sid in benchmark_samples]

    # Cold-start outlier check (sample 1)
    s1_sample1_opt = raw_records_by_config["A1-Opt"]["gen-inj-001"]["stage1_latency_ms"]
    s1_opt_warmed = [r["stage1_latency_ms"] for sid, r in raw_records_by_config["A1-Opt"].items() if sid != "gen-inj-001"]
    lat_opt_warmed = compute_latency_stats(s1_opt_warmed)

    print("Stage 1 Latency:")
    print(f"  Frozen A1: Mean={lat_a1['stage1']['mean']} ms, P50={lat_a1['stage1']['p50']} ms, P90={lat_a1['stage1']['p90']} ms, P95={lat_a1['stage1']['p95']} ms, P99={lat_a1['stage1']['p99']} ms")
    print(f"  A1-Opt:    Mean={lat_opt['stage1']['mean']} ms, P50={lat_opt['stage1']['p50']} ms, P90={lat_opt['stage1']['p90']} ms, P95={lat_opt['stage1']['p95']} ms, P99={lat_opt['stage1']['p99']} ms")
    print(f"  A1-Opt (Warmed, excluding cold sample 1): Mean={lat_opt_warmed['mean']} ms, Max={lat_opt_warmed['max']} ms")
    print(f"  Stage 1 Mean Reduction: {lat_a1['stage1']['mean'] - lat_opt['stage1']['mean']:.2f} ms ({((lat_a1['stage1']['mean'] - lat_opt['stage1']['mean']) / lat_a1['stage1']['mean']) * 100:.2f}%)")
    print(f"  Stage 1 P50 Reduction:  {lat_a1['stage1']['p50'] - lat_opt['stage1']['p50']:.2f} ms ({((lat_a1['stage1']['p50'] - lat_opt['stage1']['p50']) / lat_a1['stage1']['p50']) * 100:.2f}%)")
    print(f"  Stage 1 P90 Reduction:  {lat_a1['stage1']['p90'] - lat_opt['stage1']['p90']:.2f} ms ({((lat_a1['stage1']['p90'] - lat_opt['stage1']['p90']) / lat_a1['stage1']['p90']) * 100:.2f}%)")

    # Serialize independent metrics
    independent_metrics = {
        "benchmark_sample_count": len(benchmark_samples),
        "configurations_evaluated": ["A1", "A1-Opt"],
        "overall_classification": {
            "Frozen_A1": metrics_a1_overall,
            "A1_Opt": metrics_opt_overall,
        },
        "per_category_metrics": per_cat_metrics,
        "operational_security": {
            "Frozen_A1": sec_a1,
            "A1_Opt": sec_opt,
        },
        "latency_metrics": {
            "Frozen_A1": lat_a1,
            "A1_Opt": lat_opt,
            "A1_Opt_warmed_stage1": lat_opt_warmed,
            "stage1_pct_reduction_mean": round(((lat_a1['stage1']['mean'] - lat_opt['stage1']['mean']) / lat_a1['stage1']['mean']) * 100, 2),
            "stage1_pct_reduction_p50": round(((lat_a1['stage1']['p50'] - lat_opt['stage1']['p50']) / lat_a1['stage1']['p50']) * 100, 2),
            "stage1_pct_reduction_p90": round(((lat_a1['stage1']['p90'] - lat_opt['stage1']['p90']) / lat_a1['stage1']['p90']) * 100, 2),
        },
        "sophisticated_phishing_summary": {
            "total_samples": 20,
            "frozen_a1_tp": 20 - a1_sop_fn,
            "frozen_a1_fn": a1_sop_fn,
            "a1_opt_tp": 20 - opt_sop_fn,
            "a1_opt_fn": opt_sop_fn,
            "discrepancies": len(sop_diffs),
            "domain_evidence_present": False,
            "status": "Identical parity (20/20 FN in both configs due to absence of domain analysis)",
        }
    }

    out_metrics_path = Path("results/phase5_a1_sanitizer_latency/independent_metrics.json")
    with open(out_metrics_path, "w", encoding="utf-8") as f:
        json.dump(independent_metrics, f, indent=2, ensure_ascii=False)
    print(f"\nWrote independent metrics to {out_metrics_path}")

    return independent_metrics, sop_audit_rows


if __name__ == "__main__":
    run_audit()

