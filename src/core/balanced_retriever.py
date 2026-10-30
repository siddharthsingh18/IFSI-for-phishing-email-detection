"""Balanced RAG Retriever for Experimental Phishing Detection.

Guarantees balanced representation between legitimate and phishing exemplars,
preventing lexical keyword matches (e.g. 'Concur Expense' or 'Mandatory HR')
from monovalently poisoning the retrieval context.
"""

from __future__ import annotations

import logging
from typing import Any, Sequence
import faiss
import numpy as np

logger = logging.getLogger(__name__)

REFERENCE_DELIMITER_START = "[BEGIN BALANCED REFERENCE EXAMPLES FROM VERIFIED ARCHIVE]"
REFERENCE_DELIMITER_END = "[END BALANCED REFERENCE EXAMPLES FROM VERIFIED ARCHIVE]"


class BalancedRAGRetriever:
    """Wrapper that builds fast in-memory sub-indices for balanced label retrieval."""

    def __init__(self, base_retriever: Any) -> None:
        self.base_retriever = base_retriever
        self.model = base_retriever.model
        self.dim = base_retriever.index.d if base_retriever and base_retriever.index else 384

        self.phish_metadata: list[dict[str, Any]] = []
        self.legit_metadata: list[dict[str, Any]] = []
        self.phish_index: faiss.IndexFlatIP | None = None
        self.legit_index: faiss.IndexFlatIP | None = None

        self._build_sub_indices()

    def _build_sub_indices(self) -> None:
        if self.base_retriever is None or self.base_retriever.index is None:
            return

        base_index = self.base_retriever.index
        base_meta = self.base_retriever.metadata
        n_total = base_index.ntotal

        phish_vecs = []
        legit_vecs = []

        for i in range(n_total):
            item = base_meta[i]
            vec = base_index.reconstruct(i)
            is_phish = str(item.get("label_name", "")).lower() == "phishing" or int(item.get("label", 0)) == 1

            if is_phish:
                phish_vecs.append(vec)
                self.phish_metadata.append(item)
            else:
                legit_vecs.append(vec)
                self.legit_metadata.append(item)

        if phish_vecs:
            arr_phish = np.ascontiguousarray(np.array(phish_vecs), dtype=np.float32)
            self.phish_index = faiss.IndexFlatIP(self.dim)
            self.phish_index.add(arr_phish)

        if legit_vecs:
            arr_legit = np.ascontiguousarray(np.array(legit_vecs), dtype=np.float32)
            self.legit_index = faiss.IndexFlatIP(self.dim)
            self.legit_index.add(arr_legit)

        logger.info(
            "BalancedRAGRetriever initialized: %d phishing exemplars, %d legitimate exemplars.",
            len(self.phish_metadata),
            len(self.legit_metadata),
        )

    def retrieve_balanced(
        self,
        query_text: str,
        k_phish: int = 2,
        k_legit: int = 2,
        max_text_len: int = 1500,
    ) -> list[dict[str, Any]]:
        """Retrieve top k_legit authentic and top k_phish attack exemplars."""
        if self.model is None or self.phish_index is None or self.legit_index is None:
            return []

        query_emb = self.model.encode(
            [query_text[:max_text_len]],
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        query_emb = np.ascontiguousarray(query_emb, dtype=np.float32)

        retrieved: list[dict[str, Any]] = []

        # 1. Retrieve top legitimate exemplars
        if self.legit_index.ntotal > 0:
            d_l, i_l = self.legit_index.search(query_emb, min(k_legit, self.legit_index.ntotal))
            for score, idx in zip(d_l[0], i_l[0]):
                if 0 <= idx < len(self.legit_metadata):
                    item = dict(self.legit_metadata[idx])
                    item["similarity_score"] = float(score)
                    retrieved.append(item)

        # 2. Retrieve top phishing exemplars
        if self.phish_index.ntotal > 0:
            d_p, i_p = self.phish_index.search(query_emb, min(k_phish, self.phish_index.ntotal))
            for score, idx in zip(d_p[0], i_p[0]):
                if 0 <= idx < len(self.phish_metadata):
                    item = dict(self.phish_metadata[idx])
                    item["similarity_score"] = float(score)
                    retrieved.append(item)

        return retrieved


_cached_balanced_retriever: BalancedRAGRetriever | None = None


def get_balanced_rag_retriever() -> BalancedRAGRetriever | None:
    """Singleton accessor for balanced RAG retriever."""
    global _cached_balanced_retriever
    if _cached_balanced_retriever is None:
        from .models import get_rag_retriever
        base_retriever = get_rag_retriever()
        if base_retriever is not None:
            _cached_balanced_retriever = BalancedRAGRetriever(base_retriever)
    return _cached_balanced_retriever


def format_balanced_reference_block(
    examples: Sequence[dict[str, Any]],
    max_chars_per_sample: int = 500,
) -> str:
    """Format balanced exemplars into an organized reference block for Stage 2."""
    if not examples:
        return "No reference exemplars available."

    lines = [
        REFERENCE_DELIMITER_START,
        "These verified training examples contrast authentic business emails against real phishing attacks in this domain:\n"
    ]

    for i, ex in enumerate(examples, start=1):
        content = ex.get("text", "").strip()
        if len(content) > max_chars_per_sample:
            content = content[:max_chars_per_sample] + "... [truncated]"
        label_str = ex.get("label_name") or ("phishing" if str(ex.get("label")) in ("1", "phishing") else "legitimate")
        score = ex.get("similarity_score", 0.0)

        lines.append(f"--- Archive Reference #{i} (Verified Ground Truth: {label_str.upper()}) [Similarity: {score:.2f}] ---")
        lines.append(f"Content:\n{content}\n")

    lines.append(REFERENCE_DELIMITER_END)
    return "\n".join(lines)
