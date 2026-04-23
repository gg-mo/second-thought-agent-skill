#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$ROOT/scripts/smoke/_match.sh"

[ -f "$ROOT/.opencode/INSTALL.md" ]
[ -f "$ROOT/.opencode/plugins/second-thought.js" ]
[ -f "$ROOT/package.json" ]

match_q 'experimental.chat.messages.transform' "$ROOT/.opencode/plugins/second-thought.js"
match_q 'config.skills.paths.push' "$ROOT/.opencode/plugins/second-thought.js"
match_q 'SECOND_THOUGHT_GATE' "$ROOT/.opencode/plugins/second-thought.js"
match_q 'st:skip|#st-skip' "$ROOT/.opencode/plugins/second-thought.js"
match_q 'second-thought.js' "$ROOT/package.json"

echo "[opencode] smoke checks passed"
