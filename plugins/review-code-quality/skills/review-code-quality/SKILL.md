---
name: review-code-quality
description: Use when finishing self-review of an implementation, before requesting PR review, when inspecting someone else's PR or a PR not checked out locally (PR review mode), when a diff updates a domain model attribute (`plan_code` / `role` / `status` 等), or when the user says "コード品質をレビューして" / "品質レビュー". Analyzes the diff across cohesion and coupling (plus business-impact for domain-attribute changes — Ruby/Rails diffs only, skipped when the diff has no .rb/.rake files) and hands off every 🔴/🟠 finding to /polish-before-commit as needs-judgment without editing files. Readability-level fixes (minor renames, simplification, efficiency) are covered by the built-in /code-review skill, not this plugin.
---

# Review Code Quality

**🔴 Critical / 🟠 Major は全件 `/polish-before-commit` への申し送り (needs-judgment) に回す。本 skill はファイルを変更しない (連続スキル実行で提案が握りつぶされるのを防ぐため)。🟡 Minor 以下は提案のみ。** 申し送り contract は Step 4 を SSOT とする。

3 観点を専用 agent で分析し統合レポートを出力する。Tier 1 (常時) = 凝集度 / 結合度 の設計レベル問題 (RuboCop/ESLint で漏れるもの)、Tier 2 (条件付き) = 業務副作用 chain (feature-flag revival / auth bypass 等) で、対象 diff に domain model attribute (`plan_code` / `role` / `status` 等) の更新が含まれる場合のみ実行し、無ければ `skip` 報告。

**重大度 (全 step 共通):** 🔴 Critical (即修正 / 申し送り) / 🟠 Major (この PR で修正 / 申し送り) / 🟡 Minor (次 PR / 提案のみ) / 🔵 Info (認識のみ) / ✅ Good (維持)。詳細・出力ルールは [references/integration-output.md](references/integration-output.md) を SSOT とする。

## レビュー範囲外 (委譲)

命名の軽微改善・簡素化・効率といった readability レベルの指摘は本 skill の対象外。組み込みの `/code-review` (単体実行、または `/polish-before-commit` Step 8 の xhigh 実行) が担当する。**correctness (計算誤り・ロジックバグ・境界条件の欠陥) も本 skill の対象外**で、同じく組み込み `/code-review` が担当する (本 skill は設計構造の分析であり、実行時の正しさ・数値の正否は判定しない — read-only の金額計算バグ等もここに含む)。命名の深掘り一点変換 (機構名 → 目的表明形) は `/express-intent-in-code`。本 skill は cohesion / coupling / business-impact の設計レベル分析に特化し、全 finding を `/polish-before-commit` へ申し送る。

## Orchestrated モード

ファイル存在からの推測では判定しない。呼び出し側（将来のオーケストレータ）が Task 起動プロンプトで「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示が無い単独起動では現行動作（申し送りファイルのみへの記録）のまま進む。差分は Step 4 の記帳先追加（quality ledger）のみで、深刻度のクローズドセット基準・収束条件を含む詳細は [references/orchestrated-mode.md](references/orchestrated-mode.md) を参照。

## 委譲実行 (subagent として起動された場合)

Orchestrated モードの宣言有無に関わらず、本 skill が subagent として起動された場合に共通で適用する判定。単独起動 (ユーザーがメイン会話で直接起動) の動作は変えない。

