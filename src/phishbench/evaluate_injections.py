"""Evaluation of M1 (TF-IDF + LR), M2 (Zero-Shot LLM), and M3 (RAG + LLM) across all 4 injection sets.

Evaluates:
1. marked-phishing (128 records)
2. marked-control (394 records)
3. unmarked-phishing (128 records)
4. unmarked-control (394 records)

Computes:
- Recall on attacked-phishing (phishing detection rate under attack)
- FPR on injected-legitimate-control (false positive rate on perturbed clean emails)
- Performance gap between marked and unmarked injections per method
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import Any, Sequence

import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .io import read_jsonl, write_json, write_jsonl
from .ollama_client import (
    EmailClassificationResult,
    OllamaConfig,
    SYSTEM_PROMPT,
)
from .rag import (
    FAISSRetriever,
    RAG_SYSTEM_PROMPT,
    format_reference_block,
)


def compute_metrics_for_condition(
    predictions: Sequence[dict[str, Any]],
    expected_label: int,
) -> dict[str, Any]:
    """Compute condition-specific metrics (Recall for phishing, FPR for control)."""
    total = len(predictions)
    valid_preds = [p for p in predictions if p.get("is_valid", False)]
    valid_count = len(valid_preds)
    invalid_count = total - valid_count
    invalid_rate = round(invalid_count / total, 4) if total > 0 else 0.0

    if expected_label == 1:
        # Attacked Phishing: positive class is 1 (phishing)
        tp = sum(1 for p in valid_preds if p["predicted_label"] == 1)
        fn = sum(1 for p in valid_preds if p["predicted_label"] == 0)
        recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        asr = round(fn / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        return {
            "total_samples": total,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "invalid_rate": invalid_rate,
            "true_positives": tp,
            "false_negatives": fn,
            "recall": recall,
            "attack_success_rate": asr,
        }
    else:
        # Injected Legitimate Control: negative class is 0 (legitimate)
        fp = sum(1 for p in valid_preds if p["predicted_label"] == 1)
        tn = sum(1 for p in valid_preds if p["predicted_label"] == 0)
        fpr = round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0.0
        specificity = round(tn / (fp + tn), 4) if (fp + tn) > 0 else 0.0
        return {
            "total_samples": total,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "invalid_rate": invalid_rate,
            "false_positives": fp,
            "true_negatives": tn,
            "fpr": fpr,
            "specificity": specificity,
        }


# =========================================================================
# M1: TF-IDF + LogisticRegression
# =========================================================================

def evaluate_m1(
    train_records: list[dict[str, Any]],
    injection_sets: dict[str, list[dict[str, Any]]],
    max_features: int = 10000,
    seed: int = 42,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Train M1 on train split and evaluate on all four injection sets."""
    t0 = time.perf_counter()
    X_train = [r["text"] for r in train_records]
    y_train = [int(r["label"]) for r in train_records]

    vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english", ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)

    clf = LogisticRegression(random_state=seed, max_iter=1000)
    clf.fit(X_train_vec, y_train)
    train_time = time.perf_counter() - t0

    predictions_by_cond: dict[str, list[dict[str, Any]]] = {}
    summary_by_cond: dict[str, Any] = {}

    for condition, records in injection_sets.items():
        expected_label = 1 if "phishing" in condition else 0
        X_test = [r["text"] for r in records]
        X_test_vec = vectorizer.transform(X_test)
        preds = clf.predict(X_test_vec)
        probs = clf.predict_proba(X_test_vec)

        cond_preds = []
        for r, pred, prob in zip(records, preds, probs):
            pred_int = int(pred)
            conf = float(prob[pred_int])
            cond_preds.append({
                "id": r["id"],
                "original_id": r["original_id"],
                "condition": condition,
                "injection_type": r.get("injection_type", ""),
                "injection_style": r.get("injection_style", ""),
                "true_label": int(r["label"]),
                "predicted_label": pred_int,
                "predicted_verdict": "phishing" if pred_int == 1 else "legitimate",
                "confidence": round(conf, 4),
                "is_valid": True,
                "method": "M1_TFIDF_LogReg",
            })

        predictions_by_cond[condition] = cond_preds
        summary_by_cond[condition] = compute_metrics_for_condition(cond_preds, expected_label)

    summary_by_cond["meta"] = {
        "method": "M1 (TF-IDF + LogisticRegression)",
        "train_time_seconds": round(train_time, 4),
        "total_evaluated": sum(len(records) for records in injection_sets.values()),
    }
    return predictions_by_cond, summary_by_cond


