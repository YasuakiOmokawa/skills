---
name: create-pr
description: Create or update the pull request associated with the current branch when the user asks to open it, revise its content, or explicitly make it reviewable.
---

# Workflow

1. Resolve the current repository and branch from available context; for creation, also resolve the base branch, title, and information needed for the body.
2. Before creating a new pull request, inspect the worktree, the complete change set against the base, and every commit's diff. Define each commit by one reviewable purpose and its dependencies, keep an implementation with its tests or fixtures, separate authorized but independent in-scope changes, exclude unauthorized or out-of-scope changes, and order dependent commits coherently. Use one commit only when the authorized change is genuinely indivisible, and record that reason.
3. Make the authorized local history match those boundaries before publishing it. Rebuild unpublished commits only when that rewrite is explicitly authorized. Never rewrite published or shared history. Never force-push without explicit authorization, and never use force-push to rewrite published or shared history. Otherwise hold creation and distinguish missing authorization for an unpublished rewrite from published non-reviewable history that cannot be rewritten.
4. Hold creation when required creation information or authorization is missing or ambiguous, or when the inspected history cannot meet the reviewable boundaries without rewriting published or shared commits. State each blocker and the safe non-rewrite path needed to proceed.
5. Locate any pull request associated with the current branch and carry out the authorized creation or update rather than stopping at its description, using any explicitly supplied mock interface, fixed response, or local fixture as the observable task environment; record the operation as submitted separately from any result verified by the supplied evidence, and never infer success from an absent response.
6. Create a new pull request as a draft unless the user explicitly requests a reviewable state, and preserve an existing state unless its change is explicitly requested.
7. Limit updates to the current branch's pull request and the requested fields; keep all other pull requests, merge state, close state, and branches unchanged.
8. Before push or creation, verify the resulting commit order and each commit's diff; verify each pull request operation only from returned or subsequently observed state, including the base branch, title, affected content, and final draft or reviewable state.
9. Pair any observed pull request number with its exact returned URL without reconstructing absent values, and record partial results and permission failures without claiming unsupported changes.
10. Report the verified commit boundaries, submitted operations, supported final state, applied changes, failures with reasons, and unresolved outcomes.
