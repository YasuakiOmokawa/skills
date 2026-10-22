---
type: llm
focus: {source: file, path: billing/retry/design-doc.md}
---
Two decisions are open: whether the retry intervals are constants or configuration, and whether the failure notification goes to an individual or a team channel. Pass if, for both, the document states where or when the decision will be made (for example in the implementation PR, a later stage, or by updating this document), not only who decides. Fail if either one has no stated destination.
