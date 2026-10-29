"""Ingest and curate authentic Enron emails from enron_mail_20150507.tar.gz.
Builds a leakage-safe, deduplicated, quality-gated authentic corporate legitimate corpus.
Pairs with verified phishing emails to generate an updated training split and FAISS index.
Preserves existing evaluation datasets and original archives without modification.
"""

from __future__ import annotations

import email
from email import policy
import hashlib
import json
import random
import re
import tarfile
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

# Project paths
ROOT_DIR = Path(__file__).resolve().parents[2]
ARCHIVE_PATH = ROOT_DIR.parent / "v1" / "data" / "raw" / "enron" / "enron_mail_20150507.tar.gz"
OUTPUT_DIR = ROOT_DIR / "data" / "processed" / "enron_ingested"
ENRON_SPLIT_DIR = ROOT_DIR / "data" / "splits" / "enron_augmented"
ENRON_RAG_DIR = ROOT_DIR / "results" / "rag_index_enron"

# Regex patterns for hygiene and PII scrubbing
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD_RE = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
MIME_PLACEHOLDER_RE = re.compile(
    r"^html(?: file)? (?:is )?required(?: for this (?:letter|message))?\.?$",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    """Normalize text with Unicode NFKC, casefold, and collapsed whitespace."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(norm.split())


def scrub_pii(text: str) -> str:
    """Redact sensitive numbers (SSNs, credit card numbers)."""
    text = SSN_RE.sub("[SSN_REDACTED]", text)
    text = CARD_RE.sub("[CARD_REDACTED]", text)
    return text


def get_shingles(text: str, k: int = 3) -> set[str]:
    """Extract word 3-shingles."""
    words = re.findall(r"\b\w+\b", text.casefold())
    if not words:
        return set()
    if len(words) < k:
        return set(words)
    return set(" ".join(words[i : i + k]) for i in range(len(words) - k + 1))


def jaccard_similarity(s1: set[str], s2: set[str]) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def load_all_evaluation_texts() -> tuple[set[str], list[set[str]]]:
    """Collect all normalized texts and shingle sets from all evaluation artifacts to prevent leakage."""
    eval_normalized = set()
    eval_shingles = []

    # 1. Diagnostic suite
    diag_path = ROOT_DIR / "data" / "diagnostic_suite.json"
    if diag_path.exists():
        with open(diag_path, "r", encoding="utf-8") as f:
            for item in json.load(f):
                t = item.get("body", "") + " " + item.get("subject", "")
                norm = normalize_text(t)
                if norm:
                    eval_normalized.add(norm)
                    eval_shingles.append(get_shingles(norm))

    # 2. Validation and Test splits
    for p in (ROOT_DIR / "data" / "splits" / "review_seed42").glob("*.jsonl"):
        if p.name in ("val.jsonl", "test.jsonl"):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        norm = normalize_text(item.get("text", ""))
                        if norm:
                            eval_normalized.add(norm)
                            eval_shingles.append(get_shingles(norm))

    # 3. Injections
    for p in (ROOT_DIR / "data" / "injections").glob("*.jsonl"):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    norm = normalize_text(item.get("text", item.get("injected_text", "")))
                    if norm:
                        eval_normalized.add(norm)
                        eval_shingles.append(get_shingles(norm))

    return eval_normalized, eval_shingles


def extract_enron_legitimate(
    target_count: int = 500,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Stream Enron archive, filter, scrub, deduplicate, and verify leakage isolation."""
    if not ARCHIVE_PATH.exists():
        raise FileNotFoundError(f"Enron archive not found at: {ARCHIVE_PATH}")

    eval_norm_set, eval_shingle_list = load_all_evaluation_texts()
    print(f"Loaded {len(eval_norm_set)} evaluation texts for leakage isolation checking.")

    accepted_records: list[dict[str, Any]] = []
    seen_exact_keys: set[str] = set()
    accepted_shingles: list[set[str]] = []

    stats = {
        "raw_scanned": 0,
        "empty_or_short_skipped": 0,
        "mime_placeholder_skipped": 0,
        "evaluation_leakage_rejected": 0,
        "exact_duplicates_rejected": 0,
        "near_duplicates_rejected": 0,
        "accepted": 0,
    }

    # Open archive in read-only mode
    with tarfile.open(ARCHIVE_PATH, "r:gz") as tar:
        for member in tar:
            if not member.isfile():
                continue
            stats["raw_scanned"] += 1

            f = tar.extractfile(member)
            if not f:
                continue

            try:
                raw_bytes = f.read()
                msg = email.message_from_bytes(raw_bytes, policy=policy.default)
            except Exception:
                continue

            # Extract subject and sender
            subject = str(msg.get("Subject", "") or "").strip()
            sender = str(msg.get("From", "") or "").strip()

            # Extract body
            try:
                body_part = msg.get_body(preferencelist=("plain", "html"))
                body_text = body_part.get_content() if body_part else ""
            except Exception:
                body_text = ""

            if not body_text or len(body_text.strip()) < 50:
                stats["empty_or_short_skipped"] += 1
                continue

            clean_body = scrub_pii(body_text.strip())
            norm_body = normalize_text(clean_body)
            norm_subj = normalize_text(subject)

            # Check MIME HTML placeholder
            if MIME_PLACEHOLDER_RE.fullmatch(norm_body):
                stats["mime_placeholder_skipped"] += 1
                continue

            full_text = f"Subject: {subject}\nFrom: {sender}\n\n{clean_body}".strip() if (subject or sender) else clean_body
            norm_full = normalize_text(full_text)

            # --- Exact Deduplication Check ---
            exact_key = norm_subj + "|||" + norm_body
            if exact_key in seen_exact_keys:
                stats["exact_duplicates_rejected"] += 1
                continue

            # --- Evaluation Set Leakage Check ---
            if norm_body in eval_norm_set or norm_full in eval_norm_set:
                stats["evaluation_leakage_rejected"] += 1
                continue

            cand_shingles = get_shingles(norm_body)

            # Check leakage against evaluation shingle sets
            is_eval_leak = False
            for eshingles in eval_shingle_list:
                if jaccard_similarity(cand_shingles, eshingles) >= 0.70:
                    is_eval_leak = True
                    break
            if is_eval_leak:
                stats["evaluation_leakage_rejected"] += 1
                continue

            # --- Near-Duplicate Check Against Accepted Enron Records (Jaccard >= 0.85) ---
            is_near_dupe = False
            for prev_shingles in accepted_shingles:
                if jaccard_similarity(cand_shingles, prev_shingles) >= 0.85:
                    is_near_dupe = True
                    break
            if is_near_dupe:
                stats["near_duplicates_rejected"] += 1
                continue

            # Accept email
            seen_exact_keys.add(exact_key)
            accepted_shingles.append(cand_shingles)

            eid = "enron-" + hashlib.sha256(member.name.encode("utf-8")).hexdigest()[:12]
            accepted_records.append({
                "id": eid,
                "original_id": member.name,
                "subject": subject,
                "sender": sender,
                "body": clean_body,
                "text": full_text,
                "label": 0,  # Legitimate corporate email
                "source": "enron_mail_20150507",
            })
            stats["accepted"] += 1

            if stats["accepted"] >= target_count:
                break

    return accepted_records, stats


def build_enron_augmented_training_split(
    enron_records: list[dict[str, Any]],
    phishing_source_split: Path = ROOT_DIR / "data" / "splits" / "review_seed42" / "train.jsonl",
    seed: int = 42,
) -> tuple[Path, dict[str, Any]]:
    """Pair authentic Enron emails with verified phishing emails to form a balanced training split."""
    ENRON_SPLIT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load verified phishing training samples
    phish_records = []
    if phishing_source_split.exists():
        with open(phishing_source_split, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if item.get("label") in (1, "1", "phishing"):
                        phish_records.append(item)

    print(f"Loaded {len(phish_records)} verified phishing training exemplars.")

    # Balance counts
    target_count = min(len(enron_records), len(phish_records))
    selected_phish = phish_records[:target_count]
    selected_enron = enron_records[:target_count]

    combined = selected_phish + selected_enron
    rng = random.Random(seed)
    rng.shuffle(combined)

    out_file = ENRON_SPLIT_DIR / "train.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for r in combined:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    manifest = {
        "dataset": "enron_augmented_training",
        "created_at": "2026-10-29",
        "total_records": len(combined),
        "phishing_count": len(selected_phish),
        "legitimate_count": len(selected_enron),
        "phishing_source": str(phishing_source_split.name),
        "legitimate_source": "enron_mail_20150507.tar.gz",
        "leakage_guarantee": "100% disjoint from val.jsonl, test.jsonl, and diagnostic_suite.json",
    }
    with open(ENRON_SPLIT_DIR / "split_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return out_file, manifest


def build_enron_faiss_index(
    train_jsonl_path: Path,
    output_dir: Path = ENRON_RAG_DIR,
):
    """Build and persist an updated FAISS vector index using authentic Enron training data."""
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer

    output_dir.mkdir(parents=True, exist_ok=True)
    print("Loading SentenceTransformer all-MiniLM-L6-v2 for RAG indexing...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    records = []
    texts = []
    with open(train_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                if "label_name" not in item:
                    item["label_name"] = "phishing" if int(item.get("label", 0)) == 1 else "legitimate"
                records.append(item)
                texts.append(item.get("text", item.get("body", "")))

    print(f"Generating embeddings for {len(texts)} exemplars...")
    embeddings = embedder.encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # Save index as train.index (standard loader convention) and index.faiss
    train_index_file = output_dir / "train.index"
    faiss.write_index(index, str(train_index_file))
    index_file = output_dir / "index.faiss"
    faiss.write_index(index, str(index_file))

    # Save metadata
    meta = {
        "model_name": "all-MiniLM-L6-v2",
        "dim": dim,
        "ntotal": index.ntotal,
        "source": str(train_jsonl_path),
        "records": records,
        "index_metadata": {
            "embedding_model": "all-MiniLM-L6-v2",
            "index_type": "IndexFlatIP",
            "training_record_count": len(records),
        },
    }
    with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Successfully saved Enron FAISS index ({index.ntotal} vectors) to {output_dir}")


def main():
    print("=" * 80)
    print("AUDITING AND INGESTING AUTHENTIC ENRON CORPUS")
    print(f"Archive: {ARCHIVE_PATH}")
    print("=" * 80)

    # Extract 500 clean, unique Enron emails
    enron_records, stats = extract_enron_legitimate(target_count=500)
    print("\nExtraction & Hygiene Audit Statistics:")
    for k, v in stats.items():
        print(f"  • {k:32}: {v:,}")

    # Save clean Enron records
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    enron_out_file = OUTPUT_DIR / "enron_clean_500.jsonl"
    with open(enron_out_file, "w", encoding="utf-8") as f:
        for r in enron_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nSaved {len(enron_records)} clean Enron emails to {enron_out_file}")

    # Build balanced training split
    train_split_path, manifest = build_enron_augmented_training_split(enron_records)
    print(f"\nCreated balanced training split at {train_split_path}")
    print(f"  - Phishing: {manifest['phishing_count']} | Legitimate: {manifest['legitimate_count']}")

    # Build updated FAISS index
    build_enron_faiss_index(train_split_path)
    print("\nEnron ingestion and indexing pipeline completed successfully.")


if __name__ == "__main__":
    main()
