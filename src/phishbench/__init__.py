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


def __getattr__(name: str) -> Any:
    if name in _DATA_LOADER_EXPORTS:
        from . import data_loader

        return getattr(data_loader, name)
    if name in _BASELINE_EXPORTS:
        from . import baseline

        return getattr(baseline, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "__version__",
    *_DATA_LOADER_EXPORTS,
    *_BASELINE_EXPORTS,
]
