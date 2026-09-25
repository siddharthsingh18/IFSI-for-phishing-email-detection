"""Unit tests for decoupled RAG prompt variants and zero shared context guarantees."""

from __future__ import annotations

import unittest
from phishbench.evaluate_decoupled_rag import (
    SYSTEM_INJECTION_DETECTOR,
    SYSTEM_IS_PHISHING_ONLY,
    HasInjectionResult,
    IsPhishingResult,
    compute_metrics,
)


class TestDecoupledRAG(unittest.TestCase):
    def test_is_phishing_only_schema_and_prompt(self) -> None:
        """Assert is_phishing_only prompt and schema have ZERO references to prompt injection."""
        # Check prompt has no injection mentions
        self.assertNotIn("injection", SYSTEM_IS_PHISHING_ONLY.lower())
        self.assertNotIn("prompt injection", SYSTEM_IS_PHISHING_ONLY.lower())
        self.assertNotIn("has_prompt_injection", SYSTEM_IS_PHISHING_ONLY)

        # Check schema
        res_true = IsPhishingResult.model_validate({"is_phishing": True})
        self.assertTrue(res_true.is_phishing)
        res_false = IsPhishingResult.model_validate({"is_phishing": False})
        self.assertFalse(res_false.is_phishing)

        with self.assertRaises(Exception):
            IsPhishingResult.model_validate({"verdict": "phishing"})

    def test_injection_detector_schema_and_prompt(self) -> None:
        """Assert injection detector prompt focuses strictly on prompt injection."""
        self.assertIn("prompt injection", SYSTEM_INJECTION_DETECTOR.lower())
        self.assertNotIn("is_phishing", SYSTEM_INJECTION_DETECTOR)

        res_true = HasInjectionResult.model_validate({"has_prompt_injection": True})
        self.assertTrue(res_true.has_prompt_injection)
        res_false = HasInjectionResult.model_validate({"has_prompt_injection": False})
        self.assertFalse(res_false.has_prompt_injection)

    def test_metrics_computation_hand_computed(self) -> None:
        """Verify Recall for phishing and FPR for control on synthetic predictions."""
        # 1. Attacked Phishing (expected_label=1): 4 samples: 3 TP, 1 FN
        phish_preds = [
            {"predicted_label": 1, "is_valid": True},
            {"predicted_label": 1, "is_valid": True},
            {"predicted_label": 1, "is_valid": True},
            {"predicted_label": 0, "is_valid": True},
        ]
        phish_metrics = compute_metrics(phish_preds, expected_label=1)
        self.assertEqual(phish_metrics["true_positives"], 3)
        self.assertEqual(phish_metrics["false_negatives"], 1)
        self.assertEqual(phish_metrics["recall"], 0.75)
        self.assertEqual(phish_metrics["evasion_rate"], 0.25)

        # 2. Injected Legitimate Control (expected_label=0): 5 samples: 1 FP, 4 TN
        ctrl_preds = [
            {"predicted_label": 1, "is_valid": True},
            {"predicted_label": 0, "is_valid": True},
            {"predicted_label": 0, "is_valid": True},
            {"predicted_label": 0, "is_valid": True},
            {"predicted_label": 0, "is_valid": True},
        ]
        ctrl_metrics = compute_metrics(ctrl_preds, expected_label=0)
        self.assertEqual(ctrl_metrics["false_positives"], 1)
        self.assertEqual(ctrl_metrics["true_negatives"], 4)
        self.assertEqual(ctrl_metrics["fpr"], 0.2)
        self.assertEqual(ctrl_metrics["specificity"], 0.8)

    def test_combined_coupled_schema_and_prompt(self) -> None:
        """Assert coupled prompt asks for both fields and validates."""
        from phishbench.evaluate_decoupled_rag import (
            SYSTEM_COMBINED_COUPLED,
            CombinedInjectionPhishingResult,
        )
        self.assertIn("has_prompt_injection", SYSTEM_COMBINED_COUPLED)
        self.assertIn("is_phishing", SYSTEM_COMBINED_COUPLED)

        res = CombinedInjectionPhishingResult.model_validate({
            "has_prompt_injection": True,
            "is_phishing": False,
        })
        self.assertTrue(res.has_prompt_injection)
        self.assertFalse(res.is_phishing)


if __name__ == "__main__":
    unittest.main()
