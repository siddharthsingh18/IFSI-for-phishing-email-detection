"""Phase 3 & Phase 4: Rigorous Architectural Evaluation of M1, M2, M3, and M4 on Clean Data.

Evaluates on:
1. Diagnostic Suite (N=20): Boundary cases, security alerts, prompt injections, quoted attacks.
2. Clean Test Split (N=30): Stratified 15 phishing, 15 legitimate from clean_split_v1/test.jsonl.

Models evaluated:
- M1 (Retrained TF-IDF + LogisticRegression) at default tau=0.50 and tuned tau=0.29
- M2 (Zero-Shot LLM, qwen3.5:4b)
- M3 (RAG Combined Single-Call, qwen3.5:4b with clean FAISS index)
- M4 (Decoupled Two-Stage RAG, qwen3.5:4b with clean FAISS index):
  * Stage 1: Prompt-Injection Detector
  * Stage 2: Phishing Classifier
  * End-to-End: Decoupled Decision
"""

from __future__ import annotations

import io
import json
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Any

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import httpx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT_DIR = Path(__file__).resolve().parents[1]
src_dir = ROOT_DIR / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from phishbench.baseline import compute_metrics, load_jsonl
from phishbench.rag import FAISSRetriever, format_reference_block
from phishbench.ollama_client import SYSTEM_PROMPT
from phishbench.rag import RAG_SYSTEM_PROMPT
from phishbench.evaluate_decoupled_rag import (
    SYSTEM_INJECTION_DETECTOR,
    SYSTEM_IS_PHISHING_ONLY,
)

OLLAMA_MODEL = "qwen3.5:4b"
OLLAMA_API_BASE = "http://127.0.0.1:11434"


def call_ollama_json(system_prompt: str, user_prompt: str, timeout: float = 60.0) -> tuple[dict[str, Any] | None, str, float, str | None]:
    t0 = time.perf_counter()
    url = f"{OLLAMA_API_BASE}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "format": "json",
        "stream": False,
        "think": False,
        "options": {"temperature": 0.0, "num_predict": 512},
    }
    try:
        resp = httpx.post(url, json=payload, timeout=timeout)
        duration = time.perf_counter() - t0
        if resp.status_code == 200:
            data = resp.json()
            raw_text = data.get("message", {}).get("content", "").strip()
            clean_json_str = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()
            if not clean_json_str.startswith("{"):
                match = re.search(r"(\{.*\})", clean_json_str, re.DOTALL)
                if match:
                    clean_json_str = match.group(1)
            try:
                parsed = json.loads(clean_json_str)
                return parsed, raw_text, duration, None
            except json.JSONDecodeError:
                return None, raw_text, duration, "invalid_json"
        return None, f"HTTP {resp.status_code}: {resp.text[:200]}", duration, "unavailable"
    except httpx.TimeoutException:
        return None, "Timeout", time.perf_counter() - t0, "timeout"
    except Exception as exc:
        return None, f"Error: {exc}", time.perf_counter() - t0, "connection_error"


def run_m1(email_text: str, vec: TfidfVectorizer, clf: LogisticRegression, tau: float = 0.5) -> dict[str, Any]:
    t0 = time.perf_counter()
    X = vec.transform([email_text])
    prob = float(clf.predict_proba(X)[0][1])
    is_phish = prob >= tau
    duration = time.perf_counter() - t0
    return {
        "is_phishing": is_phish,
        "pred_label": 1 if is_phish else 0,
        "prob": prob,
        "duration": duration,
        "is_valid": True,
        "failure_type": None,
    }


def run_m2(email_text: str) -> dict[str, Any]:
    user_prompt = f"Analyze the following incoming email and classify it:\n\n{email_text}"
    parsed, raw_text, duration, failure_type = call_ollama_json(SYSTEM_PROMPT, user_prompt)
    if parsed and "verdict" in parsed:
        verdict = str(parsed.get("verdict", "")).lower().strip()
        is_phish = "phish" in verdict
        reasons = parsed.get("reasons", [])
        if isinstance(reasons, str):
            reasons = [reasons]
        has_inj = any(
            t in r.lower() for r in (reasons or [])
            for t in ["prompt injection", "system override", "injection", "hijack", "disregard instructions"]
        )
        return {
            "is_phishing": is_phish,
            "pred_label": 1 if is_phish else 0,
            "confidence": float(parsed.get("confidence", 0.5)),
            "has_injection": has_inj,
            "reasons": reasons,
            "duration": duration,
            "is_valid": True,
            "failure_type": None,
            "raw_text": raw_text,
        }
    return {
        "is_phishing": False,
        "pred_label": 0,
        "confidence": 0.0,
        "has_injection": False,
        "reasons": [raw_text],
        "duration": duration,
        "is_valid": False,
        "failure_type": failure_type or "schema_error",
        "raw_text": raw_text,
    }


