"""Central model roles and benchmark-artifact discovery."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Primary default model for production/live inference and primary evaluation
PRIMARY_BENCHMARK_MODEL = "qwen3.5:4b"
DEFAULT_LIVE_MODEL = "qwen3.5:4b"

# Preserved lightweight baseline and stress-test models
LIGHTWEIGHT_BASELINE_MODEL = "qwen2.5:0.5b"
STRESS_TEST_MODEL = "qwen2.5:0.5b"
PROMOTION_CANDIDATE_MODEL = "llama3.2:3b"

MODEL_ROLES = {
    PRIMARY_BENCHMARK_MODEL: {
        "label": "qwen3.5:4b (Primary Reasoning Model)",
        "role": "primary",
        "description": "Recommended default model for live inference and primary evaluation",
    },
    LIGHTWEIGHT_BASELINE_MODEL: {
        "label": "qwen2.5:0.5b (Lightweight Baseline)",
        "role": "baseline",
        "description": "Preserved lightweight baseline and stress test model",
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
        safe_model = model.replace(":", "_")
        
        # Check raw model directory and sanitized directory
        primary_manifest = root / "primary" / safe_model / "MANIFEST.json"
        if not primary_manifest.exists():
            try:
                raw_path = root / "primary" / model / "MANIFEST.json"
                if raw_path.exists():
                    primary_manifest = raw_path
            except OSError:
                pass

        stress_manifest = root / "stress-tests" / safe_model / "MANIFEST.json"
        if not stress_manifest.exists():
            try:
                raw_path = root / "stress-tests" / model / "MANIFEST.json"
                if raw_path.exists():
                    stress_manifest = raw_path
            except OSError:
                pass

        manifest = _complete_manifest(primary_manifest) or _complete_manifest(stress_manifest)
        entry = dict(metadata)
        entry["id"] = model
        entry["artifact"] = str(primary_manifest if primary_manifest.exists() else stress_manifest)
        entry["artifact_complete"] = manifest is not None
        models[model] = entry

    cand_safe = PROMOTION_CANDIDATE_MODEL.replace(":", "_")
    promoted = root / "primary" / cand_safe / "MANIFEST.json"
    if not promoted.exists():
        try:
            raw_path = root / "primary" / PROMOTION_CANDIDATE_MODEL / "MANIFEST.json"
            if raw_path.exists():
                promoted = raw_path
        except OSError:
            pass

    if _complete_manifest(promoted):
        models[PROMOTION_CANDIDATE_MODEL]["role"] = "primary"
        primary = PROMOTION_CANDIDATE_MODEL
    else:
        primary = PRIMARY_BENCHMARK_MODEL
    return {"primary_model": primary, "available_models": list(models.values()), "benchmarks": models}
