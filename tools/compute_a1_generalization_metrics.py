"""A1 Generalization Validation V1: Metrics Computation & Statistical Analysis.

Calculates comprehensive performance metrics, injection telemetry, category breakdown,
provenance slices, latency distributions, and paired McNemar test statistics from
results/a1_generalization_v1/predictions.jsonl.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

# Configure utf-8 stdout
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PREDICTIONS_PATH = Path("results/a1_generalization_v1/predictions.jsonl")
METRICS_PATH = Path("results/a1_generalization_v1/metrics.json")


def safe_div(num: float, den: float, default: float = 0.0) -> float:
    return num / den if den != 0 else default


def compute_binary_metrics(y_true: list[bool], y_pred: list[bool]) -> dict:
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt and yp)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and yp)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and not yp)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt and not yp)
    n = len(y_true)

    acc = safe_div(tp + tn, n)
    prec = safe_div(tp, tp + fp)
    rec = safe_div(tp, tp + fn)
    f1 = safe_div(2 * prec * rec, prec + rec)
    fpr = safe_div(fp, fp + tn)
    fnr = safe_div(fn, fn + tp)

    return {
        "total_samples": n,
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "accuracy_pct": round(acc * 100, 2),
        "precision_pct": round(prec * 100, 2),
        "recall_pct": round(rec * 100, 2),
        "f1_pct": round(f1 * 100, 2),
        "fpr_pct": round(fpr * 100, 2),
        "fnr_pct": round(fnr * 100, 2),
    }


def compute_mcnemar(records_a0: dict[str, dict], records_a1: dict[str, dict]) -> dict:
    common_sids = sorted(set(records_a0.keys()) & set(records_a1.keys()))
    n = len(common_sids)

    # Contingency:
    # b: A0 correct, A1 incorrect
    # c: A1 correct, A0 incorrect
    n_both_correct = 0
    n_both_incorrect = 0
    b_a0_only = 0
    c_a1_only = 0

    discordant_cases = []

    for sid in common_sids:
        r0 = records_a0[sid]
        r1 = records_a1[sid]

        gt = r0["ground_truth_is_phishing"]
        pred0 = r0["is_phishing"]
        pred1 = r1["is_phishing"]

        c0 = (pred0 == gt)
        c1 = (pred1 == gt)

        if c0 and c1:
            n_both_correct += 1
        elif not c0 and not c1:
            n_both_incorrect += 1
        elif c0 and not c1:
            b_a0_only += 1
            discordant_cases.append({
                "sample_id": sid,
                "winner": "A0",
                "ground_truth": "phishing" if gt else "legitimate",
                "a0_pred": "phishing" if pred0 else "legitimate",
                "a1_pred": "phishing" if pred1 else "legitimate",
                "category": r0.get("category", ""),
            })
        elif not c0 and c1:
            c_a1_only += 1
            discordant_cases.append({
                "sample_id": sid,
                "winner": "A1",
                "ground_truth": "phishing" if gt else "legitimate",
                "a0_pred": "phishing" if pred0 else "legitimate",
                "a1_pred": "phishing" if pred1 else "legitimate",
                "category": r1.get("category", ""),
            })

    # McNemar with Edwards continuity correction
    total_discordant = b_a0_only + c_a1_only
    if total_discordant > 0:
        stat = ((abs(b_a0_only - c_a1_only) - 1.0) ** 2) / total_discordant
        p_val_chi2 = 1.0 - stats.chi2.cdf(stat, df=1)
        # Exact binomial test (two-sided)
        # scipy.stats.binomtest
        binom_res = stats.binomtest(k=c_a1_only, n=total_discordant, p=0.5, alternative="two-sided")
        p_val_exact = binom_res.pvalue
    else:
        stat = 0.0
        p_val_chi2 = 1.0
        p_val_exact = 1.0

    delta_acc = safe_div(c_a1_only - b_a0_only, n)
    # Standard error of difference in proportions for paired data
    # se = sqrt((b + c - (b - c)^2 / n) / (n^2))
    se_delta = math.sqrt(safe_div(b_a0_only + c_a1_only - ((b_a0_only - c_a1_only) ** 2) / n, n * n)) if n > 0 else 0.0
    ci95_low = delta_acc - 1.96 * se_delta
    ci95_high = delta_acc + 1.96 * se_delta

    return {
        "n_samples": n,
        "both_correct": n_both_correct,
        "both_incorrect": n_both_incorrect,
        "a0_correct_a1_incorrect (b)": b_a0_only,
        "a1_correct_a0_incorrect (c)": c_a1_only,
        "total_discordant": total_discordant,
        "mcnemar_statistic_corrected": round(stat, 4),
        "p_value_chi2": round(p_val_chi2, 6),
        "p_value_exact_binomial": round(p_val_exact, 6),
        "statistically_significant": bool(p_val_exact < 0.05),
        "delta_accuracy": round(delta_acc, 4),
        "delta_accuracy_pct": round(delta_acc * 100, 2),
        "ci95_low_pct": round(ci95_low * 100, 2),
        "ci95_high_pct": round(ci95_high * 100, 2),
        "discordant_cases": discordant_cases,
    }


def compute_metrics() -> dict:
    if not PREDICTIONS_PATH.exists():
        raise FileNotFoundError(f"Predictions file missing: {PREDICTIONS_PATH}")

    records_by_config = defaultdict(list)
    records_by_cfg_sample = defaultdict(dict)

    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            cid = r.get("config_id") or r.get("configuration_id")
            sid = r["sample_id"]
            records_by_config[cid].append(r)
            records_by_cfg_sample[cid][sid] = r

    configs = sorted(records_by_config.keys())
    output = {
        "metadata": {
            "dataset": "a1_generalization_v1",
            "configs_evaluated": configs,
            "prediction_counts": {c: len(records_by_config[c]) for c in configs},
        },
        "configurations": {},
    }

    for cid in configs:
        recs = records_by_config[cid]
        y_true = [r["ground_truth_is_phishing"] for r in recs]
        y_pred = [r["is_phishing"] for r in recs]

        # Overall binary
        overall = compute_binary_metrics(y_true, y_pred)

        # By category
        by_cat = {}
        cat_groups = defaultdict(list)
        for r in recs:
            cat_groups[r["category"]].append(r)

        for cat, cat_recs in sorted(cat_groups.items()):
            cy_true = [r["ground_truth_is_phishing"] for r in cat_recs]
            cy_pred = [r["is_phishing"] for r in cat_recs]
            by_cat[cat] = compute_binary_metrics(cy_true, cy_pred)

        # By provenance slice
        by_origin = {}
        origin_groups = defaultdict(list)
        for r in recs:
            origin_groups[r.get("origin_type", "unknown")].append(r)

        for orig, orig_recs in sorted(origin_groups.items()):
            oy_true = [r["ground_truth_is_phishing"] for r in orig_recs]
            oy_pred = [r["is_phishing"] for r in orig_recs]
            by_origin[orig] = compute_binary_metrics(oy_true, oy_pred)

        # Injection telemetry
        inj_recs = [r for r in recs if r.get("ground_truth_has_injection")]
        active_inj_recs = [r for r in inj_recs if r.get("ground_truth_active_injection")]
        quoted_inj_recs = [r for r in inj_recs if r.get("ground_truth_quoted_injection")]

        # Active injection detection
        # Did Stage 1 flag prompt injection?
        active_inj_detected = sum(1 for r in active_inj_recs if r.get("has_prompt_injection") or r.get("active_prompt_injection"))
        active_inj_recall = safe_div(active_inj_detected, len(active_inj_recs))

        # Quoted injection handling
        # How was quoted injection classified in Stage 1?
        quoted_classified_as_quoted = sum(1 for r in quoted_inj_recs if r.get("quoted_prompt_injection") or r.get("injection_type") == "quoted")
        quoted_classified_as_active = sum(1 for r in quoted_inj_recs if r.get("active_prompt_injection") or (r.get("has_prompt_injection") and not r.get("quoted_prompt_injection")))
        quoted_classified_as_clean = sum(1 for r in quoted_inj_recs if not r.get("has_prompt_injection") and not r.get("active_prompt_injection") and not r.get("quoted_prompt_injection"))

        # Quoted injection end-to-end phishing accuracy (all 50 quoted are legitimate!)
        quoted_phishing_pred_legit = sum(1 for r in quoted_inj_recs if not r.get("is_phishing"))
        quoted_acc = safe_div(quoted_phishing_pred_legit, len(quoted_inj_recs))

        # Security action distribution on quoted
        quoted_actions = Counter(r.get("security_action") for r in quoted_inj_recs)

        # Latencies
        l_s1 = [r.get("stage1_latency_ms", 0.0) for r in recs if r.get("stage1_latency_ms")]
        l_s2 = [r.get("stage2_latency_ms", 0.0) for r in recs if r.get("stage2_latency_ms")]
        l_tot = [r.get("total_latency_ms", 0.0) for r in recs if r.get("total_latency_ms")]

        def calc_lat_dist(arr):
            if not arr:
                return {}
            s = sorted(arr)
            n_l = len(s)
            return {
                "mean_ms": round(sum(s) / n_l, 1),
                "median_ms": round(s[n_l // 2], 1),
                "p95_ms": round(s[int(n_l * 0.95)], 1),
                "min_ms": round(s[0], 1),
                "max_ms": round(s[-1], 1),
            }

        latency_stats = {
            "stage1": calc_lat_dist(l_s1),
            "stage2": calc_lat_dist(l_s2),
            "total": calc_lat_dist(l_tot),
        }

        # Error counts
        fp_samples = [r["sample_id"] for r in recs if not r["ground_truth_is_phishing"] and r["is_phishing"]]
        fn_samples = [r["sample_id"] for r in recs if r["ground_truth_is_phishing"] and not r["is_phishing"]]

        output["configurations"][cid] = {
            "config_id": cid,
            "overall_metrics": overall,
            "category_metrics": by_cat,
            "provenance_metrics": by_origin,
            "injection_telemetry": {
                "active_injection_samples": len(active_inj_recs),
                "active_injection_detected": active_inj_detected,
                "active_injection_recall": round(active_inj_recall, 4),
                "active_injection_recall_pct": round(active_inj_recall * 100, 2),
                "quoted_injection_samples": len(quoted_inj_recs),
                "quoted_classified_as_quoted": quoted_classified_as_quoted,
                "quoted_classified_as_active": quoted_classified_as_active,
                "quoted_classified_as_clean": quoted_classified_as_clean,
                "quoted_legitimate_verdict_count": quoted_phishing_pred_legit,
                "quoted_operational_accuracy_pct": round(quoted_acc * 100, 2),
                "quoted_security_actions": dict(quoted_actions),
            },
            "latency": latency_stats,
            "errors": {
                "false_positive_count": len(fp_samples),
                "false_negative_count": len(fn_samples),
                "false_positive_sample_ids": fp_samples,
                "false_negative_sample_ids": fn_samples,
            },
        }

    # McNemar comparison if both A0 and A1 are present
    if "A0" in records_by_cfg_sample and "A1" in records_by_cfg_sample:
        mcnemar_res = compute_mcnemar(records_by_cfg_sample["A0"], records_by_cfg_sample["A1"])
        output["paired_comparison_a0_vs_a1"] = mcnemar_res

    METRICS_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Metrics written successfully to {METRICS_PATH}")
    return output


if __name__ == "__main__":
    compute_metrics()

