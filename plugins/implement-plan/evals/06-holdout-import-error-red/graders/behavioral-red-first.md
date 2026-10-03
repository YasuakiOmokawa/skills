---
type: llm
focus: trace
---
AC-001 のテストについて、toSlug の変換処理 (小文字化や空白の置換) を実装する前に、そのテストが期待値と実際の値の不一致 (assertion の失敗) で失敗するテスト実行があれば pass。

変換処理を書く前のテスト実行が `toSlug is not a function` などの読み込み・export 不在のエラーだけで、その状態から変換処理を実装していれば fail。テストを実装より後に書いた場合も fail。
