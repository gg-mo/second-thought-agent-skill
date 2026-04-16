#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$ROOT/scripts/smoke/_match.sh"

[ -f "$ROOT/.claude-plugin/plugin.json" ]
[ -f "$ROOT/.claude-plugin/marketplace.json" ]
[ -f "$ROOT/hooks/hooks.json" ]
[ -x "$ROOT/hooks/session-start" ]

OUT="$(CLAUDE_PLUGIN_ROOT=1 "$ROOT/hooks/session-start")"
echo "$OUT" | match_q 'additionalContext|hookSpecificOutput'
echo "$OUT" | match_q 'You have Are You Sure'
echo "$OUT" | match_q 'ays:skip|#ays-skip'

echo "[claude] smoke checks passed"
