---
name: review-design
description: Use before adding a feature, file, module, interface, or seam, or when deciding where code should live; always use for auth, billing, payment, migration, or security changes. Trigger on explicit design-review requests too.
---

Q1-Q3 で reviewer subset を選び、並列レビューと Devil's Advocate を行う。fatal は設計へ反映する。

## Task complexity tier (skip / scope 判定)

| Row | 状況 | アクション |
|---|---|---|
| 1 | 既存 class 内の局所的な method 追加・修正のみで、配置決定済みかつ新しい責務・seam・外部境界を追加しない | **skip** (本 skill 不要) |
| 2 | production file 追加 or 配置に迷う or class/module 境界をまたぐ既存パターン拡張 | Q1-Q3 → matrix で reviewer subset 決定 |
| 3 | 新しい責務境界 (module / interface / seam) / 複数 production file に新しい責務を追加 / domain 跨り | Q1-Q3 でも **all 5 reviewers を default** |
| 4 | auth / billing / payment / migration / security (= **territory**, semantic 判定であり keyword match ではない) | 配置が自明でも実行 + DA を subagent dispatch |

Row 4 → 3 → 2 → 1 の順で最初に該当する行を使う。ただし Row 3+4 compound は Row 3 の all 5 reviewers と Row 4 の DA dispatch を併用する。Row 1 の局所 method 変更は Row 2 の「既存パターン拡張」に含めない。既存属性への read-only predicate / getter 追加 (例: `def admin?; role == 'admin'; end`) は Row 4 に該当せず Row 1 で **skip 可**。新たな write path / 新規ガード (`before_action :require_admin!` 等) / 新規 callback (after_save で session/token 操作) を含めば Row 4 で **強制実行**。判定不能なら Quick Start へ。territory の境界例は [references/task-tier-boundaries.md](references/task-tier-boundaries.md) を Read。

## Quick Start: Q1-Q3 → reviewer 選定

| Q | 判定 |
|---|---|
| Q1: 類似機能あり? | Yes → Q1.1 を評価してから Q2 / No → Q2 |
| Q2: 責務を一句で言える? | Yes → 1 file, Q3 へ / "X and Y" → 分割してから Q3 |
| Q3: テスト可能 (deps 差替可)? | 外部依存なしは Yes。No → DI / 引数で注入 (matrix への影響なし、Leaky Abstraction / Feature Envy 検出は anti-pattern-checker に委ねる) |

**Q1.1 健全性チェック (Q1=Yes のみ)**:

1. 対象の振る舞いを支える tests が通る
2. 責務を `X and Y` でなく一句で言える
3. public interface・callback・依存がその責務に閉じ、pass-through fan-out や隠れた状態結合を作らない
4. lifecycle callback から external API / 外部 IO を呼ばない

全項目を証拠で確認できれば healthy、具体的な違反があれば unhealthy、不足証拠があれば unknown。行数や method 件数だけで判定しない。

- **healthy** → そのパターンに従う。`anti-pattern-checker` のみ
- **unhealthy / unknown** → `anti-pattern-checker` と、違反または不足している証拠の対象に対応する reviewer の union。責務・callback 所有は `ddd-reviewer`、外部依存境界は `hexagonal-reviewer`、layer 方向は `clean-architecture-reviewer`、interface・pass-through・seam・testability は `deep-module-reviewer`。Q1.1 #1 の test 結果だけが不足なら追加 reviewer なしで Unknown を報告し、#2–#4 の証拠不足なら同じ対応表から必ず1つ以上を追加する。複合項目の特定 aspect だけが不足ならその対応 reviewer だけ、項目全体が未確認なら含まれる全 aspect の対応 reviewer を union する
- **Greenfield** は all 5。brownfield かつ Q1=No は下の matrix の None 行で決める

### Reviewer selection matrix

| Q1 | Q1.1 | Q2 | Reviewers |
|---|---|---|---|
| Similar | healthy | single | `anti-pattern-checker` |
| Similar | healthy | "X and Y" | `anti-pattern-checker` + `ddd-reviewer` |
| Similar | unhealthy / unknown | any | `anti-pattern-checker` + 違反または不足証拠に対応する reviewer の union |
| None | — | complex business rules | `ddd-reviewer` + `anti-pattern-checker` |
| None | — | external deps (API/DB swap) | `hexagonal-reviewer` + `anti-pattern-checker` |
| None | — | new layered design | `clean-architecture-reviewer` + `anti-pattern-checker` |
| None | — | new module / interface 設計 (深さ・seam が論点) | `deep-module-reviewer` + `anti-pattern-checker` |

"All 5" = `anti-pattern-checker` + `ddd-reviewer` + `hexagonal-reviewer` + `clean-architecture-reviewer` + `deep-module-reviewer`。test/doc の追加だけでは Row 3 にしない。複数行が同時該当する場合は first-match で打ち切らず、reviewers を union する (上限 all 5)。

