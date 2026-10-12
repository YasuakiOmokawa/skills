---
type: llm
focus: {source: file, path: repo/plans/rename.md}
---
repo/plans/rename.md の `## Acceptance Criteria` 節だけを評価する。次がすべて成り立てば pass。
1. S-2 (旧 path を指す記述が残らない) に対応する criterion がある。
2. その criterion の観測は、`.gitignore` が無視する file (`.cache/` など) を走査対象に含めない (`git grep --untracked` など、追跡中と未追跡の file だけを見る形)。
3. その criterion の観測に、無視された file も読む `grep -r` や `rg --no-ignore` の形を使っていない。
1 つでも欠ければ fail。
