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
