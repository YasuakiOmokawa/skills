---
type: llm
focus: {source: file, path: plans/session-store.md}
---
この設計書について、次のどちらかを満たすなら pass。

- `## MECE Review` が、外部ストアの接続先を与える環境変数を `config/env.example` に記載することが実装タスクに無いことを、欠落として挙げている。
- `config/env.example` への記載を、規約として範囲外 (enforce-conventions で担保する、などの趣旨) と返している。

`config/env.example` というファイルを名指ししていることが必要。「環境変数を設定する」「デプロイ時に注入する」だけなら fail。変数名は問わない。
