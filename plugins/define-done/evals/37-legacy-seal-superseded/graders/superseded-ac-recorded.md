---
type: llm
focus: {source: file, path: repo/plans/remove-by-zero.md}
---
計画の `## MECE Review` 節を見る。前の封の基準「数量 0 で入れようとすると拒む」(AC-001、`test/quantity.acceptance.test.js`) を、この計画の要求が置き換える既存の基準として挙げていれば pass。挙げていない、または前の基準に触れずに Gate を ready にしていれば fail。
