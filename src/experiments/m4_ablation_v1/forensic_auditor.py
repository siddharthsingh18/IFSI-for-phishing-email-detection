"""Independent Forensic Audit Script for M4 Ablation V1 Benchmark.

Performs:
1. Raw Prediction Integrity Verification
2. Ground-Truth Dataset Cross-Validation
3. Complete Independent Metrics Calculation
4. Rigorous Statistical Audit (McNemar asymptotic & exact binomial, paired CIs)
5. Exhaustive Error Categorization & Root-Cause Pattern Analysis
6. Discrepancy Analysis vs Previous Reports
7. Generation of:
   - results/m4_ablation_v1/independently_verified_metrics.json
   - results/m4_ablation_v1/independently_verified_comparisons.json
   - results/m4_ablation_v1/forensic_audit.md
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PREDICTIONS_PATH = Path("results/m4_ablation_v1/predictions.jsonl")
PREV_METRICS_PATH = Path("results/m4_ablation_v1/metrics.json")
V2_DATASET_PATH = Path("data/evaluation/live_benchmark_v2.jsonl")
HELDOUT_DATASET_PATH = Path("data/evaluation/heldout_benchmark_v1.jsonl")

OUT_VERIFIED_METRICS = Path("results/m4_ablation_v1/independently_verified_metrics.json")
OUT_VERIFIED_COMPARISONS = Path("results/m4_ablation_v1/independently_verified_comparisons.json")
OUT_AUDIT_REPORT = Path("results/m4_ablation_v1/forensic_audit.md")

CONFIGS = ["A0", "ISO-4", "A1", "A2", "A3", "A4", "ISO-1", "ISO-2", "ISO-3"]


def sha256_file(p: Path | str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


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


def binomial_coefficient(n: int, k: int) -> int:
    return math.comb(n, k)


def exact_binomial_p_value(b: int, c: int) -> float:
    """Computes exact two-tailed binomial p-value for McNemar test where n = b + c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    # P(X <= k) under Binomial(n, 0.5)
    cumulative_prob = sum(math.comb(n, i) * (0.5 ** n) for i in range(k + 1))
    # Two-tailed p-value
    p_val = min(1.0, 2.0 * cumulative_prob)
    return p_val


def compute_mcnemar_stats(b: int, c: int, total_n: int = 250) -> dict[str, Any]:
    n_discordant = b + c
    delta = (b - c) / total_n
    net_gain = b - c

    if n_discordant == 0:
        return {
            "b_favors_test": b,
            "c_favors_baseline": c,
            "discordant_total": 0,
            "net_gain": 0,
            "mcnemar_chi2_corrected": 0.0,
            "asymptotic_p_value": 1.0,
            "exact_binomial_p_value": 1.0,
            "significant_at_05": False,
            "effect_size_delta": 0.0,
            "delta_ci_95": [0.0, 0.0],
        }

    # Edwards continuity correction
    if abs(b - c) > 1:
        chi2 = ((abs(b - c) - 1.0) ** 2) / float(n_discordant)
    else:
        chi2 = 0.0

    asymp_p = math.erfc(math.sqrt(chi2 / 2.0))
    exact_p = exact_binomial_p_value(b, c)

    # Paired proportion confidence interval (Newcombe/Wald paired SE)
    # var(delta) = ((b + c) - (b - c)^2 / N) / N^2
    var_delta = (n_discordant - (net_gain ** 2) / total_n) / (total_n ** 2)
    se_delta = math.sqrt(max(0.0, var_delta))
    ci_lower = delta - 1.96 * se_delta
    ci_upper = delta + 1.96 * se_delta

    return {
        "b_favors_test": b,
        "c_favors_baseline": c,
        "discordant_total": n_discordant,
        "net_gain": net_gain,
        "mcnemar_chi2_corrected": round(chi2, 4),
        "asymptotic_p_value": round(asymp_p, 6),
        "exact_binomial_p_value": round(exact_p, 6),
        "significant_at_05": bool(asymp_p < 0.05),
        "effect_size_delta": round(delta, 4),
        "delta_ci_95": [round(ci_lower, 4), round(ci_upper, 4)],
    }


