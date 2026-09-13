---
type: llm
focus: {source: file, path: plans/notify.md}
---
`## Verification Plan` の `### AC-001`〜`### AC-003` の 3 entry を見る。次をすべて満たすなら pass。

- 各 entry に `- Oracle:`、`- Evidence anchors:`、`- Prerequisites:`、`- Required effects:` がそれぞれ 1 行ずつあり、どれも空でない。
- 各 `- Oracle:` に期待値がある (戻り値と `log.record` の呼び出し内容または回数が具体的に書かれている)。「動く」「正しい」だけの記述があれば fail。
- 各 `- Required effects:` に、検証時に実行する具体的な操作 (テストの実行、`sendNotification` の呼び出し、`log.reset()` など) がある。「確認する」だけで操作が無ければ fail。

`node_modules` 未インストールを Prerequisites に挙げていること、1 つの AC の期待値を複数の観測に分けて書いていることは fail としない。
