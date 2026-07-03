# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: lite tier 縮約 + trigger

structural review mode + trigger 判定: (a) lite tier で pr-splitter / auto-qa-planner を skip し、manual-qa-planner は main agent が inline 統合する (Step 2A→2B の lite 縮約注記)、(b) 「実装準備を追記して」「ブランチ戦略と PR 分割を決めて」が本 skill に発火する。

### Requirements checklist
1. [critical] 両セクション (AC / MECE 分析結果) 欠落時の即中断が維持されている
2. [critical] QA-ID enumerate は main agent が 1 回だけ実行し planner は再分類しない
3. lite では tier 表に従い pr-splitter / auto-qa-planner skip、manual-qa は main agent inline と読み取れる
4. 0 件カテゴリの件数表記 (省略禁止) が維持されている

## シナリオ: 正本カバレッジ・ゲート + QA 実行台帳初期化 (v3.1 QA-ID 台帳ゲート方式)

Step 3.5 (正本カバレッジ・ゲート) と Step 4 (台帳初期化) の新設を検証する。fresh executor に `<plan>.analysis.md` (正本あり版・正本なし版の 2 パターン) と Step 1.7 の enumerate 結果を与え、Step 3 の Write 後に両 Step を実行させる。

### Requirements checklist
1. [critical] `## 正本抽出結果` があり未カバー atom (差分/未実装行の atom ID が出典欄に引用されていない) が存在する分析ファイルで実行すると、該当 atom が QA-M-NN として `## 実装準備` の手動QA手順に出典 (atom ID + 期待値原文) 付きで追記され「自動補完」である旨が明記される。追記後に再実行すると差分ゼロになる
2. [critical] `## 正本抽出結果` が無い分析ファイルで実行すると、「正本カバレッジ: skip (構造化正本なし)」の 1 行のみが `## 実装準備` に残り、AC 行数と QA-ID 数の突き合わせのような追加検査は行われない
3. [critical] Step 4 実行後、Step 1.7 で enumerate した全 QA-ID が `<plan>.qa-ledger.md` に 1 行ずつ存在する。auto-qa-planner の QA-ID カバレッジマトリクスに載る QA-ID は手段=auto、それ以外で manual-qa-planner の見出しに載る QA-ID は手段=manual、どちらにも載らない QA-ID は状態=対象外(N/A) (備考「担当手段未特定、要人間確認」) で初期化される。両方に載る (dual coverage) QA-ID は manual 行が重複生成されない
