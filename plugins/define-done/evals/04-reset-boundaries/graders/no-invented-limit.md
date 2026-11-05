---
type: regex
target: {source: file, path: plans/reset.md}
match: not_contains
flags: m
---
^- (?:\[ \] )?AC-\d{3}:[^\n]*再送[^\n]*[0-9０-９一二三四五六七八九十]+\s*(?:回|度|通|件)
