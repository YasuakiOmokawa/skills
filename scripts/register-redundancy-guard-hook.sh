#!/usr/bin/env bash
set -euo pipefail

# express-intent-in-code の redundancy-guard hook を ~/.claude/settings.json に登録する (冪等)。
# スクリプト実体は skills CLI が ~/.agents/skills/express-intent-in-code/scripts/ へ配布する。
# settings.json の hook 配線だけは plain skill インストールでは運べないため、ここで登録する。
# テスト用に CLAUDE_SETTINGS で対象ファイルを差し替え可能。

SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
HOOK_CMD="bash $HOME/.agents/skills/express-intent-in-code/scripts/redundancy-guard.sh"
GUARD_SCRIPT="$HOME/.agents/skills/express-intent-in-code/scripts/redundancy-guard.sh"

if ! command -v jq >/dev/null 2>&1; then
  echo "  ✗ jq が見つかりません。インストール後に再実行してください → スキップ" >&2
  exit 0
fi

if [ ! -f "$GUARD_SCRIPT" ]; then
  echo "  ⚠ $GUARD_SCRIPT が未配置です (npx skills add で express-intent-in-code を先にインストール推奨)。登録は行います。"
fi

if [ ! -f "$SETTINGS" ]; then
  mkdir -p "$(dirname "$SETTINGS")"
  printf '{}' > "$SETTINGS"
  echo "  ⚠ $SETTINGS が無かったため新規作成しました"
fi

if ! jq empty "$SETTINGS" 2>/dev/null; then
  echo "  ✗ $SETTINGS が不正な JSON です。手動で修復してから再実行してください → 中止" >&2
  exit 1
fi

if jq -e '[.hooks.PostToolUse[]?.hooks[]?.command // ""] | any(contains("redundancy-guard.sh"))' "$SETTINGS" >/dev/null; then
  echo "  ✓ redundancy-guard hook は登録済み"
  exit 0
fi

tmp=$(mktemp)
jq --arg cmd "$HOOK_CMD" '.hooks.PostToolUse = ((.hooks.PostToolUse // []) + [{matcher: "Edit|Write", hooks: [{type: "command", command: $cmd, timeout: 10}]}])' "$SETTINGS" > "$tmp"
jq empty "$tmp"
cp "$SETTINGS" "${SETTINGS}.bak"
mv "$tmp" "$SETTINGS"
echo "  ✓ redundancy-guard hook を $SETTINGS に登録しました (バックアップ: ${SETTINGS}.bak)"
echo "  → 反映は次回セッション起動時 (即時反映したい場合は /hooks を一度開く)"
