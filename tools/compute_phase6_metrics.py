"""Independent Metrics Computation Engine for Phase 6.

Processes results/phase6_domain_evidence/predictions.jsonl and generates
results/phase6_domain_evidence/independent_metrics.json.

Strict Rules:
- Source of truth is raw predictions.jsonl only.
- Computes overall, per-dataset (regression_160 vs challenge_40), and per-category metrics.
- Computes operational security containment alongside binary classification metrics.
- Validates invariance between Config A and Config C.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

PREDS_FILE = Path("results/phase6_domain_evidence/predictions.jsonl")
METRICS_OUT = Path("results/phase6_domain_evidence/independent_metrics.json")


def calc_binary_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(1 for r in records if r["ground_truth_is_phishing"] and r["is_phishing"])
    tn = sum(1 for r in records if not r["ground_truth_is_phishing"] and not r["is_phishing"])
    fp = sum(1 for r in records if not r["ground_truth_is_phishing"] and r["is_phishing"])
    fn = sum(1 for r in records if r["ground_truth_is_phishing"] and not r["is_phishing"])

    total = len(records)
    positives = tp + fn
    negatives = tn + fp

    acc = (tp + tn) / total if total > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / positives if positives > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    fpr = fp / negatives if negatives > 0 else 0.0
    fnr = fn / positives if positives > 0 else 0.0

    return {
        "sample_count": total,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "fnr": round(fnr, 4),
        "confusion_matrix": {
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp_formula": f"{tp}/{positives} ({rec*100:.1f}%)" if positives > 0 else "0/0",
            "fp_formula": f"{fp}/{negatives} ({fpr*100:.1f}%)" if negatives > 0 else "0/0",
            "tn_formula": f"{tn}/{negatives} ({tn/negatives*100:.1f}%)" if negatives > 0 else "0/0",
            "fn_formula": f"{fn}/{positives} ({fnr*100:.1f}%)" if positives > 0 else "0/0",
        },
    }


def calc_latency_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    def stats(values: list[float]) -> dict[str, float]:
        if not values:
            return {"mean_ms": 0.0, "median_ms": 0.0, "p95_ms": 0.0}
        s = sorted(values)
        n = len(s)
        mean_val = sum(s) / n
        median_val = s[n // 2] if n % 2 != 0 else (s[n // 2 - 1] + s[n // 2]) / 2.0
        p95_idx = min(int(math.ceil(0.95 * n)) - 1, n - 1)
        return {
            "mean_ms": round(mean_val, 2),
            "median_ms": round(median_val, 2),
            "p95_ms": round(s[p95_idx], 2),
        }

    s1 = [float(r.get("stage1_latency_ms", 0.0)) for r in records if r.get("stage1_latency_ms")]
    s2 = [float(r.get("stage2_latency_ms", 0.0)) for r in records if r.get("stage2_latency_ms")]
    tot = [float(r.get("total_latency_ms", 0.0)) for r in records if r.get("total_latency_ms")]

    return {
        "stage1": stats(s1),
        "stage2": stats(s2),
        "total": stats(tot),
    }


def compute():
    if not PREDS_FILE.exists():
        print(f"Error: {PREDS_FILE} does not exist.")
        return

    records_by_config: dict[str, list[dict[str, Any]]] = {}
    with open(PREDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                cfg = r["config_id"]
                if cfg not in records_by_config:
                    records_by_config[cfg] = []
                records_by_config[cfg].append(r)

    print("Records per configuration in predictions.jsonl:")
    for cfg, recs in records_by_config.items():
        print(f"  Config {cfg}: {len(recs)} records")

    metrics_output: dict[str, Any] = {
        "total_records": sum(len(r) for r in records_by_config.values()),
        "configurations": {},
        "pairwise_attributions": {},
    }

    for cfg, recs in records_by_config.items():
        reg_recs = [r for r in recs if r["dataset"] == "phase5_regression_160"]
        chal_recs = [r for r in recs if r["dataset"] == "phase6_domain_challenge"]

        cfg_metrics = {
            "total_evaluated": len(recs),
            "overall": calc_binary_metrics(recs),
            "latency": calc_latency_stats(recs),
        }

        if reg_recs:
            cfg_metrics["regression_160"] = calc_binary_metrics(reg_recs)
            # Add specific categories
            cat_breakdown = {}
            for c in ["active_injection", "quoted_injection", "difficult_legitimate", "sophisticated_phishing", "ordinary_genuine"]:
                cat_subset = [r for r in reg_recs if r.get("category") == c or (c == "active_injection" and r.get("subcategory", "").startswith("active_")) or (c == "quoted_injection" and r.get("subcategory", "").startswith("quoted_"))]
                if cat_subset:
                    cat_breakdown[c] = {
                        "count": len(cat_subset),
                        "accuracy": round(sum(1 for r in cat_subset if r["is_phishing"] == r["ground_truth_is_phishing"]) / len(cat_subset), 4),
                        "contained": sum(1 for r in cat_subset if r.get("security_action") in ("quarantine_review", "block")),
                    }
            cfg_metrics["regression_160"]["category_breakdown"] = cat_breakdown

        if chal_recs:
            cfg_metrics["challenge_40"] = calc_binary_metrics(chal_recs)
            sop_phish = [r for r in chal_recs if r["category"] == "sophisticated_phishing"]
            dif_legit = [r for r in chal_recs if r["category"] == "difficult_legitimate"]
            cfg_metrics["challenge_40"]["sophisticated_phishing_recall"] = {
                "tp": sum(1 for r in sop_phish if r["is_phishing"]),
                "total": len(sop_phish),
                "recall": round(sum(1 for r in sop_phish if r["is_phishing"]) / len(sop_phish), 4) if sop_phish else 0.0,
            }
            cfg_metrics["challenge_40"]["difficult_legitimate_fpr"] = {
                "fp": sum(1 for r in dif_legit if r["is_phishing"]),
                "total": len(dif_legit),
                "fpr": round(sum(1 for r in dif_legit if r["is_phishing"]) / len(dif_legit), 4) if dif_legit else 0.0,
            }

        metrics_output["configurations"][cfg] = cfg_metrics

    # Check Invariance between Config A and Config C
    if "A" in records_by_config and "C" in records_by_config:
        a_map = {r["sample_id"]: r for r in records_by_config["A"]}
        c_map = {r["sample_id"]: r for r in records_by_config["C"]}
        divergences = []
        for sid, c_rec in c_map.items():
            if sid in a_map:
                a_rec = a_map[sid]
                if a_rec["is_phishing"] != c_rec["is_phishing"]:
                    divergences.append({
                        "sample_id": sid,
                        "pred_A": a_rec["is_phishing"],
                        "pred_C": c_rec["is_phishing"],
                    })

        metrics_output["pairwise_attributions"]["A_vs_C_invariance"] = {
            "samples_compared": len(c_map),
            "divergences_count": len(divergences),
            "divergences": divergences,
            "invariant": len(divergences) == 0,
        }
        print(f"Config A vs Config C Invariance check: {len(divergences)} divergences across {len(c_map)} samples.")

    # Attribution: Config A vs Config B
    if "A" in records_by_config and "B" in records_by_config:
        b_map = {r["sample_id"]: r for r in records_by_config["B"]}
        a_map = {r["sample_id"]: r for r in records_by_config["A"]}
        common_sids = set(a_map.keys()).intersection(set(b_map.keys()))

        a_common = [a_map[sid] for sid in common_sids]
        b_common = [b_map[sid] for sid in common_sids]

        m_a = calc_binary_metrics(a_common)
        m_b = calc_binary_metrics(b_common)

        metrics_output["pairwise_attributions"]["A_vs_B_domain_evidence"] = {
            "common_samples": len(common_sids),
            "config_A_accuracy": m_a["accuracy"],
            "config_B_accuracy": m_b["accuracy"],
            "delta_accuracy": round(m_b["accuracy"] - m_a["accuracy"], 4),
            "config_A_recall": m_a["recall"],
            "config_B_recall": m_b["recall"],
            "delta_recall": round(m_b["recall"] - m_a["recall"], 4),
            "config_A_fpr": m_a["fpr"],
            "config_B_fpr": m_b["fpr"],
            "delta_fpr": round(m_b["fpr"] - m_a["fpr"], 4),
        }
        print(f"Config A vs B Delta Accuracy: {m_b['accuracy'] - m_a['accuracy']:+.4f}, Delta Recall: {m_b['recall'] - m_a['recall']:+.4f}")

    with open(METRICS_OUT, "w", encoding="utf-8") as f:
        json.dump(metrics_output, f, indent=2)
    print(f"Metrics written to {METRICS_OUT}.")


if __name__ == "__main__":
    compute()

