"""Metrics Computation & Statistical Component Attribution for M4 Ablation Study.

Computes:
1. Overall, V2, and Held-out metrics for all 9 configurations:
   - Accuracy, Precision, Recall, F1, FPR, FNR, Confusion Matrix (with denominators).
   - Prompt-Injection Precision, Recall, F1.
   - Active Injection Recall & Quoted Injection Accuracy.
   - Per-category accuracy breakdowns.
   - Latency distributions (Mean, Median, P95 for Stage 1, Stage 2, Total).
   - Inference failures.
2. Paired Component Attribution:
   - ISO-4 vs A0 (Injection Classifier)
   - A1 vs ISO-4 (Sanitization)
   - A2 vs A1 (Domain Analysis)
   - A3 vs A2 (Balanced RAG)
   - A4 vs A3 (Canonical Parity)
   - A4 vs ISO-1 (Sanitizer in Full Architecture)
   - A4 vs ISO-2 (Domain Telemetry in Full Architecture)
   - A4 vs ISO-3 (Balanced RAG in Full Architecture)
   - McNemar's exact/continuity-corrected test on paired predictions.
3. Outputs results/m4_ablation_v1/metrics.json.
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Configure utf-8 stdout for Windows
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PREDICTIONS_PATH = Path("results/m4_ablation_v1/predictions.jsonl")
OUT_METRICS_PATH = Path("results/m4_ablation_v1/metrics.json")
CONFIG_ORDER = ["A0", "ISO-4", "A1", "A2", "A3", "A4", "ISO-1", "ISO-2", "ISO-3"]


def percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_d = sorted(data)
    k = (len(sorted_d) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_d[int(k)]
    d0 = sorted_d[int(f)] * (c - k)
    d1 = sorted_d[int(c)] * (k - f)
    return d0 + d1


def compute_mcnemar(b: int, c: int) -> dict[str, Any]:
    """Computes McNemar's test with continuity correction."""
    n = b + c
    if n == 0:
        return {"chi2": 0.0, "p_value": 1.0, "significant_at_05": False, "interpretation": "No discordant pairs"}
    # Continuity corrected chi-square: (|b - c| - 1)^2 / (b + c)
    chi2 = ((abs(b - c) - 1.0) ** 2) / float(n) if abs(b - c) > 1 else 0.0
    # Approximate p-value from chi2 with 1 dof using survival function approximation
    # For df=1, p = erfc(sqrt(chi2 / 2))
    p_val = math.erfc(math.sqrt(chi2 / 2.0))
    return {
        "b_favors_config1": b,
        "c_favors_config2": c,
        "total_discordant": n,
        "chi2": round(chi2, 4),
        "p_value": round(p_val, 6),
        "significant_at_05": bool(p_val < 0.05),
    }


