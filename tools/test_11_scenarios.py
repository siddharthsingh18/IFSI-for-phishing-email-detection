"""Automated Verification Suite for the 11 Required Operational Scenarios (Decision 6).

Evaluates the M4 Decoupled Two-Stage Engine (Option B) across:
1. Ordinary legitimate email
2. Conventional phishing
3. Sophisticated phishing / BEC
4. Legitimate email discussing prompt injection
5. Legitimate email with quoted malicious instructions
6. Phishing email with indirect prompt injection
7. Injection attempt manipulating detector to return legitimate
8. Email with suspicious language but no phishing intent
9. Model unavailable
10. Injection detector failure (Stage 1 failure)
11. Phishing classifier failure (Stage 2 failure)
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure src is on sys.path
root_dir = Path(__file__).resolve().parents[1]
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from core.inference import classify_email_m4, _call_ollama_json
from phishbench.evaluate_decoupled_rag import SYSTEM_INJECTION_DETECTOR, SYSTEM_IS_PHISHING_ONLY


class TestElevenScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load diagnostic suite cases
        diag_path = root_dir / "data" / "diagnostic_suite.json"
        with open(diag_path, "r", encoding="utf-8") as f:
            cases_list = json.load(f)
        cls.cases = {c["id"]: c for c in cases_list}

    def _format_case(self, case_id: str) -> str:
        case = self.cases[case_id]
        return f"Subject: {case.get('subject', '')}\nFrom: {case.get('sender', '')}\n\n{case.get('body', '')}"

    def test_01_ordinary_legitimate(self):
        """Scenario 1: Ordinary legitimate email -> legitimate, clean, allow."""
        text = self._format_case("diag-legit-01")
        res = classify_email_m4(text)
        print("\nScenario 1 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["phishing_verdict"], "legitimate")
        self.assertEqual(res["injection_verdict"], "clean")
        self.assertEqual(res["security_action"], "allow")
        self.assertFalse(res["is_phishing"])
        self.assertFalse(res["has_prompt_injection"])

    def test_02_conventional_phishing(self):
        """Scenario 2: Conventional phishing -> phishing, clean, block."""
        text = self._format_case("diag-phish-conv-08")
        res = classify_email_m4(text)
        print("\nScenario 2 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["phishing_verdict"], "phishing")
        self.assertEqual(res["injection_verdict"], "clean")
        self.assertEqual(res["security_action"], "block")
        self.assertTrue(res["is_phishing"])
        self.assertFalse(res["has_prompt_injection"])

    def test_03_sophisticated_phishing_bec(self):
        """Scenario 3: Sophisticated phishing / BEC -> phishing, clean, block."""
        text = self._format_case("diag-phish-bec-11")
        res = classify_email_m4(text)
        print("\nScenario 3 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["phishing_verdict"], "phishing")
        self.assertEqual(res["injection_verdict"], "clean")
        self.assertEqual(res["security_action"], "block")
        self.assertTrue(res["is_phishing"])
        self.assertFalse(res["has_prompt_injection"])

    def test_04_legitimate_discussing_injection(self):
        """Scenario 4: Legitimate email discussing prompt injection -> legitimate, clean, allow."""
        text = self._format_case("diag-legit-inj-discuss-06")
        res = classify_email_m4(text)
        print("\nScenario 4 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["phishing_verdict"], "legitimate")
        self.assertEqual(res["injection_verdict"], "clean")
        self.assertEqual(res["security_action"], "allow")
        self.assertFalse(res["is_phishing"])
        self.assertFalse(res["has_prompt_injection"])

    def test_05_legitimate_with_quoted_injection(self):
        """Scenario 5: Legitimate email with quoted malicious instructions -> legitimate, detected, quarantine_review."""
        text = self._format_case("diag-legit-quoted-07")
        res = classify_email_m4(text)
        print("\nScenario 5 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["phishing_verdict"], "legitimate")
        self.assertEqual(res["injection_verdict"], "detected")
        self.assertEqual(res["security_action"], "quarantine_review")
        self.assertFalse(res["is_phishing"])
        self.assertTrue(res["has_prompt_injection"])

    def test_06_phishing_with_indirect_injection(self):
        """Scenario 6: Phishing email with indirect prompt injection -> phishing, detected, block."""
        text = self._format_case("diag-phish-marked-inj-13")
        res = classify_email_m4(text)
        print("\nScenario 6 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["phishing_verdict"], "phishing")
        self.assertEqual(res["injection_verdict"], "detected")
        self.assertEqual(res["security_action"], "block")
        self.assertTrue(res["is_phishing"])
        self.assertTrue(res["has_prompt_injection"])

    def test_07_injection_manipulation_attempt(self):
        """Scenario 7: Injection attempt manipulating detector to return legitimate -> phishing, detected, block."""
        text = self._format_case("diag-phish-unmarked-inj-15")
        res = classify_email_m4(text)
        print("\nScenario 7 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["phishing_verdict"], "phishing")
        self.assertEqual(res["injection_verdict"], "detected")
        self.assertEqual(res["security_action"], "block")
        self.assertTrue(res["is_phishing"])
        self.assertTrue(res["has_prompt_injection"])

    def test_08_suspicious_language_benign_intent(self):
        """Scenario 8: Email with suspicious language but no phishing intent -> legitimate, clean, allow."""
        text = self._format_case("diag-legit-sec-05")
        res = classify_email_m4(text)
        print("\nScenario 8 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["phishing_verdict"], "legitimate")
        self.assertEqual(res["injection_verdict"], "clean")
        self.assertEqual(res["security_action"], "allow")
        self.assertFalse(res["is_phishing"])
        self.assertFalse(res["has_prompt_injection"])

    def test_09_model_unavailable(self):
        """Scenario 9: Model unavailable -> explicit failure report, manual_review, never silently legitimate."""
        text = "Synthetic test email"
        res = classify_email_m4(text, api_base="http://127.0.0.1:54321")
        print("\nScenario 9 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
        self.assertFalse(res["is_valid"])
        self.assertEqual(res["security_action"], "manual_review")
        self.assertEqual(res["phishing_verdict"], "error")
        self.assertEqual(res["injection_verdict"], "error")
        self.assertEqual(res["verdict"], "error")
        self.assertIn("Pipeline failure", res["reasons"][0])

    def test_10_injection_detector_failure(self):
        """Scenario 10: Injection detector failure (Stage 1 fails) -> explicit failure report, manual_review."""
        text = "Synthetic test email"

        def mock_call(sys_prompt, user_prompt, model=None, api_base=None):
            if sys_prompt == SYSTEM_INJECTION_DETECTOR:
                return None, "Raw broken response", 0.1, "json_parse_error"
            # Stage 2 succeeds
            return {"is_phishing": False}, '{"is_phishing": false}', 0.2, None

        with patch("core.inference._call_ollama_json", side_effect=mock_call):
            res = classify_email_m4(text)
            print("\nScenario 10 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
            self.assertFalse(res["is_valid"])
            self.assertEqual(res["security_action"], "manual_review")
            self.assertEqual(res["injection_verdict"], "error")
            self.assertEqual(res["verdict"], "error")
            self.assertIn("Stage 1 (Injection Detector)", res["failure_message"])

    def test_11_phishing_classifier_failure(self):
        """Scenario 11: Phishing classifier failure (Stage 2 fails) -> explicit failure report, manual_review."""
        text = "Synthetic test email"

        def mock_call(sys_prompt, user_prompt, model=None, api_base=None):
            if sys_prompt == SYSTEM_INJECTION_DETECTOR:
                # Stage 1 succeeds
                return {"has_prompt_injection": False}, '{"has_prompt_injection": false}', 0.1, None
            # Stage 2 fails
            return None, "Raw timeout error", 0.5, "timeout"

        with patch("core.inference._call_ollama_json", side_effect=mock_call):
            res = classify_email_m4(text)
            print("\nScenario 11 Result:", res.get("phishing_verdict"), res.get("injection_verdict"), res.get("security_action"))
            self.assertFalse(res["is_valid"])
            self.assertEqual(res["security_action"], "manual_review")
            self.assertEqual(res["phishing_verdict"], "error")
            self.assertEqual(res["verdict"], "error")
            self.assertIn("Stage 2 (Phishing Classifier)", res["failure_message"])


if __name__ == "__main__":
    unittest.main()

