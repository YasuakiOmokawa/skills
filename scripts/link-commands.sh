#!/usr/bin/env bash
set -euo pipefail

# Links all slash commands in this repository to ~/.claude/commands/, so that
# Claude Code recognizes them as user-level commands.
#
# After running:
#   ~/.claude/commands/<name>.md -> <repo>/commands/<name>.md

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.claude/commands"

mkdir -p "$DEST"

linked=0
for src in "$REPO"/plugins/*/commands/*.md; do
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
echo "Done. $linked command(s) linked. Invoke them with /<name> in Claude Code."
