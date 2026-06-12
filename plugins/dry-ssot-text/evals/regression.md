# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: tier 競合 + trigger

structural review mode + trigger 判定: (a) 55 行・重複 3 箇所 → 重複箇所数優先で lite (skip にしない)、(b) dry-run 要否は tier 表が canonical (standard/deep で必須)、(c) 「この文書の重複をまとめて」は発火し「重複コードをリファクタして」は発火しない (description の documents-only 除外)。

### Requirements checklist
1. [critical] 必要重複 (TOC / 進捗 table / AC checklist) を DRY 化対象にしない
2. [critical] tier 競合時は重複箇所数を優先 (skip は「重複 ≤2」が必須条件)
3. dry-run 要否の判定が tier 表 (standard/deep 必須) に一本化されている
4. code duplication が scope 外であることが description から読み取れる
