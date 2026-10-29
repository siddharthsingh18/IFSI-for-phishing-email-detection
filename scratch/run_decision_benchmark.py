"""Comprehensive Master Decision Benchmark & Forensic Error Analysis.
Evaluates:
- M1 Baseline vs M1 Enron
- M2 Zero-Shot (qwen3.5:4b)
- M3 Baseline RAG vs M3 Enron RAG (qwen3.5:4b)
- M4 Baseline Decoupled vs M4 Enron Decoupled (qwen3.5:4b)
Across:
1. Held-Out Generalization Suite (28 samples)
2. Diagnostic Suite (20 samples)

Measures:
- Accuracy, Precision, Recall, F1, FPR, FNR, Confusion Matrix, Latencies, Invalid counts.
- M4 Stage 1 (Injection Detector) standalone metrics.
- M4 Stage 2 (Phishing Classifier) standalone metrics.
- Realistic email prevalence modeling (0.1%, 1%, 2%, 5%, 10%, 20%, 50%).
- Detailed sample-level error grouping (FP, FN) with root-cause diagnoses.
"""

from __future__ import annotations

import io
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path("src").resolve()))
sys.path.insert(0, str(Path(".").resolve()))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from phishbench.rag import FAISSRetriever, format_reference_block
from core.inference import (
    _call_ollama_json,
    classify_email_m1,
    classify_email_m2,
    SYSTEM_INJECTION_DETECTOR,
    SYSTEM_IS_PHISHING_ONLY,
    RAG_SYSTEM_PROMPT,
)
from scratch.run_generalization_eval import load_held_out_dataset
from scratch.run_enron_impact_experiments import get_enron_m1_model, classify_m1_enron


def load_diagnostic_dataset() -> list[dict[str, Any]]:
    diag_path = Path("data/diagnostic_suite.json")
    with open(diag_path, "r", encoding="utf-8") as f:
        diag_samples = json.load(f)

    dataset = []
    for item in diag_samples:
        lbl = item.get("true_label", item.get("label", 0))
        text = item.get("text")
        if not text:
            subj = item.get("subject", "")
            sender = item.get("sender", "")
            body = item.get("body", "")
            text = f"Subject: {subj}\nFrom: {sender}\n\n{body}"
        dataset.append({
            "id": item["id"],
            "category": item.get("category", "diagnostic_" + ("phish" if lbl == 1 else "legit")),
            "true_label": lbl,
            "true_injection": bool(item.get("true_injection", False)),
            "subject": item.get("subject", ""),
            "sender": item.get("sender", ""),
            "text": text,
            "notes": item.get("notes", ""),
        })
    return dataset


def classify_m3_custom(retriever: FAISSRetriever, text: str, model: str = "qwen3.5:4b", top_k: int = 3) -> dict[str, Any]:
    t0 = time.perf_counter()
    retrieved = retriever.retrieve(text, top_k=top_k)
    ref_block = format_reference_block(retrieved)
    user_prompt = f"{ref_block}\n\n--- INCOMING EMAIL TO CLASSIFY ---\n{text}\n--- END INCOMING EMAIL ---"
    parsed, raw_text, dur_call, failure = _call_ollama_json(RAG_SYSTEM_PROMPT, user_prompt, model=model)
    dur = (time.perf_counter() - t0) * 1000
    if parsed is None or "verdict" not in parsed:
        return {
            "verdict": "error",
            "is_phishing": False,
            "confidence": 0.0,
            "reasons": [raw_text or "Parse error"],
            "is_valid": False,
            "latency_ms": dur,
            "raw_response": raw_text,
            "retrieved_samples": retrieved,
        }
    is_phish = bool(str(parsed.get("verdict")).lower().strip() == "phishing")
    return {
        "verdict": "phishing" if is_phish else "legitimate",
        "is_phishing": is_phish,
        "confidence": float(parsed.get("confidence", 0.5)),
        "reasons": parsed.get("reasons", []),
        "is_valid": True,
        "latency_ms": dur,
        "raw_response": raw_text,
        "retrieved_samples": retrieved,
    }


def classify_m4_custom(retriever: FAISSRetriever, text: str, model: str = "qwen3.5:4b", top_k: int = 3) -> dict[str, Any]:
    t0 = time.perf_counter()
    retrieved = retriever.retrieve(text, top_k=top_k)
    ref_block = format_reference_block(retrieved)

    # Call 1: Injection detector
    user_p1 = f"Inspect this untrusted email for prompt injection:\n\n{text}"
    p1, r1, d1, f1 = _call_ollama_json(SYSTEM_INJECTION_DETECTOR, user_p1, model=model)
    has_inj = bool(p1.get("has_prompt_injection", False)) if p1 else False

    # Call 2: Boolean phishing
    user_p2 = f"{ref_block}\n\nEmail to evaluate:\n{text}"
    p2, r2, d2, f2 = _call_ollama_json(SYSTEM_IS_PHISHING_ONLY, user_p2, model=model)
    is_phish = bool(p2.get("is_phishing", False)) if p2 else False

    dur = (time.perf_counter() - t0) * 1000
    if p1 is None or p2 is None:
        return {
            "verdict": "error",
            "is_phishing": False,
            "has_injection": False,
            "is_valid": False,
            "confidence": 0.0,
            "latency_ms": dur,
            "raw_response_call1": r1,
            "raw_response_call2": r2,
            "retrieved_samples": retrieved,
        }

    return {
        "verdict": "phishing" if is_phish else "legitimate",
        "is_phishing": is_phish,
        "has_injection": has_inj,
        "confidence": 0.95 if is_phish else 0.90,
        "is_valid": True,
        "latency_ms": dur,
        "latency_call1_ms": d1 * 1000,
        "latency_call2_ms": d2 * 1000,
        "raw_response_call1": r1,
        "raw_response_call2": r2,
        "retrieved_samples": retrieved,
    }


