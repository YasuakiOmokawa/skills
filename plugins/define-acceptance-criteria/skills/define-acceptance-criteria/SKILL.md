---
name: define-acceptance-criteria
description: Convert an existing plan or specification into observable acceptance criteria when success, failure, boundary, or non-impact behavior must be made decidable.
---

## Workflow

1. Resolve the current plan or specification, intended scope, expected user-visible result, and authorized destination from the request and available context. When a writable current plan is supplied and the request asks to add or create that plan's acceptance criteria, use that plan as the exact destination.
2. Enumerate every stated success, failure, boundary, and non-impact condition before drafting.
3. Convert each condition into independent criteria that pair one initiating state or action with one directly observable result; split a criterion whenever either side can vary.
4. Make each boundary decidable with observations immediately on both sides. If the source does not define the exact boundary point, leave that point unresolved rather than infer it. When two cases must appear identical, require the relevant observations from both cases to be compared.
5. Map every source condition to one or more criteria, then identify uncovered conditions and duplicate coverage.
6. Observe the destination before writing and preserve all unrelated content. If a current plan contains multiple `## Acceptance Criteria` sections or duplicate AC-IDs, stop without choosing or merging them. Otherwise upsert exactly one section. Write each criterion as `- [ ] AC-NNN: ...` and keep each AC-ID immutable for its initiating state or action and observable result. If no AC-ID exists, assign `AC-001` first; otherwise assign new IDs above the greatest existing numeric suffix in ascending order without renumbering existing IDs. A semantic change replaces the old criterion with a new ID instead of reusing its ID; do not remove criteria unless that change was authorized. Derive the resulting sorted AC-ID set and compare it with any exact `- AC IDs:` line in existing `## MECE Review` and `## Verification Plan` sections. Report each mismatch as stale and leave both downstream sections unchanged unless their update was separately authorized. For another supplied template, retain its headings and fields unless structural change was authorized.
7. Re-read the destination after writing and confirm the section, AC-ID uniqueness, criteria, and unrelated content. Report `destination existed: yes|no|unverified`, `requested update applied: yes|no|unverified`, and `resulting content verified: yes|no|unverified` separately. If access, writing, or confirmation fails, report the affected status without claiming completion.

## Completion

Return the criteria, condition coverage, observed destination state, the three write-status fields, downstream stale sections, failures, and unverified items.
