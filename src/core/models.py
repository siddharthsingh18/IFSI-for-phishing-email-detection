"""Core model management and resource loaders (cached without Streamlit)."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from phishbench.io import read_jsonl
from phishbench.rag import FAISSRetriever

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
CONFIG_DIR = BASE_DIR / "config"
RAG_INDEX_DIR = RESULTS_DIR / "rag_index"
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_m1_model() -> tuple[TfidfVectorizer, LogisticRegression]:
    """Train and cache the TF-IDF + LogisticRegression baseline model on train split."""
    train_path = DATA_DIR / "splits" / "review_seed42" / "train.jsonl"
    if not train_path.is_file():
        raise FileNotFoundError(f"M1 training data file not found: {train_path}")
    train_records = read_jsonl(train_path)
    if not train_records:
        raise ValueError(f"M1 training data file is empty: {train_path}")

    class_counts = {
        label: sum(int(record["label"]) == label for record in train_records)
        for label in (0, 1)
    }
    logger.info(
        "M1 training data loaded from %s: %d rows (legitimate=%d, phishing=%d)",
        train_path,
        len(train_records),
        class_counts[0],
        class_counts[1],
    )

    texts = [r["text"] for r in train_records]
    labels = [int(r["label"]) for r in train_records]

    vec = TfidfVectorizer(max_features=10000, stop_words="english", sublinear_tf=True)
    X = vec.fit_transform(texts)
    clf = LogisticRegression(C=1.0, random_state=42, max_iter=200, class_weight="balanced")
    clf.fit(X, labels)
    return vec, clf


@lru_cache(maxsize=1)
def get_rag_retriever() -> FAISSRetriever | None:
    """Load and cache FAISS RAG Retriever for M3 and M4."""
    if RAG_INDEX_DIR.exists() and (RAG_INDEX_DIR / "train.index").exists():
        try:
            return FAISSRetriever.load(RAG_INDEX_DIR)
        except Exception as exc:
            print(f"Warning: Failed to load FAISS index: {exc}")
            return None
    return None


def check_ollama_service(api_base: str = "http://127.0.0.1:11434") -> tuple[bool, list[str]]:
    """Check if local Ollama daemon is reachable and return list of pulled models."""
    try:
        resp = httpx.get(f"{api_base.rstrip('/')}/api/tags", timeout=2.5)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return True, models
    except Exception:
        pass
    return False, []
