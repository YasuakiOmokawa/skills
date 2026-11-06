---
type: llm
focus: {source: file, path: repo/test/reset.acceptance.test.js}
---
受け入れテストのファイルを見る。`resend` か `request` の回数に上限を置き、上限を超えたらリンクを送らない (または別の画面を返す) ことを期待するテストが 1 件でもあれば fail。上限に触れるテストが無ければ pass。