- **Task 使用可否**: 自分の利用可能ツール一覧に Task (Agent) が存在するかで判定する (「subagent = nested だから Task 不可」という推測では判定しない。判定基準・fallback は [references/execution.md](references/execution.md) の「Task 使用可否の自己判定」を SSOT とする)。
- **Step 1 スコープ判定**: ブランチ全体差分と未コミット+staged が乖離し判断に迷う場合、AskUserQuestion が利用可能なら user に確認してよい。利用不可 (subagent 実行) なら確認せず既定 (未コミット+staged が非 0 件ならそちら、0 件ならブランチ全体) のまま進める。
- **`${CLAUDE_PLUGIN_ROOT}` の解決**: `agents/*.md` や本文中に `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま見える場合、いま読んでいる SKILL.md (または agent 定義ファイル) の所在ディレクトリから skill root を導き、絶対パスへ読み替えてから agent 起動プロンプトへ埋め込む。

## Task complexity tier

| Tier | 判定 | 実行範囲 |
|---|---|---|
| **lite (skip)** | 1 ファイル <50 LoC かつ pure typo / copy / comment / lint-only / config 値変更のみ | **skip** (本 skill 不要) |
| **standard** (default) | 2 ファイル以下 (≤2) | main thread 順次 3 観点 |
| **deep** | 3 ファイル以上 (>2) | 3 agent 並列 |

tier 判定のファイル数は **Step 1 でスコープ確定した後の対象ファイル数**を使う (冒頭自動取得のブランチ全体行をそのまま tier 判定に使わない — 未コミット差分が実対象の場合に判定がずれる)。

**business-impact-analyzer (Tier 2)** は domain model attribute (`plan_code` / `role` / `status` 等) の更新を含む diff のみ実行。それ以外は skip 報告で完了。リスク領域 (auth / billing / payment / migration) は LoC によらず **deep** + business-impact-analyzer 必須。**billing/payment 認定の必要条件は永続化・課金/決済ミューテーション・invoice 発行等の副作用を伴うこと**で、read-only の金額集計・帳票 (税・返金の計算のみで書き込み無し) は override 対象外。territory 軸と business-impact 起動条件 (attribute write) 軸が交差した場合は、どちらか一方でも該当すれば deep + business-impact-analyzer を起動する (OR 条件・安全側)。

**分析範囲軸と dispatch 軸は直交**: 上記の OR 条件・tier 昇格が決めるのは**分析範囲**（どの観点を回すか = 「deep」は business-impact-analyzer 必須の意味）であって、dispatch 形態（並列 / 順次）ではない。並列 vs 順次は [references/execution.md](references/execution.md) のファイル数表（+ Task 使用可否）のみで決まる。リスク領域で LoC ≤ 2 が deep 扱いになるケースは、business-impact を含めた上で dispatch は main thread 順次のままでよい（「deep = 必ず並列」ではない）。

## 対象 diff (skill 読み込み時に自動取得)

!`git diff --name-only origin/develop...HEAD`

!`git diff --name-only HEAD`

!`git diff --name-only --cached`

> 上 3 行は Claude Code が skill 読み込み時に実行し結果へ置換する (読み取り専用・冪等)。1 行目 = ブランチ全体、2-3 行目 = 未コミット (worktree) / staged 差分で、スコープ判定 (Step 1) に使う。失敗時のフォールバックは原因別に分ける: (a) 生コマンド文字列のまま見える (注入非対応環境) → Step 1 の同コマンドを Bash で実行する。(b) `unknown revision` 等のエラー文字列が見える (base branch が origin/develop でない) → Step 1「base ブランチの確定」に従い default branch を特定して `origin/<base>...HEAD` に読み替え Bash で再実行する。

## Quick start

1. `$ARGUMENTS` 指定があればそのファイル、なければ冒頭の自動取得結果 (または `git diff --name-only origin/develop...HEAD`) で対象を確定。0 件なら終了
2. 処理方式を選ぶ — ファイル ≤ 2 は main thread 順次、> 2 かつ Task 使用可は 3 agent 並列 (同一メッセージ内に Task 3 つ)、> 2 かつ Task 使用不可は main thread fallback + 理由明示。分岐表と Task 可否判定は [references/execution.md](references/execution.md)
3. 3 agent **すべての結果を受信してから**統合分析を開始 (部分結果先行禁止)
4. 統合レポートを出力 (詳細: [references/integration-output.md](references/integration-output.md))
5. 🔴/🟠 を全件 needs-judgment として申し送りファイルへ書き込む (詳細: Step 4)

## Workflows

### Step 1: 対象ファイルの特定

引数指定時は `$ARGUMENTS` を使用。なければ `git diff --name-only origin/develop...HEAD` で取得。0 件なら終了。

**base ブランチの確定 (develop に固定しない・第一手)**: 冒頭自動取得は `origin/develop...HEAD` を使うが develop は既定値にすぎない。base が develop でないリポ (master 基準等) では第一接触で失敗するため、`gh repo view --json defaultBranchRef -q .defaultBranchRef.name` (失敗時は `git remote show origin` の HEAD branch) で base を確定してから `origin/<base>...HEAD` で取り直す。**両方失敗 (リモート無し / remote HEAD symref が dangling 等) した場合はトポロジー (`git merge-base <候補ブランチ> HEAD` / `git branch -a`) から実際の親ブランチを確定する。** 冒頭コマンドはこの確定への足場であり、develop ハードコードと読み違えない。**ブランチ全体差分が空 かつ 未コミット+staged が非 0 件は正常な self-review 状態**であり base 誤りと混同しない (この場合は未コミット+staged を対象にする)。

**未コミット差分が実対象のケース (セッション作業の self-review)**: 本 skill はセッションで書いたばかりのコードのレビューに使われることが多く、その差分はまだコミットされていないことがある。ブランチ全体 (`origin/<base>...HEAD`) と未コミット+staged (冒頭 2-3 行目) が乖離する場合は、**未コミット+staged を既定スコープにする** (過去コミット分まで巻き込むと、レビュー対象がセッションの作業と一致しない)。**ただし未コミット+staged が 0 件 (working tree が clean) の場合はこの既定の対象外とし、ブランチ全体差分を既定スコープにする** (0 件のまま既定にすると対象なしで即終了し、既にコミット済みの feature ブランチ全体を見落とすため)。ブランチ全体をレビューしたい時のみ明示指定する。判断に迷う場合の確認可否 (AskUserQuestion 利用可なら user 確認可 / subagent 実行では確認せず上記既定で進める) は「委譲実行」節を参照。

**PR レビューモード (現在チェックアウトしていない PR / 他者の PR を点検する場合)**: PR 番号 / URL が渡された、またはカレントブランチが対象 PR の head でない場合は、`gh pr checkout <番号>` か read-only worktree (`git worktree add`) で PR head を展開し、agent には PR head worktree の絶対パスと base 読み替え後の diff を渡す。現在の worktree をそのまま読むと別バージョンを silent に分析する (特に business-impact-analyzer は caller chain を grep で辿るため PR head の完全な repo context が要る)。

**ファイル数の defining unit**: `git diff --name-only` の行数で確定する。**test 未更新で diff に出ない spec ファイルは count しない** (impl 2 + spec 未更新 = 2 ファイル → main thread 順次)。spec の coverage gap (新規 attribute 値 / 新規 branch に対する spec context 不在) は coupling-analyzer の責務で別途検出される ([references/coupling.md](references/coupling.md) §spec-coverage-gap)。

### Step 2: Quality Analysis

[references/execution.md](references/execution.md) の「処理方式の選択」表に従って分岐する。

- **Task 使用可否の自己判定**: 「委譲実行」節 / [references/execution.md](references/execution.md) の own-tool-list 判定に従う (文字列一致による推測では判定しない)
- **3 agent**: cohesion / coupling / business-impact (`agents/*.md`)
- **business-impact-analyzer の skip 条件**: 対象 diff に domain model attribute (plan_code / role / status 等) の更新が含まれない場合、最低件数を満たさず skip 報告で終了してよい。`$ARGUMENTS` が diff ではなく既存ファイル単体で git diff が取れない場合も「diff 不在のため判定不能」を理由に skip 報告する
- 並列実行の agent 起動プロンプトテンプレ・観点と reference の対応表・指摘件数ルール (最低 3 件 / 50 行未満の escape hatch 等) は [references/execution.md](references/execution.md) を参照

### Step 3: 統合分析

3 agent (並列モード) の**すべての結果を受信してから**開始する (部分結果での先行実行は禁止、root cause 集約の前提が崩れるため)。main thread 代替実行では 3 観点を順次完了してから進む。business-impact-analyzer の **skip 報告も統合レポートに残す**。

手順 (根本原因の特定 → 優先度判定 → レポート出力)、重大度表、出力ルール (アイコンは該当時のみ / サマリーは 0 件含めて全表示 / 指摘は `/abs/path:line_number` 形式) とレポートテンプレは [references/integration-output.md](references/integration-output.md) を参照。

### Step 4: 申し送り (全件 needs-judgment)

統合した 🔴 Critical / 🟠 Major は **全件 needs-judgment** として申し送りファイルへ書き込む。本 skill はファイルを変更しない (cohesion / coupling / business-impact のいずれの軸でも自動修正しない)。🟡 Minor / 🔵 Info はレポート提案のみ (申し送りもしない)。analyzer agent (`agents/*.md`) は検出のみ。

**申し送りファイル (contract — `/polish-before-commit` と共有)**:

- パス: `$(git rev-parse --path-format=absolute --git-common-dir)/quality-review-handoff-$(git branch --show-current | tr '/' '-').md` (= 共有 `.git/` 配下・ブランチ名付き。commit されず repo-scoped、session / skill 跨ぎで永続)。`--path-format=absolute` を付ける理由 — 素の `--git-common-dir` は相対パス (`.git`) を返しうるため、レポート記載を絶対パスに固定する (読み手の /polish-before-commit は素の `--git-common-dir` で読むが、相対/絶対は同一ファイルに解決されるので不整合は起きない)。`--git-dir` は使わない — linked worktree では worktree 固有ディレクトリを返し、読み手の /polish-before-commit が読む `--git-common-dir` 側とずれて申し送りが届かなくなる (書き手と読み手でパスが食い違い、needs-judgment が握りつぶされた実測事例)。通常の checkout では両者は同値。
- ファイル名にブランチ名を含める理由: `--git-common-dir` は全 worktree 共有のため、ブランチ名なしの単一ファイルだと複数 worktree の並行セッションが相互 overwrite し先行セッションの申し送りが消える。`/` はファイル名に使えないため `tr '/' '-'` で置換する。
- 書き込みは **overwrite** (毎 run、現 diff に対する 🔴/🟠 の完全集合を上書き)。append しない。**0 件なら申し送りファイルを作らない** (既存があれば削除)。
- naming (public symbol のリネーム) / cohesion (クラス分割・責務分離) の finding は `/polish-before-commit` を待たず、この申し送りファイルを渡して `/express-intent-in-code` を直接起動してよい (深掘り一点変換の後段)。**クリア責務は `/polish-before-commit` のまま** — `/express-intent-in-code` は読み込むだけで削除しない。
- フォーマット:

```markdown
# 判断が必要な品質指摘 (review-code-quality 申し送り)
branch: <git branch --show-current の値>

<!-- /polish-before-commit がフロー末尾で読み込み・提示・クリアする -->

- 🔴 `/abs/path:line`: <finding 要約> — 見送り理由: <設計判断 / cross-file / business-impact 等>
- 🟠 `/abs/path:line`: <finding 要約> — 見送り理由: ...
```

- **review-only (ユーザーが「ファイル変更しない」「レビューのみ」と指示 / 他者の PR を点検)**: 全件申し送り + ファイル無変更 (通常動作と同じ)。冒頭で「review-only」と明示する。書き込み不可ならレポート inline に転記。
- **Write/Bash 不可 (利用可能ツール一覧に無い nested 実行等。nested かどうかとは無関係)**: 申し送りファイルへ書けない場合は申し送り内容 (上記フォーマット) を**レポート inline に転記して返し**、`[handoff: inline (write 不可)]` を明示する。不変条件は「ファイルへ保存できたこと」ではなく**「情報が失われないこと (握りつぶし防止)」**。永続化は呼び出し元 / 後続 `/polish-before-commit` 実行に委ねる。

各 🔴/🟠 finding に状態サフィックス `⏭ 申し送り → /polish-before-commit` を付け、統合レポートの `### 総合サマリー` 直下に件数行 `申し送り: K 件 → /polish-before-commit` を追加する。**件数 K は統合後 finding 単位で数える** (同一箇所が複数軸に該当する場合は 1 件に統合し、該当軸を併記する)。

**Orchestrated モード時**: 上記の申し送りファイル書き込みに加え、needs-judgment 全件を quality ledger にも記帳する (申し送りファイルのみへの記録では収束を機械判定できないため)。記帳形式・深刻度クローズドセット・収束条件は [references/orchestrated-mode.md](references/orchestrated-mode.md) を参照。

## Advanced

- [references/execution.md](references/execution.md) — 実行モード (並列 / main thread fallback) と Task 自己判定、指摘件数ルール
- [references/integration-output.md](references/integration-output.md) — 重大度・統合手順・レポート出力ルール
- 各観点の検出基準: [references/cohesion.md](references/cohesion.md) / [references/coupling.md](references/coupling.md) / [references/business-impact.md](references/business-impact.md)

## Gotchas（観測済みの罠 — 実測で判明したものを 1 件 1 行で追記）

- base branch 解決の三段 fallback (gh → remote HEAD → トポロジー) は Step 1「base ブランチの確定」を参照
- business-impact-analyzer の無条件 skip 条件は `.rb`/`.rake` ファイルの有無で判定しており、Node.js 等の非 Ruby プロジェクトでは domain attribute 相当の変更があっても常に skip される (Ruby/Rails 前提の判定であることに留意する)

## 併用推奨 skill

- `/code-review` (組み込み) — readability レベル (命名の軽微改善・簡素化・効率) を担当する委譲先。本 skill の対象外領域を埋める
- `/express-intent-in-code` — 本 skill が申し送った naming / 凝集 finding の深掘り一点変換先。申し送りファイル (quality-review-handoff-<branch>.md) の該当 finding を渡して起動する (後段)
- `/polish-before-commit` — 本 skill が申し送った needs-judgment 項目を受け取り、フロー末尾でユーザー判断を仰ぐ最終仕上げ役
- `/qa-ui` — コード品質と並行して実装後 UI を検証する
