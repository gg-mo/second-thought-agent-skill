#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$ROOT/scripts/smoke/_match.sh"

[ -f "$ROOT/.cursor-plugin/plugin.json" ]
[ -f "$ROOT/hooks/hooks-cursor.json" ]

if ! match_q '"skills"\s*:\s*"\./skills/"' "$ROOT/.cursor-plugin/plugin.json"; then
  echo "cursor plugin missing skills path" >&2
  exit 1
fi

OUT="$(CURSOR_PLUGIN_ROOT=1 "$ROOT/hooks/session-start")"
echo "$OUT" | match_q 'additional_context'
echo "$OUT" | match_q 'st:skip|#st-skip'

echo "[cursor] smoke checks passed"
