---
type: regex
target: {source: file, path: repo/src/shipping-label.test.ts}
match: contains
flags: s
---
"〒123-4567 葵 様"\);.*name: "葵" \}\), null\);
