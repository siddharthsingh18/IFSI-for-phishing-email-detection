"""Dual Evaluation Suite: M4 Baseline vs M4 Experimental (v2).

Evaluates both models across:
1. Live Benchmark V2 (150 samples)
2. Fresh Held-Out Benchmark V1 (100 samples)

Outputs:
- results/m4_experiment_v1/predictions.jsonl
- results/m4_experiment_v1/metrics.json
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")
root_dir = Path(__file__).resolve().parents[1]
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from core.inference import classify_email_m4
from core.inference_m4_v2 import classify_email_m4_v2
from core.model_config import DEFAULT_LIVE_MODEL


def format_email_text(subject: str, sender: str, body: str) -> str:
    headers = []
    if subject.strip():
        headers.append(f"Subject: {subject.strip()}")
    if sender.strip():
        headers.append(f"From: {sender.strip()}")
    if headers:
        return f"{'\n'.join(headers)}\n\n{body.strip()}".strip()
    return body.strip()


def compute_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    if total == 0:
        return {}

    tp = tn = fp = fn = 0
    latencies = []
    failed_count = 0

    inj_total = 0
    inj_tp = 0
    inj_fp = 0
    inj_tn = 0
    inj_fn = 0

    action_counts = {"allow": 0, "block": 0, "quarantine_review": 0, "manual_review": 0}

    for r in records:
        yt = int(r["ground_truth_label"])
        yp = int(r["predicted_phishing_label"])
        lat = r.get("latency_seconds", 0.0)
        latencies.append(lat)
        if not r.get("is_valid", True):
            failed_count += 1

        act = r.get("security_action", "allow")
        action_counts[act] = action_counts.get(act, 0) + 1

        if yt == 1 and yp == 1:
            tp += 1
        elif yt == 0 and yp == 0:
            tn += 1
        elif yt == 0 and yp == 1:
            fp += 1
        elif yt == 1 and yp == 0:
            fn += 1

        # Injection metrics
        gt_inj = bool(r.get("ground_truth_injection", False))
        pred_inj = bool(r.get("has_prompt_injection", False))
        if gt_inj:
            inj_total += 1
            if pred_inj:
                inj_tp += 1
            else:
                inj_fn += 1
        else:
            if pred_inj:
                inj_fp += 1
            else:
                inj_tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    inj_recall = inj_tp / (inj_tp + inj_fn) if (inj_tp + inj_fn) > 0 else 0.0
    inj_precision = inj_tp / (inj_tp + inj_fp) if (inj_tp + inj_fp) > 0 else 0.0

    return {
        "total_samples": total,
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "fnr": round(fnr, 4),
        "avg_latency_seconds": round(statistics.mean(latencies), 4) if latencies else 0.0,
        "median_latency_seconds": round(statistics.median(latencies), 4) if latencies else 0.0,
        "failed_inference_count": failed_count,
        "injection_metrics": {
            "total_injection_ground_truth": inj_total,
            "true_positives": inj_tp,
            "false_negatives": inj_fn,
            "false_positives": inj_fp,
            "true_negatives": inj_tn,
            "recall": round(inj_recall, 4),
            "precision": round(inj_precision, 4),
        },
        "security_actions": action_counts,
        "confusion_matrix": [
            [tn, fp],
            [fn, tp],
        ],
    }


def compute_slice_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    categories = sorted(list({r["category"] for r in records}))
    slice_res = {}
    for cat in categories:
        cat_recs = [r for r in records if r["category"] == cat]
        slice_res[cat] = compute_metrics(cat_recs)
    return slice_res


def main():
    out_dir = root_dir / "results" / "m4_experiment_v1"
    out_dir.mkdir(parents=True, exist_ok=True)
    preds_file = out_dir / "predictions.jsonl"
    metrics_file = out_dir / "metrics.json"

    # Load existing predictions to enable resume
    existing_preds: dict[tuple[str, str, str], dict] = {}
    if preds_file.exists():
        with open(preds_file, "r", encoding="utf-8") as pf:
            for line in pf:
                if line.strip():
                    d = json.loads(line)
                    k = (d.get("dataset_name", "v2"), d["email_id"], d["architecture"])
                    existing_preds[k] = d
        print(f"Loaded {len(existing_preds)} existing experimental predictions.")

    # Datasets to evaluate
    datasets = [
        ("live_benchmark_v2", root_dir / "data" / "evaluation" / "live_benchmark_v2.jsonl"),
        ("heldout_benchmark_v1", root_dir / "data" / "evaluation" / "heldout_benchmark_v1.jsonl"),
    ]

    all_records_by_key: dict[tuple[str, str], list[dict]] = {
        ("live_benchmark_v2", "M4_Baseline"): [],
        ("live_benchmark_v2", "M4_Experimental"): [],
        ("heldout_benchmark_v1", "M4_Baseline"): [],
        ("heldout_benchmark_v1", "M4_Experimental"): [],
    }

    # Historical V2 predictions lookup for M4 Baseline
    v2_hist_m4: dict[str, dict] = {}
    hist_v2_path = root_dir / "results" / "live_benchmark_v2" / "predictions.jsonl"
    if hist_v2_path.exists():
        with open(hist_v2_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    if d.get("architecture") == "M4":
                        v2_hist_m4[d["email_id"]] = d

    with open(preds_file, "a", encoding="utf-8") as pf:
        for ds_name, ds_path in datasets:
            print(f"\n=======================================================")
            print(f"EVALUATING DATASET: {ds_name} ({ds_path.name})")
            print(f"=======================================================")
            with open(ds_path, "r", encoding="utf-8") as df:
                items = [json.loads(line) for line in df if line.strip()]

            for idx, item in enumerate(items, 1):
                eid = item["id"]
                cat = item["category"]
                subcat = item.get("subcategory", "")
                gt_label = 1 if item["is_phishing"] else 0
                gt_inj = bool(item.get("has_prompt_injection", False))
                subj = item.get("subject", "")
                sndr = item.get("sender", "")
                body = item.get("body", "")
                fmt_text = format_email_text(subj, sndr, body)

                # -------------------------------------------------------------
                # 1. M4 Baseline
                # -------------------------------------------------------------
                k_base = (ds_name, eid, "M4_Baseline")
                if k_base in existing_preds:
                    rec_base = existing_preds[k_base]
                elif ds_name == "live_benchmark_v2" and eid in v2_hist_m4:
                    # Inherit verified historical baseline prediction
                    hist = v2_hist_m4[eid]
                    rec_base = {
                        "dataset_name": ds_name,
                        "email_id": eid,
                        "category": cat,
                        "subcategory": subcat,
                        "ground_truth_label": gt_label,
                        "ground_truth_injection": gt_inj,
                        "architecture": "M4_Baseline",
                        "architecture_name": "M4 Baseline (Production Decoupled RAG)",
                        "predicted_phishing_label": hist["predicted_phishing_label"],
                        "predicted_verdict": hist["predicted_verdict"],
                        "confidence": hist["confidence"],
                        "has_prompt_injection": hist["has_prompt_injection"],
                        "active_prompt_injection": hist["has_prompt_injection"],
                        "quoted_prompt_injection": False,
                        "injection_verdict": hist.get("injection_verdict", "clean"),
                        "security_action": hist.get("security_action", "allow"),
                        "latency_seconds": hist.get("latency_seconds", 0.0),
                        "is_valid": hist.get("is_valid", True),
                        "failure_type": hist.get("failure_type"),
                        "failure_message": hist.get("failure_message"),
                        "reasons": hist.get("reasons", []),
                    }
                    pf.write(json.dumps(rec_base, ensure_ascii=False) + "\n")
                    pf.flush()
                    existing_preds[k_base] = rec_base
                else:
                    # Run live inference for M4 Baseline (e.g. held-out dataset)
                    t0 = time.perf_counter()
                    res_b = classify_email_m4(fmt_text, model=DEFAULT_LIVE_MODEL, top_k=3)
                    dur_b = time.perf_counter() - t0
                    p_label_b = 1 if res_b.get("is_phishing", False) else 0
                    rec_base = {
                        "dataset_name": ds_name,
                        "email_id": eid,
                        "category": cat,
                        "subcategory": subcat,
                        "ground_truth_label": gt_label,
                        "ground_truth_injection": gt_inj,
                        "architecture": "M4_Baseline",
                        "architecture_name": "M4 Baseline (Production Decoupled RAG)",
                        "predicted_phishing_label": p_label_b,
                        "predicted_verdict": res_b.get("phishing_verdict", "phishing" if p_label_b == 1 else "legitimate"),
                        "confidence": float(res_b.get("confidence", 0.0)),
                        "has_prompt_injection": bool(res_b.get("has_prompt_injection", False)),
                        "active_prompt_injection": bool(res_b.get("has_prompt_injection", False)),
                        "quoted_prompt_injection": False,
                        "injection_verdict": res_b.get("injection_verdict", "clean"),
                        "security_action": res_b.get("security_action", "allow"),
                        "latency_seconds": round(dur_b, 4),
                        "is_valid": res_b.get("is_valid", True),
                        "failure_type": res_b.get("failure_type"),
                        "failure_message": res_b.get("failure_message"),
                        "reasons": res_b.get("reasons", []),
                    }
                    pf.write(json.dumps(rec_base, ensure_ascii=False) + "\n")
                    pf.flush()
                    existing_preds[k_base] = rec_base
                all_records_by_key[(ds_name, "M4_Baseline")].append(rec_base)

                # -------------------------------------------------------------
                # 2. M4 Experimental (v2)
                # -------------------------------------------------------------
                k_exp = (ds_name, eid, "M4_Experimental")
                if k_exp in existing_preds:
                    rec_exp = existing_preds[k_exp]
                else:
                    t0 = time.perf_counter()
                    res_e = classify_email_m4_v2(
                        fmt_text,
                        subject=subj,
                        sender=sndr,
                        model=DEFAULT_LIVE_MODEL,
                        k_phish=2,
                        k_legit=2,
                    )
                    dur_e = time.perf_counter() - t0
                    p_label_e = 1 if res_e.get("is_phishing", False) else 0
                    rec_exp = {
                        "dataset_name": ds_name,
                        "email_id": eid,
                        "category": cat,
                        "subcategory": subcat,
                        "ground_truth_label": gt_label,
                        "ground_truth_injection": gt_inj,
                        "architecture": "M4_Experimental",
                        "architecture_name": "M4 Experimental (v2 Decoupled RAG)",
                        "predicted_phishing_label": p_label_e,
                        "predicted_verdict": res_e.get("phishing_verdict", "phishing" if p_label_e == 1 else "legitimate"),
                        "confidence": float(res_e.get("confidence", 0.0)),
                        "has_prompt_injection": bool(res_e.get("has_prompt_injection", False)),
                        "active_prompt_injection": bool(res_e.get("active_prompt_injection", False)),
                        "quoted_prompt_injection": bool(res_e.get("quoted_prompt_injection", False)),
                        "injection_type": res_e.get("injection_type", "none"),
                        "injection_verdict": res_e.get("injection_verdict", "clean"),
                        "security_action": res_e.get("security_action", "allow"),
                        "latency_seconds": round(dur_e, 4),
                        "is_valid": res_e.get("is_valid", True),
                        "failure_type": res_e.get("failure_type"),
                        "failure_message": res_e.get("failure_message"),
                        "reasons": res_e.get("reasons", []),
                    }
                    pf.write(json.dumps(rec_exp, ensure_ascii=False) + "\n")
                    pf.flush()
                    existing_preds[k_exp] = rec_exp

                all_records_by_key[(ds_name, "M4_Experimental")].append(rec_exp)

                if idx % 10 == 0 or idx == len(items):
                    b_p = rec_base["predicted_phishing_label"]
                    e_p = rec_exp["predicted_phishing_label"]
                    print(
                        f"[{ds_name} {idx:03d}/{len(items):03d}] {eid} | GT:{gt_label} | "
                        f"Base:{b_p} ({rec_base['security_action']}) | "
                        f"Exp:{e_p} ({rec_exp['security_action']})"
                    )

    # Compute comprehensive metrics
    metrics_summary: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": DEFAULT_LIVE_MODEL,
        "evaluations": {},
    }

    for (ds_name, arch_name), recs in all_records_by_key.items():
        print(f"\nComputing metrics for {ds_name} - {arch_name} ({len(recs)} samples)...")
        overall = compute_metrics(recs)
        by_slice = compute_slice_metrics(recs)
        key = f"{ds_name}__{arch_name}"
        metrics_summary["evaluations"][key] = {
            "dataset": ds_name,
            "architecture": arch_name,
            "overall": overall,
            "by_slice": by_slice,
        }

    with open(metrics_file, "w", encoding="utf-8") as mf:
        json.dump(metrics_summary, mf, indent=2, ensure_ascii=False)

    print(f"\nEvaluation Complete! Metrics saved to {metrics_file}")
    print(f"Predictions saved to {preds_file}")


if __name__ == "__main__":
    main()

