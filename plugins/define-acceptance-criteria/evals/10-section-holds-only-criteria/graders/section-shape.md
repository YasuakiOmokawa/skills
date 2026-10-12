---
type: llm
focus: {source: file, path: plans/export.md}
---
plans/export.md を評価する。`##` 節はその見出しから次の `##` 見出しか文書末尾までとする。次がすべて成り立てば pass。
1. `## Acceptance Criteria` 節がちょうど 1 つある。
2. その節の中の行は、空行と `- [ ] AC-NNN: ` で始まる行だけで、表の行 (`|` で始まる行)・`###` 見出し・注記の段落を含まない。
3. S-1〜S-3 と AC の対応表が、`## Acceptance Criteria` 節の外 (別の `##` 節) にある。
1 つでも欠ければ fail。
