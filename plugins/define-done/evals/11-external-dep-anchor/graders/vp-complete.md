---
type: llm
focus: {source: file, path: repo/plans/billing-date.md}
weight: 0.5
---
計画の `## Verification Plan` を見る。`## Acceptance Criteria` の全ての AC-ID が `## Verification Plan` の `- AC IDs:` 行に並び、AC ごとに `### AC-NNN` のエントリがちょうど 1 つあり、どのエントリも空でない `- Oracle:`、`- Evidence anchors:`、`- Prerequisites:`、`- Required effects:` を持つなら pass。`## Verification Plan` が無い、エントリの無い AC がある、またはこの 4 項目のどれかが欠けたエントリがあれば fail。AC の件数や ID の番号が元の計画と違うことは fail としない。
