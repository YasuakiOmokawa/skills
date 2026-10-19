#!/usr/bin/env bash
set -euo pipefail

# omokawa-skills のグローバル設定値を ~/.claude/skills-config/*.md に書き出す対話セットアップ。
# Claude を介さず bash の read で値を受け取り、ファイルに直接書き込む。

CONFIG_DIR="$HOME/.claude/skills-config"
mkdir -p "$CONFIG_DIR"

cat <<'BANNER'
=== omokawa-skills セットアップ ===

このスクリプトは ~/.claude/skills-config/ 配下に設定ファイルを生成します。
Claude には値を渡しません。すべての入力は bash 内で完結し、ファイルに直接書き込まれます。

対話で生成するのは create-design-doc の DD 文書です。
冒頭で「使う/使わない」を聞き、使わなければスキップします。

BANNER

prompt_yes_no() {
  local prompt="$1"
  local default="${2:-n}"
  local reply
  read -r -p "$prompt [y/N]: " reply
  reply="${reply:-$default}"
  [[ "$reply" =~ ^[Yy]$ ]]
}

confirm_overwrite() {
  local file="$1"
  if [ -e "$file" ]; then
    if prompt_yes_no "$file は既に存在します。上書きしますか？"; then
      return 0
    else
      echo "  → スキップ"
      return 1
    fi
  fi
  return 0
}

echo ""
echo "─── create-design-doc の DD 文書 ───"
if prompt_yes_no "create-design-doc を使いますか？（自組織の DD 文書を配置します）"; then
  DD_DIR="$CONFIG_DIR/create-design-doc"
  mkdir -p "$DD_DIR"
  echo "  DD テンプレート・実例は組織固有情報のためリポジトリに同梱していません。"
  echo "  手元のファイルパスを入力すると $DD_DIR/ にコピーします（空 Enter でスキップ）。"

  copy_dd_doc() {
    local label="$1"
    local dest="$2"
    local src
    read -r -p "  ${label}: " src
    if [ -z "$src" ]; then
      echo "  → スキップ"
      return 0
    fi
    src="${src/#\~/$HOME}"
    if [ ! -f "$src" ]; then
      echo "  ✗ $src が見つかりません → スキップ"
      return 0
    fi
    if confirm_overwrite "$DD_DIR/$dest"; then
      cp "$src" "$DD_DIR/$dest"
      echo "  ✓ $DD_DIR/$dest 配置"
    fi
  }

  copy_dd_doc "DD テンプレート（create-design-doc が参照）" "dd_template.md"
  copy_dd_doc "完成 DD の参考実例" "dd_reference.md"
else
  echo "  → スキップ"
fi

# -----------------------------------------------------------------------------
# 完了報告
# -----------------------------------------------------------------------------
echo ""
echo "=== セットアップ完了 ==="
echo ""
echo "生成されたファイル:"
ls -la "$CONFIG_DIR"/*.md 2>/dev/null | awk '{print "  " $NF}' || echo "  （なし）"
echo ""
echo "次のアクション:"
echo "  - 値を変更したい場合は $CONFIG_DIR/*.md を直接編集"
echo "  - dotfiles で管理する場合は symlink 化を検討"
echo "  - Claude Code から /create-design-doc を呼ぶと、これらの値が透過的に使われます"
