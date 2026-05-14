#!/usr/bin/env bash
set -euo pipefail

# Links all agents in this repository to ~/.claude/agents/, so that Claude Code
# recognizes them as user-level subagents.
#
# After running:
#   ~/.claude/agents/<name>.md -> <repo>/agents/<name>.md

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.claude/agents"

mkdir -p "$DEST"

linked=0
for src in "$REPO"/plugins/*/agents/*.md; do
  [ -f "$src" ] || continue
  name="$(basename "$src")"
  target="$DEST/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "warn: $target exists as a real file, removing" >&2
    rm -f "$target"
  fi

  ln -sfn "$src" "$target"
  echo "linked $name -> $src"
  linked=$((linked + 1))
done

echo ""
echo "Done. $linked agent(s) linked. Invoke them via Task(subagent_type=\"<name>\")."
