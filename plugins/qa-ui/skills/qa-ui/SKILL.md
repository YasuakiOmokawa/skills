---
name: qa-ui
description: Verifies an implemented UI when the request provides observable checks, expected states, an accessible rendered page, and permitted interactions.
---

- Treat a supplied rendered page, local UI fixture, or mock interaction interface as an observable UI. Set the supplied display conditions and carry out every permitted interaction through that interface instead of describing how to test it.
- Distinguish an interaction submitted from the state returned or directly observed afterward. Never infer the resulting state or a successful action from submission alone.
- Mark each check PASS only when its observed state matches the expectation, FAIL when it contradicts the expectation, and unverified when no permitted observation establishes either result.
- Record reproducible evidence for each check: starting state, display conditions, interaction, resulting observation, and any relevant measurement or captured artifact.
- Preserve item-level results when another item fails; do not replace them with only an aggregate status.
- Perform only authorized interactions. Leave any check requiring a forbidden state change, unavailable credential, or inaccessible page unverified and state the blocker without attempting to bypass it.
- Report every item's observed result and evidence, failed or unverified interactions, access blockers, and any external-state change.
