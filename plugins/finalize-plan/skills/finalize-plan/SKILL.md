---
name: finalize-plan
description: Finalize an implementation-ready plan from acceptance criteria and coverage evidence when work order, dependencies, change targets, and necessary QA material must be settled before implementation.
---

## Workflow

- Build the complete requested artifact content from the supplied acceptance criteria and coverage evidence rather than returning category labels or coverage claims. Order concrete plan items by execution dependencies, and in each item state the change target, dependency or predecessor, linked criterion, verification method, and unresolved prerequisite. In separately requested QA material, map each indispensable target condition and expected result to its criterion.
- Do not invent missing prerequisites; show their effect on sequencing and leave their resolution as a handoff.
- Submit each requested artifact separately and only to its exact authorized destination. Treat an explicitly supplied mock interface, fixed response, or local fixture as observable task evidence: carry out the authorized submission and distinguish the submitted content from the observed response or readback.
- Report only what the observed evidence establishes. Do not promote a submission to a verified write, or a verified write to verified content, without evidence for that claim; leave product code and external state unchanged.
- When no destination change is explicitly authorized, return the content only in the response.

## Completion

Return the complete plan and indispensable QA content with separately evidenced status for each requested artifact. If any required artifact is not verified, report partial completion and the affected artifacts or prerequisites.
