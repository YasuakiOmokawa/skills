---
type: llm
focus: {source: file, path: repo/plans/no-app-env.md}
---
計画を見る。製品コードに `APP_ENV` が残らないこと (S-1) を受け入れ基準にせず、`## MECE Review` の要求の表がそれを規約として範囲外 (enforce-conventions で担保する、などの趣旨) と返し、`## Acceptance Criteria` に `APP_ENV` の文字列の有無を走査する基準が無く、`- Gate:` の行がこの要求を理由に ready を外していなければ pass。どれかが欠ければ fail。
