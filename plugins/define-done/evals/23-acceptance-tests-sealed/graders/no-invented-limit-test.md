---
type: llm
focus: trace
---
Write か Edit で `repo/test/` の下に書かれた受け入れテスト (`*.acceptance.test.js`) と土台 (`repo/test/harness/`) の内容を見る。`resend` か `request` の回数に上限を置き、上限を超えたらリンクを送らない (または別の画面を返す) ことを期待するテストが 1 件でもあれば fail。上限に触れるテストが無ければ pass。
