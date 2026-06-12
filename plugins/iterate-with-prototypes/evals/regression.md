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
