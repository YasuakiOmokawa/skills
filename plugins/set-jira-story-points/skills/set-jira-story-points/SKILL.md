---
name: set-jira-story-points
description: Set Jira Story Points when the user provides explicit issue-key-to-point mappings and asks to update those issues, with requested and confirmed values reported per issue.
---

# Workflow

1. Resolve the explicit issue-key-to-point mappings from the request and available context. When Jira target or field configuration is not supplied, read `~/.claude/skills-config/jira.md`; hold anything still unresolved.
2. Hold only mappings that lack one unambiguous value, and state the conflicting or missing information for each.
3. Carry out every eligible update through the available Jira interface rather than stopping at its description; record the request as submitted separately from any result verified by the returned or observed state, and never infer success from an absent response.
4. Restrict each update to the listed issue's Story Points field, and keep other issues and fields unchanged.
5. Verify success only from a returned or subsequently observed value that equals the requested value, and record item-specific failures with any value observed to remain in place.
6. Report every listed issue with its requested value and supported outcome, then summarize verified updates, failures, holds, and unresolved outcomes.
7. If no mapping is eligible, submit nothing and report the blockers.
