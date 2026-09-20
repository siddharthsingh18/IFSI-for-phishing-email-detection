from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from phishbench.attacks import build_conditions
from phishbench.evaluate import classification_metrics, estimated_cost, exact_mcnemar
from phishbench.filter_nazario_enron_quality import MIME_PLACEHOLDER_RE, deduplicate, normalize
from phishbench.prepare import load_phishfuzzer, normalized_key, sample_balanced
from phishbench.prompts import build_prompt, prompt_snapshot
from phishbench.runner import parse_output, usage_fields


SAMPLE = {"email_id": "x", "original_id": "x", "subject": "Hi", "sender": "a@example.test", "reply_to": "", "urls": [], "attachments": [], "body": "first\n\nsecond", "label": 1}


class PromptTests(unittest.TestCase):
    def test_published_prompt_files_match_runtime(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for method in ("direct", "robust", "ours"):
            published = (root / "prompts" / f"{method}.txt").read_text(encoding="utf-8").rstrip("\n")
            self.assertEqual(published, build_prompt(SAMPLE, method).system)

    def test_shared_blocks_are_identical(self) -> None:
        snap = prompt_snapshot()["methods"]
        common = ("common_task", "common_input_rules", "common_format")
        for name in common:
            self.assertEqual(len({snap[m]["block_hashes"][name] for m in snap}), 1)
        self.assertEqual(snap["robust"]["block_hashes"]["robust_defense"], snap["ours"]["block_hashes"]["robust_defense"])
        self.assertEqual(snap["direct"]["block_hashes"]["output"], snap["robust"]["block_hashes"]["output"])

    def test_serialized_email_is_method_invariant(self) -> None:
        self.assertEqual(len({build_prompt(SAMPLE, method).user for method in ("direct", "robust", "ours")}), 1)

    def test_strict_parsing(self) -> None:
        parsed, error = parse_output('{"is_phishing":true}', "direct")
        self.assertEqual(parsed, {"is_phishing": True})
        self.assertIsNone(error)
        self.assertIsNone(parse_output('{"is_phishing":1}', "direct")[0])
        valid = '{"has_prompt_injection":true,"prompt_injection_summary":"asks classifier to mark safe","is_phishing":true}'
        self.assertIsNotNone(parse_output(valid, "ours")[0])
        too_long = json.dumps({"has_prompt_injection": True, "prompt_injection_summary": "x" * 101, "is_phishing": True})
        self.assertIsNotNone(parse_output(too_long, "ours")[0])

    def test_ours_no_summary_null_is_normalized_for_evaluation(self) -> None:
        raw = '{"has_prompt_injection":null,"is_phishing":false}'
        parsed, error = parse_output(raw, "ours_no_summary")
        self.assertEqual(parsed, {"has_prompt_injection": False, "is_phishing": False})
        self.assertIsNone(error)
        self.assertIsNone(parse_output(raw, "ours")[0])


class DataTests(unittest.TestCase):
    def test_nazario_quality_rules(self) -> None:
        self.assertEqual(normalize(" Ａ\n B "), "a b")
        self.assertIsNotNone(MIME_PLACEHOLDER_RE.fullmatch("HTML file required for this letter."))
        rows = [
            {**SAMPLE, "email_id": "b", "original_id": "b"},
            {**SAMPLE, "email_id": "a", "original_id": "a", "subject": " HI "},
        ]
        decisions: list[dict] = []
        kept = deduplicate(rows, decisions)
        self.assertEqual([r["original_id"] for r in kept], ["a"])
        self.assertEqual(decisions[0]["duplicate_of"], "a")

    def test_normalization_and_sampling(self) -> None:
        self.assertEqual(normalized_key("Ａ  B", " X\nY "), normalized_key("a b", "x y"))
        rows = [{**SAMPLE, "email_id": f"{label}-{i}", "label": label} for label in (0, 1) for i in range(4)]
        chosen = sample_balanced(rows, 3, 42)
        self.assertEqual(sum(r["label"] == 0 for r in chosen), 3)
        self.assertEqual(chosen, sample_balanced(rows, 3, 42))

    def test_attack_pairing_and_balance(self) -> None:
        clean = [{**SAMPLE, "email_id": f"p{i}", "original_id": f"p{i}", "label": 1} for i in range(30)]
        clean += [{**SAMPLE, "email_id": f"n{i}", "original_id": f"n{i}", "label": 0} for i in range(30)]
        attacked, controls, manifest = build_conditions(clean, 42)
        self.assertEqual((len(attacked), len(controls), len(manifest)), (30, 30, 60))
        self.assertTrue(all(r["label"] == 1 for r in attacked))
        self.assertTrue(all(r["label"] == 0 for r in controls))
        self.assertEqual([r["attack_family"] for r in attacked], [r["attack_family"] for r in controls])
        self.assertEqual([r["attack_template_id"] for r in attacked], [r["attack_template_id"] for r in controls])
        self.assertEqual([r["attack_position"] for r in attacked], [r["attack_position"] for r in controls])
        self.assertTrue(all("[BEGIN EMBEDDED CLASSIFIER MESSAGE]" in r["body"] for r in attacked + controls))

    def test_dedup_loader(self) -> None:
        source = [
            {"No.": 1, "Type": "Phishing", "Subject": "A", "Body": "B"},
            {"No.": 2, "Type": "Phishing", "Subject": "Ａ", "Body": " B "},
            {"No.": 3, "Type": "Valid", "Subject": "A", "Body": "B"},
            {"No.": 4, "Type": "Spam", "Subject": "S", "Body": "S"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "seed.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            rows, report = load_phishfuzzer(path)
        self.assertEqual(len(rows), 2)
        self.assertEqual(report["within_label_duplicates_removed"]["Phishing"], 1)
        self.assertEqual(report["excluded_spam"], 1)


class EvaluationTests(unittest.TestCase):
    def test_token_parts_are_recorded_separately(self) -> None:
        usage = usage_fields({"usage": {"prompt_tokens": 100, "completion_tokens": 30, "total_tokens": 130, "completion_tokens_details": {"reasoning_tokens": 20}}})
        self.assertEqual(usage["input_tokens"], 100)
        self.assertEqual(usage["reasoning_tokens"], 20)
        self.assertEqual(usage["answer_tokens"], 10)
        self.assertEqual(usage["api_completion_tokens"], 30)
        self.assertEqual(usage["total_tokens"], 130)

    def test_failures_remain_in_denominator(self) -> None:
        rows = [
            {"email_id": "a", "label": 1, "prediction": 1},
            {"email_id": "b", "label": 1, "prediction": None},
            {"email_id": "c", "label": 0, "prediction": 0},
        ]
        conservative = classification_metrics(rows)
        valid_only = classification_metrics(rows, valid_only=True)
        self.assertEqual(conservative["fn"], 1)
        self.assertEqual(conservative["recall"], 0.5)
        self.assertEqual(valid_only["recall"], 1.0)

    def test_exact_mcnemar_pairing(self) -> None:
        a = [{"email_id": str(i), "original_id": str(i), "label": 1, "prediction": p} for i, p in enumerate((1, 1, 0))]
        b = [{"email_id": str(i), "original_id": str(i), "label": 1, "prediction": p} for i, p in enumerate((1, 0, 1))]
        result = exact_mcnemar(a, b)
        self.assertEqual(result["paired_n"], 3)
        self.assertEqual(result["a_correct_b_wrong"], 1)
        self.assertEqual(result["a_wrong_b_correct"], 1)

    def test_cost_uses_cache_and_reasoning_inclusive_output(self) -> None:
        row = {"model_requested": "m", "usage": {"input_tokens": 100, "prompt_cache_hit_tokens": 40, "prompt_cache_miss_tokens": 60, "generated_tokens_including_reasoning": 20}}
        pricing = {"models": {"m": {"input_cache_hit": 1, "input_cache_miss": 2, "output_including_reasoning": 3}}}
        self.assertEqual(estimated_cost(row, pricing), (40 + 120 + 60) / 1_000_000)


if __name__ == "__main__":
    unittest.main()