def calculate_metrics_for_subset(records: list[dict]) -> dict[str, Any]:
    n = len(records)
    if n == 0:
        return {}

    tp = fp = tn = fn = 0
    inj_tp = inj_fp = inj_tn = inj_fn = 0
    active_inj_tp = active_inj_fn = 0
    quoted_inj_tp = quoted_inj_fn = 0

    category_counts = defaultdict(lambda: {"total": 0, "correct": 0})
    stage1_latencies = []
    stage2_latencies = []
    total_latencies = []
    failures = 0

    for r in records:
        if not r.get("is_valid", True):
            failures += 1

        gt_phish = r["ground_truth_is_phishing"]
        pred_phish = r["is_phishing"]
        cat = r.get("category", "unknown")

        category_counts[cat]["total"] += 1
        if pred_phish == gt_phish:
            category_counts[cat]["correct"] += 1

        if gt_phish and pred_phish:
            tp += 1
        elif not gt_phish and pred_phish:
            fp += 1
        elif not gt_phish and not pred_phish:
            tn += 1
        elif gt_phish and not pred_phish:
            fn += 1

        # Prompt injection detection metrics
        gt_inj = r.get("ground_truth_has_injection", False)
        pred_inj = r.get("has_prompt_injection", False)
        if gt_inj and pred_inj:
            inj_tp += 1
        elif not gt_inj and pred_inj:
            inj_fp += 1
        elif not gt_inj and not pred_inj:
            inj_tn += 1
        elif gt_inj and not pred_inj:
            inj_fn += 1

        # Active injection recall (active injection attack in phishing email)
        is_active_gt = bool(r.get("ground_truth_active_injection", False) or (gt_inj and gt_phish))
        if is_active_gt:
            if r.get("active_prompt_injection", False) or (r.get("has_prompt_injection", False) and r.get("config_id") == "A0"):
                active_inj_tp += 1
            else:
                active_inj_fn += 1

        # Quoted injection classification (quoted injection in legitimate email)
        is_quoted_gt = bool(r.get("ground_truth_quoted_injection", False) or (gt_inj and not gt_phish))
        if is_quoted_gt:
            if r.get("quoted_prompt_injection", False):
                quoted_inj_tp += 1
            else:
                quoted_inj_fn += 1

        # Latencies
        stage1_latencies.append(r.get("stage1_latency_ms", 0.0))
        stage2_latencies.append(r.get("stage2_latency_ms", 0.0))
        total_latencies.append(r.get("total_latency_ms", 0.0))

    acc = (tp + tn) / n if n > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    inj_prec = inj_tp / (inj_tp + inj_fp) if (inj_tp + inj_fp) > 0 else 0.0
    inj_rec = inj_tp / (inj_tp + inj_fn) if (inj_tp + inj_fn) > 0 else 0.0
    inj_f1 = 2 * inj_prec * inj_rec / (inj_prec + inj_rec) if (inj_prec + inj_rec) > 0 else 0.0

    active_rec = active_inj_tp / (active_inj_tp + active_inj_fn) if (active_inj_tp + active_inj_fn) > 0 else 0.0
    quoted_acc = quoted_inj_tp / (quoted_inj_tp + quoted_inj_fn) if (quoted_inj_tp + quoted_inj_fn) > 0 else 0.0

    cat_breakdown = {}
    for cat, val in category_counts.items():
        c_tot = val["total"]
        c_cor = val["correct"]
        cat_breakdown[cat] = {
            "correct": c_cor,
            "total": c_tot,
            "accuracy": round(c_cor / c_tot, 4) if c_tot > 0 else 0.0,
        }

    return {
        "sample_count": n,
        "phishing_accuracy": round(acc, 4),
        "phishing_precision": round(prec, 4),
        "phishing_recall": round(rec, 4),
        "phishing_f1": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "confusion_matrix": {
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "tp_formula": f"{tp}/{tp+fn} ({round(rec*100, 1)}%)",
            "fp_formula": f"{fp}/{fp+tn} ({round(fpr*100, 1)}%)",
            "tn_formula": f"{tn}/{fp+tn} ({round((1-fpr)*100, 1)}%)",
            "fn_formula": f"{fn}/{tp+fn} ({round(fnr*100, 1)}%)",
        },
        "injection_metrics": {
            "injection_precision": round(inj_prec, 4),
            "injection_recall": round(inj_rec, 4),
            "injection_f1": round(inj_f1, 4),
            "active_injection_recall": round(active_rec, 4),
            "active_injection_formula": f"{active_inj_tp}/{active_inj_tp + active_inj_fn}",
            "quoted_injection_accuracy": round(quoted_acc, 4),
            "quoted_injection_formula": f"{quoted_inj_tp}/{quoted_inj_tp + quoted_inj_fn}",
        },
        "category_accuracy": cat_breakdown,
        "latency_stats": {
            "stage1_mean_ms": round(sum(stage1_latencies) / n, 1),
            "stage1_median_ms": round(percentile(stage1_latencies, 0.5), 1),
            "stage1_p95_ms": round(percentile(stage1_latencies, 0.95), 1),
            "stage2_mean_ms": round(sum(stage2_latencies) / n, 1),
            "stage2_median_ms": round(percentile(stage2_latencies, 0.5), 1),
            "stage2_p95_ms": round(percentile(stage2_latencies, 0.95), 1),
            "total_mean_ms": round(sum(total_latencies) / n, 1),
            "total_median_ms": round(percentile(total_latencies, 0.5), 1),
            "total_p95_ms": round(percentile(total_latencies, 0.95), 1),
        },
        "inference_failures": failures,
    }


