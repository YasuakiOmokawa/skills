---
name: create-pr
description: Creates a Conventional-Commits draft PR from the current branch with generated title, body, labels, and milestone, without confirmation. Use when the user says "PR を作って" / "draft PR" / "PR 作成して", optionally with `[base-branch]` argument.
disallowed-tools: AskUserQuestion
---

# create-pr

カレントブランチから Conventional Commits 形式のドラフト PR を作成する。**ユーザー確認は一切行わず、分析完了後は直接 PR 作成を実行** (frontmatter の `disallowed-tools: AskUserQuestion` で構造的にも強制)。常に `--draft` (ready-PR path なし)、positional argument は `[base-branch]` のみ。

## 現在の git 状態 (skill 読み込み時に自動取得)

!`git status -sb`

!`git log --oneline -15`

> 上 2 行は Claude Code が skill 読み込み時に実行し結果へ置換する (読み取り専用・冪等)。バッククォート付きの生コマンド文字列のまま見えている場合 (注入非対応環境) は、Step 1 で同コマンドを Bash 実行して取得する。

## Task complexity tier

| Tier | 判定 | Step 9 セルフチェック | その他 |
|---|---|---|---|
| **lite** | 1 commit, <50 LoC, single domain, 既存 pattern 踏襲 | [A] 斜め読み + [D] AI 臭 の 2 観点 | Step 4b (周辺コード比較) 省略可。Pre-work 本質リストは 1-2 点 |
| **standard** (default) | 2-5 commits, multi-file, single domain | [A] + [B] + [C] + [D] の 4 観点 (現状) | Step 1-10 を順次実行 |
| **deep** | multi-domain / breaking change / 6+ commits / migration | 4 観点 + 関連 PR 検索 + 既存 issue リンク | Step 4c で plan 全展開、Pre-work 本質リストを **最低 5 点・上限 7 点** に拡張 (5 に届かない場合は domain ごと / PR チェーン段階ごと / migration / observability / rollout / rollback の観点で分解して 5 点まで埋める) |

リスク領域 (auth / billing / payment / migration / security config) は LoC・commit 数によらず **deep**。lite でも `--draft` は維持 (ready PR path なし、現状維持)。**tier 判定の評価時点は Step 1 の `git log [base-branch]..HEAD` 時点** — Step 2 で未コミット分から作る commit は commit 数に数えない (数えると未コミット 1 ファイルの軽微変更が lite から外れてしまうため)。

**deep tier の追加規約**:
- **description-style.md との優先順位**: `references/description-style.md` の「本質リスト 5+ で PR スコープ広すぎ警告」は **standard tier の既定**。**deep tier では本 tier 表 (5-7) が優先**し、5-7 点は scope 過大の兆候ではなく分解の正常結果。standard で 5 点に達した PR は scope 過大の兆候、deep は正常運用と読み分ける。
- **BREAKING CHANGE footer 位置**: PR テンプレに専用 footer 見出しがあればそこ。無ければ本文末尾の独立 footer として `BREAKING CHANGE: <description>` を「Revert 手順」見出しの**直前**に配置 (Conventional Commits の footer 慣例。`## やらなかったこと` の直後・本文セクション群の外側)。テンプレ内の `<!-- ... -->` コメントは削除しない。

## Arguments

- `$ARGUMENTS`: ベースブランチ名（省略可、省略時はリポジトリのデフォルトブランチ）

## Quick start

