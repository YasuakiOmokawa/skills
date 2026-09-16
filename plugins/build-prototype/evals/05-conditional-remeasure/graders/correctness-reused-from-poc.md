---
type: llm
---
The reply does not treat re-measuring the PoC's correctness result (20/20) as a requirement. Acceptable: citing the PoC result as reused evidence, not mentioning correctness at all, running the app's own unit tests, or re-checking correctness while naming a concrete difference from the PoC conditions as the reason (for example a change from casefold to lower). Fail only if the reply re-runs the PoC correctness benchmark without giving such a reason, or says the PoC's correctness result cannot be relied on.
