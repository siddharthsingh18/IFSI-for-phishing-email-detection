"""Unit tests for marked and unmarked prompt injection test set generation."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from phishbench.injections import (
    UNMARKED_REWRITES,
    UNMARKED_STYLES,
    build_injected_record,
    build_injection_test_sets,
    insert_marked_injection,
    insert_unmarked_injection,
)
from phishbench.io import read_jsonl


class TestInjections(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.test_split_path = cls.root / "data" / "splits" / "test.jsonl"
        cls.injections_dir = cls.root / "data" / "injections"

        cls.test_records = read_jsonl(cls.test_split_path)
        cls.test_ids = {r["id"]: r for r in cls.test_records}
        cls.phishing_ids = {r["id"] for r in cls.test_records if r["label"] == 1}
        cls.legit_ids = {r["id"] for r in cls.test_records if r["label"] == 0}

    def test_original_test_split_unmodified(self) -> None:
        """Verify original test split remains exactly 522 items with 128 phishing and 394 legit."""
        self.assertEqual(len(self.test_records), 522)
        self.assertEqual(len(self.phishing_ids), 128)
        self.assertEqual(len(self.legit_ids), 394)

    def test_files_exist_and_counts(self) -> None:
        """Assert all four files exist with exact required counts."""
        expected_counts = {
            "marked-phishing.jsonl": 128,
            "marked-control.jsonl": 394,
            "unmarked-phishing.jsonl": 128,
            "unmarked-control.jsonl": 394,
        }

        for filename, count in expected_counts.items():
            path = self.injections_dir / filename
            self.assertTrue(path.exists(), f"Missing file: {path}")
            rows = read_jsonl(path)
            self.assertEqual(len(rows), count, f"Count mismatch in {filename}")

        manifest_path = self.injections_dir / "manifest.json"
        self.assertTrue(manifest_path.exists(), "Missing manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for cond, count in (
            ("marked-phishing", 128),
            ("marked-control", 394),
            ("unmarked-phishing", 128),
            ("unmarked-control", 394),
        ):
            self.assertIn(cond, manifest)
            self.assertEqual(manifest[cond]["count"], count)

    def test_traceability_to_original_email_ids(self) -> None:
        """Assert every record has traceable id matching its original_id in test split."""
        files = (
            ("marked-phishing.jsonl", self.phishing_ids, 1),
            ("marked-control.jsonl", self.legit_ids, 0),
            ("unmarked-phishing.jsonl", self.phishing_ids, 1),
            ("unmarked-control.jsonl", self.legit_ids, 0),
        )

        for filename, expected_id_set, expected_label in files:
            path = self.injections_dir / filename
            rows = read_jsonl(path)
            seen_ids = set()
            for r in rows:
                orig_id = r.get("original_id")
                self.assertIsNotNone(orig_id, f"Missing original_id in {r}")
                self.assertIn(orig_id, expected_id_set, f"Unknown original_id: {orig_id}")
                self.assertIn(orig_id, r["id"], f"Record ID {r['id']} does not contain {orig_id}")
                self.assertEqual(r["label"], expected_label, f"Label mismatch in {filename}")
                self.assertIn("text", r)
                self.assertTrue(len(r["text"].strip()) > 0)
                seen_ids.add(orig_id)
            self.assertEqual(seen_ids, expected_id_set, f"Did not cover all expected IDs in {filename}")

    def test_marked_injections_have_explicit_markers(self) -> None:
        """Assert marked files contain explicit delimiters like prior work."""
        for filename in ("marked-phishing.jsonl", "marked-control.jsonl"):
            path = self.injections_dir / filename
            rows = read_jsonl(path)
            for r in rows:
                text = r["text"]
                self.assertIn("[BEGIN EMBEDDED CLASSIFIER MESSAGE]", text)
                self.assertIn("[END EMBEDDED CLASSIFIER MESSAGE]", text)
                self.assertEqual(r["injection_type"], "marked")
                self.assertEqual(r["injection_style"], "explicit_marker")

    def test_unmarked_injections_have_no_special_delimiters(self) -> None:
        """Assert unmarked files do NOT contain special marker delimiters or artificial tags."""
        forbidden_delimiters = [
            "[BEGIN",
            "[END",
            "###",
            "EMBEDDED CLASSIFIER MESSAGE",
            "classifier_override",
        ]

        for filename in ("unmarked-phishing.jsonl", "unmarked-control.jsonl"):
            path = self.injections_dir / filename
            rows = read_jsonl(path)
            styles_found = set()
            for r in rows:
                text = r["text"]
                for delim in forbidden_delimiters:
                    self.assertNotIn(
                        delim,
                        text,
                        f"Found forbidden delimiter '{delim}' in unmarked record {r['id']}",
                    )
                self.assertEqual(r["injection_type"], "unmarked")
                styles_found.add(r["injection_style"])

            # Verify all 3 styles are represented
            self.assertEqual(
                styles_found,
                {"footer_disclaimer", "forwarded_notice", "signature_block"},
                f"Missing styles in {filename}",
            )

    def test_synthetic_builder_and_styles(self) -> None:
        """Test builder on synthetic records."""
        sample_records = [
            {"id": "test-p1", "text": "Subject: Urgent Wire\nPlease wire money.", "label": 1},
            {"id": "test-p2", "text": "Subject: Verify Account\nClick here.", "label": 1},
            {"id": "test-c1", "text": "Subject: Team Lunch\nSee you tomorrow.", "label": 0},
            {"id": "test-c2", "text": "Subject: Q3 Report\nAttached is report.", "label": 0},
        ]
        sets = build_injection_test_sets(sample_records, seed=42)
        self.assertEqual(len(sets["marked-phishing"]), 2)
        self.assertEqual(len(sets["marked-control"]), 2)
        self.assertEqual(len(sets["unmarked-phishing"]), 2)
        self.assertEqual(sets["marked-phishing"][0]["original_id"], "test-p1")
        self.assertTrue("[BEGIN EMBEDDED CLASSIFIER MESSAGE]" in sets["marked-phishing"][0]["text"])
        self.assertFalse("[BEGIN EMBEDDED CLASSIFIER MESSAGE]" in sets["unmarked-phishing"][0]["text"])


if __name__ == "__main__":
    unittest.main()
