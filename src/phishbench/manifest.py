"""Manifest generation and provenance tracking for benchmark runs.

Stores provenance JSON records alongside benchmark results containing:
- prompt_template_hash: sha256 of the exact prompt template used
- model_name: name of the model evaluated
- config_hash: sha256 of the configuration used
- git_commit: active git commit sha
- timestamp: UTC iso-formatted timestamp
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .io import sha256_text, write_json
from .ollama_client import SYSTEM_PROMPT, OllamaConfig
from .rag import RAG_SYSTEM_PROMPT
from .evaluate_decoupled_rag import SYSTEM_INJECTION_DETECTOR, SYSTEM_IS_PHISHING_ONLY


def get_git_commit(repo_path: Path | str | None = None) -> str:
    """Return the active git commit hash, or 'unknown' if not available."""
    env_commit = os.getenv("GIT_COMMIT") or os.getenv("GITHUB_SHA")
    if env_commit:
        return env_commit.strip()

    cwd = Path(repo_path) if repo_path else Path(__file__).resolve().parents[2]
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return proc.stdout.strip()
    except Exception:
        return "unknown"


def resolve_prompt_template(
    config: OllamaConfig | dict[str, Any] | str | Path | None = None,
    prompt_template: str | None = None,
    method: str = "default",
) -> str:
    """Resolve the prompt template text from config or explicit parameter."""
    if prompt_template is not None and prompt_template.strip():
        return prompt_template

    # Check config for prompt_template
    if isinstance(config, OllamaConfig):
        if getattr(config, "prompt_template", None):
            return config.prompt_template  # type: ignore[return-value]
    elif isinstance(config, dict) and config.get("prompt_template"):
        return str(config["prompt_template"])
    elif isinstance(config, (str, Path)) and Path(config).exists():
        try:
            with open(config, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data.get("prompt_template"):
                return str(data["prompt_template"])
        except Exception:
            pass

    # Method-based resolution
    norm_method = method.lower().strip()
    if norm_method in ("m3", "rag", "rag_combined"):
        return RAG_SYSTEM_PROMPT
    if norm_method in ("m4_call1", "injection_detector"):
        return SYSTEM_INJECTION_DETECTOR
    if norm_method in ("m4_call2", "is_phishing_only"):
        return SYSTEM_IS_PHISHING_ONLY
    if norm_method in ("m4", "decoupled", "rag_decoupled"):
        return f"{SYSTEM_INJECTION_DETECTOR}\n---\n{SYSTEM_IS_PHISHING_ONLY}"
    if norm_method in ("m1", "tfidf", "baseline"):
        return "TF-IDF + LogisticRegression baseline (no LLM prompt)"

    return SYSTEM_PROMPT


def compute_prompt_hash(
    config: OllamaConfig | dict[str, Any] | str | Path | None = None,
    prompt_template: str | None = None,
    method: str = "default",
) -> str:
    """Compute sha256 hash of the exact prompt template produced by or associated with config."""
    template = resolve_prompt_template(config=config, prompt_template=prompt_template, method=method)
    return sha256_text(template)


def compute_config_hash(config: OllamaConfig | dict[str, Any] | str | Path | None) -> str:
    """Compute deterministic sha256 hash of configuration."""
    if config is None:
        raw_dict: dict[str, Any] = {}
    elif isinstance(config, OllamaConfig):
        raw_dict = config.model_dump() if hasattr(config, "model_dump") else config.dict()
    elif isinstance(config, dict):
        raw_dict = config
    elif isinstance(config, (str, Path)) and Path(config).exists():
        try:
            with open(config, encoding="utf-8") as f:
                data = json.load(f)
            raw_dict = data if isinstance(data, dict) else {"raw": str(data)}
        except Exception:
            raw_dict = {"raw": Path(config).read_text(encoding="utf-8")}
    else:
        raw_dict = {"raw": str(config)}

    canonical_json = json.dumps(raw_dict, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(canonical_json)


def get_manifest_path(results_file: Path | str) -> Path:
    """Return the manifest path located alongside the results file."""
    p = Path(results_file)
    return p.with_suffix(".manifest.json")


def create_manifest_record(
    results_file: Path | str | None = None,
    config: OllamaConfig | dict[str, Any] | str | Path | None = None,
    model_name: str | None = None,
    prompt_template: str | None = None,
    method: str = "default",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a benchmark manifest JSON record with all required provenance fields."""
    resolved_model = model_name
    if not resolved_model:
        if isinstance(config, OllamaConfig):
            resolved_model = config.model
        elif isinstance(config, dict) and "model" in config:
            resolved_model = str(config["model"])
        elif isinstance(config, (str, Path)) and Path(config).exists():
            try:
                with open(config, encoding="utf-8") as f:
                    cfg_data = json.load(f)
                if isinstance(cfg_data, dict) and "model" in cfg_data:
                    resolved_model = str(cfg_data["model"])
            except Exception:
                pass
        if not resolved_model:
            resolved_model = "unknown"

    p_hash = compute_prompt_hash(config=config, prompt_template=prompt_template, method=method)
    c_hash = compute_config_hash(config)
    commit = get_git_commit()
    timestamp = datetime.now(timezone.utc).isoformat()

    record: dict[str, Any] = {
        "prompt_template_hash": p_hash,
        "model_name": resolved_model,
        "config_hash": c_hash,
        "git_commit": commit,
        "timestamp": timestamp,
        # Backward-compatible and convenience aliases:
        "prompt_hash": p_hash,
        "model": resolved_model,
        "timestamp_utc": timestamp,
    }

    if results_file:
        record["results_file"] = Path(results_file).name

    if extra:
        for k, v in extra.items():
            if k not in record:
                record[k] = v

    return record


def save_manifest_alongside(
    results_file: Path | str,
    manifest: dict[str, Any] | None = None,
    config: OllamaConfig | dict[str, Any] | str | Path | None = None,
    model_name: str | None = None,
    prompt_template: str | None = None,
    method: str = "default",
    extra: dict[str, Any] | None = None,
) -> Path:
    """Save manifest record to a JSON file alongside results_file."""
    target_path = get_manifest_path(results_file)
    if manifest is None:
        manifest = create_manifest_record(
            results_file=results_file,
            config=config,
            model_name=model_name,
            prompt_template=prompt_template,
            method=method,
            extra=extra,
        )
    write_json(target_path, manifest)
    return target_path


def get_all_method_prompt_hashes() -> dict[str, str]:
    """Return dictionary of prompt template hashes for M1, M2, M3, and M4."""
    return {
        "M1": compute_prompt_hash(method="m1"),
        "M2": compute_prompt_hash(method="m2"),
        "M3": compute_prompt_hash(method="m3"),
        "M4": compute_prompt_hash(method="m4"),
        "M4_call1_injection_detector": compute_prompt_hash(method="m4_call1"),
        "M4_call2_is_phishing_only": compute_prompt_hash(method="m4_call2"),
    }
