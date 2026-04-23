#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$ROOT/scripts/smoke/_match.sh"

[ -f "$ROOT/gemini-extension.json" ]
[ -f "$ROOT/GEMINI.md" ]

match_q 'using-second-thought/SKILL.md' "$ROOT/GEMINI.md"
python3 - <<PY
import sys
sys.path.insert(0, "$ROOT")
from second_thought import CritiqueInput, build_user_prompt, ProposalType
p=CritiqueInput(
  original_intent="gemini smoke",
  current_context="validate prompt builder",
  proposal_type=ProposalType.IDEA,
  proposal="check",
  rationale="smoke"
)
out=build_user_prompt(p)
assert "proposal_type" in out
PY

echo "[gemini] smoke checks passed"
