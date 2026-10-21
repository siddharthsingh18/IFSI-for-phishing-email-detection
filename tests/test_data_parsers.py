from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tools.data.parsers import parse_csv, parse_mbox
from tools.data.parsers.common import stable_content_id


def test_mbox_round_trip_and_stable_ids(tmp_path: Path) -> None:
    path = tmp_path / "sample.mbox"
    path.write_text(
        "From sender@example.com Thu Jan  1 00:00:00 1970\n"
        "Subject: Test\n\n"
        "Hello fixture.\n\n",
        encoding="utf-8",
    )
    first = parse_mbox(path, source="fixture", label="legit")
    second = parse_mbox(path, source="fixture", label="legit")
    assert first == second
    assert first[0]["id"] == stable_content_id(first[0]["text"])
    assert first[0]["source"] == "fixture"
    assert first[0]["raw_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest() or first[0]["raw_sha256"]


def test_csv_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    path.write_text("text,label\nhello,legit\nurgent,phishing\n", encoding="utf-8")
    records = parse_csv(path, source="fixture")
    assert [record["label"] for record in records] == ["legit", "phishing"]
    assert all(record["original_path"] == str(path) for record in records)


def test_checksum_mismatch_is_reported_by_check_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    from tools.data.parsers import cli

    path = tmp_path / "source.csv"
    path.write_text("text,label\nhello,legit\n", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["parser", "--format", "csv", "--input", str(path), "--output", str(tmp_path / "out.jsonl"),
         "--source", "fixture", "--label", "legit", "--check", "--sha256", "wrong"],
    )
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 3
    assert "checksum_mismatch" in capsys.readouterr().out
