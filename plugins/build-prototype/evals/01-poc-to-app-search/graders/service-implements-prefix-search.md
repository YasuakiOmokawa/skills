---
type: llm
focus: {source: file, path: app/search/service.py}
---
The file adds prefix search to the service layer. The query is trimmed and lowercased or case-folded before matching, either inline or through a helper. Matching candidates come back as a list. An empty or non-matching query yields an empty list. The file reaches records only through the store object passed to the service and never opens data.json itself. Whether the old exact-match method is kept does not matter. Pass if these hold.
