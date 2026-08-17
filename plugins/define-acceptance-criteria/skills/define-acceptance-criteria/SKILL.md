---
name: define-acceptance-criteria
description: Convert an existing plan or specification into observable acceptance criteria when success, failure, boundary, or non-impact behavior must be made decidable.
---

## Workflow

1. Resolve the source plan or specification, intended scope, expected user-visible result, and authorized destination from the request and available context.
2. Enumerate every stated success, failure, boundary, and non-impact condition before drafting.
3. Convert each condition into independent criteria that pair one initiating state or action with one directly observable result; split a criterion whenever either side can vary.
4. Make each boundary decidable with observations immediately on both sides. If the source does not define the exact boundary point, leave that point unresolved rather than infer it. When two cases must appear identical, require the relevant observations from both cases to be compared.
5. Map every source condition to one or more criteria, then identify uncovered conditions and duplicate coverage.
6. Observe the destination state before writing. If it is a supplied template, retain its headings and fields unless structural change was authorized; express required distinctions within those fields and report coverage mappings in the response when the template has no field for them. Create only the exact authorized artifact, and preserve existing material unless replacement was explicitly authorized.
7. Re-read the destination after writing and confirm that the intended criteria are present. If access, writing, or confirmation fails, report the artifact as not created or unverified instead of claiming completion.

## Completion

Return the criteria, condition coverage, observed destination state, verified write status, failures, and unverified items.