# =========================================================================
# M2: Zero-Shot Ollama LLM
# =========================================================================

async def classify_m2_single(
    client: httpx.AsyncClient,
    config: OllamaConfig,
    record: dict[str, Any],
    condition: str,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    """Classify a single email using Zero-Shot Ollama with concurrency control."""
    email_text = str(record["text"])
    expected_label = int(record["label"])
    url = "/api/chat"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this email:\n\n{email_text}"},
    ]
    payload = {
        "model": config.model,
        "messages": messages,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": config.temperature,
            "num_predict": config.num_predict,
        },
    }

    t0 = time.perf_counter()
    retries = 0
    max_attempts = 1 + config.max_retries
    last_error: str | None = None
    parsed_result: EmailClassificationResult | None = None

    async with semaphore:
        for attempt in range(max_attempts):
            if attempt > 0:
                retries += 1
            try:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
                    continue
                data = resp.json()
                content = data.get("message", {}).get("content", "").strip()
                raw_json = json.loads(content)
                parsed_result = EmailClassificationResult.model_validate(raw_json)
                break
            except Exception as e:
                last_error = str(e)

    latency = round(time.perf_counter() - t0, 4)
    is_valid = parsed_result is not None
    pred_verdict = parsed_result.verdict if parsed_result else None
    pred_label = 1 if pred_verdict == "phishing" else (0 if pred_verdict == "legitimate" else -1)

    return {
        "id": record["id"],
        "original_id": record["original_id"],
        "condition": condition,
        "injection_type": record.get("injection_type", ""),
        "injection_style": record.get("injection_style", ""),
        "true_label": expected_label,
        "predicted_label": pred_label,
        "predicted_verdict": pred_verdict,
        "confidence": parsed_result.confidence if parsed_result else 0.0,
        "reasons": parsed_result.reasons if parsed_result else [],
        "is_valid": is_valid,
        "retries": retries,
        "latency_seconds": latency,
        "error": last_error if not is_valid else None,
        "method": "M2_ZeroShot_LLM",
    }