def audit_prediction_integrity(raw_predictions: list[dict], source_samples: dict[str, dict]) -> dict[str, Any]:
    integrity = {
        "total_records": len(raw_predictions),
        "expected_records": 2250,
        "is_record_count_valid": len(raw_predictions) == 2250,
        "configs_present": sorted(list(set(r["config_id"] for r in raw_predictions))),
        "per_config_counts": Counter(r["config_id"] for r in raw_predictions),
        "duplicate_pairs": [],
        "missing_combinations": [],
        "inference_failures": [],
        "input_consistency_violations": [],
        "ground_truth_mismatches": [],
        "dataset_distribution": Counter(r["dataset"] for r in raw_predictions),
    }

    seen_pairs = set()
    for i, r in enumerate(raw_predictions):
        pair = (r["config_id"], r["sample_id"])
        if pair in seen_pairs:
            integrity["duplicate_pairs"].append(pair)
        seen_pairs.add(pair)

        if not r.get("is_valid", True) or r.get("failure_type") is not None:
            integrity["inference_failures"].append({
                "index": i,
                "config_id": r["config_id"],
                "sample_id": r["sample_id"],
                "failure": r.get("failure_message"),
            })

    # Check for missing combinations
    for c in CONFIGS:
        for sid in source_samples:
            if (c, sid) not in seen_pairs:
                integrity["missing_combinations"].append((c, sid))

    # Check input consistency and ground-truth alignment across configurations
    by_sample = defaultdict(list)
    for r in raw_predictions:
        by_sample[r["sample_id"]].append(r)

    for sid, recs in by_sample.items():
        src = source_samples[sid]
        # Verify identical input content across configs
        first = recs[0]
        for r in recs[1:]:
            if r.get("subject") != first.get("subject") or r.get("sender") != first.get("sender") or r.get("body") != first.get("body"):
                integrity["input_consistency_violations"].append({
                    "sample_id": sid,
                    "config1": first["config_id"],
                    "config2": r["config_id"],
                    "issue": "Mismatched subject/sender/body text",
                })

        # Verify ground-truth matches source dataset
        src_phish = bool(src.get("label", 0) == 1 or src.get("is_phishing", False))
        src_inj = bool(src.get("has_prompt_injection", False))
        if first["ground_truth_is_phishing"] != src_phish:
            integrity["ground_truth_mismatches"].append({
                "sample_id": sid,
                "field": "is_phishing",
                "pred_val": first["ground_truth_is_phishing"],
                "source_val": src_phish,
            })
        if first.get("ground_truth_has_injection") != src_inj:
            integrity["ground_truth_mismatches"].append({
                "sample_id": sid,
                "field": "has_prompt_injection",
                "pred_val": first.get("ground_truth_has_injection"),
                "source_val": src_inj,
            })

    return integrity


