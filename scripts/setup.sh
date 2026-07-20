#!/usr/bin/env bash
set -euo pipefail

# omokawa-skills のグローバル設定値を ~/.claude/skills-config/*.md に書き出す対話セットアップ。
# Claude を介さず bash の read で値を受け取り、ファイルに直接書き込む。
# 機密性のある値（Jira Cloud ID 等）が AI のコンテキストに乗らない設計。

CONFIG_DIR="$HOME/.claude/skills-config"
mkdir -p "$CONFIG_DIR"

cat <<'BANNER'
=== omokawa-skills セットアップ ===

このスクリプトは ~/.claude/skills-config/ 配下に設定ファイルを生成します。
Claude には値を渡しません。すべての入力は bash 内で完結し、ファイルに直接書き込まれます。

4 セクション（Jira / Release labels / Environments / create-design-doc の DD 文書）を
順番に質問します。
各セクション冒頭で「使う/使わない」を聞き、使わなければスキップします。

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
# Section A: Jira
# -----------------------------------------------------------------------------
echo ""
echo "─── Section A: Jira 設定 ───"
if prompt_yes_no "Jira を使いますか？"; then
  if confirm_overwrite "$CONFIG_DIR/jira.md"; then
    read -r -p "Jira Cloud ID (UUID 36 文字、例: 00000000-0000-0000-0000-000000000000): " cloud_id
    read -r -p "Jira プロジェクトキー (例: PROJ): " project_key
    read -r -p "Jira MCP プレフィックス (例: atlassian): " jira_mcp
    read -r -p "Atlassian MCP プレフィックス (例: atlassian): " atlassian_mcp

    cat > "$CONFIG_DIR/jira.md" <<EOF
# Jira 設定

omokawa-skills の create-jira-issues / set-jira-story-points / map-user-stories が参照する設定値。

## 設定値

- cloud_id: ${cloud_id}
- project_key: ${project_key}
- jira_mcp: ${jira_mcp}
- atlassian_mcp: ${atlassian_mcp}
- story_points_field: customfield_10005  # Jira 標準

## 使い方

スキル本体は \`<atlassian-mcp>\` / \`<jira-mcp>\` プレースホルダーを使う。実行時に上記の値で展開すること。
EOF
    echo "  ✓ $CONFIG_DIR/jira.md 作成"
  fi
else
  echo "  → スキップ"
fi

# -----------------------------------------------------------------------------
# Section B: Release labels
# -----------------------------------------------------------------------------
echo ""
echo "─── Section B: リリースラベル ───"
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

omokawa-skills の create-pr コマンドが参照するラベル定義。

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
# Section C: Environments
# -----------------------------------------------------------------------------
echo ""
echo "─── Section C: Integration 環境 ───"
if prompt_yes_no "production / sandbox / staging 以外の integration 環境がありますか？"; then
  if confirm_overwrite "$CONFIG_DIR/environments.md"; then
    echo "  環境名を入力してください（1 行 1 項目、空行で終了）:"
    echo "  例: dev1 / dev2 / qa-stage"
    rollback_targets=""
    while IFS= read -r -p "  > " env; do
      [ -z "$env" ] && break
      rollback_targets+="- ${env}"$'\n'
    done

    cat > "$CONFIG_DIR/environments.md" <<EOF
# 環境設定

omokawa-skills の create-pr コマンドが Revert 手順に列挙する環境名。

## rollback_targets

production / sandbox / staging に追加して列挙する integration 環境:

${rollback_targets:-（未設定）}
migration が含まれる PR の Revert 手順に「これらの環境すべてで \`db:migrate:down\` を実行」と展開される。
EOF
    echo "  ✓ $CONFIG_DIR/environments.md 作成"
  fi
else
  echo "  → スキップ"
fi

# -----------------------------------------------------------------------------
# Section D: create-design-doc の DD 文書
# -----------------------------------------------------------------------------
echo ""
echo "─── Section D: create-design-doc の DD 文書 ───"
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
echo "  - Claude Code から /create-pr / /create-jira-issues などを呼ぶと、これらの値が透過的に使われます"
