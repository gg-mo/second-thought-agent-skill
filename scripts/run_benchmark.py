#!/usr/bin/env python3
"""Run benchmark scenarios against the critique engine."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from are_you_sure import CritiqueInput, EngineConfig, RuleBasedCritiqueEngine

CASES_PATH = ROOT / "benchmarks" / "cases.json"


def main() -> int:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    engine = RuleBasedCritiqueEngine(config=EngineConfig(semantic_backend="semantic_keyword"))

    total = len(cases)
    correct = 0
    rows: list[str] = []

    for case in cases:
        payload = CritiqueInput.from_dict(case["input"])
        out = engine.critique(payload)
        expected = case["expected_status"]
        ok = out.status.value == expected
        correct += 1 if ok else 0
        rows.append(f"{case['name']}: expected={expected} got={out.status.value} {'OK' if ok else 'MISS'}")

    accuracy = correct / total if total else 0.0
    print("Benchmark results")
    print("-----------------")
    for row in rows:
        print(row)
    print(f"Accuracy: {correct}/{total} ({accuracy:.1%})")

    return 0 if accuracy >= 0.75 else 1


if __name__ == "__main__":
    raise SystemExit(main())
