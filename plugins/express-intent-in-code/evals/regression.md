# express-intent-in-code regression

Run each fixed scenario with a fresh blank-context executor in an isolated fixture. Score the resulting diff and evidence. All `[critical]` items must pass. Run the hold-out only after tuning and do not tune against its result.

## Rename: mechanism to domain intent

Input: `bbox_xhtml` returns non-empty word boxes. Its only caller places signing anchors; the repository contains `SigningPosition` and the UI term `署名位置`. A comment records the external PDF coordinate origin.

1. [critical] All callers are inspected and their use is stated before renaming.
2. [critical] The name advances through honest what, hidden-premise removal, and purpose before using the existing signing-position domain term.
3. Empty-line filtering is expressed in the name, type, or a separate operation rather than left hidden.
4. The external-coordinate why remains at the relevant named definition; comments that restate mechanics or purpose are promoted and removed.
5. The chosen domain term cites repository evidence. No fixed candidate count or exploration diary is required.

## Comment promotion

Input: a function has a what-comment, a magic TTL explanation, a comment prohibiting direct comparison, and an ADR pointer. The same predicate is used by decision and display paths.

1. [critical] The what-comment is removed and TTL meaning is promoted to an intent-revealing constant.
2. [critical] The prohibition is promoted to one existing-style static check; a second check is not added without a distinct undetected failure mode.
3. The ADR pointer remains as a one-line canonical reference.
4. The shared one-line predicate remains because it prevents duplicated decisions across two contexts; it is not replaced by a defensive comment.
5. [critical] When one comment mixes an external API ordering constraint with nameable procedural detail, the external/order-dependent why remains at the named definition and only the procedural detail is extracted into an intent-named private.

## Rename without a grounded domain term

Input: `bbox_xhtml` returns non-empty word boxes and its callers establish the purpose `signature_anchor_boxes`, but no repository artifact supplies a narrower domain term.

1. [critical] The name stops at the grounded purpose rung and does not invent a domain term.
2. Caller evidence and the hidden non-empty premise remain explicit in the chosen code shape.

## Reuse and cohesion

Input: a selected finding targets a function that both notifies an approver and records an audit event. A sibling notification helper already exists; no shared audit abstraction exists elsewhere.

1. [critical] The existing notification helper is reused before new code is introduced.
2. [critical] Independently changing notification and audit effects are separated.
3. No speculative shared audit abstraction is extracted from one case.
4. Unrelated adjacent cleanup is absent, and callers/tests/comment references are updated and verified.

## Delegated finding filter

Input: delegation includes one naming finding and one unrelated performance finding.

1. [critical] Only the naming finding is transformed or explicitly declined with evidence.
2. The response reports the finding disposition, edited files, verification, and residual risk.
3. The performance finding does not expand the edit scope.

## Hold-out: no applicable finding

Input: run once as direct review-only and once as delegation, each containing only a dependency-version finding and no explicit naming, cohesion, comment, suppression, helper, or new-file target.

1. [critical] Both executions return `no-op: applicable findings 0` and make no edit.
2. It does not scan the entire diff for opportunistic renames or cleanup.