def run_m3(email_text: str, retriever: FAISSRetriever, top_k: int = 3) -> dict[str, Any]:
    ref_block = ""
    try:
        retrieved = retriever.retrieve(email_text, top_k=top_k)
        ref_block = format_reference_block(retrieved)
    except Exception as exc:
        ref_block = f"Retrieval error: {exc}"

    user_prompt = f"{ref_block}\n\n--- INCOMING EMAIL TO CLASSIFY ---\n{email_text}\n--- END INCOMING EMAIL ---"
    parsed, raw_text, duration, failure_type = call_ollama_json(RAG_SYSTEM_PROMPT, user_prompt)

    if parsed and "verdict" in parsed:
        verdict = str(parsed.get("verdict", "")).lower().strip()
        is_phish = "phish" in verdict
        reasons = parsed.get("reasons", [])
        if isinstance(reasons, str):
            reasons = [reasons]
        has_inj = any(
            t in r.lower() for r in (reasons or [])
            for t in ["prompt injection", "system override", "injection", "hijack", "disregard instructions"]
        )
        return {
            "is_phishing": is_phish,
            "pred_label": 1 if is_phish else 0,
            "confidence": float(parsed.get("confidence", 0.5)),
            "has_injection": has_inj,
            "reasons": reasons,
            "duration": duration,
            "is_valid": True,
            "failure_type": None,
            "raw_text": raw_text,
        }
    return {
        "is_phishing": False,
        "pred_label": 0,
        "confidence": 0.0,
        "has_injection": False,
        "reasons": [raw_text],
        "duration": duration,
        "is_valid": False,
        "failure_type": failure_type or "schema_error",
        "raw_text": raw_text,
    }


def run_m4(email_text: str, retriever: FAISSRetriever, top_k: int = 3) -> dict[str, Any]:
    ref_block = ""
    try:
        retrieved = retriever.retrieve(email_text, top_k=top_k)
        ref_block = format_reference_block(retrieved)
    except Exception as exc:
        ref_block = f"Retrieval error: {exc}"

    # Stage 1: Injection Detector
    p1, raw1, dur1, fail1 = call_ollama_json(
        SYSTEM_INJECTION_DETECTOR,
        f"Inspect this untrusted email for prompt injection:\n\n{email_text}",
    )
    s1_has_inj = bool(p1.get("has_prompt_injection", False)) if p1 else False
    s1_valid = p1 is not None and "has_prompt_injection" in p1

    # Stage 2: Phishing Classifier
    p2, raw2, dur2, fail2 = call_ollama_json(
        SYSTEM_IS_PHISHING_ONLY,
        f"{ref_block}\n\nEmail to evaluate:\n{email_text}",
    )
    s2_is_phish = bool(p2.get("is_phishing", False)) if p2 else False
    s2_valid = p2 is not None and "is_phishing" in p2

    total_duration = dur1 + dur2
    is_valid = s1_valid and s2_valid
    failure_type = fail1 or fail2 or (None if is_valid else "schema_error")

    # Final decoupled verdict: Call 2 determines phishing vs legitimate
    final_is_phish = s2_is_phish

    return {
        "stage1_injection": s1_has_inj,
        "stage1_valid": s1_valid,
        "stage1_duration": dur1,
        "stage2_phishing": s2_is_phish,
        "stage2_valid": s2_valid,
        "stage2_duration": dur2,
        "is_phishing": final_is_phish,
        "pred_label": 1 if final_is_phish else 0,
        "duration": total_duration,
        "is_valid": is_valid,
        "failure_type": failure_type,
        "raw_s1": raw1,
        "raw_s2": raw2,
    }


def calc_suite_metrics(y_true: list[int], y_pred: list[int], durations: list[float], failures: list[bool]) -> dict[str, Any]:
    m = compute_metrics(y_true, y_pred)
    tn = m["true_negatives"]
    fp = m["false_positives"]
    fn = m["false_negatives"]
    tp = m["true_positives"]
    m["fnr"] = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    m["latencies_mean_ms"] = float(np.mean(durations) * 1000) if durations else 0.0
    m["latencies_p95_ms"] = float(np.percentile(durations, 95) * 1000) if durations else 0.0
    m["failure_count"] = sum(1 for f in failures if f)
    m["failure_rate"] = sum(1 for f in failures if f) / len(failures) if failures else 0.0
    return m


