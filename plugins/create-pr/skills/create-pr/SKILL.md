---
name: create-pr
description: Creates a Conventional Commits **draft PR** (always `--draft`, no ready-PR path) from the current branch with template-aware description and labels. Accepts only `[base-branch]` as positional argument; other options (`--draft` toggle / label override / milestone override) are not supported. Use when the user says "PR を作って" / "draft PR" / "PR 作成して". Runs without confirmation.
---

カレントブランチから Conventional Commits 形式のドラフト PR を作成する。**ユーザー確認は一切行わず、分析完了後は直接 PR 作成を実行**。

## Arguments

- `$ARGUMENTS`: ベースブランチ名（省略可、省略時はリポジトリのデフォルトブランチ）

## Quick start

最短経路:
1. **Step 0**: PR テンプレートを動的検索 (`references/template-discovery.md` 参照) → ベースブランチ確定
2. **Step 1**: `git status` / `git branch --show-current` / `git log [base-branch]..HEAD --oneline` / `git diff [base-branch]...HEAD --stat` を並列実行
3. **Step 1.5**: ブランチ妥当性検証 (`references/branch-validation.md` 参照)。違反なら **コミット前** に `git switch -c` で新ブランチ切替（コミット後 rename は GitHub API 副作用で PR が CLOSED されるため不可）
4. **Step 2**: 未コミットファイルがあれば 1 コミット = 1〜3 ファイル粒度で `<type>(<scope>): <日本語要約>` 形式コミット
5. **Step 3**: `git push -u origin <branch>`
6. **Step 4-8**: タイトル / 本文 / ラベル生成（後述 Workflows）
7. **Step 9 (必須)**: `references/description-style.md` の **[A] 斜め読み / [B] コード由来情報 / [C] 重複・冗長 / [D] AI 臭** 4 観点セルフチェックを必ず実施 (省略禁止、Quick start でもスキップ不可)
8. **Step 10**: `gh pr create --draft --title ... --body-file ... --label ... --milestone ... --base [base-branch]`

PR URL を表示して完了。

## Workflows

### Step 4: コンテキスト収集

- **4a**: 不足あれば `git diff [base-branch]...HEAD` で詳細確認
- **4b**: 周辺コードと既存パターン比較。差異あれば理由・却下した代替案を整理
- **4c**: 本セッションの plan / 設計議論から「背景 / 設計判断 / やらなかったこと」を抽出（`~/.claude/plans/` ファイル走査は不要）

### Step 5: タイトル生成

`<type>(<scope>): <description>` (72 文字以内・日本語)。
- **type**: feat / fix / docs / style / refactor / perf / test / chore / ci / build
- **複数 type 混在**: 最も大きな価値変化を生む 1 つを採用。優先順位 `feat` > `fix` > `refactor` > `perf` > `test` > `chore` > `docs` > `style` > `ci` > `build`
- **scope**: 変更主ドメインの単数形英小文字（モデル / コントローラ prefix 流用が基本）。複数ドメインなら中心価値の 1 つ、均等で絞れなければ省略。docs / chore / ci でドメイン無しなら省略

### Step 6: 本文生成

検出した PR テンプレートのセクション構成に従う。**詳細は `references/description-style.md` を必ず Read**。要点:

- **Pre-work (mandatory)**: 本文を書く前に PR の本質を **2-3 点の bullet リスト** として scratch 出力 → 「このPRでやること」 (または「やったこと」を格上げ) に貼る
- **6 文体鉄則**: コードから読めることは書かない / 斜め読み構造 / 重複禁止 / 常体 / 書かない勇気 / 読み直し
- **セクション分量**:
  - 簡潔 (やったこと / なぜやるのか / 動作確認結果 / レビューしてほしい観点) → 全 1 行・bullet なし
  - 詳細 (設計判断 / やらなかったこと) → コードから読めない情報を散文で詳細展開（該当事実なければ見出し+空行のみ）
  - 定型 (Revert 手順 / チェックリスト) → テンプレ準拠
