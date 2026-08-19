---
name: mece-plan-review
description: Compare a plan and acceptance criteria with specification and code evidence when a MECE coverage review or an explicitly authorized review update is requested.
---

## Workflow

- Resolve the current plan and require exactly one `## Acceptance Criteria` section whose `- [ ] AC-NNN:` rows have unique IDs. If the section is absent, duplicated, empty, or has duplicate IDs, report the malformed upstream artifact without fabricating a review.
- When an authorized read is exposed through a supplied mock interface, perform it and use the observed response. Treat supplied fixed-response or local-fixture content as observable evidence, then actually compare every accessible specification, relevant code source, acceptance criterion, and plan at the behavior or branch level. Record presence or absence in each source before deriving omissions, duplication, or contradictions.
- If evidence is inaccessible, mark only the comparisons that depend on it as unverified and complete every remaining comparison. Do not use access failure as evidence of conformity or nonconformity.
- Set one readiness gate using this priority: `blocked` when supported omissions, duplication, or contradictions remain; otherwise `unverified` when a required comparison lacks evidence; otherwise `ready`.
- Make no file changes unless an exact review destination is explicitly authorized. If a current plan contains multiple `## MECE Review` sections, report it as malformed without choosing or merging them. Otherwise, when the request asks to reflect the review in a writable current plan, upsert only one review section there with `- AC IDs: <sorted current IDs>`, `- Gate: ready|blocked|unverified`, and the item-level correspondence and findings. Preserve `## Acceptance Criteria`, implementation tasks, and unrelated content; return required upstream corrections instead of applying them. Distinguish the submitted update from the observed response or readback and leave product code and external state unchanged.

## Completion

Return the readiness gate, item-level correspondence, supported findings, required upstream corrections, and narrowly scoped unverified comparisons. Include review-update status only when an update was authorized.
