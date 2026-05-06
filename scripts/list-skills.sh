#!/usr/bin/env bash
set -euo pipefail

# Lists all skills, commands, and agents in this repository.

REPO="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Skills ==="
cd "$REPO"
find skills -name SKILL.md -not -path '*/node_modules/*' | sed 's|/SKILL.md$||' | sort

echo ""
echo "=== Commands ==="
for cmd_dir in commands/*/; do
  [ -d "$cmd_dir" ] || continue
  name="$(basename "$cmd_dir")"
  echo "commands/$name/$name.md"
done | sort

echo ""
echo "=== Agents ==="
for f in agents/*.md; do
  [ -f "$f" ] || continue
  echo "$f"
done | sort
