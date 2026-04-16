#!/usr/bin/env python3
"""CLI wrapper for the Are You Sure critique engine.

Usage:
  python3 scripts/are_you_sure_cli.py --input payload.json
  cat payload.json | python3 scripts/are_you_sure_cli.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from are_you_sure import CritiqueInput, RuleBasedCritiqueEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Are You Sure critique")
    parser.add_argument("--input", type=Path, help="Path to JSON payload")
    return parser.parse_args()


def load_payload(path: Path | None) -> dict:
    if path is None:
        data = sys.stdin.read().strip()
        if not data:
            raise ValueError("No input provided. Use --input or pipe JSON via stdin.")
        return json.loads(data)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    critique_input = CritiqueInput.from_dict(payload)
    engine = RuleBasedCritiqueEngine()
    output = engine.critique(critique_input)
    print(json.dumps(output.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
