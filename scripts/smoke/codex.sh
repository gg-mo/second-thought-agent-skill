#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

[ -f "$ROOT/.codex/INSTALL.md" ]
[ -f "$ROOT/.codex-plugin/plugin.json" ]
[ -f "$ROOT/skills/are-you-sure/SKILL.md" ]
[ -f "$ROOT/skills/using-are-you-sure/SKILL.md" ]

echo "[codex] smoke checks passed"
