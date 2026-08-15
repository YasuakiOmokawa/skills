---
name: apply-findings
description: Use after code review or before committing to apply mechanically safe findings and report judgment calls; use review-only when the user asks for no edits or for another PR to be inspected.
---

Apply only behavior-preserving findings whose exact patch can be guarded. Leave design and product decisions unchanged.

## Scope and mode

Resolve scope in this order:

1. files or PR explicitly named by the user;
2. staged and unstaged task changes;
3. current branch versus the repository's verified default/base branch.

If nothing changed, report that and stop. Do not include unrelated dirty files.

An explicit review-only/no-edit request or inspection of another contributor's PR without edit authorization means **review-only**. Authorship, Git user name, tool availability, and branch ownership do not grant or remove edit authority.

When a PR head differs from the current checkout, inspect it in an isolated temporary worktree and verify its tracked files are unchanged before removal. Do not switch the user's active checkout. If remote metadata is unavailable, use a supplied/local head and state what remains unknown.

## Collect findings

Use, when available:

- findings from the preceding code review;
- repository-local explicit instructions applicable to changed files;
- configured lint diagnostics;
- clear majority conventions in the same file, then sibling files, excluding the target itself.

If no preceding review exists, label a fallback review and inspect the diff for correctness, security/authorization, error paths, and applicable repository rules. Do not invoke another review workflow implicitly.

Before classifying, reread the current source/target and revalidate every finding's exact diagnostic or reference predicate. If its location or evidence no longer matches, mark it `stale`, never auto-apply it, and report the unavailable evidence.

A convention is mechanically decisive only when an explicit rule names it, comparable occurrences in the target file give one style at least a two-thirds majority, or sibling files excluding the target file give one style a strict majority. Ties, a single example, and absent peers are judgment calls or no finding.

Run only project-configured lint commands. Do not fall back to globally installed tools. First collect diagnostics without fixes. If an autofix is considered, isolate its patch and discard any hunk outside changed lines or conflicting with the selected convention.

## Classify

Auto-apply only when all are true:

- the change is local and behavior-preserving;
- the exact affected references are known;
- a relevant lint, syntax, or focused test guard exists and can run;
- the patch touches no pre-existing user hunk outside scope.

Typical candidates are changed-line lint fixes, deterministic convention alignment, and unreachable private/dead-test scaffolding with a complete reference scan. Reflection, dynamic dispatch, public APIs, partial mock removal, newly added unreferenced files, validation/authorization logic, interfaces, responsibility splits, and ambiguous naming remain unapplied proposals.

For dead mocks, extract every removed production identifier, search implementation and tests including dynamic/reflection patterns, and remove the mock only when all identifiers are gone and a focused test passes. Otherwise propose the exact partial/full change.

In review-only mode, apply nothing. Mark a finding as otherwise qualifying only from a deterministic diagnostic or complete reference scan plus an available relevant guard; report that the post-patch guard was not run.

## Apply and guard

Apply candidates as separate minimal logical batches and track the exact hunks created by each batch. After each batch, rerun the candidate-relevant lint/syntax/test guard and re-evaluate findings invalidated by earlier edits. The candidate guard must pass; record unrelated pre-existing diagnostics separately instead of treating them as candidate failures. If any exact edit in a batch or its guard fails, remove only the hunks already created by that batch, keep earlier passing batches, reclassify the failed batch's finding as a proposal, and report later findings as unprocessed. If that exact rollback cannot be isolated, stop and report the remaining hunks without reverting anything broader. Never revert unrelated or pre-existing changes.

If no passing guard is available, do not auto-apply. Report `lint 未設定` or `テスト未検証` as an unchecked guard, not as a finding.

Never stage, commit, push, or create a PR unless that action was separately requested.

## Report

Concise output contains:

- every applied or unapplied item with `source_kind`, `source_detail`, and absolute source/target location; an item missing any field is incomplete;
- auto-applied patches with guard result;
- unapplied findings ordered by severity: critical = concrete bug/data/security/authorization failure; major = material design or maintainability risk; minor = nonbehavioral polish;
- unchecked guards and unavailable evidence.

Merge duplicate findings only when they require the same action. When no judgment items remain, state that the scoped checks found none. Otherwise stop after the list without asking whether to commit or proceed.
