---
type: llm
---
plan の構造不備の報告を見る。次を両方指摘していれば pass。

- `- AC IDs:` 行に、Acceptance Criteria に存在しない AC-005 が含まれている。
- Verification Plan に AC-003 の entry (`### AC-003`) が無い。

どちらか一方しか指摘していなければ fail。指摘の言い回しや順序は問わない。
