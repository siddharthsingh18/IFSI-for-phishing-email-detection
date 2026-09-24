"""Tests for evaluation metrics and baseline classifier."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from phishbench.baseline import compute_metrics, train_and_evaluate_baseline


def test_hand_computed_metrics_example() -> None:
    """Hand-computed example testing confusion matrix, precision, recall, F1, and FPR.

    Setup:
        10 samples: 4 positives (label 1), 6 negatives (label 0)
        y_true = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        y_pred = [1, 1, 1, 0, 1, 0, 0, 0, 0, 0]

    Hand calculation:
        Index 0: True=1, Pred=1 -> TP
        Index 1: True=1, Pred=1 -> TP
        Index 2: True=1, Pred=1 -> TP
        Index 3: True=1, Pred=0 -> FN
        Index 4: True=0, Pred=1 -> FP
        Index 5: True=0, Pred=0 -> TN
        Index 6: True=0, Pred=0 -> TN
        Index 7: True=0, Pred=0 -> TN
        Index 8: True=0, Pred=0 -> TN
        Index 9: True=0, Pred=0 -> TN

    Aggregates:
        TP = 3
        FN = 1
        FP = 1
        TN = 5

    Formulas:
        Confusion Matrix = [[TN, FP], [FN, TP]] = [[5, 1], [1, 3]]
        Precision        = TP / (TP + FP) = 3 / (3 + 1) = 3/4 = 0.75
        Recall           = TP / (TP + FN) = 3 / (3 + 1) = 3/4 = 0.75
        F1               = 2 * Prec * Rec / (Prec + Rec) = 2 * 0.75 * 0.75 / 1.5 = 0.75
        FPR              = FP / (FP + TN) = 1 / (1 + 5) = 1/6 ≈ 0.1666666667
        Accuracy         = (TP + TN) / Total = (3 + 5) / 10 = 8/10 = 0.80
    """
    y_true = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    y_pred = [1, 1, 1, 0, 1, 0, 0, 0, 0, 0]

    metrics = compute_metrics(y_true, y_pred)

    assert metrics["confusion_matrix"] == [[5, 1], [1, 3]]
    assert metrics["true_positives"] == 3
    assert metrics["false_negatives"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["true_negatives"] == 5

    assert metrics["precision"] == 0.75
    assert metrics["recall"] == 0.75
    assert metrics["f1"] == 0.75
    assert metrics["fpr"] == pytest.approx(1 / 6, rel=1e-6)
    assert metrics["accuracy"] == 0.80
    assert metrics["total_samples"] == 10


def test_compute_metrics_edge_cases() -> None:
    # Perfect classifier
    perfect = compute_metrics([1, 1, 0, 0], [1, 1, 0, 0])
    assert perfect["confusion_matrix"] == [[2, 0], [0, 2]]
    assert perfect["precision"] == 1.0
    assert perfect["recall"] == 1.0
    assert perfect["f1"] == 1.0
    assert perfect["fpr"] == 0.0

    # All false positives
    all_fp = compute_metrics([0, 0], [1, 1])
    assert all_fp["confusion_matrix"] == [[0, 2], [0, 0]]
    assert all_fp["precision"] == 0.0
    assert all_fp["recall"] == 0.0
    assert all_fp["fpr"] == 1.0

    # Length mismatch
    with pytest.raises(ValueError, match="Length mismatch"):
        compute_metrics([1, 0], [1])


def test_baseline_train_and_evaluate_synthetic() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        train_file = tmp_path / "train.jsonl"
        test_file = tmp_path / "test.jsonl"
        out_file = tmp_path / "baseline.json"

        train_data = [
            {"id": "1", "text": "urgent account suspension verify password login", "label": 1},
            {"id": "2", "text": "your banking security alert update credentials", "label": 1},
            {"id": "3", "text": "meeting schedule conference room discussion report", "label": 0},
            {"id": "4", "text": "quarterly earnings summary presentation slides", "label": 0},
        ]
        test_data = [
            {"id": "5", "text": "urgent verify your account and password now", "label": 1},
            {"id": "6", "text": "project discussion report and presentation slides", "label": 0},
        ]

        for p, d in [(train_file, train_data), (test_file, test_data)]:
            with p.open("w", encoding="utf-8") as f:
                for row in d:
                    f.write(json.dumps(row) + "\n")

        res = train_and_evaluate_baseline(train_file, test_file, out_file)
        assert out_file.exists()
        assert res["test_samples"] == 2
        assert "metrics" in res
        assert "confusion_matrix" in res["metrics"]
        assert "precision" in res["metrics"]
        assert "recall" in res["metrics"]
        assert "f1" in res["metrics"]
        assert "fpr" in res["metrics"]
