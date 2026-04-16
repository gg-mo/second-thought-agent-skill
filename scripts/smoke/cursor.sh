#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

[ -f "$ROOT/.cursor-plugin/plugin.json" ]
[ -f "$ROOT/hooks/hooks-cursor.json" ]

if ! rg -q '"skills"\s*:\s*"\./skills/"' "$ROOT/.cursor-plugin/plugin.json"; then
  echo "cursor plugin missing skills path" >&2
  exit 1
fi

echo "[cursor] smoke checks passed"
