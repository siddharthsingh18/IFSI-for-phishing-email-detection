"""Central model roles and benchmark-artifact discovery."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRIMARY_BENCHMARK_MODEL = "qwen2.5:0.5b"
DEFAULT_LIVE_MODEL = "qwen2.5:0.5b"
STRESS_TEST_MODEL = "qwen2.5:0.5b"
PROMOTION_CANDIDATE_MODEL = "llama3.2:3b"

MODEL_ROLES = {
    PRIMARY_BENCHMARK_MODEL: {
        "label": "Stress test: undersized model",
        "role": "stress_test",
        "description": "Current default until a promoted primary artifact exists",
    },
    PROMOTION_CANDIDATE_MODEL: {
        "label": "llama3.2:3b",
        "role": "candidate",
        "description": "Promotion candidate; not primary until a complete artifact exists",
    },
}


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _complete_manifest(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if data.get("status") == "complete" else None


def discover_models(results_dir: Path | None = None) -> dict[str, Any]:
    root = results_dir or (_root() / "results")
    models: dict[str, Any] = {}
    for model, metadata in MODEL_ROLES.items():
        primary_manifest = root / "primary" / model / "MANIFEST.json"
        stress_manifest = root / "stress-tests" / model / "MANIFEST.json"
        manifest = _complete_manifest(primary_manifest) or _complete_manifest(stress_manifest)
        entry = dict(metadata)
        entry["id"] = model
        entry["artifact"] = str(primary_manifest if primary_manifest.exists() else stress_manifest)
        entry["artifact_complete"] = manifest is not None
        models[model] = entry
    promoted = root / "primary" / PROMOTION_CANDIDATE_MODEL / "MANIFEST.json"
    if _complete_manifest(promoted):
        models[PROMOTION_CANDIDATE_MODEL]["role"] = "primary"
        primary = PROMOTION_CANDIDATE_MODEL
    else:
        primary = PRIMARY_BENCHMARK_MODEL
    return {"primary_model": primary, "available_models": list(models.values()), "benchmarks": models}