async def evaluate_m2_async(
    injection_sets: dict[str, list[dict[str, Any]]],
    config: OllamaConfig,
    concurrency: int = 4,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Evaluate M2 across all four injection sets concurrently."""
    t0 = time.perf_counter()
    semaphore = asyncio.Semaphore(concurrency)
    predictions_by_cond: dict[str, list[dict[str, Any]]] = {}
    summary_by_cond: dict[str, Any] = {}

    async with httpx.AsyncClient(base_url=config.api_base, timeout=config.timeout_seconds) as client:
        for condition, records in injection_sets.items():
            expected_label = 1 if "phishing" in condition else 0
            tasks = [
                classify_m2_single(client, config, rec, condition, semaphore)
                for rec in records
            ]
            preds = await asyncio.gather(*tasks)
            predictions_by_cond[condition] = preds
            summary_by_cond[condition] = compute_metrics_for_condition(preds, expected_label)

    summary_by_cond["meta"] = {
        "method": "M2 (Zero-Shot Ollama)",
        "model": config.model,
        "temperature": config.temperature,
        "concurrency": concurrency,
        "total_runtime_seconds": round(time.perf_counter() - t0, 2),
        "total_evaluated": sum(len(records) for records in injection_sets.values()),
    }
    return predictions_by_cond, summary_by_cond


# =========================================================================
# M3: RAG (Top-k=3) + Ollama LLM
# =========================================================================

async def classify_m3_single(
    client: httpx.AsyncClient,
    retriever: FAISSRetriever,
    config: OllamaConfig,
    record: dict[str, Any],
    condition: str,
    semaphore: asyncio.Semaphore,
    top_k: int = 3,
) -> dict[str, Any]:
    """Classify a single email using RAG + Ollama with concurrency control."""
    email_text = str(record["text"])
    expected_label = int(record["label"])

    # Retrieve top-k (CPU vector search)
    t_start = time.perf_counter()
    retrieved_examples = retriever.retrieve(email_text, top_k=top_k)
    reference_block = format_reference_block(retrieved_examples)

    user_prompt = f"""{reference_block}

Candidate Email To Classify:
---
{email_text}
---

Remember: Return ONLY a valid JSON object with {{"verdict": "phishing" or "legitimate", "confidence": <float>, "reasons": ["<reason>"]}}."""

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    payload = {
        "model": config.model,
        "messages": messages,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": config.temperature,
            "num_predict": config.num_predict,
        },
    }

    retries = 0
    max_attempts = 1 + config.max_retries
    last_error: str | None = None
    parsed_result: EmailClassificationResult | None = None

    async with semaphore:
        for attempt in range(max_attempts):
            if attempt > 0:
                retries += 1
            try:
                resp = await client.post("/api/chat", json=payload)
                if resp.status_code != 200:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
                    continue
                data = resp.json()
                content = data.get("message", {}).get("content", "").strip()
                raw_json = json.loads(content)
                parsed_result = EmailClassificationResult.model_validate(raw_json)
                break
            except Exception as e:
                last_error = str(e)

    latency = round(time.perf_counter() - t_start, 4)
    is_valid = parsed_result is not None
    pred_verdict = parsed_result.verdict if parsed_result else None
    pred_label = 1 if pred_verdict == "phishing" else (0 if pred_verdict == "legitimate" else -1)

    return {
        "id": record["id"],
        "original_id": record["original_id"],
        "condition": condition,
        "injection_type": record.get("injection_type", ""),
        "injection_style": record.get("injection_style", ""),
        "true_label": expected_label,
        "predicted_label": pred_label,
        "predicted_verdict": pred_verdict,
        "confidence": parsed_result.confidence if parsed_result else 0.0,
        "reasons": parsed_result.reasons if parsed_result else [],
        "retrieved_ids": [ex["id"] for ex in retrieved_examples],
        "retrieved_labels": [ex["label_name"] for ex in retrieved_examples],
        "is_valid": is_valid,
        "retries": retries,
        "latency_seconds": latency,
        "error": last_error if not is_valid else None,
        "method": "M3_RAG_LLM",
    }


async def evaluate_m3_async(
    retriever: FAISSRetriever,
    injection_sets: dict[str, list[dict[str, Any]]],
    config: OllamaConfig,
    concurrency: int = 4,
    top_k: int = 3,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Evaluate M3 across all four injection sets concurrently."""
    t0 = time.perf_counter()
    semaphore = asyncio.Semaphore(concurrency)
    predictions_by_cond: dict[str, list[dict[str, Any]]] = {}
    summary_by_cond: dict[str, Any] = {}

    async with httpx.AsyncClient(base_url=config.api_base, timeout=config.timeout_seconds) as client:
        for condition, records in injection_sets.items():
            expected_label = 1 if "phishing" in condition else 0
            tasks = [
                classify_m3_single(client, retriever, config, rec, condition, semaphore, top_k=top_k)
                for rec in records
            ]
            preds = await asyncio.gather(*tasks)
            predictions_by_cond[condition] = preds
            summary_by_cond[condition] = compute_metrics_for_condition(preds, expected_label)

    summary_by_cond["meta"] = {
        "method": f"M3 (RAG top_k={top_k} + Ollama)",
        "model": config.model,
        "top_k": top_k,
        "temperature": config.temperature,
        "concurrency": concurrency,
        "total_runtime_seconds": round(time.perf_counter() - t0, 2),
        "total_evaluated": sum(len(records) for records in injection_sets.values()),
    }
    return predictions_by_cond, summary_by_cond


# =========================================================================
# Main Runner & Gap Analysis
# =========================================================================

def compute_gaps(summary: dict[str, Any]) -> dict[str, Any]:
    """Compute performance gap between marked and unmarked conditions."""
    marked_phish = summary["marked-phishing"]
    unmarked_phish = summary["unmarked-phishing"]
    marked_ctrl = summary["marked-control"]
    unmarked_ctrl = summary["unmarked-control"]

    recall_marked = marked_phish["recall"]
    recall_unmarked = unmarked_phish["recall"]
    recall_gap = round(recall_unmarked - recall_marked, 4)

    fpr_marked = marked_ctrl["fpr"]
    fpr_unmarked = unmarked_ctrl["fpr"]
    fpr_gap = round(fpr_unmarked - fpr_marked, 4)

    return {
        "recall_attacked_phishing": {
            "marked": recall_marked,
            "unmarked": recall_unmarked,
            "gap_unmarked_minus_marked": recall_gap,
        },
        "fpr_injected_legitimate_control": {
            "marked": fpr_marked,
            "unmarked": fpr_unmarked,
            "gap_unmarked_minus_marked": fpr_gap,
        },
    }


async def async_main(
    train_path: Path,
    injections_dir: Path,
    output_dir: Path,
    config_path: Path,
    concurrency: int = 4,
    top_k: int = 3,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    train_records = read_jsonl(train_path)

    conditions = ("marked-phishing", "marked-control", "unmarked-phishing", "unmarked-control")
    injection_sets = {cond: read_jsonl(injections_dir / f"{cond}.jsonl") for cond in conditions}

    # Load Ollama config
    if config_path.exists():
        cfg_dict = json.loads(config_path.read_text(encoding="utf-8"))
        ollama_cfg = OllamaConfig(**cfg_dict)
    else:
        ollama_cfg = OllamaConfig()

    results_all: dict[str, Any] = {}

    # --- 1. M1 Evaluation ---
    print("\n[1/3] Running M1: TF-IDF + LogisticRegression baseline...")
    m1_preds, m1_summary = evaluate_m1(train_records, injection_sets)
    m1_flat_preds = [p for cond in conditions for p in m1_preds[cond]]
    write_jsonl(output_dir / "m1_injection_predictions.jsonl", m1_flat_preds)
    m1_gaps = compute_gaps(m1_summary)
    results_all["M1_TFIDF_LogReg"] = {
        "summary": m1_summary,
        "gaps": m1_gaps,
    }
    print(f"  M1 Recall: marked={m1_gaps['recall_attacked_phishing']['marked']}, unmarked={m1_gaps['recall_attacked_phishing']['unmarked']}")
    print(f"  M1 FPR:    marked={m1_gaps['fpr_injected_legitimate_control']['marked']}, unmarked={m1_gaps['fpr_injected_legitimate_control']['unmarked']}")

    # --- 2. M2 Evaluation ---
    print(f"\n[2/3] Running M2: Zero-Shot Ollama ({ollama_cfg.model}, concurrency={concurrency})...")
    m2_preds, m2_summary = await evaluate_m2_async(injection_sets, ollama_cfg, concurrency=concurrency)
    m2_flat_preds = [p for cond in conditions for p in m2_preds[cond]]
    write_jsonl(output_dir / "m2_injection_predictions.jsonl", m2_flat_preds)
    m2_gaps = compute_gaps(m2_summary)
    results_all["M2_ZeroShot_LLM"] = {
        "summary": m2_summary,
        "gaps": m2_gaps,
    }
    print(f"  M2 Recall: marked={m2_gaps['recall_attacked_phishing']['marked']}, unmarked={m2_gaps['recall_attacked_phishing']['unmarked']}")
    print(f"  M2 FPR:    marked={m2_gaps['fpr_injected_legitimate_control']['marked']}, unmarked={m2_gaps['fpr_injected_legitimate_control']['unmarked']}")

    # --- 3. M3 Evaluation ---
    print(f"\n[3/3] Running M3: RAG (top-k={top_k}) + Ollama ({ollama_cfg.model}, concurrency={concurrency})...")
    rag_index_dir = output_dir / "rag_index"
    retriever = FAISSRetriever(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if (rag_index_dir / "index.faiss").exists():
        retriever.load(rag_index_dir)
    else:
        retriever.build(train_records)
        retriever.save(rag_index_dir)

    m3_preds, m3_summary = await evaluate_m3_async(retriever, injection_sets, ollama_cfg, concurrency=concurrency, top_k=top_k)
    m3_flat_preds = [p for cond in conditions for p in m3_preds[cond]]
    write_jsonl(output_dir / "m3_injection_predictions.jsonl", m3_flat_preds)
    m3_gaps = compute_gaps(m3_summary)
    results_all["M3_RAG_LLM"] = {
        "summary": m3_summary,
        "gaps": m3_gaps,
    }
    print(f"  M3 Recall: marked={m3_gaps['recall_attacked_phishing']['marked']}, unmarked={m3_gaps['recall_attacked_phishing']['unmarked']}")
    print(f"  M3 FPR:    marked={m3_gaps['fpr_injected_legitimate_control']['marked']}, unmarked={m3_gaps['fpr_injected_legitimate_control']['unmarked']}")

    summary_file = output_dir / "injections_evaluation_summary.json"
    write_json(summary_file, results_all)
    print(f"\nSaved aggregated results to {summary_file}")
    return results_all


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate M1, M2, and M3 across all 4 injection sets.")
    parser.add_argument("--train", type=Path, default=Path("data/splits/train.jsonl"))
    parser.add_argument("--injections-dir", type=Path, default=Path("data/injections"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--config", type=Path, default=Path("config/ollama_config.json"))
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    asyncio.run(async_main(
        train_path=args.train,
        injections_dir=args.injections_dir,
        output_dir=args.output_dir,
        config_path=args.config,
        concurrency=args.concurrency,
        top_k=args.top_k,
    ))


if __name__ == "__main__":
    main()
