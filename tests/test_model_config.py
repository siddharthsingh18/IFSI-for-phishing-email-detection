import os
from pathlib import Path

from core.model_config import discover_models, PRIMARY_BENCHMARK_MODEL, PROMOTION_CANDIDATE_MODEL


def test_defaults_remain_qwen_without_complete_primary_artifact(tmp_path: Path) -> None:
    catalog = discover_models(tmp_path)
    assert catalog["primary_model"] == PRIMARY_BENCHMARK_MODEL
    assert catalog["primary_model"] == "qwen3.5:4b"


def test_complete_llama_manifest_is_promoted(tmp_path: Path) -> None:
    safe_name = PROMOTION_CANDIDATE_MODEL.replace(":", "_") if os.name == "nt" else PROMOTION_CANDIDATE_MODEL
    manifest_dir = tmp_path / "primary" / safe_name
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "MANIFEST.json").write_text('{"status":"complete"}', encoding="utf-8")
    catalog = discover_models(tmp_path)
    assert catalog["primary_model"] == "llama3.2:3b"
