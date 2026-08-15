# Detection candidates

Matches are candidates; classify them with SKILL.md before changing anything.

| Pattern | Candidate | Typical false positive |
|---|---|---|
| coined compound ending in 型/主義/原則/論/系 | `Provider 内吸収型` | common `同期型` |
| emphasized phrase | `**Single Switch**` | code identifier |
| alphanumeric label | `Critical-A`, `AC-12` | Jira ID, locally defined QA-ID |
| Greek letter plus 層/相 | `α 層` | established mathematical notation |
| candidate label | `案 D` | none |
| section anchor | `§設計詳細` | resolvable local heading |
| phase nickname | `rollout enabler` | established `feature flag` |
| numbered layer/quadrant | `3 層` | OSI 7-layer model |
