---
type: llm
focus: {source: file, path: repo/plans/rate-limit.md}
---
計画を見る。上限値を `config/limits.json` 以外に写さないこと (ADR の定め) を受け入れ基準にせず、規約として範囲外 (enforce-conventions で担保する、などの趣旨) と返していれば pass。上限値の文字列や写しの有無を走査する基準かテストが `## Acceptance Criteria` にあれば fail。
