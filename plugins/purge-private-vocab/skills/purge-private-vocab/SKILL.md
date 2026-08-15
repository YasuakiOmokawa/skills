---
name: purge-private-vocab
description: Review or rewrite plan-local coinages, abbreviations, layer labels, and finding IDs in reader-facing text or plans, subject to source availability and explicit edit authority.
---

Make the target readable without its source plan. Code structure, comment placement, and naming design are out of scope.

## Input and authority

Resolve target from an explicit path or inline text, then the current non-delegated session. Resolve the source from an explicit path or a plan/spec identified in the current task; do not assume a particular plans directory. For multiple outputs, count occurrences across the set but define a retained shorthand once per independently read artifact.

Tier controls report detail, never write authority:

- lite: target ≤300 characters or at most two distinct candidates; concise report.
- standard: other PR/Jira descriptions and documents; full report.
- deep: design doc, RFC, public material, or 2000+ characters; also apply the deep preparation in [references/execution-contexts.md](references/execution-contexts.md).

Edit only when the user or delegating prompt authorized changing the target. Review-only requests return the report. A delegated run without explicit mutation authority does not edit.

A plan normally needs no purge, except when its readers lack the upstream analysis that defined `BB-N`, `WB-N`, `IM-N`, or similar labels.
Such a plan is never lite: use at least standard and emit the report before editing.

## Detect

Scan the entire target for:

- local coined compounds and emphasized labels;
- `§...`, candidate labels such as `案 A`, generic alphanumeric IDs, and analysis finding IDs;
- Greek-letter layers, numbered quadrants/layers, phase nicknames, and unexplained English compounds.

Heuristic matches are candidates, not automatic findings. Use the false-positive table in [references/heuristics-and-pitfalls.md](references/heuristics-and-pitfalls.md) for deep work.

## Classify

When the source is unavailable, the source-missing rules below override rules 2–4.

Apply the first matching rule:

1. Preserve an actual code identifier, file/class/flag name, public standard, established single- or multi-token technical term, Jira/Issue ID, or Figma node ID. Repository occurrence alone is insufficient: confirm a defining declaration, standard, or technical context.
2. Preserve a term already defined before or at first use in the target. If its definition appears later, move a short definition to first use.
3. Replace plan-only number, candidate, layer, section, or finding labels with the concrete meaning from the source. For repeated labels, expand the first occurrence and use an ordinary noun phrase thereafter; never keep the private label as shorthand.
4. A useful coined term appearing at least twice must be defined inline at first use; do not eliminate every occurrence unless the source marks the term disposable. Rewrite or delete a one-off term.

For `label: plain body`, rewrite the label and retain the body. For a local numbered section reference, include the real heading name; delete only a dangling reference.

Do not promote an unresolved option, TTL, owner, or date into a decision. If the source is unavailable:

- a layer may become a relation such as `後段の処理層` when the target establishes that relation;
- other private labels remain unchanged and are reported as `source plan 未確認のため要確認`;
- never invent the missing expansion.

## Report and apply

Report only candidates actually inspected:

| Class | Required fields |
|---|---|
| preserve | term, evidence, rule 1 or 2 |
| define inline | term, count, proposed first-use definition |
| rewrite/delete | term, locations, replacement or deletion reason |
| needs source | unchanged term, locations, literal status `source plan 未確認のため要確認` |

Standard/deep and every source-missing case receive this report before any authorized edit. Other lite cases may edit immediately only when mutation was already authorized.

After editing, reread the changed passages: the definition appears only at first use, sentences remain grammatical, and a reader without the plan can follow them. Report changed terms and replacements. Include the absolute path only for file-backed targets; for inline text, return the revised text without inventing a path.
