#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

[ -f "$ROOT/.opencode/INSTALL.md" ]
[ -f "$ROOT/.opencode/plugins/are-you-sure.js" ]
[ -f "$ROOT/package.json" ]

rg -q 'experimental.chat.messages.transform' "$ROOT/.opencode/plugins/are-you-sure.js"
rg -q 'config.skills.paths.push' "$ROOT/.opencode/plugins/are-you-sure.js"
rg -q 'are-you-sure.js' "$ROOT/package.json"

echo "[opencode] smoke checks passed"
