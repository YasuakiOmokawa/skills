---
name: review-design
description: Use when starting a new feature, adding a file or module, designing a module's interface (deep vs shallow / where a seam goes), deciding "where should this code live", or when the user requests a design review with `/review-design`. ALSO use when the change touches auth / billing / payment / migration / security territory — run even if placement seems obvious (this territory rule overrides the skip conditions).
---

# review-design

実装前の配置・パターン判定。Criticism first — default verdict は「問題あり」。Q1-Q3 で選んだ reviewer subset (anti-pattern-checker 必須 + DDD / Hexagonal / Clean Arch / Deep-Module) を並列レビュー → 必須 Devil's Advocate → 致命指摘は plan ファイルを直接書き換える。

## Task complexity tier (skip / scope 判定)

| Row | 状況 | アクション |
|---|---|---|
| 1 | 1 ファイル <50 LoC かつ既存 class 内部 method の追加・修正のみ かつ配置決定済み | **skip** (本 skill 不要) |
| 2 | ファイル追加 or 配置に迷う or 既存パターン拡張 | Q1-Q3 → matrix で reviewer subset 決定 |
| 3 | 新規 module / 複数 file 跨り / domain 跨り | Q1-Q3 でも **all 5 reviewers を default** |
| 4 | auth / billing / payment / migration / security (= **territory**, semantic 判定であり keyword match ではない) | 配置が自明でも実行 + DA を subagent dispatch |

**Row 1 vs Row 4 precedence**: territory (semantic) 判定が優先。既存属性への read-only predicate / getter 追加 (例: `def admin?; role == 'admin'; end`) は Row 4 に該当せず Row 1 で **skip 可**。新たな write path / 新規ガード (`before_action :require_admin!` 等) / 新規 callback (after_save で session/token 操作) を含めば Row 4 で **強制実行**。判定不能なら Quick Start へ。Row 3+4 compound と Row 4 core path の境界例は [references/task-tier-boundaries.md](references/task-tier-boundaries.md) を Read。

## Quick Start: Q1-Q3 → reviewer 選定

| Q | 判定 |
|---|---|
| Q1: 類似機能あり? | Yes → Q1.1 / No → Q2 |
| Q2: 責務を一句で言える? | Yes → 1 file, Q3 へ / "X and Y" → 分割してから Q3 |
| Q3: テスト可能 (deps 差替可)? | No → DI / 引数で注入 (matrix への影響なし、Leaky Abstraction / Feature Envy 検出は anti-pattern-checker に委ねる) |

**Q1.1 健全性チェック (Q1=Yes のみ)**: 以下 5 項目の AND で healthy、1 項目でも違反すれば unhealthy。**証拠が取れず検証できない項目は項目単位で違反扱い** (コード不在 / テスト基盤不在 / 情報不足など理由を問わない):

1. tests 通過 / 2. single responsibility (責務が一句で言える) / 3. 行数 ≤200 / 4. public method ≤10 かつ callback chain <3 / 5. after_commit・after_create 内で external API / 外部 IO を呼ばない

- **healthy** → そのパターンに従う。`anti-pattern-checker` のみ。ただし項目 5 違反は 1-4 充足でも unhealthy 扱い (escape hatch)
- **unhealthy** → 新パターン提案。**all 5**
- **Greenfield** (対象リポにコード不在) は項目 1/3/4 が検証不能 → unhealthy → all 5。**Q1=No の greenfield も同じく all 5**。brownfield かつ Q1=No は下の matrix の None 行で決める

### Reviewer selection matrix (first-match, top-down)

| Q1 | Q1.1 | Q2 | Reviewers |
|---|---|---|---|
| Similar | healthy | single | `anti-pattern-checker` |
| Similar | healthy | "X and Y" | `anti-pattern-checker` + `ddd-reviewer` |
| Similar | unhealthy | any | **all 5** (parallel) |
| None | — | complex business rules | `ddd-reviewer` + `anti-pattern-checker` |
| None | — | external deps (API/DB swap) | `hexagonal-reviewer` + `anti-pattern-checker` |
| None | — | new layered design | `clean-architecture-reviewer` + `anti-pattern-checker` |
| None | — | new module / interface 設計 (深さ・seam が論点) | `deep-module-reviewer` + `anti-pattern-checker` |

"All 5" = `anti-pattern-checker` + `ddd-reviewer` + `hexagonal-reviewer` + `clean-architecture-reviewer` + `deep-module-reviewer`。None ブランチの複数行が同時該当する場合は first-match で打ち切らず、該当行の reviewers を **union** する (上限 all 5)。

## Step 0: 対象解決

