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

対話で生成するのは 2 セクション（Release labels / create-design-doc の DD 文書）です。
順番に質問し、各セクション冒頭で「使う/使わない」を聞き、使わなければスキップします。

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

# -----------------------------------------------------------------------------
# Section A: Release labels
# -----------------------------------------------------------------------------
echo ""
echo "─── Section A: リリースラベル ───"
if prompt_yes_no "PR ラベル定義を生成しますか？"; then
  if confirm_overwrite "$CONFIG_DIR/release-labels.md"; then
    echo "  推奨デフォルト（Productivity / AI Contribution / Release Level）を使用します。"
    echo "  生成後、$CONFIG_DIR/release-labels.md を直接編集して自社のラベル名に合わせてください。"
    echo ""
    echo "  プロジェクトの根幹機能を入力してください（1 行 1 項目、空行で終了）:"
    echo "  例: 認証・認可 / 決済処理 / データ永続化 / 外部公開 API"
    core_features=""
    while IFS= read -r -p "  > " feature; do
      [ -z "$feature" ] && break
      core_features+="- ${feature}"$'\n'
    done

    cat > "$CONFIG_DIR/release-labels.md" <<EOF
# リリースラベル設定

omokawa-skills の create-pr スキルが参照するラベル定義。

## productivity_labels

- \`1.Feature development\`: ユーザー向け機能の追加・改善
- \`2.Bugfix & Maintenance\`: バグ修正、リファクタリング、ライブラリ更新
- \`3.Tech investment\`: 共通基盤開発、CI 改善、計測基盤
- \`4.Quality improvement\`: テスト追加、品質向上のためのリファクタ
- \`5.Others\`: Bot 生成 PR や上記に当てはまらないもの

## ai_contribution_labels

- \`ai-contribution-level:0\`: AI 生成コードが 10% 未満
- \`ai-contribution-level:1\`: AI 生成コードが 10-40%
- \`ai-contribution-level:2\`: AI 生成コードが 40-80%
- \`ai-contribution-level:3\`: AI 生成コードが 80% 以上

## release_level_labels

- \`ReleaseLevel-1\`: 表示のみの変更、パッチアップデート
- \`ReleaseLevel-2\`: 後方互換性のある変更、根幹機能に影響なし
- \`ReleaseLevel-3\`: 後方互換性のある変更、根幹機能に影響あり
- \`ReleaseLevel-4\`: 不可逆な変更、スキーマ変更、メジャーアップデート

## core_features

プロジェクトの根幹機能（ReleaseLevel 高レベル判定に使用）:

${core_features:-（未設定）}
EOF
    echo "  ✓ $CONFIG_DIR/release-labels.md 作成"
    echo "  → ラベル名を自社のものに変えるなら $CONFIG_DIR/release-labels.md を直接編集"
  fi
else
  echo "  → スキップ"
fi

# -----------------------------------------------------------------------------
# Section B: create-design-doc の DD 文書
# -----------------------------------------------------------------------------
echo ""
echo "─── Section B: create-design-doc の DD 文書 ───"
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
echo "  - Claude Code から /create-pr / /create-design-doc などを呼ぶと、これらの値が透過的に使われます"