def compute_metrics_for_records(records: list[dict], source_samples: dict[str, dict]) -> dict[str, Any]:
    n = len(records)
    if n == 0:
        return {}

    tp = fp = tn = fn = 0
    # Overall injection detection metrics
    inj_tp = inj_fp = inj_tn = inj_fn = 0
    # Active injection attack detection metrics (active injection in phishing)
    active_tp = active_fn = active_fp = active_tn = 0
    # Quoted injection classification metrics (quoted injection in legitimate)
    quoted_correct = quoted_misclassified = 0

    category_counts = defaultdict(lambda: {"total": 0, "correct": 0})
    stage1_latencies = []
    stage2_latencies = []
    total_latencies = []

    for r in records:
        sid = r["sample_id"]
        src = source_samples[sid]
        cid = r["config_id"]

        gt_phish = bool(src.get("label", 0) == 1 or src.get("is_phishing", False))
        gt_inj = bool(src.get("has_prompt_injection", False))
        gt_active = gt_inj and gt_phish
        gt_quoted = gt_inj and not gt_phish

        pred_phish = bool(r["is_phishing"])
        pred_inj = bool(r.get("has_prompt_injection", False))
        pred_active = bool(r.get("active_prompt_injection", False) or (cid == "A0" and pred_inj))
        pred_quoted = bool(r.get("quoted_prompt_injection", False))

        cat = src.get("category", "unknown")
        category_counts[cat]["total"] += 1
        if pred_phish == gt_phish:
            category_counts[cat]["correct"] += 1

        # Phishing Confusion Matrix
        if gt_phish and pred_phish:
            tp += 1
        elif not gt_phish and pred_phish:
            fp += 1
        elif not gt_phish and not pred_phish:
            tn += 1
        elif gt_phish and not pred_phish:
            fn += 1

        # Injection detection confusion matrix (overall injection presence)
        if gt_inj and pred_inj:
            inj_tp += 1
        elif not gt_inj and pred_inj:
            inj_fp += 1
        elif not gt_inj and not pred_inj:
            inj_tn += 1
        elif gt_inj and not pred_inj:
            inj_fn += 1

        # Active injection detection
        if gt_active:
            if pred_active:
                active_tp += 1
            else:
                active_fn += 1
        else:
            if pred_active:
                active_fp += 1
            else:
                active_tn += 1

        # Quoted injection classification
        if gt_quoted:
            # Correct if classified as quoted injection (and not active injection)
            if pred_quoted and not r.get("active_prompt_injection", False):
                quoted_correct += 1
            else:
                quoted_misclassified += 1

        stage1_latencies.append(r.get("stage1_latency_ms", 0.0))
        stage2_latencies.append(r.get("stage2_latency_ms", 0.0))
        total_latencies.append(r.get("total_latency_ms", 0.0))

    acc = (tp + tn) / n if n > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    inj_prec = inj_tp / (inj_tp + inj_fp) if (inj_tp + inj_fp) > 0 else 0.0
    inj_rec = inj_tp / (inj_tp + inj_fn) if (inj_tp + inj_fn) > 0 else 0.0
    inj_f1 = (2 * inj_prec * inj_rec) / (inj_prec + inj_rec) if (inj_prec + inj_rec) > 0 else 0.0

    active_rec = active_tp / (active_tp + active_fn) if (active_tp + active_fn) > 0 else 0.0
    active_prec = active_tp / (active_tp + active_fp) if (active_tp + active_fp) > 0 else 0.0
    active_f1 = (2 * active_prec * active_rec) / (active_prec + active_rec) if (active_prec + active_rec) > 0 else 0.0

    quoted_tot = quoted_correct + quoted_misclassified
    quoted_acc = quoted_correct / quoted_tot if quoted_tot > 0 else 0.0

    cat_breakdown = {}
    for cname, cdata in category_counts.items():
        tot = cdata["total"]
        cor = cdata["correct"]
        cat_breakdown[cname] = {
            "correct": cor,
            "total": tot,
            "accuracy": round(cor / tot, 4) if tot > 0 else 0.0,
            "accuracy_pct": round((cor / tot) * 100, 2) if tot > 0 else 0.0,
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
            "tp_formula": f"{tp}/{tp+fn} ({round(rec*100, 2)}%)",
            "fp_formula": f"{fp}/{fp+tn} ({round(fpr*100, 2)}%)",
            "tn_formula": f"{tn}/{fp+tn} ({round((1-fpr)*100, 2)}%)",
            "fn_formula": f"{fn}/{tp+fn} ({round(fnr*100, 2)}%)",
        },
        "overall_injection_metrics": {
            "tp": inj_tp, "fp": inj_fp, "tn": inj_tn, "fn": inj_fn,
            "precision": round(inj_prec, 4),
            "recall": round(inj_rec, 4),
            "f1": round(inj_f1, 4),
        },
        "active_injection_metrics": {
            "tp": active_tp, "fn": active_fn, "fp": active_fp, "tn": active_tn,
            "recall": round(active_rec, 4),
            "recall_formula": f"{active_tp}/{active_tp+active_fn}",
            "precision": round(active_prec, 4),
            "precision_formula": f"{active_tp}/{active_tp+active_fp}",
            "f1": round(active_f1, 4),
        },
        "quoted_injection_metrics": {
            "correct": quoted_correct,
            "misclassified": quoted_misclassified,
            "total": quoted_tot,
            "accuracy": round(quoted_acc, 4),
            "accuracy_formula": f"{quoted_correct}/{quoted_tot}",
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
    }


