#!/usr/bin/env bash
set -euo pipefail

# Lists all skills, commands, and agents across all plugins in this repository.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

echo "=== Plugins ==="
ls -1 plugins/ 2>/dev/null | sort

echo ""
echo "=== Skills ==="
find plugins -path '*/skills/*/SKILL.md' | sed 's|/SKILL.md$||' | sort

echo ""
echo "=== Commands ==="
find plugins -path '*/commands/*.md' | sort

echo ""
echo "=== Top-level Agents ==="
find plugins -path '*/agents/*.md' -not -path '*/skills/*' | sort
