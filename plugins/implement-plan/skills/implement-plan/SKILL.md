---
name: implement-plan
description: Implement a prepared plan whose Verification Plan maps every acceptance criterion, driving each test-observable criterion through red, green, and refactor in the plan's dependency order.
---

## Workflow

1. Resolve the current plan. Require one `## Acceptance Criteria` of `- [ ] AC-NNN:` rows, one `## MECE Review` whose `- Gate:` value is `ready`, and one `## Verification Plan` whose `- AC IDs:` row lists the same IDs with one `### AC-NNN` entry each carrying `Oracle`, `Evidence anchors`, `Prerequisites`, and `Required effects`. When any part is missing or disagrees, stop before editing code and report every defect; the mapping comes from the plan, never from the implementation.
2. Run the existing test suite once and record the baseline. A baseline that is already red is reported, and each later red is judged against it.
3. Take the plan's work items in their dependency order. For each item, handle its linked criteria by the kind of oracle, one criterion at a time.
4. For an oracle a test can observe, run one cycle per test:
   - **Red.** Write one test at the seam its `Evidence anchors` name, through the public interface, with the expected value taken from the oracle or a worked literal. Run it and confirm it fails because the behavior is absent; a failure from imports, types, or setup is fixed before the cycle counts as red.
   - **Green.** Make the smallest change that passes it. Run the new test and every test the change can reach.
   - **Refactor.** With everything green, remove the duplication and unclear names this cycle's diff introduced, one change at a time, rerunning the tests after each. The step is done when the cycle's diff has no duplicated logic and every new name states its intent. Record smells in pre-existing code as report items instead of editing them.
   Start the next test only after the refactor step is done.
5. For an invariant, absence, or static tripwire oracle, write the check, then prove it can go red: introduce one temporary violation, observe the check fail for that violation, and revert it.
6. For an oracle that needs a running system, a rendered UI, or external state, implement the work item, run the tests it reaches, and hand the criterion to verification with its prerequisites. Leave its result open.
7. When an item needs a change outside the plan, an oracle contradicts the code, or a prerequisite is unresolved, stop that item and report the conflict; keep the plan and its criteria as written.
8. Keep refactor changes separable from behavior changes. Commit only when the request authorizes it, and then commit them separately.
9. Run the full test suite and the repository's lint and type checks at the end.

## Completion

Report, per criterion: the test or check added, the observed red and its reason, green, and the refactors applied; the tripwire red proofs; criteria handed to verification with their prerequisites; stopped items with their conflicts; recorded pre-existing smells; and the final suite, lint, and type-check results against the baseline. Implementation ends here; acceptance of the criteria is the verification step's result.
