# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: 決定木 + lite 直接適用

structural review mode + trigger 判定: (a) Q1-Q4 決定木 (番号ラベルは出現回数に関わらず言い換え / 2+ 回造語は in-line 定義)、(b) lite は dry-run 省略のため承認不要で直接適用してよい (Step 5 冒頭)、(c) 「造語チェックして」「PR 説明の語彙を点検して」が本 skill に発火する。

### Requirements checklist
1. [critical] codebase identifier / Jira ID は維持、番号ラベル (Critical-A / AC-12 / α 層) は実値へ言い換え
2. [critical] 層ラベルで source plan 不在時は具体名を捏造せず関係性ベースの一般表現に言い換え
3. lite は Step 4 を飛ばし承認不要で直接適用と読み取れる
