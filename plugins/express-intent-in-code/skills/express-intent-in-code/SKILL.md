---
name: express-intent-in-code
description: Clarifies intent in existing code when unclear names, responsibilities, comments, or lint suppressions need behavior-preserving cleanup.
---

- Use the supplied code, behavior observations, and verification interface to identify each unclear responsibility, then perform the smallest authorized restructuring and renaming that makes it readable from the code; do not stop at suggesting names or structure.
- Preserve supplied inputs, outputs, and externally observed behavior. Keep feature and policy changes outside this cleanup, and leave any restructuring that requires an unauthorized target unapplied.
- Treat supplied editable fixtures, mock interfaces, and fixed operation responses as observable task evidence. Distinguish a write submitted from a change verified by its response, readback, or observed diff; never infer success from submission alone.
- After verified edits, run fresh lint and the supplied behavior checks, including every identified boundary case, and compare observed outputs with the pre-change evidence.
- Remove only suppressions proven unnecessary by the fresh lint result; retain explanations for constraints that the code still does not express.
- Limit edits to authorized code and corresponding verification files.
- Report the verified diff, lint and behavior-check results, out-of-scope restructuring, failed or unverified writes, and any behavior that remains unverified.