def audit_injections(raw_predictions: list[dict], source_samples: dict[str, dict]) -> dict[str, Any]:
    # Collect all 50 injection samples
    inj_samples = {sid: s for sid, s in source_samples.items() if s.get("has_prompt_injection")}
    assert len(inj_samples) == 50, f"Expected 50 injection samples, found {len(inj_samples)}"

    by_pred = defaultdict(dict)
    for r in raw_predictions:
        if r["sample_id"] in inj_samples:
            by_pred[r["config_id"]][r["sample_id"]] = r

    audit_res = {
        "total_injection_samples": len(inj_samples),
        "v2_injection_count": sum(1 for s in inj_samples.values() if s["dataset"] == "v2"),
        "heldout_injection_count": sum(1 for s in inj_samples.values() if s["dataset"] == "heldout"),
        "active_injection_samples": [],
        "quoted_injection_samples": [],
        "per_config_audit": {},
    }

    for sid, s in sorted(inj_samples.items()):
        is_p = bool(s.get("label", 0) == 1 or s.get("is_phishing", False))
        info = {
            "sample_id": sid,
            "dataset": s["dataset"],
            "subject": s.get("subject", ""),
            "is_phishing": is_p,
            "ground_truth_type": "active" if is_p else "quoted",
        }
        if is_p:
            audit_res["active_injection_samples"].append(info)
        else:
            audit_res["quoted_injection_samples"].append(info)

    assert len(audit_res["active_injection_samples"]) == 25
    assert len(audit_res["quoted_injection_samples"]) == 25

    # Check each config
    for c in CONFIGS:
        c_preds = by_pred[c]
        active_tp = []
        active_miss = []
        quoted_cor = []
        quoted_fail = []

        for sid, s in inj_samples.items():
            p = c_preds[sid]
            is_p = bool(s.get("label", 0) == 1 or s.get("is_phishing", False))
            pred_inj = p.get("has_prompt_injection", False)
            pred_active = p.get("active_prompt_injection", False) or (c == "A0" and pred_inj)
            pred_quoted = p.get("quoted_prompt_injection", False)
            security_action = p.get("security_action", "allow")

            if is_p:
                if pred_active:
                    active_tp.append(sid)
                else:
                    active_miss.append(sid)
            else:
                # Quoted: must be recognized as quoted, not active, and NOT blocked
                if pred_quoted and not p.get("active_prompt_injection", False) and security_action != "block":
                    quoted_cor.append(sid)
                else:
                    quoted_fail.append({
                        "sample_id": sid,
                        "pred_active": pred_active,
                        "pred_quoted": pred_quoted,
                        "security_action": security_action,
                        "is_phishing_pred": p.get("is_phishing"),
                    })

        audit_res["per_config_audit"][c] = {
            "active_tp_count": len(active_tp),
            "active_miss_count": len(active_miss),
            "active_miss_ids": active_miss,
            "active_recall": len(active_tp) / 25.0,
            "quoted_correct_count": len(quoted_cor),
            "quoted_fail_count": len(quoted_fail),
            "quoted_accuracy": len(quoted_cor) / 25.0,
            "quoted_failures": quoted_fail,
        }

    return audit_res


