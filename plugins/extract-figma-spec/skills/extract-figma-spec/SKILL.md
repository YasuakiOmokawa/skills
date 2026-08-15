---
name: extract-figma-spec
description: Use before or during Figma-driven implementation to extract returned design properties into atomized checks, compare them with code, and write a canonical results table.
---

Structured Figma metadata is the value source; screenshots are orientation evidence only. Figma review comments are out of scope when the available metadata capability cannot retrieve them.

## Resolve inputs

Use an explicitly supplied node/URL and plan path first, then values present in the current non-delegated session. Normalize URL `node-id=1-234` to `1:234`. A delegated run does not infer files from its working directory. Without an output path, return the results table in the final response.

Until node selection and extraction succeed, every supplied output path is metadata only: never create, replace, or append to it, including diagnostics or evaluation reports. Early-stop reporting goes only to the final response.

Resolve a Figma metadata capability and list accessible pages. If no tool exists, report that and stop. Retry one transient call failure; do not retry a missing node, missing tool, or ambiguous selection.

If no node was supplied, compare page/node names with the request's concrete keywords and inspect enough descendants to select safely. Choose only a unique match. Generic labels such as `v0`/`v1` are not evidence. If synchronous clarification is unavailable, return candidates and stop. Report `正本抽出結果: 未生成`, the unresolved reason, and for unreachable metadata ask the user to open the target file in the Figma desktop app; do not fabricate rows.

## Extract

For each selected node, obtain the available equivalents of:

- metadata tree: elements, names, types, positions, sizes;
- design context: component code and applicable properties;
- variable definitions: tokens and exact values;
- screenshot: visual orientation only.

Process multiple nodes individually. Inspect descendants adaptively until the metadata coverage is sufficient for the requested component. A missing child is definitive only when returned metadata is known to cover that subtree; otherwise record the coverage gap as unresolved.

## Atomize

Create one `FIG-NN` atom per returned applicable property or element fact. Number continuously across nodes and renumber from `FIG-01` on a full re-extraction. Apply [references/checklist-building-details.md](references/checklist-building-details.md) to avoid duplicate atoms and handle unresolved values.

Consider element presence, color, border, icon, typography, dimensions/spacing, alignment, text, and interactive states when applicable.

- Explicit `none`/absence becomes an atom such as `枠なし`.
- Tool silence is not absence. Deepen coverage or mark unresolved; do not invent a value or atom.
- Omit structurally inapplicable categories.
- Record the exact value and node/token source for each atom.

## Compare with implementation

Read the corresponding code and classify each atom as `一致`, `差分`, or `未実装`. Measure computed style when source code cannot determine a rendered value. Do not use visual similarity as proof. Record differences as `Figma value → current value`.

Check every atom returned by the extraction, not only differences named by the requester.

## Persist

When a plan path is resolved, create `<plan>.analysis.md` if needed and write or replace this section there. Never move it to the plan file. Without a plan path, return the table with `未書き込み: プランパス未指定`.

```markdown
## 正本抽出結果

| atom ID | 期待値 | 状態 |
|---|---|---|
| FIG-05 | 左ペイン背景色 #464343 | 差分 (現状 #525659) |
```

After persisting the table, transfer `差分` and `未実装` atoms to acceptance criteria by running `/define-acceptance-criteria` in the normal planning pipeline; for a PoC, add them to the plan checklist. If the context does not establish a PoC, use the normal pipeline and state why. Do not duplicate them in both after AC is actually generated. If define stops because MECE already exists, do not auto-reset it; report the required explicit `--reset-mece` and subsequent MECE rerun.

The first column contains only the atom ID. Include all resolved rows, including matches, plus a separate unresolved list. After re-extraction, replace the whole table and rerun downstream coverage gates; do not rewrite a QA ledger keyed by QA-ID.

Final reporting includes the written absolute path or `未書き込み` reason, the full results table only when generated, and unresolved atoms/reasons.
