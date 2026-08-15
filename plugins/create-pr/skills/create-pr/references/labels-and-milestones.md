# Labels and milestone

Read the configured release-label definitions when available; use their exact names and criteria. If unavailable, omit labels without blocking PR creation.

Choose at most one label in each configured group:

- productivity: classify by the PR's largest user/developer value, ignoring incidental test parity;
- AI contribution: honor an explicit user level; otherwise use observed authorship of the diff, not the fact that this PR-writing skill ran. If provenance is uncertain, report that uncertainty in the completion message, not the PR body;
- release level: use the shipped/default-state behavior visible to existing users. Schema changes are highest; core-flow behavior changes are high; backward-compatible/internal changes are middle; wording/typo/patch-only changes are lowest. Prefer configured `core_features`; otherwise use repository project documentation.

For milestones, inherit a related issue's verified milestone. Otherwise query all milestone pages for `Untracked`; use it only when confirmed. If listing fails or no configured value exists, omit the milestone option.
