---
type: llm
focus: {source: file, path: plans/session-store.md}
---
この設計書について、次のどちらかを満たすなら pass。

- `## MECE Review` が、外部ストアの接続先を与える環境変数を `config/env.example` に記載することが実装タスクにも受け入れ基準にも無いことを、欠落として挙げている。
- 受け入れ基準が、その環境変数が `config/env.example` に記載されていることを観測する。

`config/env.example` というファイルを名指ししていることが必要。「環境変数を設定する」「デプロイ時に注入する」だけなら fail。変数名は問わない。
