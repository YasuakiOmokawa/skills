---
name: apply-findings
description: Use after the user runs the built-in /code-review in the same session, when finalizing a branch before commit or /create-pr, when reviewing a PR without editing files (review-only mode), or when the user says 「指摘を適用して」「仕上げて」「コミット前チェック」「レビューのみで見て」. Collects findings from the preceding /code-review run (never invokes /code-review itself), plus deviations from codebase conventions (explicit CLAUDE.md/rules, majority patterns) and lint violations; auto-applies the mechanically safe ones with lint+tests as the guard, and presents judgment calls in one list before stopping.
---

# apply-findings

機械的に安全な finding だけ自動適用し、判断を要する finding は編集せず一覧提示して止まる。

## 対象 (skill 読み込み時に自動取得)

!`git branch --show-current`

!`git diff --name-only origin/${BASE_BRANCH:-main}...HEAD`

!`git diff --name-only HEAD`

!`git diff --name-only --cached`

> 失敗時: (a) 生コマンド文字列のまま見える → Bash で同コマンドを実行。(b) `unknown revision` 等 → ① `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name` ② `git symbolic-ref refs/remotes/origin/HEAD --short | sed 's@^origin/@@'` ③ `main` の順で `BASE_BRANCH` を確定し再実行。未コミット+staged が非 0 件ならブランチ全体 diff を使わないため base 解決はスキップしてよい。

スコープ: `$ARGUMENTS` があればそのファイル。なければ未コミット+staged (0 件ならブランチ全体)。それも 0 件なら終了。

## PR モード

PR URL / 番号が渡された、またはカレントブランチが対象 PR の head でない場合: `gh pr checkout <番号>` か read-only worktree で PR head を展開し (gh 不可時はローカル head ブランチから `git worktree add <path> <head-branch>`)、base を読み替えて分析する。worktree は分析後 `git worktree remove` で撤収し 1 行報告する。報告のパスは元リポジトリ基準・行番号は PR head 基準。事前 /code-review の指摘の根拠行が PR head と一致しない場合は指摘内容を成立させるコード式の実在行へ補正して採用し、`PR head 基準 :N (指摘時 :M)` で併記する。他者の PR は review-only を既定にする。

## review-only モード

「ファイル変更しない」「レビューのみ」の指示がある場合、他者の PR を点検する場合、または subagent 実行で `git log -1 --format='%an'` と `git config user.name` が不一致の場合 (いずれか 1 条件の成立で発火 — 他条件の不成立は打ち消さない): 編集ゼロ (= 対象リポジトリの追跡ファイルを変更しない。分析用 worktree・一時ディレクトリの作成は可)。lint は autocorrect / `--fix` を外して検出のみ実行する。自動適用可の finding も提案として一覧に含め、集約見出しは `### ⚠️ 指摘一覧 (review-only — 未適用)` に読み替えて各項目に「通常なら自動適用 / 判断系」を付記する。終了文言は「レビュー点検完了。指摘一覧を確認してください」。

## Findings の情報源 (4)

1. **直前の /code-review 実行結果** (会話内)。無ければ main thread で同等のレビュー (変更 diff のバグ・規約違反) を直接行い `(fallback)` と明示する。本 skill から /code-review を起動しない (disable-model-invocation により Skill ツール起動が失敗する)
2. **明文規約からの逸脱** — リポジトリ内 `CLAUDE.md` / `.claude/rules/*.md` とグローバル `~/.claude/CLAUDE.md` / `~/.claude/rules/*.md` を収集し diff と照合する。収集規約にコメント原則節があればコメントも照合対象 (comment-writing メタ規約 (例: `code-comments.md`) は先行パス `/express-intent-in-code` の管轄のため発火根拠にしない)。ツール実行を命じる規約 (「編集後に rubocop 実行」「テストは rspec で実行」等) は情報源 4 と「適用後の検証」の可否判定に従い、逸脱としては立てない
3. **パターン逸脱** — 統一先の優先順 (上から、一致したら止める): ① 明文規約の明示指定 ② 同一ファイル内の多数派 (2/3 以上。混在している場合のみ — 100% 一貫したファイルは ③ へ) ③ 同一ディレクトリの多数派 (5 割超) ④ 決まらない (同数 / 出現 1 件) → 判断系へ ⑤ 同種ファイル 0 件 → 違反なし (③-⑤ の母数は対象ファイル自身を除く)。観点カタログ: [references/pattern-consistency.md](references/pattern-consistency.md)。1 件修正したら同種違反を変更ファイル群に `grep` して同時修正する
4. **lint** — プロジェクトが lint を設定として採用している場合のみ実行する (Ruby: `Gemfile` + `.rubocop.yml`、TS・JS: eslint 設定、Python: `pyproject.toml` / `ruff.toml`)。コマンド: Ruby `bundle exec rubocop ${files} --autocorrect-all` / TS・JS `yarn eslint ${files} --fix` / Python `ruff check --fix ${files}`。設定が無ければ PATH 上の同名ツールへフォールバックせず「lint 未設定 — 手動確認要」と報告する (グローバル既定ルールは明文規約でも多数派パターンでもないため統一先にならない)。他言語は `Makefile` / `package.json` 等から lint タスクを探索し、なければ手動確認要と報告。最大 3 回試行、未解決なら手動対応として報告