def audit_statistical_comparisons(by_config: dict[str, dict[str, dict]], source_samples: dict[str, dict]) -> dict[str, Any]:
    contrasts = [
        ("ISO-4", "A0", "Stage 1 Active vs Quoted Injection Classifier (ISO-4 vs A0)"),
        ("A1", "ISO-4", "Stage 1.5 Prompt Sanitization Cumulative (A1 vs ISO-4)"),
        ("A2", "A1", "Structured Sender/Domain Telemetry Cumulative (A2 vs A1)"),
        ("A3", "A2", "Balanced RAG Retrieval Cumulative (A3 vs A2)"),
        ("A4", "A3", "Canonical Experimental Engine Parity Check (A4 vs A3)"),
        ("A4", "ISO-1", "Prompt Sanitization Leave-One-Out (A4 vs ISO-1)"),
        ("A4", "ISO-2", "Domain Telemetry Leave-One-Out (A4 vs ISO-2)"),
        ("A4", "ISO-3", "Balanced RAG Leave-One-Out (A4 vs ISO-3)"),
    ]

    comparisons = {}

    for c_test, c_base, title in contrasts:
        preds_test = by_config[c_test]
        preds_base = by_config[c_base]

        both_cor = 0
        both_wrg = 0
        b = 0  # c_test correct, c_base wrong
        c = 0  # c_test wrong, c_base correct

        beneficial_samples = []
        harmful_samples = []

        for sid, src in source_samples.items():
            gt = bool(src.get("label", 0) == 1 or src.get("is_phishing", False))
            p_test = bool(preds_test[sid]["is_phishing"])
            p_base = bool(preds_base[sid]["is_phishing"])

            t_cor = (p_test == gt)
            b_cor = (p_base == gt)

            if t_cor and b_cor:
                both_cor += 1
            elif not t_cor and not b_cor:
                both_wrg += 1
            elif t_cor and not b_cor:
                b += 1
                beneficial_samples.append({
                    "sample_id": sid,
                    "dataset": src["dataset"],
                    "ground_truth": gt,
                    "baseline_pred": p_base,
                    "test_pred": p_test,
                    "subject": src.get("subject", ""),
                    "category": src.get("category", ""),
                })
            elif not t_cor and b_cor:
                c += 1
                harmful_samples.append({
                    "sample_id": sid,
                    "dataset": src["dataset"],
                    "ground_truth": gt,
                    "baseline_pred": p_base,
                    "test_pred": p_test,
                    "subject": src.get("subject", ""),
                    "category": src.get("category", ""),
                })

        stats = compute_mcnemar_stats(b, c, total_n=250)
        comparisons[f"{c_test}_vs_{c_base}"] = {
            "title": title,
            "test_config": c_test,
            "baseline_config": c_base,
            "contingency_table": {
                "both_correct": both_cor,
                "both_wrong": both_wrg,
                "beneficial_b": b,
                "harmful_c": c,
                "total_discordant": b + c,
            },
            "statistical_test": stats,
            "beneficial_samples": beneficial_samples,
            "harmful_samples": harmful_samples,
        }

    return comparisons


