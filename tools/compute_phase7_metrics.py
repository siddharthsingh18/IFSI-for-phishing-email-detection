"""Compute independent metrics for Phase 7 Benchmark Evaluation.

Analyzes results/phase7_domain_precision/predictions.jsonl and outputs:
- results/phase7_domain_precision/independent_metrics.json
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results" / "phase7_domain_precision"
PREDICTIONS_PATH = RESULTS_DIR / "predictions.jsonl"
METRICS_PATH = RESULTS_DIR / "independent_metrics.json"

THREE_HISTORICAL_FPS = ["gen-ord-010", "p6-leg-007", "p6-leg-015"]


def percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


def compute_metrics():
    if not PREDICTIONS_PATH.is_file():
        print(f"Predictions file not found: {PREDICTIONS_PATH}")
        sys.exit(1)

    records = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    print(f"Total prediction records loaded: {len(records)}")

    # Group by config_id
    by_config = defaultdict(list)
    for r in records:
        by_config[r["config_id"]].append(r)

    results = {}

    for config_id, recs in sorted(by_config.items()):
        total = len(recs)
        tp = fp = tn = fn = 0
        categories = defaultdict(lambda: {"total": 0, "correct": 0})
        datasets = defaultdict(lambda: {"total": 0, "correct": 0})
        actions = Counter()

        latencies_s1 = []
        latencies_s2 = []
        latencies_total = []

        active_inj_total = 0
        active_inj_contained = 0
        quoted_inj_total = 0
        quoted_inj_safe_delivered = 0

        sop_phish_total = 0
        sop_phish_detected = 0

        diff_leg_total = 0
        diff_leg_correct = 0

        ord_leg_total = 0
        ord_leg_correct = 0

        fps_status = {}
        for fp_id in THREE_HISTORICAL_FPS:
            fps_status[fp_id] = "not_evaluated"

        for r in recs:
            sid = r["sample_id"]
            if "ground_truth_label" in r:
                gt = r["ground_truth_label"]
            elif "ground_truth_is_phishing" in r:
                gt = "phishing" if r["ground_truth_is_phishing"] else "legitimate"
            elif "ground_truth" in r:
                gt = "phishing" if (r["ground_truth"] in (1, "1", "phishing", True)) else "legitimate"
            else:
                gt = "unknown"
            is_phish_pred = r["is_phishing"]
            pred_label = "phishing" if is_phish_pred else "legitimate"
            cat = r.get("category", "unknown")
            dset = r.get("dataset", "unknown")
            action = r.get("security_action", "unknown")
            actions[action] += 1

            # Latency (only for non-zero)
            if r.get("stage1_latency_ms", 0) > 0:
                latencies_s1.append(r["stage1_latency_ms"])
            if r.get("stage2_latency_ms", 0) > 0:
                latencies_s2.append(r["stage2_latency_ms"])
            if r.get("total_latency_ms", 0) > 0:
                latencies_total.append(r["total_latency_ms"])

            # Classification correctness
            is_correct = (pred_label == gt)
            categories[cat]["total"] += 1
            if is_correct:
                categories[cat]["correct"] += 1

            datasets[dset]["total"] += 1
            if is_correct:
                datasets[dset]["correct"] += 1

            if gt == "phishing":
                if is_phish_pred:
                    tp += 1
                else:
                    fn += 1
            else:
                if is_phish_pred:
                    fp += 1
                else:
                    tn += 1

            # Prompt injection security checks
            if r.get("active_prompt_injection"):
                active_inj_total += 1
                # Contained if quarantined or blocked, or sanitized
                if action in ("quarantine_review", "block", "manual_review") or r.get("is_sanitized"):
                    active_inj_contained += 1

            if r.get("quoted_prompt_injection"):
                quoted_inj_total += 1
                if action == "allow":
                    quoted_inj_safe_delivered += 1

            # Key sub-categories
            if "sophisticated" in cat:
                sop_phish_total += 1
                if is_phish_pred:
                    sop_phish_detected += 1

            if "difficult" in cat:
                diff_leg_total += 1
                if not is_phish_pred:
                    diff_leg_correct += 1

            if "ordinary" in cat:
                ord_leg_total += 1
                if not is_phish_pred:
                    ord_leg_correct += 1

            # Check three historical false positives
            if sid in THREE_HISTORICAL_FPS:
                fps_status[sid] = {
                    "is_phishing": is_phish_pred,
                    "action": action,
                    "verdict": r.get("verdict"),
                    "status": "FALSE_POSITIVE" if is_phish_pred else "CORRECT_LEGITIMATE",
                }

        # Calculations
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        cat_breakdown = {}
        for c, counts in sorted(categories.items()):
            tot_c = counts["total"]
            cor_c = counts["correct"]
            cat_breakdown[c] = {
                "total": tot_c,
                "correct": cor_c,
                "accuracy": round(cor_c / tot_c, 4) if tot_c > 0 else 0.0,
            }

        dset_breakdown = {}
        for d, counts in sorted(datasets.items()):
            tot_d = counts["total"]
            cor_d = counts["correct"]
            dset_breakdown[d] = {
                "total": tot_d,
                "correct": cor_d,
                "accuracy": round(cor_d / tot_d, 4) if tot_d > 0 else 0.0,
            }

        results[config_id] = {
            "total_samples": total,
            "confusion_matrix": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
            "metrics": {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
                "fpr": round(fpr, 4),
                "fnr": round(fnr, 4),
            },
            "category_breakdown": cat_breakdown,
            "dataset_breakdown": dset_breakdown,
            "security_action_distribution": dict(actions),
            "sophisticated_phishing_recall": {
                "total": sop_phish_total,
                "detected": sop_phish_detected,
                "recall": round(sop_phish_detected / sop_phish_total, 4) if sop_phish_total > 0 else 0.0,
            },
            "difficult_legitimate_accuracy": {
                "total": diff_leg_total,
                "correct": diff_leg_correct,
                "accuracy": round(diff_leg_correct / diff_leg_total, 4) if diff_leg_total > 0 else 0.0,
            },
            "ordinary_legitimate_accuracy": {
                "total": ord_leg_total,
                "correct": ord_leg_correct,
                "accuracy": round(ord_leg_correct / ord_leg_total, 4) if ord_leg_total > 0 else 0.0,
            },
            "active_injection_security": {
                "total": active_inj_total,
                "contained": active_inj_contained,
                "containment_rate": round(active_inj_contained / active_inj_total, 4) if active_inj_total > 0 else 1.0,
            },
            "quoted_injection_security": {
                "total": quoted_inj_total,
                "safe_delivered": quoted_inj_safe_delivered,
                "safe_delivery_rate": round(quoted_inj_safe_delivered / quoted_inj_total, 4) if quoted_inj_total > 0 else 0.0,
            },
            "historical_fps_status": fps_status,
            "latency": {
                "stage1": {
                    "mean": round(sum(latencies_s1) / len(latencies_s1), 2) if latencies_s1 else 0.0,
                    "median": round(percentile(latencies_s1, 0.50), 2),
                    "p90": round(percentile(latencies_s1, 0.90), 2),
                    "p95": round(percentile(latencies_s1, 0.95), 2),
                },
                "stage2": {
                    "mean": round(sum(latencies_s2) / len(latencies_s2), 2) if latencies_s2 else 0.0,
                    "median": round(percentile(latencies_s2, 0.50), 2),
                    "p90": round(percentile(latencies_s2, 0.90), 2),
                    "p95": round(percentile(latencies_s2, 0.95), 2),
                },
                "total": {
                    "mean": round(sum(latencies_total) / len(latencies_total), 2) if latencies_total else 0.0,
                    "median": round(percentile(latencies_total, 0.50), 2),
                    "p90": round(percentile(latencies_total, 0.90), 2),
                    "p95": round(percentile(latencies_total, 0.95), 2),
                },
            },
        }

    # Paired comparisons between Config A and Config B
    paired_diffs = []
    a_preds = {r["sample_id"]: r for r in by_config.get("A", [])}
    b_preds = {r["sample_id"]: r for r in by_config.get("B", [])}
    c_preds = {r["sample_id"]: r for r in by_config.get("C", [])}

    all_sample_ids = sorted(set(a_preds.keys()) | set(b_preds.keys()))
    for sid in all_sample_ids:
        if sid in a_preds and sid in b_preds:
            ra = a_preds[sid]
            rb = b_preds[sid]
            if ra["is_phishing"] != rb["is_phishing"] or ra["security_action"] != rb["security_action"]:
                paired_diffs.append({
                    "sample_id": sid,
                    "dataset": ra.get("dataset"),
                    "category": ra.get("category"),
                    "ground_truth": ra.get("ground_truth_label"),
                    "config_a": {"is_phishing": ra["is_phishing"], "action": ra["security_action"], "verdict": ra["verdict"]},
                    "config_b": {"is_phishing": rb["is_phishing"], "action": rb["security_action"], "verdict": rb["verdict"]},
                })

    comparison = {
        "total_shared_samples_a_b": len([sid for sid in all_sample_ids if sid in a_preds and sid in b_preds]),
        "total_discrepancies_a_b": len(paired_diffs),
        "discrepancies": paired_diffs,
    }

    output_data = {
        "configurations": results,
        "paired_comparison_a_vs_b": comparison,
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Independent metrics computed and written to {METRICS_PATH}")
    for cid, data in results.items():
        m = data["metrics"]
        cm = data["confusion_matrix"]
        print(f"\n--- Config {cid} Summary (N={data['total_samples']}) ---")
        print(f"Accuracy:  {m['accuracy']:.4f} ({cm['TP']+cm['TN']}/{data['total_samples']})")
        print(f"Precision: {m['precision']:.4f}")
        print(f"Recall:    {m['recall']:.4f}")
        print(f"F1 Score:  {m['f1']:.4f}")
        print(f"FPR:       {m['fpr']:.4f} (FP={cm['FP']})")
        print(f"FNR:       {m['fnr']:.4f} (FN={cm['FN']})")
        print(f"Confusion: TP={cm['TP']}, FP={cm['FP']}, TN={cm['TN']}, FN={cm['FN']}")
        print(f"Sophisticated Phish Recall: {data['sophisticated_phishing_recall']['recall']:.4f} ({data['sophisticated_phishing_recall']['detected']}/{data['sophisticated_phishing_recall']['total']})")
        print(f"Difficult Legitimate Acc:   {data['difficult_legitimate_accuracy']['accuracy']:.4f} ({data['difficult_legitimate_accuracy']['correct']}/{data['difficult_legitimate_accuracy']['total']})")
        print(f"Historical FPs Status:     {data['historical_fps_status']}")
        print(f"Total Mean Latency:        {data['latency']['total']['mean']}ms")

    print(f"\nTotal Discrepancies between A and B: {len(paired_diffs)}")
    for d in paired_diffs:
        print(f"  {d['sample_id']} [{d['category']}]: GT={d['ground_truth']} | A={d['config_a']['verdict']} -> B={d['config_b']['verdict']}")


if __name__ == "__main__":
    compute_metrics()

