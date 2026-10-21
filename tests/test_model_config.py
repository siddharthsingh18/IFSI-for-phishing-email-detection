from pathlib import Path

from core.model_config import discover_models


def test_defaults_remain_qwen_without_complete_primary_artifact(tmp_path: Path) -> None:
    catalog = discover_models(tmp_path)
    assert catalog["primary_model"] == "qwen2.5:0.5b"


def test_complete_llama_manifest_is_promoted(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "primary" / "llama3.2:3b"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "MANIFEST.json").write_text('{"status":"complete"}', encoding="utf-8")
    catalog = discover_models(tmp_path)
    assert catalog["primary_model"] == "llama3.2:3b"
