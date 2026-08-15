---
name: create-pr
description: Use to create or update a Conventional-Commits PR from the current branch; draft by default, ready only when explicitly requested.
---

カレントブランチの Conventional Commits PR を作成または更新する。ユーザー確認は行わない。新規 PR は既定 `--draft` で、ready 明示時だけ外す。既存 PR は状態を保持し、ready 明示時だけ draft から昇格する。

## Task complexity tier

| Tier | 判定 | Step 9 セルフチェック | その他 |
|---|---|---|---|
| **lite** | 1 commit, <50 LoC, single domain, 既存 pattern 踏襲 | [A] 斜め読み + [D] AI 臭 の 2 観点 | Step 4b (周辺コード比較) 省略可。Pre-work 本質リストは 1-2 点 |
| **standard** (default) | 2-5 commits, multi-file, single domain | [A] + [B] + [C] + [D] の 4 観点 (現状) | Step 1-10 を順次実行。Pre-work 本質リストは 2-3 点 |
| **deep** | multi-domain / breaking change / 6+ commits / migration | 4 観点 + 関連 PR 検索 + 既存 issue リンク | Step 4c で plan 全展開。Pre-work は重要事実を漏れなく列挙 |

リスク領域 (auth / billing / payment / migration / security config) は常に deep。draft/ready は tier に依存しない。tier の commit 数は Step 1 の `git log [base-branch]..HEAD` で数え、Step 2 の commit は含めない。

**deep tier の追加規約**:
- **BREAKING CHANGE footer 位置**: PR テンプレに専用 footer 見出しがあればそこ。無ければ本文末尾の独立 footer として `BREAKING CHANGE: <description>` を「Revert 手順」見出しの**直前**に配置 (Conventional Commits の footer 慣例。`## やらなかったこと` の直後・本文セクション群の外側)。テンプレ内の `<!-- ... -->` コメントは削除しない。

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
3. **Step 1.5**: ブランチ妥当性検証 ([references/branch-validation.md](references/branch-validation.md))。違反なら **コミット前** に `git switch -c` で新ブランチ切替 (コミット後 rename は GitHub API 副作用で PR が CLOSED されるため不可)
4. **Step 2**: 未コミットのうち本タスク関連ファイルだけを意味的に一貫した単位で `<type>(<scope>): <日本語要約>` 形式コミット
5. **Step 3**: `git push -u origin <branch>`
6. **Step 4-8**: タイトル / 本文 / ラベル生成 (後述)
7. **Step 9 (必須)**: [references/description-style.md](references/description-style.md) のセルフチェックを **tier 表の観点セット**で必ず実施 (tier が指定する観点の省略禁止。観点セットと deep の関連 PR 検索は下記 Workflows Step 9)
8. **Step 10**: 対象ブランチに open PR が無ければ `gh pr create` (既定 `--draft`)、既に open PR があれば `gh pr create` はスキップし push 後 `gh pr edit --body-file` で本文更新 (コマンド全文と draft/ready 判定は下記 Workflows Step 10)

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
- **タイトル prefix**: 呼び出し側が prefix (例: `[DONOTMERGE]`) を明示指定した場合、`<type>(...)` の直前に半角スペース区切りで付与する。72 文字カウントは prefix 込みで数える

### Step 6: 本文生成

検出した PR テンプレートに従う。lite は下記で完結してよい。standard / deep は [references/description-style.md](references/description-style.md) を Read する。

- **Pre-work (mandatory)**: 本文を書く前に PR の本質を **bullet リスト** (点数は tier 表が SSOT) として scratch 出力 → 「このPRでやること」型の本質列挙系セクションがあればそこへ番号リストで貼る。**無ければ tier によらず「やったこと」1 文に畳み込む** (番号リスト格上げは本質列挙系セクション実在時のみ。分岐の詳細は description-style.md「Pre-work」節が SSOT)
- **6 文体鉄則**: コードから読めることは書かない / 斜め読み構造 / 重複禁止 / 常体 / 書かない勇気 / 読み直し
- **セクション分量 (既定 = 1 行サマリー)**:
  - 定型 (Revert 手順 / チェックリスト) → テンプレ準拠
  - それ以外の全セクション → **1 行サマリーのみ** (bullet・複数文段落・表・コードブロックを書かない。該当事実がなければ見出し+空行)。行数の例外は本質列挙系セクションの番号リストと「やらなかったこと」の 1 項目 1 行のみ
  - **詳細展開はユーザーが明示指示したセクションだけ** (`$ARGUMENTS` またはセッション中の発話。例: 「設計判断は詳しく」)。指示されたセクションはサマリー行の直下に散文展開を追加する。棄却案・実測表などの素材が session にあっても、**自己判断では展開せず**完了報告で「展開可能」と伝える (詳細は description-style.md「分量の既定」節)。**指示対象のセクションが解決済みテンプレート (フォールバック構成含む) の見出し集合に無い場合**は新規見出しを追加せず、[references/description-style.md](references/description-style.md)「テンプレートに無い見出しに相当する議論の反映先」節の手順 (代替見出しへの要約、それも無ければ本文非反映 + 完了報告での提示) に従う
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

[references/description-style.md](references/description-style.md) の Step 9 を tier 表の観点セットで実施する。deep は scope とタイトル語で関連 PR/issue を検索し、十分な結果が得られたら止める。ヒット時は「関連 Issue」の `related -` をリンクで置換する。

### Step 10: PR 作成 (新規 / 既存更新)

**既存 PR の確認**: `gh pr list --head <branch> --state open --json number,url,isDraft` を実行する。1件なら create をスキップし、push 後に本文だけを更新する。ready 指定かつ draft なら `gh pr ready <number>` を実行し、それ以外は既存 draft/ready 状態と metadata を保持する。0件なら新規作成する。完了報告には PR URL を含める。

**draft / ready の判定**: 既定は `--draft`。呼び出し側が「ready for review」「出荷用」等を明示指定した場合のみ `--draft` を付けずに作成する。

下記コマンド例の `--label` は 3 種のプレースホルダで、実値は Step 7-8 で Read した `~/.claude/skills-config/release-labels.md` の該当リストから選んだラベル名に置き換える。

`--body-file` を統一採用 (`--body "$(cat ...)"` 経路は使わない)。`$PR_BODY_FILE` は **`mktemp` でユニークパス生成 + コマンド完了後に削除** ([references/post-create-edit.md](references/post-create-edit.md) の「固定パス禁止」参照)。固定パス `/tmp/pr-body.md` は過去セッション残骸混入事故源で禁止。

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

## Gotchas（観測済みの罠 — 実測で判明したものを 1 件 1 行で追記）

- **積み PR (open PR を持つ前段ブランチから派生したブランチ) の base**: base をデフォルトブランチでなく前段ブランチにすると diff が自タスク分に絞れる。ただし前段 merge 後の base 自動付け替え確認・close 時の reopen・squash merge 時の rebase が必要 (詳細は [references/stacked-pr-base.md](references/stacked-pr-base.md))
