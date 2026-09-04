---
name: create-jira-issues
description: Create Jira issues when the user explicitly asks to file listed, approved stories or tasks in a specified project and issue type, with per-item keys and failures.
---

# Workflow

1. Resolve the explicitly authorized items and their target project, issue type, and required fields from the request and available context. When target or field configuration is not supplied, read `~/.claude/skills-config/jira.md`; hold anything still unresolved.
2. Hold only items whose required information is missing or conflicting, and state the blocker for each.
3. Carry out every eligible creation through the available Jira interface rather than stopping at its description; record the request as submitted separately from any result verified by the returned or observed state, and never infer success from an absent response.
4. Restrict creation requests to the listed authorized items and never update existing issues.
5. Verify creation only from a returned or subsequently observed state; associate any observed issue key with its original item and record item-specific failures without assigning invented keys.
6. Report every item with its supported outcome, then summarize verified creations, failures, holds, and unresolved outcomes.
7. If no item is eligible, submit nothing and report the blockers.
