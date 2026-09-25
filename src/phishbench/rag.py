"""Retrieval-Augmented Generation (RAG) using sentence-transformers and FAISS on TRAIN split only."""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any, Sequence

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .baseline import compute_metrics
from .ollama_client import (
    EmailClassificationResult,
    OllamaClient,
    OllamaConfig,
)

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
REFERENCE_DELIMITER_START = "[BEGIN REFERENCE EXAMPLES FROM VERIFIED ARCHIVE]"
REFERENCE_DELIMITER_END = "[END REFERENCE EXAMPLES FROM VERIFIED ARCHIVE]"

RAG_SYSTEM_PROMPT = """You are a cybersecurity email classification system.
Your task is to analyze the candidate email and decide if it is 'phishing' or 'legitimate'.

You are provided with verified reference examples from the training archive to guide your assessment.
Study how patterns, urgency, headers, links, and tone in the reference examples correspond to their verified labels.

Rules:
1. Return ONLY a single valid JSON object.
2. The JSON object must strictly match this schema:
{
  "verdict": "phishing" or "legitimate",
  "confidence": <float between 0.0 and 1.0>,
  "reasons": ["<reason 1>", "<reason 2>", ...]
}
3. Do not include markdown codeblocks, explanation, or commentary outside the JSON object.
"""


