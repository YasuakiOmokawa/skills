---
name: create-pr
description: Use to create or update a Conventional-Commits PR from the current branch; draft by default, ready only when explicitly requested.
---

カレントブランチの Conventional Commits PR を作成または更新する。ユーザー確認は行わない。新規 PR は既定 `--draft` で、ready 明示時だけ外す。既存 PR は状態を保持し、ready 明示時だけ draft から昇格する。

## Task complexity tier

| Tier | 判定 | 投稿前セルフチェック | その他 |
|---|---|---|---|
| **lite** | 1 production file の局所変更、single domain、既存 pattern 踏襲、非自明な設計判断なし | 斜め読み・本質回収 / 私語彙・生成痕跡 | 周辺コード比較を省略可 |
| **standard** (default) | single domain の multi-file / multi-commit 変更、または非自明な設計判断あり | 斜め読み・本質回収 / コードから読める情報 / 分量・重複・事実整合 / 私語彙・生成痕跡 | 全工程を実行 |
| **deep** | multi-domain / breaking change / migration | standard の4観点 + 関連 PR 検索 + ヒットした既存 issue のリンク | plan / 設計議論を全て確認 |

リスク領域 (auth / billing / payment / migration / security config) は常に deep。deep 条件を先に判定し、lite は全条件を満たす場合だけ、残りは standard とする。draft/ready は tier に依存しない。

**deep tier の追加規約**:
- **BREAKING CHANGE footer 位置**: 実際に breaking change がある場合だけ生成し、deep 判定だけでは生成しない。PR テンプレに専用 footer 見出しがあればそこ。無ければ本文末尾の独立 footer として `BREAKING CHANGE: <description>` を「Revert 手順」見出しの**直前**に配置 (Conventional Commits の footer 慣例。`## やらなかったこと` の直後・本文セクション群の外側)。テンプレ内の `<!-- ... -->` コメントは削除しない。

## Arguments

- `$ARGUMENTS`: `[base-branch] [詳細展開指示...]`（いずれも省略可）
  - 先頭トークンがリモートブランチとして存在すればベースブランチ（確認: `git ls-remote --heads origin <トークン>`。省略時はリポジトリのデフォルトブランチ）
  - 残り（または全体）は**詳細展開指示**として解釈する（例: `/create-pr develop 設計判断は詳しく`）。詳細展開指示はセッション中のユーザー発話でも受け付ける（Step 6 参照）
  - draft/ready 指定（例: 「ready for review で」「出荷用」）も詳細展開指示と同様、`$ARGUMENTS` またはセッション中の発話で自然文として受け付ける（Step 10 参照。既定は draft）

## 会話履歴を持たない委譲実行

**委譲実行では、まず [references/delegated-execution.md](references/delegated-execution.md) を読み**、情報源・AI Contribution・複雑なブランチ状態・`gh` 失敗時の読み替えを適用する。

## Quick start

最短経路:
1. **Step 0**: PR テンプレートを動的検索 ([references/template-discovery.md](references/template-discovery.md)) → ベースブランチ確定
2. **Step 1**: `git status -sb`、`git log --oneline -15`、`git log [base-branch]..HEAD --oneline`、`git diff [base-branch]...HEAD --stat` を実行する。ローカルに base ref がなければ fetch 後に `origin/[base-branch]` で比較する
3. **Step 1.5**: current branch に対して `gh pr list --head <branch> --state open --json number,url,isDraft` を read-only 実行して結果を cache してから、[references/branch-validation.md](references/branch-validation.md) で妥当性と必要なら新ブランチ名を決める。open PR があれば全 tier で切り替えず更新経路を保つ。0件なら deep はまだ切り替えず、他 tier はここで切り替える。query 失敗時は branch切替・commit・push前に停止する
4. **Step 4-5**: 現行 commit と task-related worktree diff からコンテキスト・タイトルを確定する
5. **deep preflight**: Step 9 の既存 PR/issue 検索を read-only で実行する。重複 PR または検索失敗なら branch 切替・commit・push 前に停止する。継続時は結果を保持し、必要なら Step 1.5 の新ブランチへ切り替える
6. **Step 2**: 未コミットのうち本タスク関連ファイルだけを意味的に一貫した単位で `<type>(<scope>): <日本語要約>` 形式コミット
7. **Step 3**: `git push -u origin <branch>`
8. **Step 6-8**: 本文 / ラベル生成
9. **Step 9 (必須)**: [references/description-style.md](references/description-style.md) のセルフチェックを tier 表の観点セットで実施。deep の検索結果は preflight を再利用し再検索しない
10. **Step 10**: 対象ブランチに open PR が無ければ `gh pr create` (既定 `--draft`)、既に open PR があれば `gh pr create` はスキップし push 後 `gh pr edit --body-file` で本文更新 (コマンド全文と draft/ready 判定は下記 Workflows Step 10)

