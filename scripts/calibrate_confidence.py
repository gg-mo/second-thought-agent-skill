#!/usr/bin/env python3
"""Grid-search confidence calibration parameters using benchmark cases."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from second_thought import CritiqueInput, EngineConfig, RuleBasedCritiqueEngine

CASES_PATH = ROOT / "benchmarks" / "cases.json"
CAL_PATH = ROOT / "benchmarks" / "confidence_calibration.json"


def evaluate(slope: float, intercept: float) -> float:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    engine = RuleBasedCritiqueEngine(
        config=EngineConfig(
            semantic_backend="semantic_keyword",
            confidence_slope=slope,
            confidence_intercept=intercept,
        )
    )
    brier = 0.0
    n = 0
    for case in cases:
        payload = CritiqueInput.from_dict(case["input"])
        out = engine.critique(payload)
        ok = 1.0 if out.status.value == case["expected_status"] else 0.0
        brier += (out.confidence - ok) ** 2
        n += 1
    return brier / max(1, n)


def main() -> int:
    best = (1.0, 0.0)
    best_score = evaluate(*best)

    for i in range(6, 19):
        slope = i / 10
        for j in range(-30, 31, 5):
            intercept = j / 100
            score = evaluate(slope, intercept)
            if score < best_score:
                best = (slope, intercept)
                best_score = score

    out = {"slope": best[0], "intercept": best[1], "brier_score": best_score}
    CAL_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
