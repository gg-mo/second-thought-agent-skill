#!/usr/bin/env python3
"""Run benchmark scenarios against the critique engine with quality metrics."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from second_thought import CritiqueInput, EngineConfig, RuleBasedCritiqueEngine

CASES_PATH = ROOT / "benchmarks" / "cases.json"
REPORT_PATH = ROOT / "benchmarks" / "latest_report.json"
CAL_PATH = ROOT / "benchmarks" / "confidence_calibration.json"


def _load_calibration() -> tuple[float, float]:
    if not CAL_PATH.exists():
        return (1.0, 0.0)
    data = json.loads(CAL_PATH.read_text(encoding="utf-8"))
    return (float(data.get("slope", 1.0)), float(data.get("intercept", 0.0)))


def main() -> int:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    slope, intercept = _load_calibration()
    engine = RuleBasedCritiqueEngine(
        config=EngineConfig(
            semantic_backend="semantic_keyword",
            confidence_slope=slope,
            confidence_intercept=intercept,
        )
    )

    total = len(cases)
    correct = 0
    rows: list[str] = []

    by_stage = defaultdict(lambda: {"total": 0, "correct": 0})
    by_expected = defaultdict(lambda: {"total": 0, "correct": 0})

    prompt_quality_hits = 0
    prompt_total = 0
    factor_hits = 0
    brier_sum = 0.0

    for case in cases:
        payload = CritiqueInput.from_dict(case["input"])
        out = engine.critique(payload)

        expected = case["expected_status"]
        got = out.status.value
        ok = got == expected

        correct += 1 if ok else 0
        rows.append(f"{case['name']}: expected={expected} got={got} {'OK' if ok else 'MISS'}")

        stage = case["input"].get("stage", "unknown")
        by_stage[stage]["total"] += 1
        by_stage[stage]["correct"] += 1 if ok else 0

        by_expected[expected]["total"] += 1
        by_expected[expected]["correct"] += 1 if ok else 0

        if out.status.value == "prompt_human":
            prompt_total += 1
            q = out.prompt_to_human or ""
            if "?" in q and len(q.split()) >= 8:
                prompt_quality_hits += 1

        if out.decision_factors:
            factor_hits += 1

        target = 1.0 if ok else 0.0
        brier_sum += (out.confidence - target) ** 2

    accuracy = correct / total if total else 0.0
    factor_coverage = factor_hits / total if total else 0.0
    prompt_quality = prompt_quality_hits / prompt_total if prompt_total else 1.0
    brier = brier_sum / total if total else 1.0

    print("Benchmark results")
    print("-----------------")
    for row in rows:
        print(row)
    print(f"Accuracy: {correct}/{total} ({accuracy:.1%})")
    print(f"Prompt quality: {prompt_quality_hits}/{prompt_total} ({prompt_quality:.1%})")
    print(f"Decision factor coverage: {factor_hits}/{total} ({factor_coverage:.1%})")
    print(f"Confidence Brier score: {brier:.4f}")

    print("By stage:")
    for stage, stats in sorted(by_stage.items()):
        s_acc = stats["correct"] / stats["total"] if stats["total"] else 0.0
        print(f"- {stage}: {stats['correct']}/{stats['total']} ({s_acc:.1%})")

    report = {
        "accuracy": accuracy,
        "prompt_quality": prompt_quality,
        "decision_factor_coverage": factor_coverage,
        "brier_score": brier,
        "by_stage": {
            key: {
                "total": value["total"],
                "correct": value["correct"],
                "accuracy": (value["correct"] / value["total"] if value["total"] else 0.0),
            }
            for key, value in by_stage.items()
        },
        "by_expected_status": {
            key: {
                "total": value["total"],
                "correct": value["correct"],
                "accuracy": (value["correct"] / value["total"] if value["total"] else 0.0),
            }
            for key, value in by_expected.items()
        },
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return 0 if accuracy >= 0.75 and prompt_quality >= 0.7 and factor_coverage >= 0.95 else 1


if __name__ == "__main__":
    raise SystemExit(main())
