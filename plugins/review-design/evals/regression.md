# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: greenfield reviewer (agents/anti-pattern-checker.md または ddd-reviewer.md)

コード未着手・対象リポジトリ不在 (Grep 反例検索が成立しない) の plan: OrderDiscountService 新設 (責務 1 つ / public method 1 / 外部 IO なし / 戻り値 Integer)。チェック観点ごとに判定 (✅/⚠️/❌/Unknown) を出させる。

### Requirements checklist
1. [critical] plan から forward-looking に判定できる観点を Unknown にしない (Unknown 乱発しない)
2. plan からも判定材料が得られない観点のみ `<観点>: Unknown (理由)` 形式で棄権
3. デフォルト ⚠️ 原則を維持し、greenfield のため ✅ 項目にも判定根拠を 1 行付記
4. 全観点の判定を列挙 (黙って省略しない)
