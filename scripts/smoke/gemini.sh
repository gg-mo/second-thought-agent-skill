#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

[ -f "$ROOT/gemini-extension.json" ]
[ -f "$ROOT/GEMINI.md" ]

if ! rg -q 'using-are-you-sure/SKILL.md' "$ROOT/GEMINI.md"; then
  echo "GEMINI.md missing using-are-you-sure reference" >&2
  exit 1
fi

echo "[gemini] smoke checks passed"