- `$ARGUMENTS` = プランファイルパス or 自由文 feature description (任意)。`--strict-da` は DA subagent 強制。
- 空なら `Plan File Info:` → プランファイル Read → 会話文脈の順。**この 2 経路は単独起動時のみ有効** (委譲時は「## 委譲実行」)。
- feature description のみでも実行可。プランの有無は Step 4 (Edit 対象) と Step 6 (Write 先) にのみ影響する。
- プランが PoC の仮説 ledger や「やらなかったこと→対応先」マッピング表を別ファイルで参照していれば、それも Read する (Step 5 の grounding 材料)。

## Workflow

1. **Step 1-2**: Q1-Q3 → matrix で reviewer 選定。
2. **Step 3 — Parallel Review**: 選定 reviewer を `Task(subagent_type="general-purpose")` で並列 dispatch。各 Task は対応する `agents/*.md` を Read して適用。greenfield (まだコードが無い設計レビュー) では判定基準を Grep/Glob 反例検索でなく提案構造への forward-looking 制約として適用する。Task 不可時 fallback / `${CLAUDE_PLUGIN_ROOT}` 解決は「## 委譲実行」。
3. **Step 4 — Plan edit**: 指摘があればプランファイルを `Edit` で直接修正 — 設計本文そのものを書き換える (分析要約の貼り付けは禁止)。ここで報告は出さず Step 5 へ。
4. **Step 5 — Devil's Advocate (必須)**: 全 reviewer ✅ でも実行する (各 reviewer は自分のレンズしか見ない)。default は inline (main agent の自己批判):
   1. Step 3 出力に**無い**角度から critique 3 件 (reviewer 指摘の再掲は禁止) — 運用 (deploy 直後 / 廃止直前 / incident) / スケール (100x traffic or data) / 他チーム・plugin から見た interface / rollback コスト。
   2. ラベル付け前に grounding — critique が依存する行を Read するか反例を grep。前提がコードに成立しない critique は `fatal` でなく `acceptable`。greenfield はプランの記載構造で grounding。PoC 仮説 ledger / マッピング表に対応済み・意図的 deferral・killed と記録済みの論点は fatal 化しない。
   3. 各 critique を `fatal` / `acceptable` にラベル付け。fatal = `anti-pattern-checker` ❌ OR 4 escalator (DB tx boundary / concurrency / security / contract breach) の closed set — 集合外の問題はどれほど深刻でも `acceptable` + recommendation。
   4. hidden assumption を 1-2 件 (保存先は [references/final-report-format.md](references/final-report-format.md) の Hidden assumption 節)。

   inline → **subagent dispatch** の切替条件 (reviewers の ❌ ≥ 2 / escalator hit / `--strict-da` / Row 4 territory) と dispatch 失敗の permanent / temporary / hung 分類は [references/escalation-rules.md](references/escalation-rules.md) が canonical (SSOT)。恒久的に dispatch 不能なら inline 実行 + 報告末尾に in-context fallback タグ。DA prompt 全文は [references/reviewer-modes.md](references/reviewer-modes.md)。
5. **Feedback loop**: fatal があれば Edit → Step 3-5 再実行。全 DA findings が acceptable になるまで繰り返す。
6. **Step 6 — Final report**: 1 issue = 1 line でチャット表示 + 同内容を `<plan>.design-review.md` へ `Write`。パス規則・必須 3 節・プラン不在時の扱いは [references/final-report-format.md](references/final-report-format.md)。

## 委譲実行 (subagent として起動された場合)

Task 経由で起動されたなら (判定基準: AskUserQuestion が利用可能ツールに無いか、で機械的に行う)、**進む前に [references/delegated-execution.md](references/delegated-execution.md) を必ず Read すること。** 同ファイルが規定: 入力解決順位 (`Plan File Info:` / 会話文脈は使わない) / 入力不足・指定パス不在時の即時完結 (捏造せず待たず終了) / Step 3 の Task 不可時 fallback / Design It Twice の非対話進行 / `${CLAUDE_PLUGIN_ROOT}` 解決 / 完了報告。

## Gotchas（観測済みの罠 — 実測で判明したものを 1 件 1 行で追記）

## Advanced

- [references/escalation-rules.md](references/escalation-rules.md) — 実行 3 mode / DA escalation 条件 / Fatal vs single-trigger 全表 (canonical)
- [references/reviewer-modes.md](references/reviewer-modes.md) — DA prompts (inline & subagent) / feedback loop 詳細 / fallback 規則
- [references/final-report-format.md](references/final-report-format.md) — 報告テンプレ / 保存 3 節 / "1-issue-1-line" 粒度 / fallback tag 例
- [references/task-tier-boundaries.md](references/task-tier-boundaries.md) — tier 境界規則 (Row 3+4 compound / core path 境界例)
- [references/detailed-workflow.md](references/detailed-workflow.md) — Quick Start で解決しない場合 (配置・依存方向・パターン選択)
- [references/rails-patterns.md](references/rails-patterns.md) — Rails 配置の第一候補表 (anti-pattern-checker の判定や detailed-workflow の配置決定で参照)
- Reviewer specs: `agents/anti-pattern-checker.md`, `agents/ddd-reviewer.md`, `agents/hexagonal-reviewer.md`, `agents/clean-architecture-reviewer.md`, `agents/deep-module-reviewer.md` (各 reviewer の quickref / 詳細 references は agent 定義から辿る)

## Companion skills

- `/define-acceptance-criteria` — define AC after design review, before implementation.
