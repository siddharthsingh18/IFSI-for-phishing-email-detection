"""Compute Comprehensive Phase 5 Metrics.

Compares Frozen A1 vs Optimized A1 (A1-Opt) across:
1. Binary Phishing Classification (Precision, Recall, F1, Accuracy, FPR, FNR).
2. Injection Disambiguation & Sanitization Reliability.
3. Operational Security Actions & Malicious Containment.
4. Latency Analysis (Stage 1, Stage 2, Total End-to-End).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

PREDS_FILE = Path("results/phase5_a1_sanitizer_latency/predictions.jsonl")
OUT_METRICS_FILE = Path("results/phase5_a1_sanitizer_latency/regression_metrics.json")


def percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_d = sorted(data)
    k = (len(sorted_d) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_d[int(k)]
    d0 = sorted_d[int(f)] * (c - k)
    d1 = sorted_d[int(c)] * (k - f)
    return d0 + d1


def compute_metrics_for_config(records: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(records)
    
    # 1. Binary classification metrics (is_phishing vs ground_truth_is_phishing)
    tp = fp = tn = fn = 0
    for r in records:
        pred_p = bool(r["is_phishing"])
        gt_p = bool(r["ground_truth_is_phishing"])
        if pred_p and gt_p:
            tp += 1
        elif pred_p and not gt_p:
            fp += 1
        elif not pred_p and not gt_p:
            tn += 1
        else:
            fn += 1
            
    acc = (tp + tn) / n if n else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    fnr = fn / (fn + tp) if (fn + tp) else 0.0
    
    # 2. Injection & Sanitization metrics
    active_inj_samples = [r for r in records if r["ground_truth_active_injection"]]
    quoted_inj_samples = [r for r in records if r["ground_truth_quoted_injection"]]
    clean_samples = [r for r in records if not r["ground_truth_has_injection"]]
    
    # Active injection recall
    active_detected = sum(1 for r in active_inj_samples if r.get("active_prompt_injection"))
    active_recall = active_detected / len(active_inj_samples) if active_inj_samples else 0.0
    
    # Quoted injection recall
    quoted_detected = sum(1 for r in quoted_inj_samples if r.get("quoted_prompt_injection"))
    quoted_recall = quoted_detected / len(quoted_inj_samples) if quoted_inj_samples else 0.0
    
    # Sanitization success on active injection samples
    sanitized_count = sum(1 for r in active_inj_samples if r.get("is_sanitized"))
    sanitization_success_rate = sanitized_count / len(active_inj_samples) if active_inj_samples else 0.0
    
    # Chinese active injection samples (gen-inj-008, 018, 028, 038, 048)
    chinese_samples = [r for r in active_inj_samples if r["sample_id"] in ["gen-inj-008", "gen-inj-018", "gen-inj-028", "gen-inj-038", "gen-inj-048"]]
    chinese_sanitized = sum(1 for r in chinese_samples if r.get("is_sanitized"))
    chinese_manual_review = sum(1 for r in chinese_samples if r.get("security_action") == "manual_review")
    
    # Sanitization match methods
    match_methods = {}
    for r in active_inj_samples:
        m = r.get("match_method") or r.get("sanitization_info", {}).get("match_method", "unknown")
        match_methods[m] = match_methods.get(m, 0) + 1
        
    # 3. Security Actions
    actions = {}
    for r in records:
        a = r.get("security_action", "unknown")
        actions[a] = actions.get(a, 0) + 1
        
    # Security action breakdown:
    # Malicious containment: % of phishing and % of active injections prevented from reaching inbox (block, quarantine_review, manual_review)
    phish_samples = [r for r in records if r["ground_truth_is_phishing"]]
    phish_contained = sum(1 for r in phish_samples if r.get("security_action") in ["block", "quarantine_review", "manual_review"])
    phish_containment_rate = phish_contained / len(phish_samples) if phish_samples else 0.0
    
    active_contained = sum(1 for r in active_inj_samples if r.get("security_action") in ["block", "quarantine_review", "manual_review"])
    active_containment_rate = active_contained / len(active_inj_samples) if active_inj_samples else 0.0
    
    legit_clean_samples = [r for r in records if not r["ground_truth_is_phishing"] and not r["ground_truth_active_injection"]]
    legit_clean_delivered = sum(1 for r in legit_clean_samples if r.get("security_action") == "allow")
    legit_clean_delivery_rate = legit_clean_delivered / len(legit_clean_samples) if legit_clean_samples else 0.0
    
    # 4. Latency profiles
    s1_lats = [r.get("stage1_latency_ms", 0.0) for r in records if r.get("stage1_latency_ms")]
    s2_lats = [r.get("stage2_latency_ms", 0.0) for r in records if r.get("stage2_latency_ms")]
    tot_lats = [r.get("total_latency_ms", 0.0) for r in records if r.get("total_latency_ms")]
    
    def lat_stats(vals: list[float]) -> dict[str, float]:
        if not vals:
            return {"mean": 0.0, "p50": 0.0, "p90": 0.0, "p99": 0.0, "min": 0.0, "max": 0.0}
        return {
            "mean": round(sum(vals) / len(vals), 2),
            "p50": round(percentile(vals, 50), 2),
            "p90": round(percentile(vals, 90), 2),
            "p99": round(percentile(vals, 99), 2),
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
        }
        
    return {
        "sample_count": n,
        "valid_count": sum(1 for r in records if r.get("is_valid", True)),
        "error_count": sum(1 for r in records if not r.get("is_valid", True)),
        "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "classification_metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "fpr": round(fpr, 4),
            "fnr": round(fnr, 4),
        },
        "injection_metrics": {
            "active_injection_count": len(active_inj_samples),
            "active_injection_detected": active_detected,
            "active_injection_recall": round(active_recall, 4),
            "quoted_injection_count": len(quoted_inj_samples),
            "quoted_injection_detected": quoted_detected,
            "quoted_injection_recall": round(quoted_recall, 4),
            "sanitization_success_count": sanitized_count,
            "sanitization_success_rate": round(sanitization_success_rate, 4),
            "match_methods": match_methods,
            "chinese_samples_total": len(chinese_samples),
            "chinese_samples_sanitized": chinese_sanitized,
            "chinese_samples_manual_review": chinese_manual_review,
        },
        "security_policy_metrics": {
            "action_distribution": actions,
            "phishing_containment_rate": round(phish_containment_rate, 4),
            "active_injection_containment_rate": round(active_containment_rate, 4),
            "legitimate_clean_delivery_rate": round(legit_clean_delivery_rate, 4),
        },
        "latency_metrics": {
            "stage1_ms": lat_stats(s1_lats),
            "stage2_ms": lat_stats(s2_lats),
            "total_ms": lat_stats(tot_lats),
        }
    }


def main():
    if not PREDS_FILE.exists():
        print(f"Predictions file not found: {PREDS_FILE}")
        return

    records_by_config: dict[str, list[dict[str, Any]]] = {}
    with open(PREDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                records_by_config.setdefault(r["config_id"], []).append(r)

    print(f"Loaded configurations: {list(records_by_config.keys())}")
    for cid, recs in records_by_config.items():
        print(f"  {cid}: {len(recs)} predictions")

    results = {}
    for cid, recs in records_by_config.items():
        results[cid] = compute_metrics_for_config(recs)

    # Compute comparative deltas if both A1 and A1-Opt exist
    if "A1" in results and "A1-Opt" in results:
        a1 = results["A1"]
        opt = results["A1-Opt"]
        
        s1_mean_diff = opt["latency_metrics"]["stage1_ms"]["mean"] - a1["latency_metrics"]["stage1_ms"]["mean"]
        s1_pct_diff = (s1_mean_diff / a1["latency_metrics"]["stage1_ms"]["mean"]) * 100 if a1["latency_metrics"]["stage1_ms"]["mean"] else 0.0
        
        tot_mean_diff = opt["latency_metrics"]["total_ms"]["mean"] - a1["latency_metrics"]["total_ms"]["mean"]
        tot_pct_diff = (tot_mean_diff / a1["latency_metrics"]["total_ms"]["mean"]) * 100 if a1["latency_metrics"]["total_ms"]["mean"] else 0.0
        
        results["comparison_deltas"] = {
            "accuracy_delta": round(opt["classification_metrics"]["accuracy"] - a1["classification_metrics"]["accuracy"], 4),
            "f1_delta": round(opt["classification_metrics"]["f1"] - a1["classification_metrics"]["f1"], 4),
            "sanitization_success_rate_delta": round(opt["injection_metrics"]["sanitization_success_rate"] - a1["injection_metrics"]["sanitization_success_rate"], 4),
            "chinese_samples_resolved": f"{opt['injection_metrics']['chinese_samples_sanitized']} / {opt['injection_metrics']['chinese_samples_total']} (A1: {a1['injection_metrics']['chinese_samples_sanitized']})",
            "stage1_latency_mean_delta_ms": round(s1_mean_diff, 2),
            "stage1_latency_pct_reduction": round(-s1_pct_diff, 2),
            "total_latency_mean_delta_ms": round(tot_mean_diff, 2),
            "total_latency_pct_reduction": round(-tot_pct_diff, 2),
        }

    OUT_METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nWrote comprehensive regression metrics to {OUT_METRICS_FILE}")
    if "comparison_deltas" in results:
        print("\nComparative Summary (A1-Opt vs. Frozen A1):")
        for k, v in results["comparison_deltas"].items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()

