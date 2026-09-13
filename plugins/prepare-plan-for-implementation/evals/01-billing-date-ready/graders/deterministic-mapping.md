---
type: llm
focus: {source: file, path: plans/billing-date.md}
---
`## Verification Plan` の `### AC-001`〜`### AC-004` の 4 entry を見る。次をすべて満たすなら pass。

- 各 `- Oracle:` に期待値がある (戻り値、列の値、前後比較のいずれかが具体的に書かれている)。「正しく動く」「仕様どおり」のような期待値の無い記述があれば fail。
- 各 `- Required effects:` に、検証時に実行する具体的な操作 (テストの実行、関数の呼び出し、SQL の発行、行の挿入など) がある。「確認する」だけで操作が無ければ fail。
- AC-004 の `runBillingCycle` は外部パッケージ `@acme/billing-schedule` にあり、本リポジトリに実装が無い。AC-004 の `- Prerequisites:` が、その実行環境・呼び出し方・変更前の請求日付の取得方法のいずれかを未解決として残していれば pass。観測方法を確定済みとして書いていれば fail。

`node_modules` 未インストールや実 DB 不在を Prerequisites に挙げていること、1 つの AC の期待値を複数の観測に分けて書いていることは fail としない。
