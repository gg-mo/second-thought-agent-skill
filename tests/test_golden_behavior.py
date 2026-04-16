from __future__ import annotations

import json
import unittest
from pathlib import Path

from are_you_sure import CritiqueInput, RuleBasedCritiqueEngine


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests" / "golden" / "cases.json"


class GoldenBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RuleBasedCritiqueEngine()

    def test_golden_statuses_and_contract_shape(self) -> None:
        cases = json.loads(CASES_PATH.read_text())
        for case in cases:
            with self.subTest(case=case["name"]):
                payload = CritiqueInput.from_dict(case["input"])
                result = self.engine.critique(payload).to_dict()

                self.assertEqual(result["status"], case["expected_status"])
                self.assertTrue(result["summary"])
                self.assertTrue(result["goal_alignment"])
                self.assertIsInstance(result["concerns"], list)
                self.assertIsInstance(result["assumptions"], list)
                self.assertIsInstance(result["better_options"], list)
                self.assertTrue(result["challenge_prompt"])
                self.assertTrue(result["recommended_next_step"])
                self.assertGreaterEqual(result["confidence"], 0)
                self.assertLessEqual(result["confidence"], 1)
                self.assertIsInstance(result["decision_factors"], list)

                if result["status"] == "prompt_human":
                    self.assertTrue(result["prompt_to_human"])


if __name__ == "__main__":
    unittest.main()
