"""Run Diagnostic Suite (20 samples) on Enron-augmented models."""
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

from phishbench.rag import FAISSRetriever, format_reference_block
from core.inference import (
    _call_ollama_json,
    classify_email_m1,
    SYSTEM_INJECTION_DETECTOR,
    SYSTEM_IS_PHISHING_ONLY,
    RAG_SYSTEM_PROMPT,
)
from scratch.run_enron_impact_experiments import (
    get_enron_m1_model,
    classify_m1_enron,
    classify_m3_with_retriever,
    classify_m4_with_retriever,
    compute_metrics,
)

def main():
    diag_path = Path("data/diagnostic_suite.json")
    with open(diag_path, "r", encoding="utf-8") as f:
        diag_samples = json.load(f)

    # Convert to standard format
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
            "text": text,
        })

    print(f"Loaded {len(dataset)} diagnostic samples.")
    m1_enron = get_enron_m1_model()
    baseline_retriever = FAISSRetriever.load("results/rag_index")
    enron_retriever = FAISSRetriever.load("results/rag_index_enron")

    methods = ["M1_Enron", "M3_Enron", "M4_Enron"]
    results = {m: [] for m in methods}

    for idx, sample in enumerate(dataset, 1):
        text = sample["text"]
        r_m1 = classify_m1_enron(m1_enron, text)
        results["M1_Enron"].append({"sample": sample, "res": r_m1})

        r_m3 = classify_m3_with_retriever(enron_retriever, text, model="qwen3.5:4b")
        results["M3_Enron"].append({"sample": sample, "res": r_m3})

        r_m4 = classify_m4_with_retriever(enron_retriever, text, model="qwen3.5:4b")
        results["M4_Enron"].append({"sample": sample, "res": r_m4})

    summary = {}
    for m in methods:
        summary[m] = compute_metrics(results[m])
        print(f"\n--- {m} on Diagnostic Suite ---")
        print(f"  Accuracy : {summary[m]['accuracy']*100:.1f}%")
        print(f"  Precision: {summary[m]['precision']*100:.1f}%")
        print(f"  Recall   : {summary[m]['recall']*100:.1f}%")
        print(f"  F1-Score : {summary[m]['f1']*100:.1f}%")
        print(f"  FPR      : {summary[m]['fpr']*100:.1f}%")
        print(f"  FNR      : {summary[m]['fnr']*100:.1f}%")

    with open("scratch/enron_diagnostic_experiment_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()

