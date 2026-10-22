---
type: llm
focus: {source: file, path: billing/retry/design-doc.md}
---
Two decisions are open: whether the retry intervals are constants or configuration, and whether the failure notification goes to an individual or a team channel. Pass if, for both, the document states what the implementation does until the decision is made (constants, and notifying the individual, as the prototype did). Fail if either one has no stated interim behaviour.
