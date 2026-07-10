---
name: review-code-quality
description: Use when finishing self-review of an implementation, before requesting PR review, when a diff updates a domain model attribute (`plan_code` / `role` / `status` 等), or when the user says "コード品質をレビューして" / "品質レビュー". Analyzes the diff across cohesion, coupling, and readability (plus business-impact for domain-attribute changes), auto-applies only mechanically safe readability-axis critical/major fixes (cohesion/coupling/business-impact findings are always handed off), and routes design-judgment items to /polish-before-commit.
---

# Review Code Quality

**🔴 Critical / 🟠 Major のうち機械的に安全なものは自動適用 + 適用後に lint/test で検証する。設計判断を要するものは `/polish-before-commit` への申し送りに回す (連続スキル実行で提案が握りつぶされるのを防ぐため)。🟡 Minor 以下は提案のみ。** 振り分け基準・検証・申し送り contract は [references/auto-apply.md](references/auto-apply.md) を SSOT とする。

4 観点を専用 agent で分析し統合レポートを出力する。Tier 1 (常時) = 凝集度 / 結合度 / 可読性 の設計レベル問題 (RuboCop/ESLint で漏れるもの)、Tier 2 (条件付き) = 業務副作用 chain (feature-flag revival / auth bypass 等) で、対象 diff に domain model attribute (`plan_code` / `role` / `status` 等) の更新が含まれる場合のみ実行し、無ければ `skip` 報告。

**重大度 (全 step 共通):** 🔴 Critical (即修正 / auto-apply 対象) / 🟠 Major (この PR で修正 / auto-apply 対象) / 🟡 Minor (次 PR / 提案のみ) / 🔵 Info (認識のみ) / ✅ Good (維持)。詳細・出力ルールは [references/integration-output.md](references/integration-output.md) を SSOT とする。

## Orchestrated モード

ファイル存在からの推測では判定しない。呼び出し側（将来のオーケストレータ）が Task 起動プロンプトで「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示が無い単独起動では現行動作（申し送りファイルのみへの記録）のまま進む。差分は Step 4 の記帳先追加（quality ledger）のみで、深刻度のクローズドセット基準・収束条件を含む詳細は [references/orchestrated-mode.md](references/orchestrated-mode.md) を参照。

## 委譲実行 (subagent として起動された場合)

Orchestrated モードの宣言有無に関わらず、本 skill が subagent として起動された場合に共通で適用する判定を以下にまとめる。単独起動 (ユーザーがメイン会話で直接起動) の動作は変えない。

