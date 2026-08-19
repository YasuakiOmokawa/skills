---
name: verify-plan
description: Use when an implemented change must be verified against a plan or acceptance criteria before it can be considered complete.
---

## Workflow

1. Resolve the current plan and implemented changes from the request, task context, and repository. Require exactly one `## Acceptance Criteria`, `## MECE Review`, and `## Verification Plan`; unique `- [ ] AC-NNN:` rows; matching `- AC IDs:` lines in both downstream sections; `- Gate: ready`; and exactly one `### AC-NNN` verification entry per current AC with one nonempty `Oracle`, `Evidence anchors`, `Prerequisites`, and `Required effects` field. If any structural check or AC-ID-set comparison fails, stop without reconstructing requirements after implementation and identify the stale or malformed upstream artifact.
2. Use each complete verification entry as the contract for its AC. Execute a required effect only when the live request authorizes it; otherwise leave the criterion unverified and state the missing authorization.
3. Inspect repository scripts, tests, documentation, fixtures, APIs, database queries, logs, and rendered interfaces to resolve the strongest permitted direct observation for each criterion. Prefer existing mechanisms; create a minimal local probe only when authorized and necessary.
4. Execute every feasible check. For stateful behavior, compare the relevant state before and after the action. For rendered UI behavior, set the required display conditions and interact with the actual page; source inspection, an HTTP success, or an action submission is not visual evidence.
5. Mark a criterion PASS only when the observed result matches its oracle, FAIL when it contradicts the oracle, and unverified when permitted evidence establishes neither. Preserve each result when another criterion fails.
6. Diagnose every FAIL from its evidence. When the root cause is in the implementation and its correction remains within the original authorization, make the smallest failure-scoped correction and rerun the failed criterion plus any previously passed checks the correction can affect. Continue only while new evidence identifies another authorized correction; stop before repeating an ineffective attempt, changing the requirement, expanding scope, or performing an unapproved action.
7. For an unavailable environment or transient dependency, try an available documented and safe recovery. If the required observation still cannot be made, leave the criterion unverified and state the exact access, service, credential, data, or interaction needed to complete it.
8. Remove temporary probes and restore verification-created data when possible. Report any residue or external-state change.
9. Report the method, observation, and result for every criterion; all corrections and reruns; and every remaining failure or unverified prerequisite. Claim complete verification only when every criterion passes. Verification does not authorize commits, pushes, pull requests, or external mutations that the request did not authorize.
