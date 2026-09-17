---
type: llm
focus: {source: file, path: billing/retry/design-doc.md}
---
The document states retrying up to 3 times with a fixed idempotency key as an adopted design decision, gives a reason for it, and names at least one rejected alternative (pre-retry status lookup, or next-day batch re-billing). Pass if all three parts (decision, reason, rejected alternative) are present anywhere in the document, even if spread across sections.
