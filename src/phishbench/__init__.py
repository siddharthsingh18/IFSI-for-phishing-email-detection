"""Reproducible injection-first phishing benchmark."""

from typing import Any

__version__ = "0.1.0"

_DATA_LOADER_EXPORTS = {
    "clean_text",
    "deduplicate_exact",
    "deduplicate_near_duplicates",
    "load_raw_records",
    "run_pipeline",
    "save_splits_to_jsonl",
    "stratified_split",
    "validate_splits",
}


_BASELINE_EXPORTS = {
    "compute_metrics",
    "train_and_evaluate_baseline",
}

_RAG_EXPORTS = {
    "FAISSRetriever",
    "classify_with_rag",
    "format_reference_block",
    "run_rag_pilot",
}

_INJECTION_EXPORTS = {
    "UNMARKED_REWRITES",
    "UNMARKED_STYLES",
    "build_injected_record",
    "build_injection_test_sets",
    "insert_marked_injection",
    "insert_unmarked_injection",
    "save_injection_datasets",
}


def __getattr__(name: str) -> Any:
    if name in _DATA_LOADER_EXPORTS:
        from . import data_loader

        return getattr(data_loader, name)
    if name in _BASELINE_EXPORTS:
        from . import baseline

        return getattr(baseline, name)
    if name in _RAG_EXPORTS:
        from . import rag

        return getattr(rag, name)
    if name in _INJECTION_EXPORTS:
        from . import injections

        return getattr(injections, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "__version__",
    *_DATA_LOADER_EXPORTS,
    *_BASELINE_EXPORTS,
    *_RAG_EXPORTS,
    *_INJECTION_EXPORTS,
]
