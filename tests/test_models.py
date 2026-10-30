from __future__ import annotations

import logging
import re
from collections.abc import Iterator

import pytest

from core import models


@pytest.fixture(autouse=True)
def clear_m1_model_cache() -> Iterator[None]:
    models.get_m1_model.cache_clear()
    yield
    models.get_m1_model.cache_clear()


def test_m1_raises_when_training_file_is_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(models, "DATA_DIR", tmp_path)
    expected_path = tmp_path / "splits" / "clean_split_v1" / "train.jsonl"

    with pytest.raises(FileNotFoundError, match=re.escape(str(expected_path))):
        models.get_m1_model()


def test_m1_raises_when_training_file_is_empty(tmp_path, monkeypatch) -> None:
    train_path = tmp_path / "splits" / "clean_split_v1" / "train.jsonl"
    train_path.parent.mkdir(parents=True)
    train_path.touch()
    monkeypatch.setattr(models, "DATA_DIR", tmp_path)

    with pytest.raises(ValueError, match=re.escape(str(train_path))):
        models.get_m1_model()


def test_m1_logs_loaded_row_count_and_class_balance(
    tmp_path, monkeypatch, caplog
) -> None:
    train_path = tmp_path / "splits" / "clean_split_v1" / "train.jsonl"
    train_path.parent.mkdir(parents=True)
    train_path.write_text(
        '{"text":"ordinary team project update","label":0}\n'
        '{"text":"urgent bank verify password","label":1}\n'
        '{"text":"account login transfer now","label":1}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(models, "DATA_DIR", tmp_path)

    with caplog.at_level(logging.INFO, logger=models.__name__):
        models.get_m1_model()

    assert "3 rows (legitimate=1, phishing=2)" in caplog.text