## Workflows

### Step 4: コンテキスト収集

- **4a**: 不足あれば `git diff [base-branch]...HEAD`、`git diff`、`git diff --cached` から task-related な committed / unstaged / staged 内容を詳細確認
- **4b**: 周辺コードと既存パターン比較。差異あれば理由・却下した代替案を整理
- **4c**: 本セッションの plan / 設計議論から「背景 / 設計判断 / やらなかったこと」を抽出 (`~/.claude/plans/` ファイル走査は不要)

### Step 5: タイトル生成

`<type>(<scope>): <description>` (72 文字以内・日本語)。
- **type**: feat / fix / docs / style / refactor / perf / test / chore / ci / build
- **複数 type 混在**: 最も大きな価値変化を生む 1 つを採用。優先順位 `feat` > `fix` > `refactor` > `perf` > `test` > `chore` > `docs` > `style` > `ci` > `build`
- **scope**: 変更主ドメインの単数形英小文字 (モデル / コントローラ prefix 流用が基本)。複数ドメインなら中心価値の 1 つ、均等で絞れなければ省略。docs / chore / ci でドメイン無しなら省略
- **タイトル prefix**: 呼び出し側が prefix (例: `[DONOTMERGE]`) を明示指定した場合、`<type>(...)` の直前に半角スペース区切りで付与する。72 文字カウントは prefix 込みで数える

### Step 6: 本文生成

検出した PR テンプレートに従う。lite は下記で完結してよい。standard / deep は [references/description-style.md](references/description-style.md) を Read する。

- **本質の回収**: 読者に必要な成果と運用事実を本文から全て回収可能にする。本質列挙系セクションがあれば番号リスト、無ければ既存セクションへ分配する
- **6 文体鉄則**: コードから読めることは書かない / 斜め読み構造 / 重複禁止 / 常体 / 書かない勇気 / 読み直し
- **セクション分量 (既定 = 1 行サマリー)**:
  - 定型 (Revert 手順 / チェックリスト) → テンプレ準拠
  - それ以外の全セクション → **1 行サマリーのみ** (bullet・複数文段落・表・コードブロックを書かない。該当事実がなければ見出し+空行)。行数の例外は本質列挙系セクションの番号リストと「やらなかったこと」の 1 項目 1 行のみ
  - **詳細展開はユーザーが明示指示したセクションだけ** (`$ARGUMENTS` またはセッション中の発話。例: 「設計判断は詳しく」)。指示されたセクションはサマリー行の直下に散文展開を追加する。棄却案・実測表などの素材が session にあっても、自己判断では展開せず完了報告で「展開可能」と伝える。指示対象の見出しがテンプレートに無ければ新設せず、[references/description-style.md](references/description-style.md) の Content ownership で対応する既存セクションへ要約し、対応先も無ければ本文へ入れず完了報告で提示する
- **本文冒頭の注記**: 呼び出し側が本文冒頭の注記 (例: merge しない参照用) を明示指定した場合、テンプレ本文の最初の見出しより前に独立した 1 行として挿入する (新規見出しは追加しない)
- **テンプレ内 `<!-- ... -->` コメントは削除しない** (migration 無しでも rollback サンプルブロックを残す)
- **テンプレに無い見出しは追加しない**

### Step 7-8: ラベル・マイルストーン

新規 PR にだけ適用する。既存 PR の title / labels / milestone は保持し、本文だけを更新する。詳細は [references/labels-and-milestones.md](references/labels-and-milestones.md) を参照。`~/.claude/skills-config/release-labels.md` を Read し以下 3 種を 1 つずつ選択:

1. **Productivity ラベル** (`productivity_labels`)
2. **AI Contribution ラベル** (`ai_contribution_labels`): セッション内で AI が PR 差分コードを生成・変更したか
3. **Release Level ラベル** (`release_level_labels`): `db/migrate/` 配下があれば最高 / 根幹機能 + 体感変化なら高 / 後方互換なら中 / 表示文言のみなら最低