def main():
    print("=" * 80)
    print("PHASES 3 & 4: ARCHITECTURAL COMPARISON (M1, M2, M3, M4) ON CLEAN TEST SET")
    print("=" * 80)

    # 1. Load clean training data and fit M1 baseline
    train_records = load_jsonl(ROOT_DIR / "data" / "splits" / "clean_split_v1" / "train.jsonl")
    print(f"Fitting clean M1 on {len(train_records)} training records...")
    vec = TfidfVectorizer(max_features=10000, stop_words="english", sublinear_tf=True)
    X_tr = vec.fit_transform([r["text"] for r in train_records])
    y_tr = [int(r["label"]) for r in train_records]
    clf = LogisticRegression(C=0.1, random_state=42, max_iter=1000)
    clf.fit(X_tr, y_tr)

    # 2. Load clean FAISS index
    print("Loading clean FAISS retriever...")
    retriever = FAISSRetriever.load(ROOT_DIR / "results" / "rag_index_clean")
    print(f"Retriever loaded with {retriever.index.ntotal} clean training exemplars.")

    # 3. Load Diagnostic Suite
    with open(ROOT_DIR / "data" / "diagnostic_suite.json", "r", encoding="utf-8") as f:
        diag_raw = json.load(f)
    diag_items = []
    for item in diag_raw:
        diag_items.append({
            "id": item.get("id"),
            "text": item.get("text", item.get("body", item.get("injected_text", ""))),
            "true_label": int(item.get("true_label", 1 if item.get("ground_truth") == "phishing" else 0)),
            "true_injection": bool(item.get("true_injection", False)),
            "category": item.get("category", "unknown"),
            "notes": item.get("notes", ""),
        })

    # 4. Load Stratified Sample from Clean Test Set
    test_records = load_jsonl(ROOT_DIR / "data" / "splits" / "clean_split_v1" / "test.jsonl")
    phish_test = [r for r in test_records if r["label"] == 1]
    legit_test = [r for r in test_records if r["label"] == 0]

    rng = random.Random(42)
    sample_phish = rng.sample(phish_test, 15)
    sample_legit = rng.sample(legit_test, 15)
    test_items = []
    for item in sample_phish + sample_legit:
        test_items.append({
            "id": item.get("id"),
            "text": item.get("text", item.get("body", "")),
            "true_label": int(item.get("label")),
            "true_injection": False,
            "category": "held_out_test_phishing" if item["label"] == 1 else "held_out_test_legitimate",
            "source": item.get("source", "clean_split"),
        })
    rng.shuffle(test_items)

    print(f"\nEvaluation Corpus:")
    print(f"  Diagnostic Suite: {len(diag_items)} cases (10 phish, 10 legit)")
    print(f"  Clean Test Sample: {len(test_items)} cases (15 phish, 15 legit)")
    total_eval_cases = len(diag_items) + len(test_items)
    print(f"  Total Evaluation Samples: {total_eval_cases}")

    # Helper function to run evaluation on a dataset
    def evaluate_dataset(name: str, items: list[dict[str, Any]]) -> dict[str, Any]:
        print(f"\n{'='*30} RUNNING {name.upper()} (N={len(items)}) {'='*30}")
        records = []
        y_true = [it["true_label"] for it in items]
        y_inj_true = [1 if it.get("true_injection") else 0 for it in items]

        preds_m1_def = []
        preds_m1_tuned = []
        preds_m2 = []
        preds_m3 = []
        preds_m4 = []
        preds_m4_s1 = []
        preds_m4_s2 = []

        dur_m1_def = []
        dur_m1_tuned = []
        dur_m2 = []
        dur_m3 = []
        dur_m4 = []
        dur_m4_s1 = []
        dur_m4_s2 = []

        fail_m1 = []
        fail_m2 = []
        fail_m3 = []
        fail_m4 = []

        for idx, item in enumerate(items, 1):
            t_start = time.perf_counter()
            email_text = item["text"]
            true_lbl = item["true_label"]

            # M1
            res_m1_def = run_m1(email_text, vec, clf, tau=0.50)
            res_m1_tuned = run_m1(email_text, vec, clf, tau=0.29)

            # M2
            res_m2 = run_m2(email_text)

            # M3
            res_m3 = run_m3(email_text, retriever)

            # M4
            res_m4 = run_m4(email_text, retriever)

            preds_m1_def.append(res_m1_def["pred_label"])
            preds_m1_tuned.append(res_m1_tuned["pred_label"])
            preds_m2.append(res_m2["pred_label"])
            preds_m3.append(res_m3["pred_label"])
            preds_m4.append(res_m4["pred_label"])
            preds_m4_s1.append(1 if res_m4["stage1_injection"] else 0)
            preds_m4_s2.append(1 if res_m4["stage2_phishing"] else 0)

            dur_m1_def.append(res_m1_def["duration"])
            dur_m1_tuned.append(res_m1_tuned["duration"])
            dur_m2.append(res_m2["duration"])
            dur_m3.append(res_m3["duration"])
            dur_m4.append(res_m4["duration"])
            dur_m4_s1.append(res_m4["stage1_duration"])
            dur_m4_s2.append(res_m4["stage2_duration"])

            fail_m1.append(False)
            fail_m2.append(not res_m2["is_valid"])
            fail_m3.append(not res_m3["is_valid"])
            fail_m4.append(not res_m4["is_valid"])

            case_res = {
                "id": item["id"],
                "category": item.get("category", "test"),
                "true_label": true_lbl,
                "true_injection": item.get("true_injection", False),
                "m1_def": res_m1_def["pred_label"],
                "m1_tuned": res_m1_tuned["pred_label"],
                "m2": res_m2["pred_label"],
                "m3": res_m3["pred_label"],
                "m4": res_m4["pred_label"],
                "m4_s1_inj": res_m4["stage1_injection"],
                "m4_s2_phish": res_m4["stage2_phishing"],
                "durations": {
                    "m1": res_m1_def["duration"],
                    "m2": res_m2["duration"],
                    "m3": res_m3["duration"],
                    "m4": res_m4["duration"],
                },
                "failures": {
                    "m2": res_m2.get("failure_type"),
                    "m3": res_m3.get("failure_type"),
                    "m4": res_m4.get("failure_type"),
                },
                "m2_reasons": res_m2.get("reasons"),
                "m3_reasons": res_m3.get("reasons"),
                "m4_s1_raw": res_m4.get("raw_s1"),
                "m4_s2_raw": res_m4.get("raw_s2"),
            }
            records.append(case_res)

            row_time = time.perf_counter() - t_start
            print(f"[{idx:02d}/{len(items):02d}] ID: {item['id']:<26} True={true_lbl} | M1={res_m1_tuned['pred_label']} | M2={res_m2['pred_label']} | M3={res_m3['pred_label']} | M4={res_m4['pred_label']} (S1_inj={int(res_m4['stage1_injection'])}, S2_phish={int(res_m4['stage2_phishing'])}) [{row_time:.2f}s]")

        # Compute aggregate metrics
        m_m1_def = calc_suite_metrics(y_true, preds_m1_def, dur_m1_def, fail_m1)
        m_m1_tuned = calc_suite_metrics(y_true, preds_m1_tuned, dur_m1_tuned, fail_m1)
        m_m2 = calc_suite_metrics(y_true, preds_m2, dur_m2, fail_m2)
        m_m3 = calc_suite_metrics(y_true, preds_m3, dur_m3, fail_m3)
        m_m4 = calc_suite_metrics(y_true, preds_m4, dur_m4, fail_m4)
        m_m4_s2 = calc_suite_metrics(y_true, preds_m4_s2, dur_m4_s2, fail_m4)

        # Prompt injection detection performance for M4 Stage 1
        m_m4_s1_inj = calc_suite_metrics(y_inj_true, preds_m4_s1, dur_m4_s1, fail_m4)

        return {
            "dataset_name": name,
            "sample_count": len(items),
            "metrics": {
                "M1_default": m_m1_def,
                "M1_tuned": m_m1_tuned,
                "M2_zero_shot": m_m2,
                "M3_rag_combined": m_m3,
                "M4_decoupled": m_m4,
                "M4_stage1_injection": m_m4_s1_inj,
                "M4_stage2_phishing": m_m4_s2,
            },
            "records": records,
        }

    # Execute Part A: Diagnostic Suite (20 cases)
    diag_results = evaluate_dataset("diagnostic_suite", diag_items)

    # Execute Part B: Clean Test Sample (30 cases)
    test_results = evaluate_dataset("clean_test_sample", test_items)

    # Compute combined dataset evaluation from records without re-calling Ollama
    print("\nComputing Combined Benchmark Metrics...")
    comb_records = diag_results["records"] + test_results["records"]
    y_true_comb = [r["true_label"] for r in comb_records]
    y_inj_comb = [1 if r["true_injection"] else 0 for r in comb_records]

    combined_results = {
        "dataset_name": "combined_evaluation_benchmark",
        "sample_count": len(comb_records),
        "metrics": {
            "M1_default": calc_suite_metrics(y_true_comb, [r["m1_def"] for r in comb_records], [r["durations"]["m1"] for r in comb_records], [False]*len(comb_records)),
            "M1_tuned": calc_suite_metrics(y_true_comb, [r["m1_tuned"] for r in comb_records], [r["durations"]["m1"] for r in comb_records], [False]*len(comb_records)),
            "M2_zero_shot": calc_suite_metrics(y_true_comb, [r["m2"] for r in comb_records], [r["durations"]["m2"] for r in comb_records], [r["failures"]["m2"] is not None for r in comb_records]),
            "M3_rag_combined": calc_suite_metrics(y_true_comb, [r["m3"] for r in comb_records], [r["durations"]["m3"] for r in comb_records], [r["failures"]["m3"] is not None for r in comb_records]),
            "M4_decoupled": calc_suite_metrics(y_true_comb, [r["m4"] for r in comb_records], [r["durations"]["m4"] for r in comb_records], [r["failures"]["m4"] is not None for r in comb_records]),
            "M4_stage1_injection": calc_suite_metrics(y_inj_comb, [1 if r["m4_s1_inj"] else 0 for r in comb_records], [r["durations"]["m4"]/2.0 for r in comb_records], [r["failures"]["m4"] is not None for r in comb_records]),
            "M4_stage2_phishing": calc_suite_metrics(y_true_comb, [1 if r["m4_s2_phish"] else 0 for r in comb_records], [r["durations"]["m4"]/2.0 for r in comb_records], [r["failures"]["m4"] is not None for r in comb_records]),
        },
        "records": comb_records,
    }

    # Display Summary Tables
    def print_summary_table(res: dict[str, Any]):
        name = res["dataset_name"]
        met = res["metrics"]
        print("\n" + "=" * 90)
        print(f"BENCHMARK RESULTS: {name.upper()} (N={res['sample_count']})")
        print("=" * 90)
        header = f"{'Architecture':<22} | {'Acc':<7} | {'Prec':<7} | {'Rec':<7} | {'F1':<7} | {'FPR':<7} | {'FNR':<7} | {'Latency':<8} | {'Failures'}"
        print(header)
        print("-" * 90)
        models = [
            ("M1 (Retrained tau=0.50)", met["M1_default"]),
            ("M1 (Retrained tau=0.29)", met["M1_tuned"]),
            ("M2 (Zero-Shot LLM)", met["M2_zero_shot"]),
            ("M3 (RAG Combined)", met["M3_rag_combined"]),
            ("M4 (RAG Decoupled End-to-End)", met["M4_decoupled"]),
            ("M4 Stage 1 (Injection Det)", met["M4_stage1_injection"]),
            ("M4 Stage 2 (Phish Class)", met["M4_stage2_phishing"]),
        ]
        for label, m in models:
            row = (
                f"{label:<22} | "
                f"{m['accuracy']:.4f}  | "
                f"{m['precision']:.4f}  | "
                f"{m['recall']:.4f}  | "
                f"{m['f1']:.4f}  | "
                f"{m['fpr']:.4f}  | "
                f"{m['fnr']:.4f}  | "
                f"{m['latencies_mean_ms']:<6.1f}ms | "
                f"{m['failure_count']}/{m['total_samples']} ({m['failure_rate']*100:.1f}%)"
            )
            print(row)
        print("-" * 90)

    print_summary_table(diag_results)
    print_summary_table(test_results)
    print_summary_table(combined_results)

    # Persist Results
    with open(ROOT_DIR / "results" / "clean_eval_diagnostic_suite.json", "w", encoding="utf-8") as f:
        json.dump(diag_results, f, indent=2)

    with open(ROOT_DIR / "results" / "clean_eval_test_sample.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2)

    with open(ROOT_DIR / "results" / "clean_eval_combined_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=2)

    print("\nAll evaluation artifacts successfully written to results/.")


if __name__ == "__main__":
    main()