最短経路:
1. **Step 0**: PR テンプレートを動的検索 ([references/template-discovery.md](references/template-discovery.md)) → ベースブランチ確定
2. **Step 1**: 冒頭の自動取得結果 (status -sb = ブランチ + 未コミット / log) を使い、base-branch 依存の `git log [base-branch]..HEAD --oneline` / `git diff [base-branch]...HEAD --stat` のみ実行 (自動取得が生コマンド文字列のままなら `git status -sb` / `git log --oneline -15` も Bash 実行)
3. **Step 1.5**: ブランチ妥当性検証 ([references/branch-validation.md](references/branch-validation.md))。違反なら **コミット前** に `git switch -c` で新ブランチ切替 (コミット後 rename は GitHub API 副作用で PR が CLOSED されるため不可)
4. **Step 2**: 未コミットファイルがあれば 1 コミット = 1〜3 ファイル粒度で `<type>(<scope>): <日本語要約>` 形式コミット
5. **Step 3**: `git push -u origin <branch>`
6. **Step 4-8**: タイトル / 本文 / ラベル生成 (後述)
7. **Step 9 (必須)**: [references/description-style.md](references/description-style.md) のセルフチェックを **tier 表の観点セット** (lite = [A]+[D] / standard = [A]-[D] 4 観点 / deep = 4 観点 + 関連 PR 検索) で必ず実施 (tier が指定する観点の省略禁止)
8. **Step 10**: `gh pr create --draft --title ... --body-file ... --label ... --milestone ... --base [base-branch]`

PR URL を表示して完了。

## Workflows

### Step 4: コンテキスト収集

- **4a**: 不足あれば `git diff [base-branch]...HEAD` で詳細確認
- **4b**: 周辺コードと既存パターン比較。差異あれば理由・却下した代替案を整理
- **4c**: 本セッションの plan / 設計議論から「背景 / 設計判断 / やらなかったこと」を抽出 (`~/.claude/plans/` ファイル走査は不要)

### Step 5: タイトル生成

`<type>(<scope>): <description>` (72 文字以内・日本語)。
- **type**: feat / fix / docs / style / refactor / perf / test / chore / ci / build
- **複数 type 混在**: 最も大きな価値変化を生む 1 つを採用。優先順位 `feat` > `fix` > `refactor` > `perf` > `test` > `chore` > `docs` > `style` > `ci` > `build`
- **scope**: 変更主ドメインの単数形英小文字 (モデル / コントローラ prefix 流用が基本)。複数ドメインなら中心価値の 1 つ、均等で絞れなければ省略。docs / chore / ci でドメイン無しなら省略

### Step 6: 本文生成

検出した PR テンプレートのセクション構成に従う。下記の要点で書ける lite-tier は inline 完結でよい。**standard / deep tier、または初めて本 skill を使う場合は [references/description-style.md](references/description-style.md) を Read**（NG/OK 例対比・Pre-work の具体手順・セクション分量対比表が必要になるため）。要点:

- **Pre-work (mandatory)**: 本文を書く前に PR の本質を **bullet リスト** (standard 既定 2-3 点 / deep 5-7 点、tier 表が SSOT) として scratch 出力 → 「このPRでやること」 (または「やったこと」を格上げ) に貼る
- **6 文体鉄則**: コードから読めることは書かない / 斜め読み構造 / 重複禁止 / 常体 / 書かない勇気 / 読み直し
- **セクション分量**:
  - 簡潔 (やったこと / なぜやるのか / 動作確認結果 / レビューしてほしい観点) → 全 1 行・bullet なし
  - 詳細 (設計判断 / やらなかったこと) → コードから読めない情報を散文で詳細展開 (該当事実なければ見出し+空行のみ)
  - 定型 (Revert 手順 / チェックリスト) → テンプレ準拠
- **テンプレ内 `<!-- ... -->` コメントは削除しない** (migration 無しでも rollback サンプルブロックを残す)
- **テンプレに無い見出しは追加しない**

### Step 7-8: ラベル・マイルストーン

詳細は [references/labels-and-milestones.md](references/labels-and-milestones.md) を参照。`~/.claude/skills-config/release-labels.md` を Read し以下 3 種を 1 つずつ選択:

1. **Productivity ラベル** (`productivity_labels`)
2. **AI Contribution ラベル** (`ai_contribution_labels`): セッション内で AI が PR 差分コードを生成・変更したか
3. **Release Level ラベル** (`release_level_labels`): `db/migrate/` 配下があれば最高 / 根幹機能 + 体感変化なら高 / 後方互換なら中 / 表示文言のみなら最低

