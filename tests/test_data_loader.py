"""Tests for data loading, deduplication, stratified splitting, and validation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from phishbench.data_loader import (
    clean_text,
    deduplicate_exact,
    deduplicate_near_duplicates,
    jaccard_similarity,
    run_pipeline,
    save_splits_to_jsonl,
    stratified_split,
    validate_splits,
)


def test_clean_text() -> None:
    raw = "  \n\tSubject: Urgent Account Update \u200b \xa0\n\n "
    cleaned = clean_text(raw)
    assert cleaned.startswith("Subject: Urgent")
    assert not cleaned.startswith(" ")
    assert not cleaned.endswith(" ")


def test_exact_deduplication() -> None:
    records = [
        {"id": "1", "text": "Subject: meeting tomorrow at 10am", "label": 0},
        {"id": "2", "text": "Subject: meeting tomorrow at 10am", "label": 0},  # Exact raw dup
        {"id": "3", "text": "Subject:  Meeting Tomorrow At  10am\n", "label": 0},  # Normalized dup
        {"id": "4", "text": "Subject: different email content", "label": 1},
    ]
    kept, stats = deduplicate_exact(records)
    assert len(kept) == 2
    assert stats["exact_raw_duplicates_removed"] == 1
    assert stats["normalized_whitespace_duplicates_removed"] == 1
    assert stats["total_exact_duplicates_removed"] == 2
    assert {r["id"] for r in kept} == {"1", "4"}


def test_near_deduplication() -> None:
    # Two emails differing by only a phone number or 1 word out of many
    base_text = "Subject: Important security alert. Your corporate banking password will expire today. Please verify your credentials immediately by visiting the secure portal. Contact helpdesk at 555-0101."
    altered_text = "Subject: Important security alert. Your corporate banking password will expire today. Please verify your credentials immediately by visiting the secure portal. Contact helpdesk at 555-0199."
    different_text = "Subject: Lunch order confirmation. Your delivery from the cafeteria has arrived in the main lobby."

    records = [
        {"id": "1", "text": base_text, "label": 1},
        {"id": "2", "text": altered_text, "label": 1},  # Near-duplicate of #1
        {"id": "3", "text": different_text, "label": 0},
    ]

    kept, removed = deduplicate_near_duplicates(records, threshold=0.80)
    assert removed == 1
    assert len(kept) == 2
    assert kept[0]["id"] == "1"
    assert kept[1]["id"] == "3"


def test_stratified_split_ratios_and_reproducibility() -> None:
    # Create 100 legitimate and 50 phishing records
    records = []
    for i in range(100):
        records.append({"id": f"legit-{i}", "text": f"Legitimate corporate message number {i}", "label": 0})
    for i in range(50):
        records.append({"id": f"phish-{i}", "text": f"Phishing urgent scam alert number {i}", "label": 1})

    splits_1 = stratified_split(records, train_ratio=0.80, val_ratio=0.10, test_ratio=0.10, seed=42)
    splits_2 = stratified_split(records, train_ratio=0.80, val_ratio=0.10, test_ratio=0.10, seed=42)

    # Determinism
    assert splits_1 == splits_2

    # Ratios per class:
    # Label 0 (100 total): 80 train, 10 val, 10 test
    # Label 1 (50 total): 40 train, 5 val, 5 test
    # Totals: 120 train, 15 val, 15 test
    assert len(splits_1["train"]) == 120
    assert len(splits_1["val"]) == 15
    assert len(splits_1["test"]) == 15

    # Check stratification balance (33.3% phishing in all splits)
    train_phish = sum(r["label"] == 1 for r in splits_1["train"])
    val_phish = sum(r["label"] == 1 for r in splits_1["val"])
    test_phish = sum(r["label"] == 1 for r in splits_1["test"])

    assert train_phish == 40
    assert val_phish == 5
    assert test_phish == 5


def test_no_email_appears_in_two_splits() -> None:
    """Core requirement: Verify that no email appears in more than one split."""
    records = []
    for i in range(40):
        records.append({"id": f"legit-{i:03d}", "text": f"Safe email text content for user {i}", "label": 0})
    for i in range(20):
        records.append({"id": f"phish-{i:03d}", "text": f"Malicious attack payload text {i}", "label": 1})

    splits = stratified_split(records, seed=42)

    train_ids = {r["id"] for r in splits["train"]}
    val_ids = {r["id"] for r in splits["val"]}
    test_ids = {r["id"] for r in splits["test"]}

    # IDs must be completely disjoint
    assert train_ids.isdisjoint(val_ids), f"Overlapping IDs between train and val: {train_ids & val_ids}"
    assert train_ids.isdisjoint(test_ids), f"Overlapping IDs between train and test: {train_ids & test_ids}"
    assert val_ids.isdisjoint(test_ids), f"Overlapping IDs between val and test: {val_ids & test_ids}"

    # Texts must be completely disjoint
    train_texts = {r["text"] for r in splits["train"]}
    val_texts = {r["text"] for r in splits["val"]}
    test_texts = {r["text"] for r in splits["test"]}

    assert train_texts.isdisjoint(val_texts), "Overlapping email texts between train and val"
    assert train_texts.isdisjoint(test_texts), "Overlapping email texts between train and test"
    assert val_texts.isdisjoint(test_texts), "Overlapping email texts between val and test"


def test_validator_and_leakage_detection() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = Path(tmp_dir)
        records = []
        for i in range(20):
            records.append({"id": f"mail-{i}", "text": f"Unique email body content {i}", "label": i % 2})

        splits = stratified_split(records, seed=42)
        saved_paths = save_splits_to_jsonl(splits, out_path)

        # 1. Valid splits pass cleanly
        report = validate_splits(saved_paths["train"], saved_paths["val"], saved_paths["test"])
        assert report["is_valid"] is True
        assert report["total_emails"] == 20

        # Verify JSONL schema format {id, text, label}
        with open(saved_paths["train"], "r", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                assert set(item.keys()) == {"id", "text", "label"}
                assert isinstance(item["id"], str)
                assert isinstance(item["text"], str)
                assert item["label"] in (0, 1)

        # 2. Tampering test: Inject duplicate email text into test split to simulate data leakage
        with open(saved_paths["train"], "r", encoding="utf-8") as f:
            first_train_email = json.loads(f.readline())

        with open(saved_paths["test"], "a", encoding="utf-8") as f:
            # Append same text with a different ID
            leaked_item = {"id": "leaked-999", "text": first_train_email["text"], "label": first_train_email["label"]}
            f.write(json.dumps(leaked_item) + "\n")

        # Validator MUST raise AssertionError due to leakage
        with pytest.raises(AssertionError, match="Data leakage detected"):
            validate_splits(saved_paths["train"], saved_paths["val"], saved_paths["test"])
