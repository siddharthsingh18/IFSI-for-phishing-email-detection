"""Unit tests for statistical evaluation, McNemar tests, and bootstrap confidence intervals."""

from __future__ import annotations

import unittest
from phishbench.benchmark_suite import (
    bootstrap_metric_cis,
    compute_cell_metrics,
    exact_mcnemar_test,
)


class TestBenchmarkSuiteStats(unittest.TestCase):
    def test_mcnemar_hand_computed_exact_binomial(self) -> None:
        """Verify exact binomial two-sided p-value calculation against manual combinatorics."""
        # Case 1: b=10, c=0 -> discordant=10.
        # Two-sided p-value = 2 * (1 / 2^10) = 2 / 1024 = 0.001953125
        preds_a = [{"id": f"e{i}", "true_label": 1, "predicted_label": 1} for i in range(10)]
        preds_b = [{"id": f"e{i}", "true_label": 1, "predicted_label": 0} for i in range(10)]

        res = exact_mcnemar_test(preds_a, preds_b)
        self.assertEqual(res["a_correct_b_wrong (b)"], 10)
        self.assertEqual(res["a_wrong_b_correct (c)"], 0)
        self.assertEqual(res["discordant_pairs"], 10)
        self.assertAlmostEqual(res["p_value"], 0.001953125, places=6)
        self.assertTrue(res["significant_alpha_0_05"])

        # Case 2: Symmetric discordance: b=5, c=5 -> p-value = 1.0
        preds_a = [{"id": f"e{i}", "true_label": 1, "predicted_label": 1 if i < 5 else 0} for i in range(10)]
        preds_b = [{"id": f"e{i}", "true_label": 1, "predicted_label": 0 if i < 5 else 1} for i in range(10)]

        res2 = exact_mcnemar_test(preds_a, preds_b)
        self.assertEqual(res2["a_correct_b_wrong (b)"], 5)
        self.assertEqual(res2["a_wrong_b_correct (c)"], 5)
        self.assertAlmostEqual(res2["p_value"], 1.0, places=6)
        self.assertFalse(res2["significant_alpha_0_05"])

        # Case 3: Zero discordance: b=0, c=0 -> p-value = 1.0
        preds_same = [{"id": f"e{i}", "true_label": 1, "predicted_label": 1} for i in range(5)]
        res3 = exact_mcnemar_test(preds_same, preds_same)
        self.assertEqual(res3["discordant_pairs"], 0)
        self.assertEqual(res3["p_value"], 1.0)

    def test_compute_cell_metrics_hand_computed(self) -> None:
        """Verify confusion matrix and derived rates on hand-computed synthetic records."""
        # 10 records:
        # TP = 3, FN = 1 (Recall = 3/4 = 0.75)
        # TN = 5, FP = 1 (FPR = 1/6 = 0.1667, Specificity = 5/6 = 0.8333)
        # Precision = 3/4 = 0.75
        # F1 = 0.75
        # Accuracy = 8/10 = 0.80
        preds = [
            {"true_label": 1, "predicted_label": 1, "is_valid": True},  # TP
            {"true_label": 1, "predicted_label": 1, "is_valid": True},  # TP
            {"true_label": 1, "predicted_label": 1, "is_valid": True},  # TP
            {"true_label": 1, "predicted_label": 0, "is_valid": True},  # FN
            {"true_label": 0, "predicted_label": 1, "is_valid": True},  # FP
            {"true_label": 0, "predicted_label": 0, "is_valid": True},  # TN
            {"true_label": 0, "predicted_label": 0, "is_valid": True},  # TN
            {"true_label": 0, "predicted_label": 0, "is_valid": True},  # TN
            {"true_label": 0, "predicted_label": 0, "is_valid": True},  # TN
            {"true_label": 0, "predicted_label": 0, "is_valid": True},  # TN
        ]

        metrics = compute_cell_metrics(preds)
        self.assertEqual(metrics["true_positives"], 3)
        self.assertEqual(metrics["false_negatives"], 1)
        self.assertEqual(metrics["false_positives"], 1)
        self.assertEqual(metrics["true_negatives"], 5)
        self.assertAlmostEqual(metrics["accuracy"], 0.80, places=4)
        self.assertAlmostEqual(metrics["precision"], 0.75, places=4)
        self.assertAlmostEqual(metrics["recall"], 0.75, places=4)
        self.assertAlmostEqual(metrics["specificity"], 0.8333, places=4)
        self.assertAlmostEqual(metrics["fpr"], 0.1667, places=4)
        self.assertAlmostEqual(metrics["f1"], 0.75, places=4)

    def test_bootstrap_metric_cis(self) -> None:
        """Verify bootstrap confidence intervals produce ordered bounds."""
        preds = [
            {"true_label": 1, "predicted_label": 1, "is_valid": True},
            {"true_label": 1, "predicted_label": 1, "is_valid": True},
            {"true_label": 1, "predicted_label": 0, "is_valid": True},
            {"true_label": 0, "predicted_label": 0, "is_valid": True},
            {"true_label": 0, "predicted_label": 0, "is_valid": True},
            {"true_label": 0, "predicted_label": 1, "is_valid": True},
        ]

        cis = bootstrap_metric_cis(preds, n_iterations=200, seed=42)
        for metric_name in ("accuracy", "precision", "recall", "specificity", "fpr", "f1"):
            lo, hi = cis[metric_name]
            self.assertLessEqual(lo, hi)
            self.assertGreaterEqual(lo, 0.0)
            self.assertLessEqual(hi, 1.0)


if __name__ == "__main__":
    unittest.main()
