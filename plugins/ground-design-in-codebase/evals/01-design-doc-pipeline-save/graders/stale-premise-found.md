---
type: llm
focus: {source: file, path: design.md}
---
design.md の `## Ground Review` 節だけを読み、次をすべて満たせば合格。
1. `###` 小節が 6 つあり、順序が「境界適合 → 重大な risk と影響 → 反証した risk 候補 → 推奨 → 未決事項 → 未検証の結論」に相当する (見出し語は日本語で言い換えてよい)。
2. 重大な risk として、設計 §2 の前提事実「validateSession は期限を検証する」が誤りであることを挙げ、その根拠として src/session.ts (署名のみ検証、期限検査は requireFreshSession に委譲) または src/middleware.ts の該当箇所を引いている。
3. その帰結として、/api/export が requireFreshSession を経由しないと期限切れ token を受け入れ、仕様 S-1 (または S-2) に違反することを具体的に述べている。
4. 節の本文が日本語で書かれている。