`release-labels.md` が無ければラベル付与をスキップし、設定方法を案内する (リポジトリ root の `scripts/setup.sh` 実行、または `~/.claude/skills-config/release-labels.md` を手動作成。サンプルは `examples/skills-config/`。npx skills add 経由では plugin 内に `scripts/` が無いため裸の相対パス案内をしない)。マイルストーンは関連 Issue 由来、それ以外は `Untracked` (存在確認は `gh api repos/{owner}/{repo}/milestones --paginate --jq '.[].title'` で行う。`per_page=100` でも 100 件超リポジトリでは漏れるため `--paginate` 必須。無ければ `--milestone` 省略)。

### Step 9: セルフチェック (投稿前必須)

[references/description-style.md](references/description-style.md) の「Step 9 セルフチェック」を **tier 表の観点セット** (lite = [A]+[D] のみ / standard = 4 観点 / deep = 4 観点 + 関連 PR 検索) で実施。1 つでも該当があれば修正:
- **[A] 斜め読みテスト**: 各セクション 1 行目だけで PR 意図再構築可能か / 本質リスト (tier 依存: standard 2-3 点 / deep 5-7 点) と一致か / plan 由来 internal 語彙 (`α 層` / `AC-9` / `Critical-A` 等) が残っていないか
- **[B] コードから読める情報の混入**: ファイル名・関数名・パラメータ追加・import 等が簡潔セクションに残っていないか
- **[C] 重複・冗長**: 「やったこと」と「なぜやるのか」の事実重複 / 簡潔セクションの bullet 化 / 動作確認結果のケース列挙 / 詳細セクションが 1〜2 行で済まされていないか
- **[D] AI 臭**: 「以下に〜を示す」「具体的には」「適切に」等の生成検出語 / 太字 bullet 3 つ以上 / 機械的絵文字 / 「〜のため」段落内 2 回以上 / 「特になし」埋め文 / 矢印チェーン等の作業中 shorthand (詳細は description-style.md [D])

### Step 10: ドラフト PR 作成

`--body-file` を統一採用 (`--body "$(cat ...)"` 経路は使わない)。`$PR_BODY_FILE` は **`mktemp` でユニークパス生成 + コマンド完了後に削除** ([references/post-create-edit.md](references/post-create-edit.md) の「固定パス禁止」参照)。固定パス `/tmp/pr-body.md` は過去セッション残骸混入事故源で禁止。

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

## Advanced

- [references/template-discovery.md](references/template-discovery.md) — PR テンプレート 7 段階優先順位 / ベースブランチ 3 段階フォールバック
- [references/branch-validation.md](references/branch-validation.md) — ブランチ妥当性検証 (同名禁止 / conventional prefix / プロジェクト規約) と自動切替
- [references/description-style.md](references/description-style.md) — 文体 6 鉄則 / セクション分量対比表 / Pre-work 本質リスト / Step 9 セルフチェック [A]-[D]
- [references/labels-and-milestones.md](references/labels-and-milestones.md) — ラベル 3 種判定基準 / Untracked マイルストーン事前確認
- [references/post-create-edit.md](references/post-create-edit.md) — 作成後の description 更新 (`gh pr edit --body` 失敗回避) / `mktemp` 規約

## 注意事項

全内容を日本語で記述 / 既存コミット全てを考慮 (最新だけでない) / セキュリティ・パフォーマンス影響を考慮 / 完了時に PR URL を表示。

## 併用推奨 skill

- `/polish-before-commit` — コミット前にプロジェクト規約・パターン一貫性を仕上げてから本 skill を起動
- `/finalize-plan` — プランを実装可能形式に変換し、その流れで本 skill を呼ぶ
- `/purge-private-vocab` — PR description 生成後に plan 内造語を点検
