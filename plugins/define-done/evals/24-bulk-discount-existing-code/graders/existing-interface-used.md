---
type: llm
focus: trace
---
Write か Edit で `repo/test/` の下に書かれた受け入れテスト (`*.acceptance.test.js`) と土台 (`repo/test/harness/`) を見る。既存の試験が固定する `createCart`・`add`・`total` を通してカートの合計を観測していれば pass。`src/cart.js` の中の新しい関数や内部の値を直接呼んで観測していれば fail。
