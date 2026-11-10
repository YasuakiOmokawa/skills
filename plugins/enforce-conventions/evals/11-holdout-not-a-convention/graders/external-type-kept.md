---
type: regex
target: {source: file, path: repo/src/article-import.ts}
match: contains
---
publishedAt:\s*(?:string\s*\|\s*null|null\s*\|\s*string)