class FAISSRetriever:
    """Vector similarity retriever using sentence-transformers and FAISS IndexFlatIP (cosine similarity)."""

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        model: SentenceTransformer | None = None,
    ) -> None:
        self.model_name = model_name
        self.model = model or SentenceTransformer(model_name)
        self.index: faiss.Index | None = None
        self.metadata: list[dict[str, Any]] = []

    @classmethod
    def build_from_train_split(
        cls,
        train_jsonl_path: Path | str,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        batch_size: int = 64,
        max_text_len: int = 1500,
    ) -> FAISSRetriever:
        """Build and populate FAISS index exclusively from the train split records."""
        train_path = Path(train_jsonl_path)
        if not train_path.exists():
            raise FileNotFoundError(f"Train split not found: {train_path}")

        records: list[dict[str, Any]] = []
        with train_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))

        retriever = cls(model_name=model_name)
        retriever.metadata = [
            {
                "id": str(r["id"]),
                "text": str(r["text"]),
                "label": int(r["label"]),
                "label_name": "phishing" if int(r["label"]) == 1 else "legitimate",
            }
            for r in records
        ]

        # Truncate overly long text for embedding to fit context efficiently
        texts_to_embed = [r["text"][:max_text_len] for r in retriever.metadata]

        logger.info("Computing embeddings for %d training samples...", len(texts_to_embed))
        embeddings = retriever.model.encode(
            texts_to_embed,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)

        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        retriever.index = index

        return retriever

    def save(self, directory: Path | str) -> None:
        """Persist FAISS index and metadata to disk."""
        target_dir = Path(directory)
        target_dir.mkdir(parents=True, exist_ok=True)

        if self.index is None:
            raise ValueError("Cannot save uninitialized index")

        faiss.write_index(self.index, str(target_dir / "train.index"))
        with (target_dir / "metadata.json").open("w", encoding="utf-8") as f:
            json.dump({"model_name": self.model_name, "records": self.metadata}, f)

    @classmethod
    def load(cls, directory: Path | str) -> FAISSRetriever:
        """Load persisted FAISS index and metadata from disk."""
        target_dir = Path(directory)
        meta_file = target_dir / "metadata.json"
        index_file = target_dir / "train.index"

        if not meta_file.exists() or not index_file.exists():
            raise FileNotFoundError(f"Missing index or metadata in {target_dir}")

        with meta_file.open("r", encoding="utf-8") as f:
            meta_data = json.load(f)

        retriever = cls(model_name=meta_data.get("model_name", DEFAULT_EMBEDDING_MODEL))
        retriever.index = faiss.read_index(str(index_file))
        retriever.metadata = meta_data["records"]
        return retriever

    @property
    def indexed_ids(self) -> set[str]:
        """Return the set of all email IDs present in the index."""
        return {r["id"] for r in self.metadata}

    @property
    def indexed_texts(self) -> set[str]:
        """Return the set of all raw email texts present in the index."""
        return {r["text"] for r in self.metadata}

    def retrieve(self, query_text: str, top_k: int = 3, max_text_len: int = 1500) -> list[dict[str, Any]]:
        """Retrieve top-k most similar labeled training emails for a query email."""
        if self.index is None:
            raise ValueError("FAISS index is not initialized")

        query_emb = self.model.encode(
            [query_text[:max_text_len]],
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        query_emb = np.ascontiguousarray(query_emb, dtype=np.float32)

        distances, indices = self.index.search(query_emb, top_k)
        retrieved: list[dict[str, Any]] = []

        for score, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx < len(self.metadata):
                item = dict(self.metadata[idx])
                item["similarity_score"] = float(score)
                retrieved.append(item)

        return retrieved


def format_reference_block(examples: Sequence[dict[str, Any]], max_chars_per_sample: int = 600) -> str:
    """Format retrieved examples into a clearly delimited reference block."""
    lines = [REFERENCE_DELIMITER_START]
    for i, ex in enumerate(examples, start=1):
        content = ex["text"].strip()
        if len(content) > max_chars_per_sample:
            content = content[:max_chars_per_sample] + "... [truncated]"
        lines.append(f"\n--- Reference Example #{i} ---")
        lines.append(f"True Label: {ex['label_name']}")
        lines.append(f"Email Content:\n{content}")
    lines.append(f"\n{REFERENCE_DELIMITER_END}")
    return "\n".join(lines)


def classify_with_rag(
    client: OllamaClient,
    retriever: FAISSRetriever,
    candidate_text: str,
    top_k: int = 3,
) -> tuple[EmailClassificationResult | None, dict[str, Any]]:
    """Retrieve top-k similar training emails, insert reference block, and classify with Ollama."""
    t0 = time.perf_counter()
    retrieved_examples = retriever.retrieve(candidate_text, top_k=top_k)
    reference_block = format_reference_block(retrieved_examples)

    user_prompt = f"""{reference_block}

Candidate Email To Classify:
---
{candidate_text}
---

Remember: Return ONLY a valid JSON object with {{"verdict": "phishing" or "legitimate", "confidence": <float>, "reasons": ["<reason>"]}}."""

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    payload = {
        "model": client.config.model,
        "messages": messages,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": client.config.temperature,
            "num_predict": client.config.num_predict,
        },
    }

    retries_used = 0
    last_error: str | None = None
    raw_response_content = ""
    max_attempts = 1 + client.config.max_retries

    for attempt in range(max_attempts):
        if attempt > 0:
            retries_used += 1

        try:
            resp = client.client.post("/api/chat", json=payload)
            if resp.status_code != 200:
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                continue

            res_json = resp.json()
            message_content = res_json.get("message", {}).get("content", "").strip()
            raw_response_content = message_content

            parsed_data = json.loads(message_content)
            validated = EmailClassificationResult.model_validate(parsed_data)
            latency = time.perf_counter() - t0

            metadata = {
                "is_valid": True,
                "retries": retries_used,
                "latency_seconds": round(latency, 4),
                "raw_response": raw_response_content,
                "retrieved_ids": [r["id"] for r in retrieved_examples],
                "retrieved_labels": [r["label_name"] for r in retrieved_examples],
                "error": None,
            }
            return validated, metadata

        except (json.JSONDecodeError, Exception) as exc:
            last_error = f"{type(exc).__name__}: {str(exc)}"

    latency = time.perf_counter() - t0
    metadata = {
        "is_valid": False,
        "retries": retries_used,
        "latency_seconds": round(latency, 4),
        "raw_response": raw_response_content,
        "retrieved_ids": [r["id"] for r in retrieved_examples],
        "retrieved_labels": [r["label_name"] for r in retrieved_examples],
        "error": last_error or "Unknown error",
    }
    return None, metadata


