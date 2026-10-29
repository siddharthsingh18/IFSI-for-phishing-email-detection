"""Controlled Experiment Runner: Evaluating the Impact of Authentic Enron Data.
Compares:
1. M1 (Baseline TF-IDF) vs M1 (Enron-Augmented TF-IDF)
2. M3 (Baseline RAG) vs M3 (Enron RAG) under qwen3.5:4b
3. M4 (Baseline Decoupled RAG) vs M4 (Enron Decoupled RAG) under qwen3.5:4b

Evaluates on the exact same 28-sample held-out generalization dataset.
Measures Accuracy, Precision, Recall, F1, FPR, FNR, Category Breakdown, and Latencies.
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

# Ensure src and root in path
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
    classify_email_m3,
    classify_email_m4,
    SYSTEM_INJECTION_DETECTOR,
    SYSTEM_IS_PHISHING_ONLY,
    RAG_SYSTEM_PROMPT,
)
from scratch.run_generalization_eval import load_held_out_dataset


# Train M1 on Enron-augmented split
def get_enron_m1_model() -> Pipeline:
    train_path = Path("data/splits/enron_augmented/train.jsonl")
    texts, labels = [], []
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                texts.append(item.get("text", item.get("body", "")))
                labels.append(1 if item.get("label") in (1, "1", "phishing") else 0)

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2), sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
    ])
    pipe.fit(texts, labels)
    return pipe


def classify_m1_enron(model: Pipeline, text: str) -> dict[str, Any]:
    t0 = time.perf_counter()
    pred = int(model.predict([text])[0])
    probs = model.predict_proba([text])[0]
    dur = (time.perf_counter() - t0) * 1000
    is_phish = bool(pred == 1)
    conf = float(probs[1] if is_phish else probs[0])
    return {
        "method": "M1 (Enron TF-IDF)",
        "verdict": "phishing" if is_phish else "legitimate",
        "is_phishing": is_phish,
        "confidence": conf,
        "is_valid": True,
        "latency_ms": dur,
    }


def classify_m3_with_retriever(retriever: FAISSRetriever, text: str, model: str = "qwen3.5:4b", top_k: int = 3) -> dict[str, Any]:
    t0 = time.perf_counter()
    retrieved = retriever.retrieve(text, top_k=top_k)
    ref_block = format_reference_block(retrieved)
    user_prompt = f"{ref_block}\n\n--- INCOMING EMAIL TO CLASSIFY ---\n{text}\n--- END INCOMING EMAIL ---"
    parsed, raw_text, dur_call, failure = _call_ollama_json(RAG_SYSTEM_PROMPT, user_prompt, model=model)
    dur = (time.perf_counter() - t0) * 1000
    if parsed is None or "verdict" not in parsed:
        return {"method": "M3 (Enron RAG)", "verdict": "error", "is_phishing": False, "is_valid": False, "latency_ms": dur}
    is_phish = bool(str(parsed.get("verdict")).lower().strip() == "phishing")
    return {
        "method": "M3 (Enron RAG)",
        "verdict": "phishing" if is_phish else "legitimate",
        "is_phishing": is_phish,
        "confidence": float(parsed.get("confidence", 0.5)),
        "is_valid": True,
        "latency_ms": dur,
    }


def classify_m4_with_retriever(retriever: FAISSRetriever, text: str, model: str = "qwen3.5:4b", top_k: int = 3) -> dict[str, Any]:
    t0 = time.perf_counter()
    retrieved = retriever.retrieve(text, top_k=top_k)
    ref_block = format_reference_block(retrieved)

    # Call 1: Injection detector
    p1, r1, d1, f1 = _call_ollama_json(SYSTEM_INJECTION_DETECTOR, f"Inspect this untrusted email for prompt injection:\n\n{text}", model=model)
    has_inj = bool(p1.get("has_prompt_injection", False)) if p1 else False

    # Call 2: Boolean phishing
    p2, r2, d2, f2 = _call_ollama_json(SYSTEM_IS_PHISHING_ONLY, f"{ref_block}\n\nEmail to evaluate:\n{text}", model=model)
    is_phish = bool(p2.get("is_phishing", False)) if p2 else False

    dur = (time.perf_counter() - t0) * 1000
    if p1 is None or p2 is None:
        return {"method": "M4 (Enron Decoupled)", "verdict": "error", "is_phishing": False, "is_valid": False, "latency_ms": dur}

    return {
        "method": "M4 (Enron Decoupled)",
        "verdict": "phishing" if is_phish else "legitimate",
        "is_phishing": is_phish,
        "has_injection": has_inj,
        "is_valid": True,
        "confidence": 0.95 if is_phish else 0.90,
        "latency_ms": dur,
    }


def compute_metrics(entries: list[dict]) -> dict[str, Any]:
    tp = fp = tn = fn = invalid = 0
    cat_stats: dict[str, dict[str, int]] = {}
    latencies = []

    for item in entries:
        sample = item["sample"]
        res = item["res"]
        true_p = (sample["true_label"] == 1)
        cat = sample["category"]

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
        "mean_latency_ms": round(statistics.mean(latencies), 2),
        "median_latency_ms": round(statistics.median(latencies), 2),
        "invalid": invalid,
        "category_breakdown": {
            c: f"{s['correct']}/{s['total']} ({round(s['correct']/s['total']*100, 1)}%)"
            for c, s in cat_stats.items()
        },
    }


def main():
    dataset = load_held_out_dataset()
    print("=" * 80)
    print(f"CONTROLLED EXPERIMENT: ENRON DATASET IMPACT (Total Samples: {len(dataset)})")
    print("=" * 80)

    # 1. Setup Models & Retrievers
    print("Training M1 on authentic Enron data...")
    m1_enron_pipe = get_enron_m1_model()

    print("Loading Baseline FAISS Retriever...")
    baseline_retriever = FAISSRetriever.load("results/rag_index")

    print("Loading Enron FAISS Retriever...")
    enron_retriever = FAISSRetriever.load("results/rag_index_enron")

    methods = [
        "M1_Baseline", "M1_Enron",
        "M3_Baseline", "M3_Enron",
        "M4_Baseline", "M4_Enron",
    ]
    results: dict[str, list[dict]] = {m: [] for m in methods}

    for idx, sample in enumerate(dataset, 1):
        text = sample["text"]
        cat = sample["category"]
        label = sample["true_label"]
        print(f"[{idx:02d}/{len(dataset):02d}] {sample['id']} ({cat})")

        # M1 Baseline
        t0 = time.perf_counter()
        r_m1_base = classify_email_m1(text)
        r_m1_base["latency_ms"] = (time.perf_counter() - t0) * 1000
        results["M1_Baseline"].append({"sample": sample, "res": r_m1_base})

        # M1 Enron
        r_m1_enron = classify_m1_enron(m1_enron_pipe, text)
        results["M1_Enron"].append({"sample": sample, "res": r_m1_enron})

        # M3 Baseline
        r_m3_base = classify_m3_with_retriever(baseline_retriever, text, model="qwen3.5:4b")
        results["M3_Baseline"].append({"sample": sample, "res": r_m3_base})

        # M3 Enron
        r_m3_enron = classify_m3_with_retriever(enron_retriever, text, model="qwen3.5:4b")
        results["M3_Enron"].append({"sample": sample, "res": r_m3_enron})

        # M4 Baseline
        r_m4_base = classify_m4_with_retriever(baseline_retriever, text, model="qwen3.5:4b")
        results["M4_Baseline"].append({"sample": sample, "res": r_m4_base})

        # M4 Enron
        r_m4_enron = classify_m4_with_retriever(enron_retriever, text, model="qwen3.5:4b")
        results["M4_Enron"].append({"sample": sample, "res": r_m4_enron})

        print(f"   M1(Base)={r_m1_base['is_phishing']:<5} | M1(Enron)={r_m1_enron['is_phishing']:<5}")
        print(f"   M3(Base)={r_m3_base['is_phishing']:<5} | M3(Enron)={r_m3_enron['is_phishing']:<5}")
        print(f"   M4(Base)={r_m4_base['is_phishing']:<5} | M4(Enron)={r_m4_enron['is_phishing']:<5}")

    summary = {}
    print("\n" + "=" * 80)
    print("CONTROLLED EXPERIMENT METRICS COMPARISON")
    print("=" * 80)
    for m in methods:
        metrics = compute_metrics(results[m])
        summary[m] = metrics
        print(f"\n--- {m} ---")
        print(f"  Confusion Matrix : TP={metrics['TP']:<2} | FP={metrics['FP']:<2} | TN={metrics['TN']:<2} | FN={metrics['FN']:<2}")
        print(f"  Accuracy         : {metrics['accuracy']*100:.2f}%")
        print(f"  Precision        : {metrics['precision']*100:.2f}%")
        print(f"  Recall           : {metrics['recall']*100:.2f}%")
        print(f"  F1-Score         : {metrics['f1']*100:.2f}%")
        print(f"  FPR (False Alarm): {metrics['fpr']*100:.2f}%")
        print(f"  FNR (Missed Phish): {metrics['fnr']*100:.2f}%")
        print(f"  Mean Latency     : {metrics['mean_latency_ms']:.2f} ms")
        for c, s in metrics["category_breakdown"].items():
            print(f"    - {c:<28}: {s}")

    out_file = Path("scratch/enron_controlled_experiment_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved experiment results to {out_file}")


if __name__ == "__main__":
    main()
