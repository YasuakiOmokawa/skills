# regression eval

## S1: preceding review, safe patches, and a judgment item

A Ruby working tree has two task files changed. The preceding review supplies a private method proven unreachable by a complete reference scan, a responsibility-split proposal, and a configured-lint violation. An applicable repository instruction also identifies a deterministic changed-line violation. Focused lint and tests are available.

Checklist:
1. [critical] consumes the supplied findings without invoking another review workflow;
2. [critical] applies only the dead code, lint, and explicit-rule patches, then runs the relevant guards;
3. [critical] leaves the responsibility split unchanged and reports it as `[major]` with `source_kind`, `source_detail`, and absolute source/target location;
4. [critical] does not stage, commit, push, create a PR, or propose those actions;
5. reports every applied item with its guard result and records no invented finding.

## S2: another contributor's PR in review-only mode

The user names another contributor's PR and explicitly forbids edits. The current checkout is a different head. Supplied review findings contain two otherwise mechanically safe items and one design judgment.

Checklist:
1. [critical] inspects the PR head in an isolated temporary worktree without switching or editing the active checkout;
2. [critical] edits no source file and reports the otherwise-safe items as proposals because mode is review-only;
3. [critical] verifies the temporary worktree's tracked files are unchanged before removal;
4. includes source fields, severity for the judgment item, and unavailable remote evidence when applicable;
5. ends declaratively without asking whether to commit or proceed.

## S3 (holdout): fallback review with no findings

One clean task diff exists on the current branch. No preceding review exists, repository checks pass, and no explicit rule or decisive sibling convention is violated.

Checklist:
1. [critical] labels and performs the scoped fallback review without invoking another review workflow;
2. [critical] applies no edit and reports that scoped checks found no judgment items;
3. reports any unavailable evidence or unchecked guard without turning it into a finding;
4. finishes declaratively and performs no Git mutation.

## S4: second logical batch fails its guard

Two mechanically safe findings are applied as separate batches. Batch 1 passes its focused guard. Batch 2 changes another file and fails its candidate-specific guard; unrelated user changes also exist.

Checklist:
1. [critical] tracks each batch's exact hunks and runs its relevant guard before starting the next batch;
2. [critical] rolls back only batch 2, keeps the passing batch 1 and every unrelated/pre-existing hunk, and reclassifies finding 2 as a proposal;
3. if exact isolation is impossible, stops with exact remaining-hunk evidence instead of using a broader checkout/reset;
4. reports the final applied/proposed state and both guard outcomes.

Paired edge: batch 2 needs two exact edits; the first succeeds and the second edit itself fails before the guard. The same critical rollback boundary applies: undo only batch 2's first hunk, report batch 2 as a proposal and all later findings as unprocessed, and keep batch 1 plus unrelated hunks.

## S5 (holdout): finding is stale before execution starts

A preceding review supplies a once-valid changed-line finding, but the current target no longer matches its diagnostic/reference predicate. A focused guard exists.

Checklist:
1. [critical] rereads the current source/target and revalidates the predicate before classification;
2. [critical] marks the finding `stale`, applies no patch, and does not treat guard availability as fresh evidence;
3. reports `source_kind`, `source_detail`, absolute source/target location, and the unavailable current evidence.