def analyze_all_metrics() -> dict[str, Any]:
    if not PREDICTIONS_PATH.exists():
        raise FileNotFoundError(f"Predictions file not found: {PREDICTIONS_PATH}")

    all_records = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                all_records.append(json.loads(line))

    # Group by config and dataset
    by_config: dict[str, list[dict]] = defaultdict(list)
    by_config_v2: dict[str, list[dict]] = defaultdict(list)
    by_config_heldout: dict[str, list[dict]] = defaultdict(list)
    by_sample_config: dict[str, dict[str, dict]] = defaultdict(dict)

    for r in all_records:
        cid = r["config_id"]
        sid = r["sample_id"]
        dset = r["dataset"]

        by_config[cid].append(r)
        if dset == "v2":
            by_config_v2[cid].append(r)
        elif dset == "heldout":
            by_config_heldout[cid].append(r)
        by_sample_config[sid][cid] = r

    results: dict[str, Any] = {
        "configurations": {},
        "pairwise_attributions": {},
        "total_records": len(all_records),
    }

    # Compute metrics for each configuration
    for cid in CONFIG_ORDER:
        records_all = by_config.get(cid, [])
        records_v2 = by_config_v2.get(cid, [])
        records_heldout = by_config_heldout.get(cid, [])

        results["configurations"][cid] = {
            "combined_250": calculate_metrics_for_subset(records_all),
            "v2_150": calculate_metrics_for_subset(records_v2),
            "heldout_100": calculate_metrics_for_subset(records_heldout),
        }

    # Compute Paired Component Attributions
    paired_contrasts = [
        ("ISO-4", "A0", "Injection Classifier Contribution (ISO-4 vs A0)"),
        ("A1", "ISO-4", "Sanitization Contribution (A1 vs ISO-4)"),
        ("A2", "A1", "Domain Telemetry Contribution (A2 vs A1)"),
        ("A3", "A2", "Balanced RAG Contribution (A3 vs A2)"),
        ("A4", "A3", "Canonical Parity Check (A4 vs A3)"),
        ("A4", "ISO-1", "Sanitization in Full System (A4 vs ISO-1)"),
        ("A4", "ISO-2", "Domain Telemetry in Full System (A4 vs ISO-2)"),
        ("A4", "ISO-3", "Balanced RAG in Full System (A4 vs ISO-3)"),
    ]

    for c1, c2, label in paired_contrasts:
        b = 0  # c1 correct, c2 incorrect (beneficial to c1)
        c = 0  # c1 incorrect, c2 correct (harmful to c1)
        both_correct = 0
        both_incorrect = 0
        changed_predictions = []

        for sid, conf_dict in by_sample_config.items():
            if c1 in conf_dict and c2 in conf_dict:
                r1 = conf_dict[c1]
                r2 = conf_dict[c2]
                gt = r1["ground_truth_is_phishing"]
                p1 = r1["is_phishing"]
                p2 = r2["is_phishing"]

                c1_cor = bool(p1 == gt)
                c2_cor = bool(p2 == gt)

                if c1_cor and c2_cor:
                    both_correct += 1
                elif not c1_cor and not c2_cor:
                    both_incorrect += 1
                elif c1_cor and not c2_cor:
                    b += 1
                    changed_predictions.append({
                        "sample_id": sid,
                        "dataset": r1["dataset"],
                        "ground_truth": gt,
                        "direction": f"{c2} Incorrect ({p2}) -> {c1} Correct ({p1}) [BENEFICIAL]",
                    })
                elif not c1_cor and c2_cor:
                    c += 1
                    changed_predictions.append({
                        "sample_id": sid,
                        "dataset": r1["dataset"],
                        "ground_truth": gt,
                        "direction": f"{c2} Correct ({p2}) -> {c1} Incorrect ({p1}) [HARMFUL]",
                    })

        mcnemar = compute_mcnemar(b, c)
        results["pairwise_attributions"][f"{c1}_vs_{c2}"] = {
            "label": label,
            "config1": c1,
            "config2": c2,
            "both_correct": both_correct,
            "both_incorrect": both_incorrect,
            "beneficial_to_config1": b,
            "harmful_to_config1": c,
            "total_changed": b + c,
            "net_gain": b - c,
            "mcnemar_test": mcnemar,
            "changed_samples": changed_predictions,
        }

    OUT_METRICS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    res = analyze_all_metrics()
    print("METRICS_CALCULATION_COMPLETE")

