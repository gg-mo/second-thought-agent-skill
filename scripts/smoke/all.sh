#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

"$ROOT/scripts/smoke/codex.sh"
"$ROOT/scripts/smoke/claude.sh"
"$ROOT/scripts/smoke/cursor.sh"
"$ROOT/scripts/smoke/gemini.sh"
"$ROOT/scripts/smoke/opencode.sh"

echo "[all] smoke checks passed"
