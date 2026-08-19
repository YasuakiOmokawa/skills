---
name: finalize-plan
description: Finalize an implementation-ready plan when acceptance criteria, MECE readiness, work order, and verification intent must be settled before implementation.
---

## Workflow

- Resolve the writable current plan and require exactly one `## Acceptance Criteria` section with unique `- [ ] AC-NNN:` rows, exactly one `## MECE Review` whose `- AC IDs:` equals the sorted current AC-ID set and whose gate is `ready`, and at most one existing `## Verification Plan`. If a required section is absent or duplicated, the verification section is duplicated, IDs are duplicated or stale, or the gate is `blocked` or `unverified`, do not finalize; report the upstream work needed.
- Build the complete requested plan content from its acceptance criteria and coverage evidence rather than returning category labels or coverage claims. Order concrete plan items by execution dependencies, and in each item state the change target, dependency or predecessor, linked criterion, verification method, and unresolved prerequisite.
- Upsert exactly one `## Verification Plan` in the same plan with `- AC IDs: <sorted current IDs>`. For every AC-ID, create exactly one `### AC-NNN` entry containing one nonempty `- Oracle:`, `- Evidence anchors:`, `- Prerequisites:`, and `- Required effects:` field. Derive the oracle from the criterion; record only known repository or runtime entry points as evidence anchors; preserve unresolved prerequisites; and record the minimum actions or state changes needed to observe the oracle as required effects. Required effects describe later authorization needs and never grant them.
- Do not invent missing prerequisites; show their effect on sequencing and leave their resolution as a handoff.
- Submit the finalized plan only to its exact authorized destination. Keep downstream verification intent exclusively in its `## Verification Plan`; do not create a second verification source. Treat an explicitly supplied mock interface, fixed response, or local fixture as observable task evidence: carry out the authorized submission and distinguish the submitted content from the observed response or readback.
- Report only what the observed evidence establishes. Do not promote a submission to a verified write, or a verified write to verified content, without evidence for that claim; leave product code and external state unchanged.
- When no destination change is explicitly authorized, return the content only in the response.

## Completion

Return the complete plan, AC-to-verification correspondence, and evidenced write status. If the plan or any required AC mapping is not verified, report partial completion and the affected criteria or prerequisites.
