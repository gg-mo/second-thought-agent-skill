#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$ROOT/scripts/smoke/_match.sh"

[ -f "$ROOT/.opencode/INSTALL.md" ]
[ -f "$ROOT/.opencode/plugins/are-you-sure.js" ]
[ -f "$ROOT/package.json" ]

match_q 'experimental.chat.messages.transform' "$ROOT/.opencode/plugins/are-you-sure.js"
match_q 'config.skills.paths.push' "$ROOT/.opencode/plugins/are-you-sure.js"
match_q 'are-you-sure.js' "$ROOT/package.json"

echo "[opencode] smoke checks passed"
