---
name: dry-ssot-text
description: Collapse repeated prose or code-comment explanations into one SSOT and replace other occurrences with deletion or the shortest resolvable reference, while preserving navigation and distinct facts.
---

Code structure and logic refactoring are out of scope. For a change set, scope with `git diff --name-only`, aggregate line and occurrence counts, and emit one report.

## Tier

Count occurrences per concept; use the largest duplicate group, not the sum. References left by this skill do not count.

| Tier | Condition | Action |
|---|---|---|
| skip | duplicates ≤2, customer-facing enumeration, or API reference | no edit |
| lite | duplicates 3-5 | edit directly |
| standard | duplicates ≥6, ≥300 total lines, or shared preliminary document | inline dry-run, then edit |
| deep | ≥600 total lines, repeated prose across documents, or existing non-TOC references depend on moved anchors | standard plus anchor and final occurrence checks |

Duplicate count overrides line count. Short linear reader-facing documents use lite regardless of count. A mixed code+markdown change is not deep by itself. An explicit dry-run request always produces one.

Line count is tier evidence only, never an output invariant; do not pad or optimize for it.

## Classify

Consolidate repeated prose, tables, code quotes, notation variants, and an older explanation fully contained by a newer one. Preserve:

- TOCs, progress tables, AC/QA-ID checklists, headings that index their bodies, and dated audit logs;
- short glossary entries;
- facts serving different section roles, unless the passages are verbatim;
- any independent fact not present in the chosen SSOT.

Judge semantic repetition at paragraph or sentence level. Shared keywords alone are not duplicates.

## Resolve input

Use `$ARGUMENTS`, then an explicit path in the prompt, then a document mentioned in the current non-delegated session. Delegated runs have no prior conversation context. If unresolved, do not search; return `不足入力: 対象文書パス` and stop.

## Choose the SSOT

Use the fullest existing standalone dedicated section; if none exists, create one without adding facts. A PR/chapter occurrence is never a dedicated section and must never be the SSOT. Put the standalone section near the beginning only when later scope cannot be understood without it; otherwise prefer the end. Retain each chapter's scope sentence; a chapter must not become reference-only. Synchronize numbering and TOC when headings move.

## Replace duplicates

- Referenced long-form documents (plan, design doc, RFC, ADR, README) use this branch regardless of length: delete fully subsumed paragraphs. Keep a required template heading with one anchor reference. For partial overlap, retain independent facts and add the shortest markdown anchor reference. If multiple ADR sections qualify, use `Rationale`.
- Short linear documents: condense inline without anchors or new facts.
- Code comments: prefer an existing markdown design section as SSOT. Delete a comment only when its identifier or file path already reaches the SSOT by search; otherwise retain one file-path reference. Do not add identifiers to the SSOT merely to justify deletion.

Within markdown use anchors; from code to markdown use file paths. Anchor text is the lowercase heading with punctuation removed and spaces replaced by hyphens.

## Apply and verify

For standard/deep or an explicit request, first emit one inline report listing unnecessary and necessary duplicates with locations, the chosen SSOT, tier evidence, and planned replacements. A delegated run self-approves and continues.

After any required report, edit immediately; delegated runs must not stop at the report. Preserve navigation. Verify a differentiating phrase occurs once and every new anchor resolves. For code, run the smallest syntax check that does not modify logic. Report each concept as `N → 1` with absolute paths. On skip, report the matched criterion and paths.
