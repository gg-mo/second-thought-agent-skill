#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

[ -f "$ROOT/.claude-plugin/plugin.json" ]
[ -f "$ROOT/.claude-plugin/marketplace.json" ]
[ -f "$ROOT/hooks/hooks.json" ]
[ -x "$ROOT/hooks/session-start" ]

OUT="$(CLAUDE_PLUGIN_ROOT=1 "$ROOT/hooks/session-start")"
echo "$OUT" | rg -q 'additionalContext|hookSpecificOutput'
echo "$OUT" | rg -q 'You have Are You Sure'

echo "[claude] smoke checks passed"
