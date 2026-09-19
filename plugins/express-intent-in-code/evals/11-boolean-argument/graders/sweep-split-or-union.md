---
type: llm
focus: {source: file, path: src/sweep-signups.ts}
---
src/sweep-signups.ts を評価する。「候補を列挙するだけ」と「候補を削除する」の 2 つの処理が、別々の関数として定義されているか、または名前付きの union 値 (例: `"dry-run" | "execute"`) で選ばれていれば pass。1 つの関数が boolean 引数で両方を切り替えていれば fail。Signup の `verified: boolean` フィールドは評価対象外。
