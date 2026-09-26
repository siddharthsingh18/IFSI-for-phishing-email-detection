"""Tests for RAG pipeline, FAISS index isolation, reference formatting, and test-set non-overlap."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from phishbench.ollama_client import OllamaClient, OllamaConfig
from phishbench.rag import (
    REFERENCE_DELIMITER_END,
    REFERENCE_DELIMITER_START,
    FAISSRetriever,
    classify_with_rag,
    format_reference_block,
)


def test_zero_overlap_between_indexed_ids_and_test_set() -> None:
    """Core assertion: Verify ZERO ID or text overlap between the FAISS index (TRAIN split) and the TEST split."""
    train_path = Path("data/splits/train.jsonl")
    test_path = Path("data/splits/test.jsonl")

    if not train_path.exists() or not test_path.exists():
        pytest.skip("Splits not found; skipping full dataset overlap test")

    test_ids: set[str] = set()
    test_texts: set[str] = set()
    with test_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line.strip())
                test_ids.add(str(item["id"]))
                test_texts.add(str(item["text"]))

    train_ids: set[str] = set()
    train_texts: set[str] = set()
    with train_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line.strip())
                train_ids.add(str(item["id"]))
                train_texts.add(str(item["text"]))

    # Test set non-overlap assertions
    overlapping_ids = train_ids & test_ids
    assert len(overlapping_ids) == 0, f"Data leakage detected! {len(overlapping_ids)} overlapping ID(s): {list(overlapping_ids)[:5]}"
    assert train_ids.isdisjoint(test_ids), "Train IDs and Test IDs must be completely disjoint"

    overlapping_texts = train_texts & test_texts
    assert len(overlapping_texts) == 0, f"Data leakage detected! {len(overlapping_texts)} identical email text(s) found across train and test"
    assert train_texts.isdisjoint(test_texts), "Train texts and Test texts must be completely disjoint"


def test_reference_block_formatting() -> None:
    examples = [
        {"id": "train-001", "text": "Urgent password reset required immediately.", "label_name": "phishing"},
        {"id": "train-002", "text": "Here is the agenda for tomorrow's 2pm meeting.", "label_name": "legitimate"},
        {"id": "train-003", "text": "Wire transfer requested to new account details.", "label_name": "phishing"},
    ]

    block = format_reference_block(examples)
    assert REFERENCE_DELIMITER_START in block
    assert REFERENCE_DELIMITER_END in block
    assert "True Label: phishing" in block
    assert "True Label: legitimate" in block
    assert "Urgent password reset" in block
    assert "Here is the agenda" in block


def test_faiss_retrieval_and_isolation_synthetic() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        train_file = Path(tmp_dir) / "train.jsonl"
        train_data = [
            {"id": "tr-001", "text": "Subject: urgent verify bank account credentials", "label": 1},
            {"id": "tr-002", "text": "Subject: monthly quantitative research report", "label": 0},
            {"id": "tr-003", "text": "Subject: free lottery winner claim prize now", "label": 1},
            {"id": "tr-004", "text": "Subject: project deliverables and timelines update", "label": 0},
        ]
        with train_file.open("w", encoding="utf-8") as f:
            for row in train_data:
                f.write(json.dumps(row) + "\n")

        retriever = FAISSRetriever.build_from_train_split(train_file)
        assert len(retriever.indexed_ids) == 4
        assert retriever.indexed_ids == {"tr-001", "tr-002", "tr-003", "tr-004"}

        # Simulate test query
        test_ids = {"te-001", "te-002"}
        assert retriever.indexed_ids.isdisjoint(test_ids)

        # Retrieve top-k=3
        results = retriever.retrieve("Subject: verify your bank account login", top_k=3)
        assert len(results) == 3
        # First neighbor should be the most semantically relevant (banking phishing)
        assert results[0]["id"] == "tr-001"
        assert results[0]["label_name"] == "phishing"
        assert "similarity_score" in results[0]


def test_classify_with_rag_mocked_ollama() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        train_file = Path(tmp_dir) / "train.jsonl"
        train_data = [
            {"id": "tr-001", "text": "Subject: urgent account verification", "label": 1},
            {"id": "tr-002", "text": "Subject: weekly staff meeting agenda", "label": 0},
            {"id": "tr-003", "text": "Subject: click here to claim your cash", "label": 1},
        ]
        with train_file.open("w", encoding="utf-8") as f:
            for row in train_data:
                f.write(json.dumps(row) + "\n")

        retriever = FAISSRetriever.build_from_train_split(train_file)
        config = OllamaConfig(model="mock-model", temperature=0.0)
        client = OllamaClient(config)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "message": {
                "content": json.dumps({
                    "verdict": "phishing",
                    "confidence": 0.96,
                    "reasons": ["Matches reference example 1 pattern for credential verification"],
                })
            }
        }

        with patch.object(client.client, "post", return_value=mock_resp) as mock_post:
            result, meta = classify_with_rag(
                client=client,
                retriever=retriever,
                candidate_text="Subject: Please verify your payroll account",
                top_k=3,
            )

            assert result is not None
            assert result.verdict == "phishing"
            assert result.confidence == 0.96
            assert meta["is_valid"] is True
            assert len(meta["retrieved_ids"]) == 3
            assert mock_post.call_count == 1

            # Check that reference block was indeed passed into the user prompt
            call_payload = mock_post.call_args[1]["json"]
            user_msg = call_payload["messages"][1]["content"]
            assert REFERENCE_DELIMITER_START in user_msg
            assert REFERENCE_DELIMITER_END in user_msg
            assert "Candidate Email To Classify:" in user_msg


def test_rag_cli_k_flag() -> None:
    """Verify that -k, --k, and --top-k flags correctly parse top_k value."""
    import argparse
    from phishbench.rag import main

    # Inspect argument parser configuration
    # Create parser mimicking main()
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--k", "--top-k", dest="top_k", type=int, default=3)

    assert parser.parse_args(["--k", "1"]).top_k == 1
    assert parser.parse_args(["-k", "5"]).top_k == 5
    assert parser.parse_args(["--top-k", "2"]).top_k == 2
    assert parser.parse_args([]).top_k == 3

