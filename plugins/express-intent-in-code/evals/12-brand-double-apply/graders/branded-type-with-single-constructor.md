---
type: llm
focus: {source: file, path: src/display-text.ts}
---
src/display-text.ts を評価する。sanitize 済みの文字列を表す型 (例: `string & { readonly [brand]: true }` の branded type、または同等の nominal な型) が定義され、その型の値を作る関数がこのファイルの 1 箇所だけで、sanitize 関数の戻り型がその型になっていれば pass。戻り型が `string` のまま、または呼び手が `as` で型を付けられるだけの alias (`type DisplayText = string`) なら fail。
