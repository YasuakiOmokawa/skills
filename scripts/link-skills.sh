#!/usr/bin/env bash
set -euo pipefail

# Links all skills in this repository to ~/.claude/skills/, so that Claude Code
# recognizes them as user-level skills.
#
# After running:
#   ~/.claude/skills/<name> -> <repo>/skills/<bucket>/<name>

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.claude/skills"

# Safety: if ~/.claude/skills is itself a symlink into this repo, bail out.
if [ -L "$DEST" ]; then
  resolved="$(readlink -f "$DEST")"
  case "$resolved" in
    "$REPO"|"$REPO"/*)
      echo "error: $DEST is a symlink into this repo ($resolved)." >&2
      echo "Remove it (rm \"$DEST\") and re-run; the script will recreate it as a real directory." >&2
      exit 1
      ;;
  esac
fi

mkdir -p "$DEST"

linked=0
find "$REPO/plugins" -path '*/skills/*/SKILL.md' -not -path '*/node_modules/*' -print0 |
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  name="$(basename "$src")"
  target="$DEST/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "warn: $target exists as a real file/dir, removing" >&2
    rm -rf "$target"
  fi

  ln -sfn "$src" "$target"
  echo "linked $name -> $src"
  linked=$((linked + 1))
done

echo ""
echo "Done. linked skills can be invoked from Claude Code."
