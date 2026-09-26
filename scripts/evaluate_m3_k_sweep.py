"""Run M3 RAG retrieval sweep across k=1, k=3, k=5 on the fixed 50-email pilot."""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import time
from pathlib import Path
from typing import Any

import httpx

from phishbench.benchmark_suite import (
    classify_m3_single,
    compute_cell_metrics,
)
from phishbench.io import read_jsonl, write_json, write_jsonl
from phishbench.manifest import save_manifest_alongside
from phishbench.ollama_client import OllamaConfig
from phishbench.rag import FAISSRetriever, format_reference_block


async def run_batch_with_progress(
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
        res = await classify_m3_single(client, config, rec, condition, semaphore)
        predictions[idx] = res
        completed += 1
        if completed % 10 == 0 or completed == total:
            print(f"      progress: {completed}/{total} completed", flush=True)

    await asyncio.gather(*[_worker(i, r) for i, r in enumerate(records)])
    return predictions


async def run_k_sweep(
    config_path: Path,
    test_path: Path,
    rag_index_dir: Path,
    results_dir: Path,
    k_values: list[int] = [1, 3, 5],
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

    model_clean = config.model.replace(":", "_").replace(".", "_")
    print("=" * 60)
    print(f"M3 RAG Retrieval k-Sweep for Model: {config.model}")
    print(f"k values: {k_values} | Pilot subsample: first {limit} test emails")
    print(f"Config: {config_path}")
    print("=" * 60)

    # 1. Load the fixed pilot subsample (first N emails)
    all_test = read_jsonl(test_path)
    base_records = [dict(r) for r in all_test[:limit]]
    for r in base_records:
        if "original_id" not in r:
            r["original_id"] = r["id"]

    print(f"\nLoaded {len(base_records)} fixed pilot emails.")
    print("Loading FAISS RAG index from:", rag_index_dir)
    retriever = FAISSRetriever.load(rag_index_dir)
    print("Retriever ready.\n")

    semaphore = asyncio.Semaphore(concurrency)
    sweep_results: dict[str, Any] = {
        "model": config.model,
        "k_values": k_values,
        "results_by_k": {},
    }

    async with httpx.AsyncClient(base_url=config.api_base, timeout=config.timeout_seconds) as client:
        for k in k_values:
            print(f"\n---> Evaluating M3 with k={k} ({len(base_records)} emails)...")
            # Build records with k-specific reference block
            k_records = []
            for r in base_records:
                rec_copy = copy.deepcopy(r)
                rec_copy["ref_block"] = format_reference_block(
                    retriever.retrieve(rec_copy["text"], top_k=k)
                )
                k_records.append(rec_copy)

            t0 = time.perf_counter()
            preds = await run_batch_with_progress(
                k_records, "clean", client, config, semaphore
            )
            duration = round(time.perf_counter() - t0, 2)

            pred_file = results_dir / f"pilot_50_{model_clean}_M3_k{k}_predictions.jsonl"
            write_jsonl(pred_file, preds)
            save_manifest_alongside(pred_file, config=config, model_name=config.model, method="m3", extra={"k": k})

            metrics = compute_cell_metrics(preds)
            metrics["runtime_seconds"] = duration
            metrics["avg_latency"] = round(duration / len(preds), 2)
            metrics["k"] = k

            sweep_results["results_by_k"][f"k={k}"] = {
                "k": k,
                "metrics": metrics,
                "predictions_file": str(pred_file),
            }

            print(f"      Completed k={k} in {duration}s:")
            print(f"      Accuracy: {metrics['accuracy'] * 100:.1f}%, F1: {metrics['f1']:.4f}, FPR: {metrics['fpr'] * 100:.1f}%, Recall: {metrics['recall'] * 100:.1f}%, Valid: {metrics['valid_count']}/{metrics['total_samples']}")

    summary_file = results_dir / f"pilot_50_{model_clean}_m3_k_sweep_summary.json"
    write_json(summary_file, sweep_results)
    save_manifest_alongside(summary_file, config=config, model_name=config.model, method="m3", extra={"k_values": k_values})
    print(f"\nSaved k-sweep summary and manifest to {summary_file}")

    # Print summary table
    print("\n" + "=" * 65)
    print(f"M3 Pilot k-Sweep Results ({config.model}, N={limit})")
    print("=" * 65)
    print(f"{'k':<5} | {'Accuracy':<10} | {'F1 Score':<10} | {'FPR':<10} | {'Recall':<10} | {'Valid':<8}")
    print("-" * 65)
    for k in k_values:
        m = sweep_results["results_by_k"][f"k={k}"]["metrics"]
        print(f"k={k:<3} | {m['accuracy']*100:>8.1f}% | {m['f1']:>10.4f} | {m['fpr']*100:>8.1f}% | {m['recall']*100:>8.1f}% | {m['valid_count']}/{m['total_samples']}")
    print("=" * 65 + "\n")

    return sweep_results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/ollama_llama3.2_3b.json"))
    parser.add_argument("--test", type=Path, default=Path("data/splits/test.jsonl"))
    parser.add_argument("--rag-index", type=Path, default=Path("results/rag_index"))
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("-k", "--k", type=int, nargs="+", default=[1, 3, 5], help="List of k values to evaluate")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()

    asyncio.run(
        run_k_sweep(
            config_path=args.config,
            test_path=args.test,
            rag_index_dir=args.rag_index,
            results_dir=args.results_dir,
            k_values=args.k,
            limit=args.limit,
            concurrency=args.concurrency,
        )
    )


if __name__ == "__main__":
    main()