- **テンプレ内 `<!-- ... -->` コメントは削除しない**（migration 無しでも rollback サンプルブロックを残す）
- **テンプレに無い見出しは追加しない**

### Step 7-8: ラベル・マイルストーン

詳細は `references/labels-and-milestones.md` 参照。`~/.claude/skills-config/release-labels.md` を Read し以下 3 種を 1 つずつ選択:

1. **Productivity ラベル** (`productivity_labels`): 開発生産性カテゴリ
2. **AI Contribution ラベル** (`ai_contribution_labels`): セッション内で AI が PR 差分コードを生成・変更したか
3. **Release Level ラベル** (`release_level_labels`): `db/migrate/` 配下があれば最高 / 根幹機能 + 体感変化なら高 / 後方互換なら中 / 表示文言のみなら最低

`release-labels.md` が無ければ `bash scripts/setup.sh` をユーザーに促しラベル付与スキップ。マイルストーンは関連 Issue 由来、それ以外は `Untracked`（存在確認後、無ければ `--milestone` 省略）。

### Step 9: セルフチェック (投稿前必須)

`references/description-style.md` の「Step 9 セルフチェック」を実施。4 観点で 1 つでも該当があれば修正:
- **[A] 斜め読みテスト**: 各セクション 1 行目だけで PR 意図再構築可能か / 本質 2-3 点リストと一致か / plan 由来 internal 語彙 (`α 層` / `AC-9` / `Critical-A` 等) が残っていないか
- **[B] コードから読める情報の混入**: ファイル名・関数名・パラメータ追加・import 等が簡潔セクションに残っていないか
- **[C] 重複・冗長**: 「やったこと」と「なぜやるのか」の事実重複 / 簡潔セクションの bullet 化 / 動作確認結果のケース列挙 / 詳細セクションが 1〜2 行で済まされていないか
- **[D] AI 臭**: 「以下に〜を示す」「具体的には」「適切に」等の生成検出語 / 太字 bullet 3 つ以上 / 機械的絵文字 / 「〜のため」段落内 2 回以上 / 「特になし」埋め文

### Step 10: ドラフト PR 作成

`--body-file` を統一採用 (`--body "$(cat ...)"` 経路は使わない)。`$PR_BODY_FILE` は **`mktemp` でユニークパス生成 + コマンド完了後に削除** (`references/post-create-edit.md` の「固定パス禁止」参照)。固定パス `/tmp/pr-body.md` は過去セッション残骸混入事故源で禁止。

```bash
PR_BODY_FILE="$(mktemp -t pr-body-XXXXXX.md)"
# (本文を $PR_BODY_FILE に書き出した後)
gh pr create --draft \
  --title "feat(order): 注文確定後の通知機能を追加" \
  --body-file "$PR_BODY_FILE" \
  --label "1.Feature development,ai-contribution-level:2,ReleaseLevel-2" \
  --milestone "Untracked" \
  --base develop
rm -f "$PR_BODY_FILE"
```

## Advanced features

- **PR テンプレート 7 段階優先順位 / ベースブランチ 3 段階フォールバック**: `references/template-discovery.md`
- **ブランチ妥当性検証 (同名禁止 / conventional prefix / プロジェクト規約) と自動切替**: `references/branch-validation.md`
- **文体 6 鉄則 / セクション分量対比表 / Pre-work 本質リスト / Step 9 セルフチェック [A]-[D]**: `references/description-style.md`
- **ラベル 3 種判定基準 / Untracked マイルストーン事前確認**: `references/labels-and-milestones.md`
- **作成後の description 更新 (`gh pr edit --body` 失敗回避) / `mktemp` 規約**: `references/post-create-edit.md`

## 注意事項

全内容を日本語で記述 / 既存コミット全てを考慮（最新だけでない）/ セキュリティ・パフォーマンス影響を考慮 / 完了時に PR URL を表示。

## 併用推奨 skill

- `/polish-before-commit` — コミット前にプロジェクト規約・パターン一貫性を仕上げてから本 skill を起動
- `/finalize-plan` — プランを実装可能形式に変換し、その流れで本 skill を呼ぶ