## Step 0: 対象解決

- `$ARGUMENTS` = プランファイルパス or 自由文 feature description (任意)。`--strict-da` は DA subagent 強制。
- 空なら `Plan File Info:` → プランファイル Read → 会話文脈の順。**この 2 経路は単独起動時のみ有効** (委譲時は「## 委譲実行」)。単独起動でいずれからもプランパスまたは feature description を解決できなければ、対話可能時は一度だけ対象を質問して返答まで停止する。その返答でも解決できなければ再質問せず `不足入力: レビュー対象のプランファイルまたは feature description` を返して終了する。対話不能時は同じ不足入力を最終メッセージで返して即時終了する。質問前後に reviewer / DA / Edit / Write を実行しない。
- feature description のみでも実行可。プランの有無は Step 4 (Edit 対象) と Step 6 (Write 先) にのみ影響する。
- プランが PoC の仮説 ledger や「やらなかったこと→対応先」マッピング表を別ファイルで参照していれば、それも Read する (Step 5 の grounding 材料)。

## Workflow

1. **Step 1-2**: Q1-Q3 → matrix で reviewer 選定。
2. **Step 3 — Parallel Review**: independent-executor capability があれば選定 reviewer を並列 dispatch し、各 executor は対応する `agents/*.md` を適用する。greenfield は反例検索でなく提案構造への forward-looking 制約として判定する。capability が無ければ実行形態にかかわらず [references/reviewer-modes.md](references/reviewer-modes.md) の inline fallback を使う。
3. **Step 4 — Design revision**: reviewer ❌ または fatal に新しい grounded な処置があれば設計本文を修正する。プランがあれば本文を `Edit` し、なければ修正版を内部状態として保持する。修正後は選択済み reviewer と DA を再実行する。⚠️ / Unknown は編集せず残存リスクにする。分析要約はプランへ貼らない。
4. **Step 5 — Devil's Advocate (必須)**: 全 reviewer ✅ でも実行する (各 reviewer は自分のレンズしか見ない)。default は inline (main agent の自己批判):
   1. Step 3 出力にない根拠付き critique を最大3件挙げる。0件なら `critique: 該当なし` と書く。観点は運用、100x scale、他チーム向け interface、rollback cost。
   2. ラベル付け前に grounding — critique が依存する行を Read するか反例を grep。前提がコードに成立しない critique は `fatal` でなく `acceptable`。greenfield はプランの記載構造で grounding。PoC 仮説 ledger / マッピング表に対応済み・意図的 deferral・killed と記録済みの論点は fatal 化しない。
   3. 各 critique を `fatal` / `acceptable` にラベル付け。fatal = `anti-pattern-checker` ❌ OR 4 escalator (DB tx boundary / concurrency / security / contract breach) の closed set — 集合外の問題はどれほど深刻でも `acceptable` + recommendation。
   4. 根拠のある hidden assumption を最大2件挙げ、0件なら `hidden assumption: 該当なし` と書く。

   inline → **subagent dispatch** の切替条件 (reviewers の ❌ ≥ 2 / escalator hit / `--strict-da` / Row 4 territory) と dispatch 失敗の permanent / temporary / hung 分類は [references/escalation-rules.md](references/escalation-rules.md) が canonical (SSOT)。恒久的に dispatch 不能なら inline 実行 + 報告末尾に in-context fallback タグ。subagent prompt は [references/reviewer-modes.md](references/reviewer-modes.md) へ review target、grounding source paths、PoC status を埋めて渡す。
5. **Feedback loop**: Step 4 で1件でも編集したら selected reviewers と DA を再実行する。reviewer ❌ / fatal に新しい grounded な処置がある間だけ修正を繰り返す。同じ reviewer ❌ / fatal が同じ根拠で残り、新しい処置が無ければ未解決として停止し、完了を主張しない。⚠️ / Unknown / acceptable は反復しても feedback loop や未解決停止へ入れず、残存リスクとして完了 route へ送る
6. **Step 6 — Final report**: 1 issue = 1 line でチャット表示 + 同内容を `<plan>.design-review.md` へ `Write`。パス規則・必須 3 節・プラン不在時の扱いは [references/final-report-format.md](references/final-report-format.md)。

## 委譲実行 (subagent として起動された場合)

委譲が明示されたか対話不能なら、**進む前に [references/delegated-execution.md](references/delegated-execution.md) を Read する。** 同ファイルが入力解決、入力不足時の終了、並列実行不可時の fallback、非対話進行、path 解決、完了報告を規定する。

Rails の配置判断が必要な場合だけ [references/rails-patterns.md](references/rails-patterns.md) を読む。
