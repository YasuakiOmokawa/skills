---
type: llm
focus: {source: file, path: repo/src/company-state.ts}
---
repo/src/company-state.ts を評価する。読み込み中、401、それ以外の失敗の 3 つの状態のうち 2 つ以上が同時に成り立つ値を、型エラー無しに組み立てられない定義になっていれば pass。手段は問わない。3 つの独立した boolean のままで、どの組み合わせも組み立てられるなら fail。optional にしただけでも fail。
