#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$ROOT/scripts/smoke/_match.sh"

[ -f "$ROOT/.codex/INSTALL.md" ]
[ -f "$ROOT/.codex-plugin/plugin.json" ]
[ -f "$ROOT/skills/second-thought/SKILL.md" ]

TMP_JSON="$(mktemp)"
cat > "$TMP_JSON" <<JSON
{
  "request": "We are about to merge a risky change to production quickly."
}
JSON

OUT="$(python3 "$ROOT/scripts/second_thought_cli.py" --input "$TMP_JSON")"
rm -f "$TMP_JSON"

echo "$OUT" | match_q '"status"'

echo "[codex] smoke checks passed"
