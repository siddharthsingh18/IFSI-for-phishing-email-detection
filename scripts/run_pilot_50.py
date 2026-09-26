"""50-email pilot benchmark for M2, M3, and M4 across model configurations."""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import Any

import httpx

from phishbench.benchmark_suite import (
    classify_m2_single,
    classify_m3_single,
    classify_m4_single,
    compute_cell_metrics,
)
from phishbench.io import read_jsonl, write_json, write_jsonl
from phishbench.manifest import save_manifest_alongside
from phishbench.ollama_client import OllamaConfig
from phishbench.rag import FAISSRetriever, format_reference_block


async def run_batch_with_pilot_progress(
    classifier_fn: Any,
    records: list[dict[str, Any]],
    condition: str,
    client: httpx.AsyncClient,
    config: OllamaConfig,
    semaphore: asyncio.Semaphore,
) -> list[dict[str, Any]]:
    completed = 0
    total = len(records)
    predictions: list[Any] = [None] * total

    async def _worker(idx: int, rec: dict[str, Any]) -> None:
        nonlocal completed
        res = await classifier_fn(client, config, rec, condition, semaphore)
        predictions[idx] = res
        completed += 1
        if completed % 10 == 0 or completed == total:
            print(f"    progress: {completed}/{total} completed", flush=True)

    await asyncio.gather(*[_worker(i, r) for i, r in enumerate(records)])
    return predictions


async def run_pilot_suite(
    config_path: Path,
    test_path: Path,
    rag_index_dir: Path,
    results_dir: Path,
    limit: int = 50,
    concurrency: int = 4,
) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as f:
        cfg_dict = json.load(f)
    config = OllamaConfig(
        model=cfg_dict.get("model", "llama3.2:3b"),
        temperature=float(cfg_dict.get("temperature", 0.0)),
        api_base=cfg_dict.get("api_base", "http://127.0.0.1:11434"),
        timeout_seconds=float(cfg_dict.get("timeout_seconds", 30.0)),
        max_retries=int(cfg_dict.get("max_retries", 1)),
        num_predict=int(cfg_dict.get("num_predict", 512)),
    )

    model_clean_name = config.model.replace(":", "_").replace(".", "_")
    print(f"\n=======================================================")
    print(f"Running 50-Email Pilot for Model: {config.model}")
    print(f"Config: {config_path}")
    print(f"=======================================================\n")

    # 1. Load test samples (first N)
    all_test = read_jsonl(test_path)
    pilot_records = [dict(r) for r in all_test[:limit]]
    print(f"Loaded first {len(pilot_records)} test emails from {test_path}.")

    # 2. Attach RAG references
    print("Loading FAISS RAG index for reference exemplars...")
    retriever = FAISSRetriever.load(rag_index_dir)
    for r in pilot_records:
        if "original_id" not in r:
            r["original_id"] = r["id"]
        if "ref_block" not in r:
            r["ref_block"] = format_reference_block(retriever.retrieve(r["text"], top_k=3))
    print("RAG references ready.")

    semaphore = asyncio.Semaphore(concurrency)
    results: dict[str, Any] = {"model": config.model, "methods": {}}

    async with httpx.AsyncClient(base_url=config.api_base, timeout=config.timeout_seconds) as client:
        # --- M2: Zero-Shot LLM ---
        m2_pred_file = results_dir / f"pilot_50_{model_clean_name}_M2_predictions.jsonl"
        print(f"\n[M2] Running Zero-Shot LLM on {len(pilot_records)} emails...")
        t0 = time.perf_counter()
        m2_preds = await run_batch_with_pilot_progress(
            classify_m2_single, pilot_records, "clean", client, config, semaphore
        )
        m2_duration = round(time.perf_counter() - t0, 2)
        write_jsonl(m2_pred_file, m2_preds)
        save_manifest_alongside(m2_pred_file, config=config, model_name=config.model, method="m2")
        m2_metrics = compute_cell_metrics(m2_preds)
        m2_metrics["runtime_seconds"] = m2_duration
        results["methods"]["M2"] = {
            "metrics": m2_metrics,
            "predictions_file": str(m2_pred_file),
        }
        print(f"  [M2] Completed in {m2_duration}s. Valid: {m2_metrics['valid_count']}/{m2_metrics['total_samples']}, Acc: {m2_metrics['accuracy']}, Recall: {m2_metrics['recall']}, FPR: {m2_metrics['fpr']}")

        # --- M3: RAG Combined Single-Call ---
        m3_pred_file = results_dir / f"pilot_50_{model_clean_name}_M3_predictions.jsonl"
        print(f"\n[M3] Running RAG Combined Single-Call on {len(pilot_records)} emails...")
        t0 = time.perf_counter()
        m3_preds = await run_batch_with_pilot_progress(
            classify_m3_single, pilot_records, "clean", client, config, semaphore
        )
        m3_duration = round(time.perf_counter() - t0, 2)
        write_jsonl(m3_pred_file, m3_preds)
        save_manifest_alongside(m3_pred_file, config=config, model_name=config.model, method="m3")
        m3_metrics = compute_cell_metrics(m3_preds)
        m3_metrics["runtime_seconds"] = m3_duration
        results["methods"]["M3"] = {
            "metrics": m3_metrics,
            "predictions_file": str(m3_pred_file),
        }
        print(f"  [M3] Completed in {m3_duration}s. Valid: {m3_metrics['valid_count']}/{m3_metrics['total_samples']}, Acc: {m3_metrics['accuracy']}, Recall: {m3_metrics['recall']}, FPR: {m3_metrics['fpr']}")

        # --- M4: RAG Two-Call Decoupled ---
        m4_pred_file = results_dir / f"pilot_50_{model_clean_name}_M4_predictions.jsonl"
        print(f"\n[M4] Running RAG Two-Call Decoupled on {len(pilot_records)} emails...")
        t0 = time.perf_counter()
        m4_preds = await run_batch_with_pilot_progress(
            classify_m4_single, pilot_records, "clean", client, config, semaphore
        )
        m4_duration = round(time.perf_counter() - t0, 2)
        write_jsonl(m4_pred_file, m4_preds)
        save_manifest_alongside(m4_pred_file, config=config, model_name=config.model, method="m4")
        m4_metrics = compute_cell_metrics(m4_preds)
        m4_metrics["runtime_seconds"] = m4_duration
        results["methods"]["M4"] = {
            "metrics": m4_metrics,
            "predictions_file": str(m4_pred_file),
        }
        print(f"  [M4] Completed in {m4_duration}s. Valid: {m4_metrics['valid_count']}/{m4_metrics['total_samples']}, Acc: {m4_metrics['accuracy']}, Recall: {m4_metrics['recall']}, FPR: {m4_metrics['fpr']}")

    # Save summary json
    summary_path = results_dir / f"pilot_50_{model_clean_name}_summary.json"
    write_json(summary_path, results)
    save_manifest_alongside(summary_path, config=config, model_name=config.model)
    print(f"\nSaved pilot summary and manifest to {summary_path}")


    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/ollama_llama3.2_3b.json"))
    parser.add_argument("--test", type=Path, default=Path("data/splits/test.jsonl"))
    parser.add_argument("--rag-index", type=Path, default=Path("results/rag_index"))
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()

    asyncio.run(
        run_pilot_suite(
            config_path=args.config,
            test_path=args.test,
            rag_index_dir=args.rag_index,
            results_dir=args.results_dir,
            limit=args.limit,
            concurrency=args.concurrency,
        )
    )


if __name__ == "__main__":
    main()