- **Task 使用可否**: 自分の利用可能ツール一覧に Task (Agent) が存在するかで判定する。「subagent として呼ばれた = nested 実行だから Task が使えない」という推測では判定しない。Claude Code は subagent からの nested 起動を深さ 5 まで許可しており、subagent であること自体は Task 不可の理由にならない。判定基準・fallback 手順は [references/execution.md](references/execution.md) を参照。
- **Step 1 スコープ判定**: ブランチ全体差分と未コミット+staged が乖離し判断に迷う場合、AskUserQuestion が利用可能なら user に確認してよい。利用不可 (subagent 実行) なら確認せず既定 (未コミット+staged が非 0 件ならそちら、0 件ならブランチ全体) のまま進める。
- **`${CLAUDE_PLUGIN_ROOT}` の解決**: `agents/*.md` や本文中に `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま見える場合、いま読んでいる SKILL.md (または agent 定義ファイル) の所在ディレクトリから skill root を導き、絶対パスへ読み替えてから agent 起動プロンプトへ埋め込む。

## Task complexity tier

| Tier | 判定 | 実行範囲 |
|---|---|---|
| **lite (skip)** | 1 ファイル <50 LoC かつ pure typo / copy / comment / lint-only / config 値変更のみ | **skip** (本 skill 不要) |
| **standard** (default) | 2 ファイル以下 (≤2) | main thread 順次 4 観点 |
| **deep** | 3 ファイル以上 (>2) | 4 agent 並列 |

tier 判定のファイル数は **Step 1 でスコープ確定した後の対象ファイル数**を使う (冒頭自動取得のブランチ全体行をそのまま tier 判定に使わない — 未コミット差分が実対象の場合に判定がずれる)。

**business-impact-analyzer (Tier 2)** は domain model attribute (`plan_code` / `role` / `status` 等) の更新を含む diff のみ実行。それ以外は skip 報告で完了。リスク領域 (auth / billing / payment / migration) は LoC によらず **deep** + business-impact-analyzer 必須。

## 対象 diff (skill 読み込み時に自動取得)

!`git diff --name-only origin/develop...HEAD`

!`git diff --name-only HEAD`

!`git diff --name-only --cached`

> 上 3 行は Claude Code が skill 読み込み時に実行し結果へ置換する (読み取り専用・冪等)。1 行目 = ブランチ全体、2-3 行目 = 未コミット (worktree) / staged 差分で、スコープ判定 (Step 1) に使う。失敗時のフォールバックは原因別に分ける: (a) 生コマンド文字列のまま見える (注入非対応環境) → Step 1 の同コマンドを Bash で実行する。(b) `unknown revision` 等のエラー文字列が見える (base branch が origin/develop でない) → `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` か `git remote show origin` の HEAD branch で base を特定し、`origin/<base>...HEAD` に読み替えて Bash で再実行する。

## Quick start

1. `$ARGUMENTS` 指定があればそのファイル、なければ冒頭の自動取得結果 (または `git diff --name-only origin/develop...HEAD`) で対象を確定。0 件なら終了
2. 処理方式を選ぶ (詳細: [references/execution.md](references/execution.md)):
   - ファイル ≤ 2 → **main thread で 4 観点を順次分析**
   - ファイル > 2 かつ Task 使用可 → **4 agent 並列** (同一メッセージ内に Task 4 つ)
   - ファイル > 2 かつ Task 使用不可 (利用可能ツール一覧に Task/Agent が無い場合。nested 実行かどうかとは無関係) → **main thread fallback** + 冒頭で fallback 理由を明示
3. 4 agent **すべての結果を受信してから**統合分析を開始 (部分結果先行禁止)
4. 統合レポートを出力 (詳細: [references/integration-output.md](references/integration-output.md))
5. 🔴/🟠 を auto-apply-safe / needs-judgment に振り分け、safe を自動適用 → lint/test 検証、needs-judgment を申し送りファイルへ (詳細: [references/auto-apply.md](references/auto-apply.md))

## Workflows

### Step 1: 対象ファイルの特定

引数指定時は `$ARGUMENTS` を使用。なければ `git diff --name-only origin/develop...HEAD` で取得。0 件なら終了。

**base ブランチの確定 (develop に固定しない・第一手)**: 冒頭自動取得は `origin/develop...HEAD` を使うが develop は既定値にすぎない。base が develop でないリポ (master 基準等) では第一接触で失敗するため、`gh repo view --json defaultBranchRef -q .defaultBranchRef.name` (失敗時は `git remote show origin` の HEAD branch) で base を確定してから `origin/<base>...HEAD` で取り直す。冒頭コマンドはこの確定への足場であり、develop ハードコードと読み違えない。

**未コミット差分が実対象のケース (セッション作業の self-review)**: 本 skill はセッションで書いたばかりのコードのレビューに使われることが多く、その差分はまだコミットされていないことがある。ブランチ全体 (`origin/<base>...HEAD`) と未コミット+staged (冒頭 2-3 行目) が乖離する場合は、**未コミット+staged を既定スコープにする** (過去コミット分まで巻き込むと、レビュー対象がセッションの作業と一致しない)。**ただし未コミット+staged が 0 件 (working tree が clean) の場合はこの既定の対象外とし、ブランチ全体差分を既定スコープにする** (0 件のまま既定にすると対象なしで即終了し、既にコミット済みの feature ブランチ全体を見落とすため)。ブランチ全体をレビューしたい時のみ明示指定する。判断に迷う場合、AskUserQuestion が利用可能なら user に確認してよいが、利用不可 (subagent 実行) なら確認せず上記既定 (未コミット+staged が非 0 件ならそちら、0 件ならブランチ全体) のまま進める (詳細: 「委譲実行」節)。

**PR レビューモード (現在チェックアウトしていない PR / 他者の PR を点検する場合)**: PR 番号 / URL が渡された、またはカレントブランチが対象 PR の head でない場合は、`gh pr checkout <番号>` か read-only worktree (`git worktree add`) で PR head を展開し、agent には PR head worktree の絶対パスと base 読み替え後の diff を渡す。現在の worktree をそのまま読むと別バージョンを silent に分析する (特に business-impact-analyzer は caller chain を grep で辿るため PR head の完全な repo context が要る)。

**ファイル数の defining unit**: `git diff --name-only` の行数で確定する。**test 未更新で diff に出ない spec ファイルは count しない** (impl 2 + spec 未更新 = 2 ファイル → main thread 順次)。spec の coverage gap (新規 attribute 値 / 新規 branch に対する spec context 不在) は coupling-analyzer の責務で別途検出される ([references/coupling.md](references/coupling.md) §spec-coverage-gap)。

### Step 2: Quality Analysis

[references/execution.md](references/execution.md) の「処理方式の選択」表に従って分岐する。

- **Task 使用可否の自己判定**: 自分の利用可能ツール一覧に Task (Agent) が存在するかで判定する (「委譲実行」節参照)。文字列一致による推測では判定しない。詳細・fallback 手順は references/execution.md を参照
- **4 agent**: cohesion / coupling / readability / business-impact (`agents/*.md`)
- **business-impact-analyzer の skip 条件**: 対象 diff に domain model attribute (plan_code / role / status 等) の更新が含まれない場合、最低件数を満たさず skip 報告で終了してよい。`$ARGUMENTS` が diff ではなく既存ファイル単体で git diff が取れない場合も「diff 不在のため判定不能」を理由に skip 報告する
- 並列実行の agent 起動プロンプトテンプレ・観点と reference の対応表・指摘件数ルール (最低 3 件 / 50 行未満の escape hatch 等) は [references/execution.md](references/execution.md) を参照

### Step 3: 統合分析

**前提**: Step 2 で起動した 4 agent (並列実行モード) の**すべての結果を受信してから** Step 3 を開始する (部分結果での先行実行は禁止、root cause 集約の前提が崩れるため)。main thread 代替実行の場合は 4 観点を順次完了してから本ステップへ進む。

business-impact-analyzer の **skip 報告も統合レポートに残す**。

手順 (根本原因の特定 → 優先度判定 → レポート出力)、重大度表、出力ルール (アイコンは該当時のみ / サマリーは 0 件含めて全表示 / 指摘は `/abs/path:line_number` 形式) とレポートテンプレは [references/integration-output.md](references/integration-output.md) を参照。

### Step 4: 自動適用・検証・申し送り

統合した 🔴 Critical / 🟠 Major を [references/auto-apply.md](references/auto-apply.md) の 5 条件で **auto-apply-safe / needs-judgment** に振り分ける。

- **auto-apply-safe** (**readability 軸の finding のみ** — cohesion / coupling / business-impact は条件を満たしても常に申し送り。かつ局所・public interface 不変・意味保存・非リスク領域): Edit で適用 → 編集言語に応じて lint/test を実行 (Ruby: rubocop + rspec / TS: eslint + prettier)。検証 fail なら逆 Edit で revert し申し送りへ。
- **needs-judgment** (クラス分割 / 責務分離 / シグネチャ変更 / レイヤー移動 / business-impact 全件 / 修正方針が一意でないもの): 自動適用せず申し送りファイル `$(git rev-parse --git-common-dir)/quality-review-handoff-$(git branch --show-current | tr '/' '-').md` に overwrite 書き込み (ブランチ名を含める理由と `--git-dir` 禁止は [references/auto-apply.md](references/auto-apply.md) 参照)。判断に迷ったら needs-judgment 側へ倒す。
- **review-only (ユーザーが「ファイル変更しない」「レビューのみ」と指示 / 他者の PR を点検)**: auto-apply を行わず 🔴/🟠 を全件申し送りに回す (書き込み不可ならレポート inline に転記)。冒頭で「review-only のため auto-apply は提案に留める」と明示する。
- **Edit/Bash 不可 (利用可能ツール一覧に無い場合。nested 実行かどうかとは無関係)**: 自動適用せず 🔴/🟠 全件を申し送りに回し、冒頭で明示。ファイル書き込みも不可なら申し送り内容をレポート inline に転記して情報欠落を防ぐ ([references/auto-apply.md](references/auto-apply.md))。

各 finding に状態サフィックス (`✏️ 自動適用済 (検証 pass)` / `↩️ 適用 revert (検証 fail) → 申し送り` / `⏭ 申し送り → /polish-before-commit`) を付け、総合サマリー直下に件数行 `自動適用: N 件 (検証 pass) / revert: M 件 / 申し送り: K 件 → /polish-before-commit` を追加 ([references/auto-apply.md](references/auto-apply.md) が SSOT)。

**Orchestrated モード時**: 上記の申し送りファイル書き込みに加え、auto-apply 結果 (適用済み / revert→申し送り) と needs-judgment 全件を quality ledger にも記帳する (申し送りファイルのみへの記録では収束を機械判定できないため)。記帳形式・深刻度クローズドセット・収束条件は [references/orchestrated-mode.md](references/orchestrated-mode.md) を参照。

## Advanced

- [references/execution.md](references/execution.md) — 実行モード (並列 / main thread fallback) と Task 自己判定、指摘件数ルール
- [references/integration-output.md](references/integration-output.md) — 重大度・統合手順・レポート出力ルール
- [references/auto-apply.md](references/auto-apply.md) — 🔴/🟠 の自動適用振り分け・検証・申し送り contract
- 各観点の検出基準: [references/cohesion.md](references/cohesion.md) / [references/coupling.md](references/coupling.md) / [references/readability.md](references/readability.md) / [references/business-impact.md](references/business-impact.md)

## Gotchas（観測済みの罠 — 実測で判明したものを 1 件 1 行で追記）

- base branch 解決: `gh repo view --json defaultBranchRef` と `git remote show origin` の両方が失敗する環境 (ローカル bare リポジトリ等で remote HEAD symref が機能しない場合) がある。両方失敗したら `git branch -a` と `git merge-base <候補ブランチ> HEAD` でトポロジーから実際の親ブランチを特定する
- TS/JS の検証コマンド (`yarn eslint` / `yarn prettier`) は対象プロジェクトに ESLint/Prettier が未導入だと実行できない。[references/auto-apply.md](references/auto-apply.md) の「その他/コマンド不明」区分にフォールバックし、プロジェクトの test コマンド (`package.json` の `scripts.test` 等) のみで検証して `未検証 (lint コマンド不明)` と明記する
- business-impact-analyzer の無条件 skip 条件は `.rb`/`.rake` ファイルの有無で判定しており、Node.js 等の非 Ruby プロジェクトでは domain attribute 相当の変更があっても常に skip される (Ruby/Rails 前提の判定であることに留意する)

## 併用推奨 skill

- `/express-intent-in-code` — 本 skill が needs-judgment とした naming / 凝集 finding の深掘り一点変換先。申し送りファイル (quality-review-handoff-<branch>.md) の該当 finding を渡して起動する (後段)
- `/polish-before-commit` — 本 skill が申し送った needs-judgment 項目を受け取り、フロー末尾でユーザー判断を仰ぐ最終仕上げ役
- `/qa-ui` — コード品質と並行して実装後 UI を検証する
