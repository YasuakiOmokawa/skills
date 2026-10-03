---
name: implement-plan
description: Implement a prepared plan whose Verification Plan maps every acceptance criterion, driving each test-observable criterion through red, green, and refactor in the plan's dependency order.
---

## Workflow

1. Resolve the current plan. Require exactly one `## Acceptance Criteria` of unique `- [ ] AC-NNN:` rows, exactly one `## MECE Review` with one `- AC IDs:` row and one `- Gate:` row whose value is `ready`, and exactly one `## Verification Plan` with one `- AC IDs:` row. Both ID rows list the current IDs in ascending order joined by `, `, and the Verification Plan has one `### AC-NNN` entry per ID, each carrying `Oracle`, `Evidence anchors`, `Prerequisites`, and `Required effects`. When any part is missing or disagrees, stop before editing code and report every defect; the mapping comes from the plan, never from the implementation.
2. Run the existing test suite, lint, and type checks once and record the baseline. A check that is already red is reported, and each later red is judged against it.
3. Take the plan's work items in their dependency order. For each item, handle its linked criteria by the kind of oracle, one criterion at a time.
4. For an oracle a test can observe, run one cycle per test:
   - **Red.** Write one test at the seam its `Evidence anchors` name, through the public interface, with the expected value taken from the oracle or a worked literal. Run it and confirm it fails because the behavior is absent; a failure from imports, types, or setup is fixed before the cycle counts as red.
   - **Green.** Make the smallest change that passes it. Run the new test and every test the change can reach.
   - **Refactor.** With everything green, remove the duplication and unclear names this cycle's diff introduced, one change at a time, rerunning the tests after each. The step is done when the cycle's diff has no duplicated logic and every new name states its intent. Record smells in pre-existing code as report items instead of editing them.
   Start the next test only after the refactor step is done.
5. For an invariant, absence, or static tripwire oracle, write the check, then prove it can go red: introduce one temporary violation, observe the check fail for that violation, revert it, and observe the check pass again.
6. For an oracle that needs a running system, a rendered UI, or external state, implement the work item, run the tests it reaches, and hand the criterion to verification with its prerequisites. Leave its result open; a prerequisite needed only to observe the oracle does not block implementation.
7. When an item needs a change outside the plan, an oracle contradicts the code, or an unresolved prerequisite blocks the implementation itself, stop that item and every item that depends on it, and report the conflict; keep the plan and its criteria as written.
8. Keep refactor changes separable from behavior changes. Commit only when the request authorizes it, and then commit them separately.
9. Run the full test suite and the repository's lint and type checks at the end.

## Completion

Account for every AC ID in exactly one state: tested, tripwire proved, handed to verification, or stopped; an ID no work item links is stopped with that gap as its conflict. Report, per criterion: the test or check added, the observed red and its reason, green, and the refactors applied; the tripwire red proofs; criteria handed to verification with their prerequisites; stopped items with their conflicts; recorded pre-existing smells; and the final suite, lint, and type-check results against the baseline. Implementation ends here; acceptance of the criteria is the verification step's result.
