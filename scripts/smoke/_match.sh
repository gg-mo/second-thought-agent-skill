#!/usr/bin/env bash
set -euo pipefail

# Portable regex matcher: prefer rg, fallback to grep -E.
match_q() {
  local pattern="$1"
  local target="${2:-}"

  if command -v rg >/dev/null 2>&1; then
    if [ -n "$target" ]; then
      rg -q "$pattern" "$target"
    else
      rg -q "$pattern"
    fi
  else
    if [ -n "$target" ]; then
      grep -Eq "$pattern" "$target"
    else
      grep -Eq "$pattern"
    fi
  fi
}
