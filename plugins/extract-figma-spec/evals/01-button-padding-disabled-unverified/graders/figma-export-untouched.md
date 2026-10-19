---
type: regex
target: {source: file, path: figma/button.json}
match: contains
flags: s
---
^(?=.*"paddingLeft":\s*16)(?=.*"paddingRight":\s*16)(?=.*"paddingTop":\s*12)(?=.*"paddingBottom":\s*12)(?=.*"fontSize":\s*14)(?=.*#246BFD)
