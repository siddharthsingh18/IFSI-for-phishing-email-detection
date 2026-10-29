"""Generalization and Model Comparison Evaluation Runner.
Evaluates M1, M2, M3, M4 on a held-out dataset across qwen2.5:0.5b and qwen3.5:4b.
Held-out dataset:
- 6 clean phishing from val.jsonl (unseen in train.jsonl or RAG index)
- 6 clean legitimate from val.jsonl (unseen in train.jsonl or RAG index)
- 4 marked attacked phishing (from marked-phishing.jsonl)
- 4 unmarked attacked phishing (from unmarked-phishing.jsonl)
- 4 marked control legitimate (from marked-control.jsonl)
- 4 unmarked control legitimate (from unmarked-control.jsonl)
Total: 28 balanced samples (14 phishing, 14 legitimate).
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

# Ensure src in path
sys.path.insert(0, str(Path("src").resolve()))

from core.inference import (
    classify_email_m1,
    classify_email_m2,
    classify_email_m3,
    classify_email_m4,
)


def load_held_out_dataset() -> list[dict]:
    dataset = []

    # 1. Load clean samples from val.jsonl (seeded but never used for train.jsonl or rag index)
    val_path = Path("data/splits/review_seed42/val.jsonl")
    if val_path.exists():
        with open(val_path, "r", encoding="utf-8") as f:
            val_items = [json.loads(line) for line in f if line.strip()]
        
        phish_val = [v for v in val_items if v.get("label") in (1, "1", "phishing")][:6]
        legit_val = [v for v in val_items if v.get("label") in (0, "0", "legitimate")][:6]

        for idx, item in enumerate(phish_val, 1):
            dataset.append({
                "id": f"heldout-clean-phish-{idx:02d}",
                "category": "clean_phishing",
                "true_label": 1,
                "subject": item.get("subject", ""),
                "sender": item.get("sender", ""),
                "body": item.get("body", ""),
                "text": item.get("text", item.get("body", "")),
            })

        for idx, item in enumerate(legit_val, 1):
            dataset.append({
                "id": f"heldout-clean-legit-{idx:02d}",
                "category": "clean_legitimate",
                "true_label": 0,
                "subject": item.get("subject", ""),
                "sender": item.get("sender", ""),
                "body": item.get("body", ""),
                "text": item.get("text", item.get("body", "")),
            })

    # 2. Load marked injection samples
    mp_path = Path("data/injections/marked-phishing.jsonl")
    if mp_path.exists():
        with open(mp_path, "r", encoding="utf-8") as f:
            mp_items = [json.loads(line) for line in f if line.strip()][:4]
        for idx, item in enumerate(mp_items, 1):
            full_text = item.get("text") or item.get("injected_text", "")
            dataset.append({
                "id": f"heldout-marked-phish-{idx:02d}",
                "category": "marked_attacked_phishing",
                "true_label": 1,
                "subject": item.get("subject", ""),
                "sender": item.get("sender", ""),
                "body": full_text,
                "text": full_text,
            })

    # 3. Load unmarked injection samples
    up_path = Path("data/injections/unmarked-phishing.jsonl")
    if up_path.exists():
        with open(up_path, "r", encoding="utf-8") as f:
            up_items = [json.loads(line) for line in f if line.strip()][:4]
        for idx, item in enumerate(up_items, 1):
            full_text = item.get("text") or item.get("injected_text", "")
            dataset.append({
                "id": f"heldout-unmarked-phish-{idx:02d}",
                "category": "unmarked_attacked_phishing",
                "true_label": 1,
                "subject": item.get("subject", ""),
                "sender": item.get("sender", ""),
                "body": full_text,
                "text": full_text,
            })

    # 4. Load marked control legitimate samples
    mc_path = Path("data/injections/marked-control.jsonl")
    if mc_path.exists():
        with open(mc_path, "r", encoding="utf-8") as f:
            mc_items = [json.loads(line) for line in f if line.strip()][:4]
        for idx, item in enumerate(mc_items, 1):
            full_text = item.get("text") or item.get("injected_text", "")
            dataset.append({
                "id": f"heldout-marked-control-{idx:02d}",
                "category": "marked_control_legitimate",
                "true_label": 0,
                "subject": item.get("subject", ""),
                "sender": item.get("sender", ""),
                "body": full_text,
                "text": full_text,
            })

    # 5. Load unmarked control legitimate samples
    uc_path = Path("data/injections/unmarked-control.jsonl")
    if uc_path.exists():
        with open(uc_path, "r", encoding="utf-8") as f:
            uc_items = [json.loads(line) for line in f if line.strip()][:4]
        for idx, item in enumerate(uc_items, 1):
            full_text = item.get("text") or item.get("injected_text", "")
            dataset.append({
                "id": f"heldout-unmarked-control-{idx:02d}",
                "category": "unmarked_control_legitimate",
                "true_label": 0,
                "subject": item.get("subject", ""),
                "sender": item.get("sender", ""),
                "body": full_text,
                "text": full_text,
            })

    return dataset


def evaluate_generalization(model_name: str = "qwen2.5:0.5b"):
    dataset = load_held_out_dataset()
    print("=" * 80)
    print(f"HELDOUT GENERALIZATION EVALUATION (Model: {model_name}, Total Samples: {len(dataset)})")
    labels = [d["true_label"] for d in dataset]
    print(f"Distribution: Phishing={labels.count(1)} | Legitimate={labels.count(0)}")
    print("=" * 80)

    methods = ["M1", "M2", "M3", "M4"]
    raw_results: dict[str, list[dict]] = {m: [] for m in methods}
    latencies: dict[str, list[float]] = {m: [] for m in methods}

    for idx, sample in enumerate(dataset, 1):
        text = sample["text"]
        true_label = sample["true_label"]
        cat = sample["category"]

        print(f"[{idx:02d}/{len(dataset):02d}] {sample['id']} ({cat}) | True: {'PHISH' if true_label==1 else 'LEGIT'}")

        # M1
        t0 = time.perf_counter()
        try:
            r1 = classify_email_m1(text)
        except Exception as e:
            r1 = {"verdict": "error", "is_phishing": False, "is_valid": False, "failure_message": str(e), "latency_ms": 0}
        dur1 = (time.perf_counter() - t0) * 1000
        latencies["M1"].append(dur1)
        raw_results["M1"].append({"sample": sample, "res": r1, "dur_ms": dur1})

        # M2
        t0 = time.perf_counter()
        r2 = classify_email_m2(text, model=model_name)
        dur2 = (time.perf_counter() - t0) * 1000
        latencies["M2"].append(dur2)
        raw_results["M2"].append({"sample": sample, "res": r2, "dur_ms": dur2})

        # M3
        t0 = time.perf_counter()
        r3 = classify_email_m3(text, model=model_name)
        dur3 = (time.perf_counter() - t0) * 1000
        latencies["M3"].append(dur3)
        raw_results["M3"].append({"sample": sample, "res": r3, "dur_ms": dur3})

        # M4
        t0 = time.perf_counter()
        r4 = classify_email_m4(text, model=model_name)
        dur4 = (time.perf_counter() - t0) * 1000
        latencies["M4"].append(dur4)
        raw_results["M4"].append({"sample": sample, "res": r4, "dur_ms": dur4})

        p1 = r1.get("is_phishing", False)
        p2 = r2.get("is_phishing", False)
        p3 = r3.get("is_phishing", False)
        p4 = r4.get("is_phishing", False)
        print(f"   M1={p1:<5} ({dur1:4.0f}ms) | M2={p2:<5} ({dur2:4.0f}ms) | M3={p3:<5} ({dur3:4.0f}ms) | M4={p4:<5} inj={r4.get('has_injection')} ({dur4:4.0f}ms)")

    # Metrics computation
    metrics_summary = {}
    print("\n" + "=" * 80)
    print(f"METRICS SUMMARY FOR MODEL: {model_name}")
    print("=" * 80)

    for m in methods:
        entries = raw_results[m]
        tp = fp = tn = fn = 0
        invalid = 0
        cat_stats: dict[str, dict[str, int]] = {}

        for item in entries:
            sample = item["sample"]
            res = item["res"]
            true_p = (sample["true_label"] == 1)
            cat = sample["category"]

            if cat not in cat_stats:
                cat_stats[cat] = {"total": 0, "correct": 0}
            cat_stats[cat]["total"] += 1

            if not res.get("is_valid", True):
                invalid += 1

            pred_p = bool(res.get("is_phishing", False))
            if pred_p and true_p:
                tp += 1
                cat_stats[cat]["correct"] += 1
            elif pred_p and not true_p:
                fp += 1
            elif not pred_p and not true_p:
                tn += 1
                cat_stats[cat]["correct"] += 1
            elif not pred_p and true_p:
                fn += 1

        total = len(entries)
        acc = (tp + tn) / total if total else 0.0
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) else 0.0
        fpr = fp / (fp + tn) if (fp + tn) else 0.0
        fnr = fn / (fn + tp) if (fn + tp) else 0.0

        mean_lat = statistics.mean(latencies[m])
        med_lat = statistics.median(latencies[m])

        metrics_summary[m] = {
            "total": total,
            "invalid": invalid,
            "TP": tp,
            "FP": fp,
            "TN": tn,
            "FN": fn,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "fpr": round(fpr, 4),
            "fnr": round(fnr, 4),
            "mean_latency_ms": round(mean_lat, 2),
            "median_latency_ms": round(med_lat, 2),
            "category_breakdown": {
                c: f"{s['correct']}/{s['total']} ({round(s['correct']/s['total']*100, 1)}%)"
                for c, s in cat_stats.items()
            },
        }

        print(f"\n--- Method: {m} ---")
        print(f"  Confusion Matrix : TP={tp:<2} | FP={fp:<2} | TN={tn:<2} | FN={fn:<2}")
        print(f"  Accuracy         : {acc * 100:.2f}%")
        print(f"  Precision        : {prec * 100:.2f}%")
        print(f"  Recall           : {rec * 100:.2f}%")
        print(f"  F1-Score         : {f1 * 100:.2f}%")
        print(f"  FPR (False Alarm): {fpr * 100:.2f}%")
        print(f"  FNR (Missed Phish): {fnr * 100:.2f}%")
        print(f"  Latency (Mean)   : {mean_lat:.2f} ms | Median: {med_lat:.2f} ms")
        print(f"  Invalid / Errors : {invalid} of {total}")
        for c, s in metrics_summary[m]["category_breakdown"].items():
            print(f"    - {c:<28}: {s}")

    return {
        "model": model_name,
        "metrics": metrics_summary,
        "raw_results": [
            {
                "sample_id": item["sample"]["id"],
                "category": item["sample"]["category"],
                "true_label": item["sample"]["true_label"],
                "predictions": {m: raw_results[m][i]["res"] for m in methods},
            }
            for i, item in enumerate(raw_results["M1"])
        ],
    }


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:0.5b"
    res = evaluate_generalization(model)
    out_file = Path(f"scratch/generalization_results_{model.replace(':', '_')}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(f"\nSaved generalization results to {out_file}")

