---
name: finalize-plan
description: Finalize an implementation-ready plan when acceptance criteria, MECE readiness, work order, and verification intent must be settled before implementation.
---

## Workflow

- Resolve the current plan and whether changing its exact destination is authorized. Require exactly one `## Acceptance Criteria` section that, apart from blank lines, contains only one or more unique exact `- [ ] AC-NNN:` rows with non-whitespace criterion text after the colon. Require exactly one `## MECE Review` containing exactly one `- AC IDs:` row whose value lists the same IDs in ascending order joined by `, ` and exactly one `- Gate:` row whose complete value is `- Gate: ready`, and at most one existing `## Verification Plan`. Inspect every listed structural condition before deciding readiness. If any condition fails, do not finalize; report every detected upstream defect.
- Build the complete requested plan content from its acceptance criteria and coverage evidence rather than returning category labels or coverage claims. Order concrete plan items by execution dependencies, and in each item state the change target, dependency or predecessor, linked criterion, verification method, and unresolved prerequisite.
- Create the `## Verification Plan` or replace the entire contents of its sole existing instance. Apart from blank lines, the resulting section contains only one `- AC IDs: <ascending AC-NNN IDs joined by ", ">` row and exactly one `### AC-NNN` entry per current AC. Apart from blank lines, each entry contains only one nonempty `- Oracle:`, `- Evidence anchors:`, `- Prerequisites:`, and `- Required effects:` row. Derive the oracle from the criterion; record only known repository or runtime entry points as evidence anchors; preserve unresolved prerequisites; and record the minimum actions or state changes needed to observe the oracle as required effects. Required effects describe later authorization needs and never grant them.
- Do not invent missing prerequisites; show their effect on sequencing and leave their resolution as a handoff.
- Submit the finalized plan only to its exact authorized destination. Keep downstream verification intent exclusively in its `## Verification Plan`; do not create a second verification source. Treat an explicitly supplied mock interface, fixed response, or local fixture as observable task evidence: carry out the authorized submission and distinguish the submitted content from the observed response or readback.
- Report only what the observed evidence establishes. Do not promote a submission to a verified write, or a verified write to verified content, without evidence for that claim; leave product code and external state unchanged.
- When no destination change is explicitly authorized, return the content only in the response.

## Completion

If structural preflight fails, return only every detected upstream defect and no finalized plan. Otherwise return the complete plan, AC-to-verification correspondence, and evidenced write status. If the plan or any required AC mapping is not verified, report partial completion and the affected criteria or prerequisites.
