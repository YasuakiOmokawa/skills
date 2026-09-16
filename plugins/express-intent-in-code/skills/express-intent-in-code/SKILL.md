---
name: express-intent-in-code
description: Reduces comments in existing code by moving their intent into names, structure, types, and checks when a file or diff carries comments that restate or stand in for what the code could express itself.
---

- Treat every comment in the supplied code as a candidate for removal and decide each in this order: delete it when the code already says the same thing; move it into the code by renaming, extracting a function, introducing a named constant or type, or adding an assertion or test, then delete it; keep it only when it states something the code cannot express, such as an external specification, a workaround for a defect elsewhere, or a deliberate trade-off chosen against the obvious alternative; a comment that ties this code to another place it must stay consistent with is such a constraint until the tie becomes a shared symbol or a test, so move it into a test or keep it.
- Apply the same order to unclear names and responsibilities even where no comment exists: perform the smallest restructuring and renaming that makes the intent readable from the code; do not stop at suggesting names or structure. Leave names that are already clear unchanged.
- Do not add comments during the cleanup, including for a constraint that the request or the edit reveals and no existing comment states: pin it with a test or assertion, and if neither can hold it, report it instead of writing it.
- Preserve supplied inputs, outputs, and externally observed behavior. Keep feature and policy changes outside this cleanup, including changes a comment or TODO asks for, and leave any restructuring that requires an unauthorized target unapplied.
- Distinguish a write submitted from a change verified by its response, readback, or observed diff; never infer success from submission alone.
- After verified edits, run fresh lint and the supplied behavior checks, including every identified boundary case, and compare observed outputs with the pre-change evidence.
- Remove a lint suppression only when the fresh lint result proves it unnecessary; a suppression that remains keeps the one-line reason the code still does not express.
- Limit edits to authorized code and corresponding verification files.
- Report the verified diff, each kept comment with the reason the code cannot express it, lint and behavior-check results, out-of-scope restructuring, failed or unverified writes, and any behavior that remains unverified.

