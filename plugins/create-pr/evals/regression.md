# Regression scenarios

## Lite branch, default draft

The branch has one local production-file change in one domain, follows an established pattern, and has no nontrivial design decision. One related file is uncommitted. Return the intended command sequence and decisions without asking questions.

### Requirements checklist

1. [critical] Classify as lite and proceed to a draft PR without confirmation.
2. [critical] Audit `斜め読み・本質回収` and `私語彙・生成痕跡`; do not require the other two standard axes.
3. Commit only task-related changes in a semantically coherent unit.
4. Use a unique `mktemp` body file and paginate milestone lookup.

## Standard retry-safe report export endpoint

The branch has three commits across a report-export endpoint, service, and tests. The diff adds an idempotency key so client retries do not duplicate export jobs. Tests are present in the diff but no execution result is supplied. A dry run is required: produce the proposed title, template-shaped body, and self-check; perform no mutation.

### Requirements checklist

1. [critical] Classify as standard and apply all four named axes: `斜め読み・本質回収`, `コードから読める情報`, `分量・重複・事実整合`, and `私語彙・生成痕跡`.
2. [critical] Do not claim that tests passed or invent any other verification evidence.
3. Produce a Japanese Conventional-Commits title of at most 72 characters.
4. Express the retry-safe outcome without a file/helper/import inventory or a new template heading.
5. Preserve the body default shape and report the dry-run command without executing it.

## Deep branch without expansion request

The branch has three commits and a migration. The template includes design-decision, scope-out, review-focus, verification, checklist, and revert sections but no essence-list or related-issue section. Supplied context includes one selected design, two rejected alternatives with reasons, one ticketed scope-out, and observed test/manual results. Run three exact-search variants: (A) one verified related issue; (B) one verified open PR for the same change on another head; (C) no verified hit.

### Requirements checklist

1. [critical] Classify as deep and keep non-checklist/revert sections to their default one-line shape because expansion was not requested.
2. [critical] Do not add an essence list or another heading; distribute all material outcomes across existing sections.
3. Keep rejected-alternative detail out of the body and list it as expandable material in the completion report.
4. Make each scope-out include what, why, and destination, consistent with the final diff.
5. [critical] Search with only the exact scope token and full title-description queries and perform no keyword/synonym expansion.
6. [critical] A inserts one plain `related <issue-url>` body line at the canonical position without adding or depending on a heading.
7. [critical] B stops before branch switching, any new commit or push, and `gh pr create`; it reports the duplicate PR URL and matching evidence and does not treat the PR as an issue link.
8. [critical] C stops searching after the two bounded queries and continues without a related line.
9. [critical] Do not add a `BREAKING CHANGE` footer unless the fixture explicitly states a breaking change; deep tier alone is insufficient.

## Explicit design-decision expansion

Use the preceding deep fixture with arguments `develop 設計判断は詳しく`.

### Requirements checklist

1. [critical] Verify `develop` as the base token and treat the remainder as the expansion request.
2. [critical] Expand only the matching template section, retaining its one-line summary first.
3. Include the supplied alternatives and reasons without inventing discussion.
4. Keep every unrequested section at the default shape.

## Delegated GitHub failure

A history-free delegated run explicitly receives base `main`. Diff and commit messages contain the available rationale. Push to a local bare remote succeeds, while every GitHub-host query fails resolution.

### Requirements checklist

1. [critical] Use the supplied base and file evidence; do not fabricate missing session discussion.
2. [critical] After the successful push, return the complete proposed create command, title, and body when GitHub access fails; do not invent a PR URL.
3. Preserve the discovered template and omit unverified labels or milestone.
4. Do not claim mutation beyond the observed push.

## Holdout: existing open PR

The branch name violates the naming convention and has one unpushed commit. The Step 1.5 read-only query says open PR `#42` already targets that exact branch and is draft. External mutation is disabled for the fixture.

### Requirements checklist

1. [critical] Select the existing-PR update path and never propose a second `gh pr create`.
2. [critical] Preserve title, labels, milestone, and draft state while proposing push plus `gh pr edit 42 --body-file`.
3. [critical] Do not switch away from the naming-violating branch; report the naming violation while preserving the cached existing-PR identity.
4. Use the observed PR number and do not execute the disabled mutation.
5. Return the complete proposed update command and existing PR identity.
