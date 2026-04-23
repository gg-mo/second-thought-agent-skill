#!/usr/bin/env python3
"""CLI wrapper for the Second Thought critique engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from second_thought import (
    CritiqueInput,
    CritiqueMode,
    EngineConfig,
    ExplainabilityMode,
    RuleBasedCritiqueEngine,
    build_payload_from_partial,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Second Thought critique")
    parser.add_argument("--input", type=Path, help="Path to JSON payload")
    parser.add_argument(
        "--input-mode",
        choices=["auto", "manual"],
        default="auto",
        help="auto: infer missing fields from partial input/context, manual: require full payload",
    )
    parser.add_argument(
        "--mode",
        choices=[CritiqueMode.STRICT.value, CritiqueMode.FAST.value],
        help="Override critique mode",
    )
    parser.add_argument(
        "--explainability",
        choices=[ExplainabilityMode.COMPACT.value, ExplainabilityMode.STANDARD.value, ExplainabilityMode.DETAILED.value],
        help="Output verbosity level",
    )
    parser.add_argument(
        "--semantic-backend",
        choices=["heuristic", "semantic_keyword"],
        default="heuristic",
        help="Alignment scoring backend",
    )
    parser.add_argument("--confidence-slope", type=float, default=1.0)
    parser.add_argument("--confidence-intercept", type=float, default=0.0)
    return parser.parse_args()


def load_payload(path: Path | None) -> dict:
    if path is None:
        data = sys.stdin.read().strip()
        if not data:
            raise ValueError("No input provided. Use --input or pipe JSON via stdin.")
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"request": data}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    if args.input_mode == "auto":
        payload = build_payload_from_partial(payload)
    if args.mode:
        payload["mode"] = args.mode
    if args.explainability:
        payload["explainability"] = args.explainability

    critique_input = CritiqueInput.from_dict(payload)
    engine = RuleBasedCritiqueEngine(
        config=EngineConfig(
            semantic_backend=args.semantic_backend,
            confidence_slope=args.confidence_slope,
            confidence_intercept=args.confidence_intercept,
        )
    )
    output = engine.critique(critique_input)
    print(json.dumps(output.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
