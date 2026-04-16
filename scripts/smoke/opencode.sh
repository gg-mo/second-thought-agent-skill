#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

[ -f "$ROOT/.opencode/INSTALL.md" ]
[ -f "$ROOT/.opencode/plugins/are-you-sure.js" ]
[ -f "$ROOT/package.json" ]

if ! rg -q 'are-you-sure.js' "$ROOT/package.json"; then
  echo "package.json missing OpenCode main plugin entry" >&2
  exit 1
fi

echo "[opencode] smoke checks passed"
