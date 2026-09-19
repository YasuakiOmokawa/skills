---
type: llm
focus: {source: file, path: src/attempt-budget.ts}
---
src/attempt-budget.ts を評価する。counter の結果から verdict ("unavailable" / "exhausted" / "accepted") を決める判断が、その一部 (count の有効性判定を含む) も含めて spendBudget の本体に残っていれば pass。判断の全部または一部が新しい関数や述語 (exported かどうか、1 行かどうかを問わず) に切り出されていれば fail。型の別名や定数の導入は判断の切り出しに数えない。
