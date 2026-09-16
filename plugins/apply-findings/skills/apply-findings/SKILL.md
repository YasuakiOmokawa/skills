---
name: apply-findings
description: Applies review findings when a request authorizes mechanically safe edits or asks for concrete edit candidates without changing files.
---

- Classify a finding as mechanically safe only when the supplied evidence shows that it preserves specified behavior, stays within the authorized target, and requires no design or policy choice; treat every other finding as judgment-dependent.
- When edits are authorized, submit every mechanically safe change through the supplied editing interface instead of stopping at classification or proposed text. Leave judgment-dependent findings unchanged.
- Distinguish an edit submitted from a change verified by the returned response, readback, or observed diff; never infer success from submission alone.
- Keep the observed diff limited to the authorized findings. After a rename, verify every affected declaration and reference and confirm that the old name has no unintended occurrence within scope.
- Grade every reported finding, including applied, deferred, and review-only candidates, with exactly one of `[critical]`, `[major]`, or `[minor]`: critical is must fix (a bug, data loss, or security/authorization failure); major is imo (a design or maintainability improvement with valid alternatives); minor is nits (behavior-preserving naming or style polish). Severity is independent of mechanical safety and edit authorization.
- Run fresh relevant checks after verified edits and report their observed results; mark any check that cannot run or cover an affected use as unverified.
- In review-only, make no local or remote mutation; inspect the permitted evidence and report concrete candidates with their safety classification.
- Report one ledger of every finding ordered critical → major → minor regardless of application status; each entry opens with its `[critical]`/`[major]`/`[minor]` tag, then the file location and finding, then its status (applied and verified / submitted but unverified / deferred with the decision factors needed to proceed / review-only candidate). After the ledger, report check results and any external-state change.