## 適用 / 判断の振り分け

- **自動適用**: lint autocorrect (変更差分の行に限る — 差分外の既存行を書き換える修正・ファイル内多数派スタイルと衝突する修正は適用せず報告に回す) / 明文規約・多数派パターンへの機械的統一 / dead code 削除 (対象は private / protected かつ `send` 等の動的呼び出しが grep で 0 件のもの — public は判断系へ。削除で意味を失う付随構文 — 空になった `private` 宣言・未使用 require 等 — も同一適用に含める) / 全 identifier が削除済みの dead mock (Ruby/RSpec — impl 側の `delegate :X` / `def X` 撤去がある場合のみ。手順: [references/dead-mock-removal.md](references/dead-mock-removal.md)) / その他、単一ファイル局所で挙動不変をテストで検証できるもの
- **判断系 (編集しない)**: 設計判断 (責務分離・分割・切り出し) / メソッド名・引数・戻り値変更の影響範囲 / バリデーション・認可等のビジネスロジック / dead mock の部分削除 (書換え候補を併記) / 統一先が決まらないパターン逸脱 / 直近ブランチで追加された参照 0 件の dead file (`__mocks__/**`・`spike*`・`scratch*` prefix) / diff で追加された呼び出し元 0 件の public メソッド・クラス (テストからの参照も呼び出し元に数える。未接続か dead かコードから判別不能のため自動削除しない)
- 迷ったら判断系 (安全側)
- **適用後の検証**: lint + 編集対象のテストを実行 (lint は情報源 4 の可否判定に従う — 未設定なら「lint 未設定 — 手動確認要」の 1 行をもって検証結果とする)。テストランナーは `Gemfile` / `package.json` / `Makefile` / test ディレクトリ構成から特定し、特定できない・対象テストが無い場合は「テスト未検証」と明示する。fail は revert して判断系へ降格する。自動適用 0 件なら検証は省略してよい (実行した場合のみ結果を報告)

## 実行順

規約収集 → スコープ確定 → パターン逸脱の検出・適用 → lint → dead mock → /code-review findings の取り込み・適用 → 集約提示。逆順の再評価ループはしない。skip (= 工程を実行しなかった場合) と、実行して検出 0 件だった工程は、いずれも最終出力に 1 行で明示する (silent skip 禁止)。

## 集約提示 (最終出力)

判断系 finding を `### ⚠️ ユーザー判断が必要な項目` に集約する: 各項目 severity + `/abs/path:line` + 要約 + 出所 (/code-review / 規約 / パターン / 外部診断ツール) + 推奨対応。severity は行頭に `[critical]` / `[major]` / `[minor]` で付け、critical → major → minor の順に並べる — **critical** (must fix: 放置するとバグ・データ破壊・セキュリティ / 認可の欠陥として顕在化する) / **major** (imo: 設計・保守性の改善提案 — 対応を推奨するが代替判断も成立する) / **minor** (nits: 命名・スタイル等、挙動に影響しない微修正)。tier に迷ったら上位側に倒す。同一箇所・同一の判断を指す指摘は出所を併記して 1 件に統合する (統合は推奨対応が同一になる場合に限る — 同一箇所でも取るべきアクションが異なれば別項目)。本 skill 実行前に会話内で共有された外部診断ツール (react-doctor 等) の未修正指摘も集約に含める。自動適用分も `/abs/path` + 適用内容 + 出所 の 1 行で列挙する (未コミット行の削除は diff に痕跡が残らず、レポートが唯一の記録になるため)。点検不能の工程報告 (lint 未設定・テスト未検証等) は判断項目に数えない。

- 0 件: 「判断項目なし。コミット可能な状態」と報告して終了する (質問しない)
- 1 件以上: 一覧を提示して停止し、ユーザーの指示を待つ
- 自発的に commit / `git add` / `/create-pr` を実行・提案しない (フロー開始時点で指示済みの場合はそれに従う)

## Gotchas（観測済みの罠 — 実測で判明したものを 1 件 1 行で追記）

- URL 生成・リダイレクト・route helper に触れる diff は、フレームワークの暗黙リクエスト文脈自動付与 (Rails `default_url_options` 等) による結合契約破壊を追加点検する (静的レビューで取りこぼしやすく、実機操作で発覚した実測あり)

## 併用推奨 skill

- 組み込み /code-review — 本 skill の直前にユーザーが起動する最終レビュー (本 skill からは起動しない)
