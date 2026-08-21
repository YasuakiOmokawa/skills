---
name: qa-ui
description: Verifies an implemented UI when the request provides observable checks, expected states, an accessible rendered page, and permitted interactions.
---

- Treat a supplied rendered page, local UI fixture, or mock interaction interface as an observable UI. Set the supplied display conditions and carry out through that interface only the permitted interactions needed to establish the supplied checks instead of describing how to test them.
- Before running checks, establish through the selected interface that the page is reachable and serves the implementation under test. Reachability from another process does not establish interface reachability, and an HTTP response alone does not establish rendered artifact identity; leave affected checks unverified when either cannot be proven.
- Distinguish an interaction submitted from the state returned or directly observed afterward. Never infer the resulting state or a successful action from submission alone.
- Mark each check PASS only when its observed state matches the expectation, FAIL when it contradicts the expectation, and unverified when no permitted observation establishes either result.
- Record reproducible evidence for each check: starting state, display conditions, interaction, resulting observation, and any relevant measurement or captured artifact.
- When the UI or its evidence contains credentials or one-time secrets, exclude or redact them from snapshots, tool output, and reports. Before using a disposable credential, require a non-disclosing interaction path and an authorized invalidation path; otherwise leave the credential-dependent check unverified. Invalidate it immediately after observing the result.
- Preserve item-level results when another item fails; do not replace them with only an aggregate status.
- Perform only authorized interactions. Leave any check requiring a forbidden state change, unavailable credential, or inaccessible page unverified and state the blocker without attempting to bypass it.
- Report every item's observed result and evidence, failed or unverified interactions, access blockers, and any external-state change.
