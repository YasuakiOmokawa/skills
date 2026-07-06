# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: 静的チェック + ledger 規律

structural review mode: description (negative trigger 含む) と本文の整合、および「Start here」step 3 の ledger 規律を確認する。

### Requirements checklist
1. [critical] ledger の status が unverified / grounded / killed の 3 値で、grounded の立証責任は証拠側 (照合不能なら unverified のまま step 1 へ戻る) と読み取れる
2. [critical] ガードレール: 戻しにくい決定 (DB スキーマ / 公開 API 契約) では code-first 不可 → design-first or 狭い spike + ADR、と読み取れる
3. Common mistakes「相対比較で合否を決めない (ground-truth への絶対値で出す)」が維持されている

## シナリオ: finalize-plan への合流分岐 (step 5 完走 vs ledger 駆動 vs 前提崩れ)

fresh executor に The loop 表とその直下の note (step 4→6 の note 群) を渡し、次の 3 パターンで step 6 の挙動を判定させる: (a) step 5 (`/define-acceptance-criteria` → `/mece-plan-review`) を完走し `<plan>.analysis.md` に `## 受け入れ条件` `## MECE分析結果` が揃った状態、(b) step 4-5 自体を省略し分析ファイルが一度も無いまま ledger 駆動で step 6 に進む状態、(c) 周回途中で DB スキーマ変更のような戻しにくい決定が必要になった状態。

### Requirements checklist
1. [critical] (a) では `/finalize-plan` を通常どおり起動すると判定し、AC/MECE 欠落のまま finalize-plan の即中断ゲートを迂回する提案をしない
2. [critical] 合流手順が実行順で書ける: 「step5 完走 → 分析ファイル成立 → finalize-plan 通常起動」(a) と「step4-5 省略 → ledger 追記代替」(b) の分岐を取り違えない
3. (c) では loop を中断し `When to use` のガードレールに従って design-first (`/mece-plan-review` 等の実装前ゲート) へ切り替えると判定される

収束記録: 未実施。
