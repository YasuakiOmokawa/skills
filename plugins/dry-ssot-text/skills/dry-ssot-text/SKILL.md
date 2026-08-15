---
name: dry-ssot-text
description: Use when reader-facing prose or code-comment explanations repeat across a document or change set; not for code structure or logic duplication.
---

Code structure and logic refactoring are out of scope. For an explicitly named change set, use that diff. For the current worktree, scope to the deduplicated union of `git diff --name-only`, `git diff --cached --name-only`, and `git ls-files --others --exclude-standard`; aggregate occurrence counts and emit one report. This selection is the editable scope and the boundary for counts, tier, SSOT choice, and `N → 1`. Files outside it may be read only to resolve references; never count, choose, or edit them.

## Tier

Count occurrences per concept; use the largest duplicate group, not the sum. References left by this skill do not count.

| Tier | Condition | Action |
|---|---|---|
| skip | duplicates ≤2, customer-facing enumeration, or API reference | no edit |
| lite | duplicates 3-5 | edit directly |
| standard | duplicates ≥6 or shared preliminary document | inline dry-run, then edit |
| deep | repeated prose across documents or existing non-TOC references depend on moved anchors | standard plus anchor and final occurrence checks |

After skip exclusions, choose the highest matching tier. A single linear reader-facing document and a mixed code+markdown change are not deep by themselves. An explicit dry-run request reports only and never edits.

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

For a linear document, keep the fullest occurrence in place and condense the others inline; do not create a dedicated section. Otherwise use the fullest existing standalone dedicated section, or create one without adding facts. A PR/chapter occurrence is never a dedicated section. Put a new standalone section near the beginning only when later scope needs it; otherwise prefer the end. Retain each chapter's scope sentence; a chapter must not become reference-only. Before moving or renaming a heading, search non-TOC inbound references, including read-only files outside the editable scope. If an outside-scope reference targets its anchor, keep that heading and anchor in place, choose a placement that preserves it, and report the constrained anchor and referring path; do not edit the outside-scope file. Synchronize numbering and TOC when headings move.

## Replace duplicates

- Referenced long-form documents (plan, design doc, RFC, ADR, README) use this branch regardless of length: delete fully subsumed paragraphs. Keep a required template heading with one anchor reference. For partial overlap, retain independent facts and add the shortest markdown anchor reference. If multiple ADR sections qualify, use `Rationale`.
- Linear reader-facing documents: condense inline without anchors or new facts.
- Code comments: prefer an existing markdown design section as SSOT. Delete a comment only when its identifier or file path already reaches the SSOT by search; otherwise retain one file-path reference. Do not add identifiers to the SSOT merely to justify deletion.

Within markdown use anchors; from code to markdown use file paths. Anchor text is the lowercase heading with punctuation removed and spaces replaced by hyphens.

## Apply and verify

For standard/deep or an explicit dry-run, emit one inline report listing unnecessary and necessary duplicates with locations, the chosen SSOT, tier evidence, and planned replacements. An explicit dry-run, review-only, or no-edit request stops after the report. A delegated run inherits edit authority from its delegation prompt exactly: explicit edit authority continues, while absent or read-only authority reports and stops. Delegation itself is never self-approval.

After a required report, edit immediately only when the invoking request grants edit authority. Preserve navigation. Verify a differentiating phrase occurs once and every new anchor resolves. For code, run the smallest syntax check that does not modify logic. Report each concept as `N → 1` with absolute paths. On skip, report the matched criterion and paths.
