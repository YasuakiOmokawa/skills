---
type: llm
focus: {source: file, path: docs/billing-design.md}
---
The retry section itself states the retry limit (3), the retry intervals (1 min / 5 min / 30 min), and that the idempotency key is the invoice_id held fixed across attempts. Pass if all three values appear in the document body. Fail if any of them is only available by following a reference to poc.md.