def run_rag_pilot(
    test_jsonl: Path,
    train_jsonl: Path,
    output_predictions: Path,
    output_summary: Path,
    index_cache_dir: Path | None = None,
    config_path: Path | None = None,
    limit: int = 50,
    top_k: int = 3,
) -> dict[str, Any]:
    """Execute RAG pilot on the exact same 50 test emails."""
    config = OllamaConfig.from_file(config_path) if config_path else OllamaConfig()
    client = OllamaClient(config)

    # Initialize or load retriever
    if index_cache_dir and (index_cache_dir / "train.index").exists():
        logger.info("Loading cached FAISS index from %s", index_cache_dir)
        retriever = FAISSRetriever.load(index_cache_dir)
    else:
        logger.info("Building FAISS index from %s", train_jsonl)
        retriever = FAISSRetriever.build_from_train_split(train_jsonl)
        if index_cache_dir:
            retriever.save(index_cache_dir)

    # Read test emails up to limit
    test_records: list[dict[str, Any]] = []
    with test_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                test_records.append(json.loads(line.strip()))
                if len(test_records) >= limit:
                    break

    output_predictions.parent.mkdir(parents=True, exist_ok=True)
    start_time = time.perf_counter()
    valid_count = 0
    invalid_count = 0
    y_true: list[int] = []
    y_pred: list[int] = []

    with output_predictions.open("w", encoding="utf-8") as out_f:
        for idx, rec in enumerate(test_records, start=1):
            email_id = rec.get("id", f"email-{idx}")
            true_label = int(rec.get("label", 0))
            text = rec.get("text", "")

            result, meta = classify_with_rag(
                client=client,
                retriever=retriever,
                candidate_text=text,
                top_k=top_k,
            )

            is_valid = meta["is_valid"]
            if is_valid and result is not None:
                valid_count += 1
                pred_label = 1 if result.verdict == "phishing" else 0
                y_true.append(true_label)
                y_pred.append(pred_label)
                verdict_str = result.verdict
                confidence_val = result.confidence
                reasons_list = result.reasons
            else:
                invalid_count += 1
                pred_label = None
                verdict_str = "error"
                confidence_val = None
                reasons_list = []

            record_out = {
                "id": email_id,
                "true_label": true_label,
                "true_label_name": "phishing" if true_label == 1 else "legitimate",
                "predicted_verdict": verdict_str,
                "predicted_label": pred_label,
                "confidence": confidence_val,
                "reasons": reasons_list,
                "is_valid": is_valid,
                "retries": meta["retries"],
                "latency_seconds": meta["latency_seconds"],
                "retrieved_ids": meta.get("retrieved_ids", []),
                "retrieved_labels": meta.get("retrieved_labels", []),
                "error": meta["error"],
            }
            out_f.write(json.dumps(record_out, ensure_ascii=False) + "\n")
            out_f.flush()

    total_runtime = time.perf_counter() - start_time
    total_samples = len(test_records)
    invalid_rate = (invalid_count / total_samples) if total_samples > 0 else 0.0

    metrics = {}
    if y_true and y_pred and len(y_true) == len(y_pred):
        metrics = compute_metrics(y_true, y_pred)

    summary = {
        "model": config.model,
        "method": f"RAG (top_k={top_k}) + Ollama",
        "top_k": top_k,
        "temperature": config.temperature,
        "total_emails_evaluated": total_samples,
        "total_runtime_seconds": round(total_runtime, 4),
        "avg_latency_per_email_seconds": round(total_runtime / total_samples, 4) if total_samples > 0 else 0.0,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "invalid_rate": round(invalid_rate, 4),
        "metrics_on_valid": metrics,
        "predictions_file": str(output_predictions),
    }

    output_summary.parent.mkdir(parents=True, exist_ok=True)
    with output_summary.open("w", encoding="utf-8") as sum_f:
        json.dump(summary, sum_f, indent=2)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", type=Path, default=Path("data/splits/test.jsonl"), help="Test split path")
    parser.add_argument("--train", type=Path, default=Path("data/splits/train.jsonl"), help="Train split path")
    parser.add_argument("--output", type=Path, default=Path("results/rag_predictions_50.jsonl"), help="Predictions output")
    parser.add_argument("--summary", type=Path, default=Path("results/rag_summary_50.json"), help="Summary output")
    parser.add_argument("--index-cache", type=Path, default=Path("results/rag_index"), help="Index cache dir")
    parser.add_argument("--config", type=Path, default=Path("config/ollama_config.json"), help="Ollama config")
    parser.add_argument("--limit", type=int, default=50, help="Number of test emails")
    parser.add_argument("--top-k", type=int, default=3, help="Top k neighbors to retrieve")
    args = parser.parse_args()

    res = run_rag_pilot(
        test_jsonl=args.test,
        train_jsonl=args.train,
        output_predictions=args.output,
        output_summary=args.summary,
        index_cache_dir=args.index_cache,
        config_path=args.config,
        limit=args.limit,
        top_k=args.top_k,
    )
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
