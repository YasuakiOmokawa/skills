---
name: mece-plan-review
description: Compare a plan and acceptance criteria with specification and code evidence when a MECE coverage review or an explicitly authorized review update is requested.
---

## Workflow

- When an authorized read is exposed through a supplied mock interface, perform it and use the observed response. Treat supplied fixed-response or local-fixture content as observable evidence, then actually compare every accessible specification, relevant code source, acceptance criterion, and plan at the behavior or branch level. Record presence or absence in each source before deriving omissions, duplication, or contradictions.
- If evidence is inaccessible, mark only the comparisons that depend on it as unverified and complete every remaining comparison. Do not use access failure as evidence of conformity or nonconformity.
- Make no file changes unless an exact review destination is explicitly authorized. Before an authorized update, observe the destination and preserve its supplied structure and unrelated content unless their change was authorized. Update only that review artifact through the supplied interface and distinguish the submitted update from the observed response or readback; confirm only what that evidence establishes. Leave product code and external state unchanged.

## Completion

Return the item-level correspondence, supported findings, and narrowly scoped unverified comparisons. Include review-update status only when an update was authorized.