`release-labels.md` が無ければラベル付与をスキップし、設定方法を案内する (リポジトリ root の `scripts/setup.sh` 実行、または `~/.claude/skills-config/release-labels.md` を手動作成。サンプルは `examples/skills-config/`。npx skills add 経由では plugin 内に `scripts/` が無いため裸の相対パス案内をしない)。マイルストーンは関連 Issue 由来、それ以外は `Untracked` (存在確認は `gh api repos/{owner}/{repo}/milestones --paginate --jq '.[].title'` で行う。`per_page=100` でも 100 件超リポジトリでは漏れるため `--paginate` 必須。無ければ `--milestone` 省略)。

### Step 9: セルフチェック (投稿前必須)

[references/description-style.md](references/description-style.md) の同名4観点を tier 表どおりに実施する。deep の関連検索だけは Quick start の preflight として Step 5 の直後・branch切替/commit/push前に行い、ここでは保存結果を再利用する。検索は `gh search issues --repo <owner/repo> --include-prs --match title --limit 20 "<query>"` だけを使い、query は (1) タイトルの scope token (存在時)、(2) `<description>` 全体、の最大2個とする。語の抽出・言い換え・追加検索はしない。返却された最大40件だけを順に diff / plan と照合し、次の precedence で一度だけ分岐する。

1. 現在の head に紐づく Step 10 の既存 PR を除き、同じ変更を実装する verified open PR が1件でもあれば重複として停止する。PR URL と一致根拠を報告し、branch切替・commit・push・issue link 化・`gh pr create` / `gh pr edit` は行わない。
2. 重複 PR がなく verified issue があれば、検索順で最初の1件を [references/description-style.md](references/description-style.md) の canonical related line に置く。
3. verified hit がなければ追加検索せず、related line なしで続行する。

検索失敗は no-hit とみなさず、失敗を報告して同じ preflight 位置で停止する。現在の head の既存 PR URL は Step 1.5 の read-only query で識別し、query 対象の branch 名と組で保持する。deferred branch switch が無ければ Step 10 で再利用し、切り替えた場合は新 branch に対して Step 10 で再取得する。

### Step 10: PR 作成 (新規 / 既存更新)

**既存 PR の確認**: deep preflight の cached query が現在の branch と一致すれば再利用し、それ以外は `gh pr list --head <branch> --state open --json number,url,isDraft` を実行する。1件なら create をスキップし、push 後に本文だけを更新する。ready 指定かつ draft なら `gh pr ready <number>` を実行し、それ以外は既存 draft/ready 状態と metadata を保持する。0件なら新規作成する。完了報告には PR URL を含める。

**draft / ready の判定**: 既定は `--draft`。呼び出し側が「ready for review」「出荷用」等を明示指定した場合のみ `--draft` を付けずに作成する。

下記コマンド例の `--label` は 3 種のプレースホルダで、実値は Step 7-8 で Read した `~/.claude/skills-config/release-labels.md` の該当リストから選んだラベル名に置き換える。

`--body-file` を統一採用 (`--body "$(cat ...)"` 経路は使わない)。`$PR_BODY_FILE` は **`mktemp` でユニークパス生成 + コマンド完了後に削除** ([references/post-create-edit.md](references/post-create-edit.md) の「固定パス禁止」参照)。固定パスは禁止。

```bash
PR_BODY_FILE="$(mktemp -t pr-body-XXXXXX.md)"
# (本文を $PR_BODY_FILE に書き出した後)
gh pr create --draft \
  --title "feat(order): 注文確定後の通知機能を追加" \
  --body-file "$PR_BODY_FILE" \
  --label "<productivity-label>,<ai-contribution-label>,<release-level-label>" \
  --milestone "Untracked" \
  --base develop
rm -f "$PR_BODY_FILE"
```

ready 指定時は上記コマンドから `--draft` を省く。既存 PR を更新する場合は `gh pr create` の代わりに `gh pr edit <number> --body-file "$PR_BODY_FILE"` を使う。

## 注意事項

全内容を日本語で記述し、既存コミット全てを考慮する。完了時に PR URL と、詳細展開できる素材が残るセクションを列挙する。展開依頼後は [references/post-create-edit.md](references/post-create-edit.md) で更新する。

## Gotchas

- **積み PR (open PR を持つ前段ブランチから派生したブランチ) の base**: base をデフォルトブランチでなく前段ブランチにすると diff が自タスク分に絞れる。ただし前段 merge 後の base 自動付け替え確認・close 時の reopen・squash merge 時の rebase が必要 (詳細は [references/stacked-pr-base.md](references/stacked-pr-base.md))