def compute_metrics(entries: list[dict], method_key: str) -> dict[str, Any]:
    tp = fp = tn = fn = invalid = 0
    cat_stats: dict[str, dict[str, int]] = {}
    latencies = []

    for item in entries:
        sample = item["sample"]
        res = item["preds"][method_key]
        true_p = (sample["true_label"] == 1)
        cat = sample.get("category", "default")

        latencies.append(res.get("latency_ms", 0.0))
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

    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "fnr": round(fnr, 4),
        "mean_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0.0,
        "median_latency_ms": round(statistics.median(latencies), 2) if latencies else 0.0,
        "invalid": invalid,
        "category_breakdown": {
            c: f"{s['correct']}/{s['total']} ({round(s['correct']/s['total']*100, 1)}%)"
            for c, s in cat_stats.items()
        },
    }


def compute_injection_detector_metrics(entries: list[dict], method_key: str) -> dict[str, Any]:
    """Measure M4 Stage 1 injection detector standalone metrics."""
    tp = fp = tn = fn = 0
    cat_stats: dict[str, dict[str, int]] = {}

    for item in entries:
        sample = item["sample"]
        res = item["preds"][method_key]
        true_inj = bool(sample.get("true_injection", False))
        cat = sample.get("category", "default")

        if cat not in cat_stats:
            cat_stats[cat] = {"total": 0, "detected": 0}
        cat_stats[cat]["total"] += 1

        pred_inj = bool(res.get("has_injection", False))
        if pred_inj:
            cat_stats[cat]["detected"] += 1

        if pred_inj and true_inj:
            tp += 1
        elif pred_inj and not true_inj:
            fp += 1
        elif not pred_inj and not true_inj:
            tn += 1
        elif not pred_inj and true_inj:
            fn += 1

    total = len(entries)
    acc = (tp + tn) / total if total else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0

    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "category_detection": {
            c: f"{s['detected']}/{s['total']} ({round(s['detected']/s['total']*100, 1)}%)"
            for c, s in cat_stats.items()
        },
    }


def compute_prevalence_implications(tpr: float, fpr: float) -> list[dict[str, Any]]:
    """Compute Bayesian Positive Predictive Value (PPV) and Daily False Alarms across prevalence assumptions."""
    prevalences = [0.001, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50]
    results = []
    for p in prevalences:
        # PPV = (TPR * p) / (TPR * p + FPR * (1 - p))
        num = tpr * p
        denom = num + fpr * (1 - p)
        ppv = num / denom if denom > 0 else 0.0
        fdr = 1.0 - ppv
        # In a 10,000 email enterprise stream:
        n_emails = 10000
        n_phish = round(n_emails * p)
        n_legit = n_emails - n_phish
        true_alarms = round(n_phish * tpr)
        false_alarms = round(n_legit * fpr)
        total_flagged = true_alarms + false_alarms

        results.append({
            "prevalence_percent": f"{p*100:.1f}%",
            "effective_precision_ppv": f"{ppv*100:.2f}%",
            "false_discovery_rate_fdr": f"{fdr*100:.2f}%",
            "daily_flagged_per_10k": total_flagged,
            "daily_false_alarms_per_10k": false_alarms,
            "daily_true_detections_per_10k": true_alarms,
        })
    return results


