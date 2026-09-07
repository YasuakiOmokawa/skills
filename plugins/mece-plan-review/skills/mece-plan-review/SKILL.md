---
name: mece-plan-review
description: Compare a plan and acceptance criteria with specification and code evidence when a MECE coverage review or an explicitly authorized review update is requested.
---

## Purpose

Decide whether one current plan and its acceptance criteria cover the specification and the code without omission, duplication, or contradiction, and record that decision as a gate the next stage can trust. The review is only as good as the evidence it actually read, so every conclusion names the evidence behind it and every comparison it could not make is reported as unverified rather than silently assumed.

## Preconditions

- The current plan is exactly one readable resource supplied inline or through an authorized read. A whole-resource read counts as complete unless the tool marks it truncated or paginated; a range, snippet, or unfinished pagination is partial. A missing, partial, unreadable, or ambiguous plan is an upstream defect: report it and produce no review.
- A `##` section runs from its heading to the next `##` heading or end of document. The plan must contain exactly one `## Acceptance Criteria` section consisting, apart from blank lines, only of rows `- [ ] AC-NNN: <criterion text>` with unique IDs. Duplicate sections, duplicate IDs, or rows of any other shape are upstream defects: report every defect found and produce no gate or review.
- An update is requested only when the request asks to write the review into the current plan. It is authorized only when that same plan is the exact named destination and a write interface exists. Prior `## MECE Review` sections and anything labeled as a prior review are never evidence.

## What the review must establish

Compare every current criterion, in both directions, against every specification source and every code source the request, plan, or criteria explicitly name. A source is an exact artifact, link target, path, code span, or symbol; a bare domain term, directory, or scalar is not one. Both categories must be represented, and the evidence set is fixed before any evidence is read so that later reads cannot quietly widen or narrow it.

Because omissions hide in code the plan never mentions, extend the code evidence inside the current repository to the definitions that criterion-relevant branches call, and, for any definition whose behavior is shared, to every repository-local site that calls or references it, even sites the plan does not name. Stop at repository boundaries and cycles. Anything absent, external, or ambiguous is an inaccessible required comparison, not a non-finding.

For each criterion, record whether each source and plan item shows presence, absence, contradiction, or inaccessibility. Then check the obligations the evidence itself imposes back against the criteria: reachable async lifecycle outcomes, direct consumers of shared behavior, boundary ownership and exhaustiveness, and evidence that rests on absence, time, count, concurrency, or non-impact. A negative claim is supported only when a positive witness shows the path and observation boundary completed and a deterministic failure signal or controlled seam exists; otherwise it is an omission when the evidence supports that, and unverified when it does not. Report reverse-check gaps by those four families, at most one gap per family with every concrete omission named inside it, and say nothing about families that are covered. Never declare a source non-applicable unless the source itself excludes the criterion. Finish every comparison that inaccessible evidence does not block.

## Gate

Derive one gate from the evidence comparison alone: `blocked` when a supported omission, duplication, or contradiction remains; otherwise `unverified` when any required comparison lacked evidence; otherwise `ready`. Update-destination problems never change the gate.

## Output

Return a review containing item-level correspondence, supported findings, the upstream corrections required, and the unverified comparisons with their scope. When the review is embedded in the plan it uses only `###` or deeper headings and contains no line beginning `- AC IDs:` or `- Gate:`.

When an update was requested and authorized and the plan holds at most one `## MECE Review`, replace that section (or insert one) immediately after the Acceptance Criteria section and before the next `##` section, containing exactly one `- AC IDs: <ascending IDs joined by ", ">` row, exactly one `- Gate: ready|blocked|unverified` row, and the review; leave every other line of the plan untouched. When an update was requested but not authorized, or more than one review section exists, write nothing, report the destination defect, and still return the review if the input was valid.

Report the write honestly: `review-update submitted: yes|no` records whether the write was issued at all; `review-update operation: succeeded|failed|unverified|not-submitted` records only what the interface's final, unambiguous response established, so a timeout, error, missing, or partial response is `unverified`; `review-update content: verified|mismatch|unverified|not-submitted` comes only from a separate authorized readback of the exact destination compared against the submitted text, never from the write response itself. Issue the write and the readback once each; a repeat cannot add evidence and can add damage. Leave product code and all other external state unchanged.
