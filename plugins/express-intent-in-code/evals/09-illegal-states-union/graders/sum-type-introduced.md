---
type: llm
focus: {source: file, path: src/company-state.ts}
---
src/company-state.ts を評価する。読み込み状態 (loading / unauthorized / loadFailed / loaded に相当する 4 状態) が、判別子を持つ union 型 (例: `{ kind: "loading" } | { kind: "unauthorized" } | ...`) または相互排他を型で保証する同等の表現で定義され、複数の状態が同時に真になる値を型の上で構築できなくなっていれば pass。3 つの独立した boolean が残っている、または boolean を optional にしただけなら fail。