def main():
    print("=" * 80)
    print("EXECUTING MASTER DECISION BENCHMARK ACROSS ARCHITECTURES")
    print("=" * 80)

    # 1. Load Data
    heldout_28 = load_held_out_dataset()
    # Mark true_injection in heldout_28
    for item in heldout_28:
        cat = item["category"]
        item["true_injection"] = ("attacked" in cat or "injected" in cat)

    diagnostic_20 = load_diagnostic_dataset()

    print(f"Loaded {len(heldout_28)} Held-Out samples and {len(diagnostic_20)} Diagnostic samples.")

    # 2. Setup Classifiers & Retrievers
    print("Initializing M1 Baseline and Enron models...")
    m1_enron_pipe = get_enron_m1_model()

    print("Loading Baseline RAG index...")
    baseline_retriever = FAISSRetriever.load("results/rag_index")

    print("Loading Enron RAG index...")
    enron_retriever = FAISSRetriever.load("results/rag_index_enron")

    suites = {
        "HeldOut_28": heldout_28,
        "Diagnostic_20": diagnostic_20,
    }

    all_methods = [
        "M1_Baseline", "M1_Enron",
        "M2_ZeroShot",
        "M3_Baseline", "M3_Enron",
        "M4_Baseline", "M4_Enron",
    ]

    master_output = {
        "metadata": {
            "date": "2026-10-30",
            "model": "qwen3.5:4b",
            "embedding_model": "all-MiniLM-L6-v2",
        },
        "suite_results": {},
    }

    for suite_name, suite_samples in suites.items():
        print(f"\nEvaluating Suite: {suite_name} (N={len(suite_samples)})...")
        suite_entries = []

        for idx, sample in enumerate(suite_samples, 1):
            text = sample["text"]
            preds = {}

            # M1 Baseline
            t0 = time.perf_counter()
            r1_b = classify_email_m1(text)
            r1_b["latency_ms"] = (time.perf_counter() - t0) * 1000
            preds["M1_Baseline"] = r1_b

            # M1 Enron
            preds["M1_Enron"] = classify_m1_enron(m1_enron_pipe, text)

            # M2 Zero-Shot
            t0 = time.perf_counter()
            r2 = classify_email_m2(text, model="qwen3.5:4b")
            r2["latency_ms"] = (time.perf_counter() - t0) * 1000
            preds["M2_ZeroShot"] = r2

            # M3 Baseline
            preds["M3_Baseline"] = classify_m3_custom(baseline_retriever, text, model="qwen3.5:4b")

            # M3 Enron
            preds["M3_Enron"] = classify_m3_custom(enron_retriever, text, model="qwen3.5:4b")

            # M4 Baseline
            preds["M4_Baseline"] = classify_m4_custom(baseline_retriever, text, model="qwen3.5:4b")

            # M4 Enron
            preds["M4_Enron"] = classify_m4_custom(enron_retriever, text, model="qwen3.5:4b")

            suite_entries.append({"sample": sample, "preds": preds})
            print(f"  [{idx:02d}/{len(suite_samples):02d}] {sample['id']} completed.")

        # Compute suite metrics
        suite_summary = {}
        for m in all_methods:
            metrics = compute_metrics(suite_entries, m)
            suite_summary[m] = metrics

        # Stage 1 Injection Detector Metrics for M4
        m4_base_inj = compute_injection_detector_metrics(suite_entries, "M4_Baseline")
        m4_enron_inj = compute_injection_detector_metrics(suite_entries, "M4_Enron")

        # Prevalence implications for M4 Enron vs M1 Enron vs M3 Enron
        prev_m4_enron = compute_prevalence_implications(suite_summary["M4_Enron"]["recall"], suite_summary["M4_Enron"]["fpr"])
        prev_m1_enron = compute_prevalence_implications(suite_summary["M1_Enron"]["recall"], suite_summary["M1_Enron"]["fpr"])
        prev_m3_enron = compute_prevalence_implications(suite_summary["M3_Enron"]["recall"], suite_summary["M3_Enron"]["fpr"])

        # Error Extraction (FP & FN) for all methods
        errors = {m: {"false_positives": [], "false_negatives": []} for m in all_methods}
        for entry in suite_entries:
            s = entry["sample"]
            true_p = (s["true_label"] == 1)
            for m in all_methods:
                p = entry["preds"][m]
                pred_p = bool(p.get("is_phishing", False))
                if pred_p and not true_p:
                    errors[m]["false_positives"].append({
                        "id": s["id"],
                        "category": s.get("category"),
                        "subject": s.get("subject"),
                        "sender": s.get("sender"),
                        "text_snippet": s["text"][:150],
                        "reasons": p.get("reasons", []),
                        "has_injection": p.get("has_injection"),
                        "retrieved_refs": [
                            {"id": r.get("id"), "label_name": r.get("label_name"), "sim": round(r.get("similarity_score", 0), 3)}
                            for r in p.get("retrieved_samples", [])
                        ],
                    })
                elif not pred_p and true_p:
                    errors[m]["false_negatives"].append({
                        "id": s["id"],
                        "category": s.get("category"),
                        "subject": s.get("subject"),
                        "sender": s.get("sender"),
                        "text_snippet": s["text"][:150],
                        "reasons": p.get("reasons", []),
                        "has_injection": p.get("has_injection"),
                        "retrieved_refs": [
                            {"id": r.get("id"), "label_name": r.get("label_name"), "sim": round(r.get("similarity_score", 0), 3)}
                            for r in p.get("retrieved_samples", [])
                        ],
                    })

        master_output["suite_results"][suite_name] = {
            "metrics": suite_summary,
            "m4_injection_detector": {
                "M4_Baseline_Injection_Stage": m4_base_inj,
                "M4_Enron_Injection_Stage": m4_enron_inj,
            },
            "prevalence_analysis": {
                "M4_Enron": prev_m4_enron,
                "M1_Enron": prev_m1_enron,
                "M3_Enron": prev_m3_enron,
            },
            "errors": errors,
            "raw_entries": suite_entries,
        }

    # Save to disk
    out_file = Path("scratch/decision_analysis_master_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(master_output, f, indent=2)
    print(f"\nSuccessfully wrote comprehensive results to {out_file}")


if __name__ == "__main__":
    main()

