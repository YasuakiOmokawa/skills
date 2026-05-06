#!/usr/bin/env bash
set -euo pipefail

# Links all slash commands in this repository to ~/.claude/commands/, so that
# Claude Code recognizes them as user-level commands.
#
# After running:
#   ~/.claude/commands/<name>.md -> <repo>/commands/<name>/<name>.md

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.claude/commands"

mkdir -p "$DEST"

linked=0
for cmd_dir in "$REPO/commands"/*/; do
  [ -d "$cmd_dir" ] || continue
  name="$(basename "$cmd_dir")"
  src="$cmd_dir$name.md"

  if [ ! -f "$src" ]; then
    echo "warn: expected $src, skipping" >&2
    continue
  fi

  target="$DEST/$name.md"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "warn: $target exists as a real file, removing" >&2
    rm -f "$target"
  fi

  ln -sfn "$src" "$target"
  echo "linked $name.md -> $src"
  linked=$((linked + 1))
done

echo ""
echo "Done. $linked command(s) linked. Invoke them with /<name> in Claude Code."
