#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

[ -f "$ROOT/.claude-plugin/plugin.json" ]
[ -f "$ROOT/.claude-plugin/marketplace.json" ]
[ -f "$ROOT/hooks/hooks.json" ]
[ -x "$ROOT/hooks/session-start" ]

echo "[claude] smoke checks passed"
