from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "benchmarks" / "cases.json"


class BenchmarkHarnessTests(unittest.TestCase):
    def test_benchmark_cases_have_expected_shape(self) -> None:
        cases = json.loads(CASES.read_text())
        self.assertGreaterEqual(len(cases), 20)
        for case in cases:
            self.assertIn("name", case)
            self.assertIn("input", case)
            self.assertIn("expected_status", case)
            self.assertIn(case["expected_status"], ["proceed", "revise", "prompt_human"])


if __name__ == "__main__":
    unittest.main()
