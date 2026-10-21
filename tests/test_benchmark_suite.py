"""Unit tests for statistical evaluation, McNemar tests, and bootstrap confidence intervals."""

from __future__ import annotations

from pathlib import Path
import re
import unittest
from phishbench.benchmark_suite import (
    build_markdown_report,
    bootstrap_metric_cis,
    compute_cell_metrics,
    derive_findings,
    exact_mcnemar_test,
)



class TestBenchmarkSuiteStats(unittest.TestCase):
    @staticmethod
    def _synthetic_summary() -> dict:
        cells = {}
        for method in ("M1", "M2", "M3", "M4"):
            for condition in ("clean", "marked", "unmarked"):
                recall = 0.8 if condition == "clean" else 0.4
                specificity = 0.95
                if method == "M2" and condition == "clean":
                    recall = 1.0
                    specificity = 0.0
                metrics = {
                    "accuracy": 0.8,
                    "precision": 0.8,
                    "recall": recall,
                    "specificity": specificity,
                    "fpr": 1 - specificity,
                    "f1": 0.8,
                    "true_positives": 8,
                    "false_positives": 2 if specificity < 0.1 else 1,
                    "valid_count": 10,
                    "invalid_rate": 0.0,
                    "total_samples": 10,
                    "invalid_count": 0,
                    "false_negatives": 2,
                    "true_negatives": 9 if specificity > 0.1 else 0,
                    "mean_latency_seconds": 0.1,
                    "total_runtime_seconds": 1.0,
                }
                cells[f"{method}_{condition}"] = {
                    "metrics": metrics,
                    "bootstrap_95_ci": {
                        metric: [max(0.0, value - 0.01), min(1.0, value + 0.01)]
                        for metric, value in (
                            ("accuracy", metrics["accuracy"]),
                            ("precision", metrics["precision"]),
                            ("recall", metrics["recall"]),
                            ("specificity", metrics["specificity"]),
                            ("fpr", metrics["fpr"]),
                            ("f1", metrics["f1"]),
                        )
                    },
                }
        paired = {}
        for key in (
            "M2_vs_M3__clean",
            "M2_vs_M3__marked",
            "M2_vs_M3__unmarked",
            "marked_vs_unmarked__M1",
            "marked_vs_unmarked__M2",
            "marked_vs_unmarked__M3",
            "marked_vs_unmarked__M4",
            "combined_vs_decoupled_M3_vs_M4__clean",
            "combined_vs_decoupled_M3_vs_M4__marked",
            "combined_vs_decoupled_M3_vs_M4__unmarked",
        ):
            paired[key] = {
                "paired_samples": 10,
                "both_correct": 8,
                "a_correct_b_wrong (b)": 1,
                "a_wrong_b_correct (c)": 1,
                "p_value": 1.0,
                "significant_alpha_0_05": False,
                "holm_bonferroni_rank": 1,
                "holm_bonferroni_factor": 1,
                "holm_bonferroni_p_value": 1.0,
                "significant_after_holm_bonferroni": False,
            }
        return {"cells": cells, "paired_tests": paired}

    def test_derive_findings_uses_same_method_for_injection_effects(self) -> None:
        summary = self._synthetic_summary()
        findings = derive_findings(summary)
        m3_effect = next(
            finding
            for finding in findings
            if finding.kind == "injection_effect"
            and finding.method == "M3"
            and finding.condition == "unmarked"
        )
        self.assertAlmostEqual(m3_effect.delta, -0.4)
        self.assertNotIn("M4", m3_effect.details)

    def test_derive_findings_flags_degenerate_m2_clean(self) -> None:
        findings = derive_findings(self._synthetic_summary())
        self.assertTrue(
            any(
                finding.kind == "degenerate_clean" and finding.method == "M2"
                for finding in findings
            )
        )

    def test_report_percentages_come_from_summary_metrics(self) -> None:
        summary = self._synthetic_summary()
        report = build_markdown_report(summary)
        allowed = {
            round(value * 100, 2)
            for cell in summary["cells"].values()
            for value in (
                cell["metrics"]["accuracy"],
                cell["metrics"]["precision"],
                cell["metrics"]["recall"],
                cell["metrics"]["specificity"],
                cell["metrics"]["fpr"],
                cell["metrics"]["f1"],
                cell["metrics"]["invalid_rate"],
            )
        }
        allowed.update(
            round(
                abs(
                    summary["cells"][f"{method}_clean"]["metrics"]["recall"]
                    - summary["cells"][f"{method}_{condition}"]["metrics"]["recall"]
                )
                * 100,
                2,
            )
            for method in ("M1", "M2", "M3", "M4")
            for condition in ("marked", "unmarked")
        )
        percentages = [
            float(match)
            for match in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)%", report)
        ]
        self.assertTrue(percentages)
        self.assertTrue(all(round(value, 2) in allowed for value in percentages))

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


