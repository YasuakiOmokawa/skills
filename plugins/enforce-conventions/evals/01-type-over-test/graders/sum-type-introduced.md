---
type: llm
focus: {source: file, path: repo/src/company-state.ts}
---
repo/src/company-state.ts を評価する。読み込み状態 (読み込み中、401、それ以外の失敗、読み込み済み) が、判別子を持つ union 型か、真偽値のリテラル型の組を並べた union 型で定義され、2 つ以上の状態が同時に真になる値を型の上で作れなければ pass。3 つの独立した boolean が残っている、または optional にしただけなら fail。
