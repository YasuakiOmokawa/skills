---
type: regex
target: {source: file, path: repo/plans/tags.md}
match: contains
---
- D1: 重複を除く処理を `uniq\(values\)` として `src/tags\.js` から export し、`tagsInUse` がそれを使う。\n\n## 3\. 変更対象\n\| ファイル \| 変更 \|\n\|---\|---\|\n\| src/tags\.js \| `uniq` を足して export し、`tagsInUse` が使う \|
