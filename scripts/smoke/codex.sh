#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$ROOT/scripts/smoke/_match.sh"

[ -f "$ROOT/.codex/INSTALL.md" ]
[ -f "$ROOT/.codex-plugin/plugin.json" ]
[ -f "$ROOT/skills/are-you-sure/SKILL.md" ]

TMP_JSON="$(mktemp)"
cat > "$TMP_JSON" <<JSON
{
  "original_intent": "Validate codex smoke behavior",
  "current_context": "Testing local critique CLI",
  "proposal_type": "idea",
  "proposal": "Run smoke check",
  "rationale": "Quick packaging validation",
  "mode": "fast",
  "explainability": "compact"
}
JSON

OUT="$(python3 "$ROOT/scripts/are_you_sure_cli.py" --input "$TMP_JSON")"
rm -f "$TMP_JSON"

echo "$OUT" | match_q '"status"'

echo "[codex] smoke checks passed"