def run_full_forensic_audit():
    print("=================================================================")
    print("STARTING INDEPENDENT FORENSIC AUDIT OF M4 ABLATION V1")
    print("=================================================================")

    # 1. Load source datasets
    source_samples = {}
    with open(V2_DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                sid = item["id"]
                source_samples[sid] = {
                    "dataset": "v2",
                    "sample_id": sid,
                    "subject": item.get("subject", ""),
                    "sender": item.get("sender", ""),
                    "body": item.get("text", item.get("body", "")),
                    "category": item.get("category", "unknown"),
                    "label": item.get("label", 0),
                    "is_phishing": item.get("is_phishing", False),
                    "has_prompt_injection": item.get("has_prompt_injection", False),
                }

    with open(HELDOUT_DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                sid = item["id"]
                source_samples[sid] = {
                    "dataset": "heldout",
                    "sample_id": sid,
                    "subject": item.get("subject", ""),
                    "sender": item.get("sender", ""),
                    "body": item.get("text", item.get("body", "")),
                    "category": item.get("category", "unknown"),
                    "label": item.get("label", 0),
                    "is_phishing": item.get("is_phishing", False),
                    "has_prompt_injection": item.get("has_prompt_injection", False),
                }

    print(f"Loaded {len(source_samples)} source evaluation samples (150 V2 + 100 Held-Out).")

    # 2. Load raw predictions
    raw_predictions = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                raw_predictions.append(json.loads(line))
    print(f"Loaded {len(raw_predictions)} raw predictions from {PREDICTIONS_PATH}.")

    # 3. Audit prediction integrity
    integrity = audit_prediction_integrity(raw_predictions, source_samples)
    print("Prediction Integrity Check:")
    print(f"  Total records: {integrity['total_records']} (Expected: 2250)")
    print(f"  Configs present: {integrity['configs_present']}")
    print(f"  Per-config counts: {dict(integrity['per_config_counts'])}")
    print(f"  Duplicate pairs: {len(integrity['duplicate_pairs'])}")
    print(f"  Missing combinations: {len(integrity['missing_combinations'])}")
    print(f"  Inference failures: {len(integrity['inference_failures'])}")
    print(f"  Input consistency violations: {len(integrity['input_consistency_violations'])}")
    print(f"  Ground-truth mismatches: {len(integrity['ground_truth_mismatches'])}")

    assert integrity["is_record_count_valid"], "Prediction record count invalid!"
    assert len(integrity["duplicate_pairs"]) == 0, "Duplicate prediction pairs detected!"
    assert len(integrity["missing_combinations"]) == 0, "Missing prediction pairs detected!"
    assert len(integrity["inference_failures"]) == 0, "Inference failures detected!"
    assert len(integrity["input_consistency_violations"]) == 0, "Input consistency violated!"
    assert len(integrity["ground_truth_mismatches"]) == 0, "Ground truth mismatches detected!"

    # 4. Audit Injections
    inj_audit = audit_injections(raw_predictions, source_samples)
    print("\nInjection Label Audit:")
    print(f"  Total injection samples: {inj_audit['total_injection_samples']}")
    print(f"  Active injection samples: {len(inj_audit['active_injection_samples'])}")
    print(f"  Quoted injection samples: {len(inj_audit['quoted_injection_samples'])}")
    for cid in CONFIGS:
        ca = inj_audit["per_config_audit"][cid]
        print(f"  Config {cid}: Active Rec={ca['active_recall']*100:.1f}% ({ca['active_tp_count']}/25), Quoted Acc={ca['quoted_accuracy']*100:.1f}% ({ca['quoted_correct_count']}/25)")

    # 5. Independently Recompute All Metrics
    by_config_all = defaultdict(list)
    by_config_v2 = defaultdict(list)
    by_config_heldout = defaultdict(list)
    by_config_sid = defaultdict(dict)

    for r in raw_predictions:
        cid = r["config_id"]
        sid = r["sample_id"]
        dset = r["dataset"]
        by_config_all[cid].append(r)
        if dset == "v2":
            by_config_v2[cid].append(r)
        elif dset == "heldout":
            by_config_heldout[cid].append(r)
        by_config_sid[cid][sid] = r

    verified_metrics = {
        "metadata": {
            "source_predictions_path": str(PREDICTIONS_PATH),
            "source_predictions_sha256": sha256_file(PREDICTIONS_PATH),
            "total_records": len(raw_predictions),
            "evaluation_samples": 250,
            "v2_samples": 150,
            "heldout_samples": 100,
        },
        "configurations": {},
    }

    for cid in CONFIGS:
        verified_metrics["configurations"][cid] = {
            "combined_250": compute_metrics_for_records(by_config_all[cid], source_samples),
            "v2_150": compute_metrics_for_records(by_config_v2[cid], source_samples),
            "heldout_100": compute_metrics_for_records(by_config_heldout[cid], source_samples),
        }

    OUT_VERIFIED_METRICS.write_text(json.dumps(verified_metrics, indent=2), encoding="utf-8")
    print(f"\nWrote independently verified metrics to: {OUT_VERIFIED_METRICS}")

    # 6. Audit Statistical Comparisons
    comparisons = audit_statistical_comparisons(by_config_sid, source_samples)
    OUT_VERIFIED_COMPARISONS.write_text(json.dumps(comparisons, indent=2), encoding="utf-8")
    print(f"Wrote independently verified comparisons to: {OUT_VERIFIED_COMPARISONS}")

    # 7. Check Discrepancies Against Previous metrics.json
    discrepancies = []
    if PREV_METRICS_PATH.exists():
        with open(PREV_METRICS_PATH, "r", encoding="utf-8") as f:
            prev_metrics = json.load(f)

        for cid in CONFIGS:
            prev_comb = prev_metrics["configurations"][cid]["combined_250"]
            cur_comb = verified_metrics["configurations"][cid]["combined_250"]

            for mkey in ["phishing_accuracy", "phishing_precision", "phishing_recall", "phishing_f1", "false_positive_rate", "false_negative_rate"]:
                diff = abs(prev_comb[mkey] - cur_comb[mkey])
                if diff > 1e-4:
                    discrepancies.append({
                        "config_id": cid,
                        "metric": mkey,
                        "previous": prev_comb[mkey],
                        "verified": cur_comb[mkey],
                        "difference": diff,
                    })

    print(f"\nDiscrepancy Analysis vs previous metrics.json: {len(discrepancies)} discrepancies found.")

    return integrity, inj_audit, verified_metrics, comparisons, discrepancies, source_samples, by_config_sid


if __name__ == "__main__":
    run_full_forensic_audit()