class TestBenchmarkManifest(unittest.TestCase):
    def test_same_config_produces_same_prompt_hash(self) -> None:
        """Verify that identical configurations produce deterministic and identical prompt hashes."""
        from phishbench.manifest import compute_prompt_hash
        from phishbench.ollama_client import OllamaConfig
        from pathlib import Path

        # 1. Two separately instantiated OllamaConfig objects with identical parameters
        cfg1 = OllamaConfig(model="qwen2.5:0.5b", temperature=0.0)
        cfg2 = OllamaConfig(model="qwen2.5:0.5b", temperature=0.0)

        hash1 = compute_prompt_hash(cfg1)
        hash2 = compute_prompt_hash(cfg2)
        self.assertEqual(hash1, hash2)
        self.assertEqual(cfg1.compute_prompt_hash(), cfg2.compute_prompt_hash())
        self.assertEqual(cfg1.prompt_hash, cfg2.prompt_hash)
        self.assertEqual(len(hash1), 64)  # Valid 64-char sha256 hex string

        # 2. Configs loaded from identical file
        cfg_file = Path("config/ollama_config.json")
        if cfg_file.exists():
            cfg_a = OllamaConfig.from_file(cfg_file)
            cfg_b = OllamaConfig.from_file(cfg_file)
            self.assertEqual(compute_prompt_hash(cfg_a), compute_prompt_hash(cfg_b))
            self.assertEqual(cfg_a.prompt_hash, cfg_b.prompt_hash)

        # 3. Two configs with same custom prompt template
        custom_prompt = "You are an email security reviewer: {{email}}\nOutput valid json."
        cfg_custom1 = OllamaConfig(model="llama3.2:3b", prompt_template=custom_prompt)
        cfg_custom2 = OllamaConfig(model="llama3.2:3b", prompt_template=custom_prompt)
        self.assertEqual(compute_prompt_hash(cfg_custom1), compute_prompt_hash(cfg_custom2))
        self.assertEqual(cfg_custom1.prompt_hash, cfg_custom2.prompt_hash)

        # 4. Config with different prompt template produces different hash
        cfg_diff = OllamaConfig(model="llama3.2:3b", prompt_template="A completely different template.")
        self.assertNotEqual(cfg_custom1.prompt_hash, cfg_diff.prompt_hash)

    def test_manifest_creation_and_fields(self) -> None:
        """Verify manifest record contains exact required fields and is saved alongside results file."""
        import tempfile
        from phishbench.manifest import create_manifest_record, get_manifest_path, save_manifest_alongside
        from phishbench.ollama_client import OllamaConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            results_file = Path(tmpdir) / "test_eval_predictions.jsonl"
            results_file.write_text('{"id": 1, "verdict": "phishing"}\n', encoding="utf-8")

            cfg = OllamaConfig(model="qwen2.5:0.5b")
            record = create_manifest_record(results_file=results_file, config=cfg)

            # Check exact 5 required fields
            self.assertIn("prompt_template_hash", record)
            self.assertIn("model_name", record)
            self.assertIn("config_hash", record)
            self.assertIn("git_commit", record)
            self.assertIn("timestamp", record)

            self.assertEqual(record["model_name"], "qwen2.5:0.5b")
            self.assertEqual(record["prompt_template_hash"], cfg.prompt_hash)
            self.assertEqual(len(record["config_hash"]), 64)
            self.assertTrue(len(record["git_commit"]) > 0)
            self.assertTrue("T" in record["timestamp"])  # ISO 8601 format

            # Save alongside results file
            manifest_path = save_manifest_alongside(results_file, manifest=record)
            self.assertEqual(manifest_path, Path(tmpdir) / "test_eval_predictions.manifest.json")
            self.assertTrue(manifest_path.exists())
            self.assertEqual(manifest_path, get_manifest_path(results_file))


if __name__ == "__main__":
    unittest.main()
