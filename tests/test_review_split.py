from __future__ import annotations

import pytest

from tools.data.build_review_split import (
    _make_group_ids,
    _stratified_group_splits,
    build_review_split,
)


def test_review_split_refuses_to_overwrite_existing_output(tmp_path) -> None:
    output_dir = tmp_path / "existing"
    output_dir.mkdir()

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        build_review_split(tmp_path / "missing.mbox", tmp_path / "missing.jsonl", output_dir)


def test_grouped_split_keeps_each_sender_in_one_partition() -> None:
    records = []
    clustered = []
    for label, source in ((1, "nazario"), (0, "spamassassin_ham")):
        for sender_index in range(10):
            for message_index in range(2):
                record = {
                    "id": f"{source}-{sender_index}-{message_index}",
                    "text": (
                        f"From: sender-{sender_index}@example.test\n"
                        f"Subject: unique subject {source} {sender_index} {message_index}\n\n"
                        f"Unique body token {source} sender {sender_index} message {message_index}."
                    ),
                    "label": label,
                    "source": source,
                }
                records.append(record)
                clustered.append({**record, "cluster_id": record["id"]})

    groups, sender_summary = _make_group_ids(records, clustered)
    splits = _stratified_group_splits(records, groups, seed=42)

    split_for_id = {
        record["id"]: split
        for split, rows in splits.items()
        for record in rows
    }
    for group in set(groups):
        locations = {
            split_for_id[record["id"]]
            for record, record_group in zip(records, groups, strict=True)
            if record_group == group
        }
        assert len(locations) == 1
    assert all({row["label"] for row in rows} == {0, 1} for rows in splits.values())
    assert sender_summary["distinct_sender_groups_by_source"] == {
        "nazario": 10,
        "spamassassin_ham": 10,
    }
