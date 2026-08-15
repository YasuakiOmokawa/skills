# PR body contract

Every material reader-visible outcome and operational fact must be recoverable from the body. If the template has an essence-list section such as `このPRでやること`, use a numbered list there; otherwise distribute them across existing sections without adding a heading.

## Default shape

- Preserve every template heading, order, and HTML comment. Do not add headings.
- A verified related issue uses one canonical preamble line, `related <issue-url>`, after any explicitly requested opening note and before the template's first original line (or as the body first line when there is no note). This is not a heading or section and remains valid when the template has no headings or related-issue slot. Omit it when no issue is verified.
- Except template checklists/revert blocks, essence lists, and multiple explicit scope-outs, each section is one physical line by default.
- Expand only the section the user explicitly named. Keep its summary as the first line; when supplied, preserve that section's rationale, rejected alternatives, tradeoffs, and measured detail.
- Leave an inapplicable section blank with one blank line. Do not write filler such as `特になし`, `該当なし`, or `自明な観点なし`.
- Mark a template checkbox only when verified. For an either/or branch, mark exactly the applicable choice.

## Content ownership

| Section role | Include | Exclude |
|---|---|---|
| related issue/DD | verified links and one relationship label | summaries |
| what changed | reader-visible intent/outcome | filenames, helpers, imports, parameters, implementation inventory |
| why | user/business problem enabled or removed | restatement of what changed |
| design decision | selected approach and decisive rationale | unrelated implementation details |
| review focus | one concrete tradeoff or risk grounded in the diff | generic requests |
| verification | method, result, key condition/number | invented tests, raw logs, case lists |
| not done | explicit scope-out, reason, and known destination | speculative omissions |

A principal symbol may appear once when it is the PR's subject. Otherwise prefer reader vocabulary over identifiers. If motivation is not explicit, infer only the immediate user inconvenience implied by the behavior; do not invent business context.

For performance evidence, summarize `before → after` with the decisive condition in one line unless detail was requested. Use `目視確認のみ` only when visual inspection was observed; with no observed result, leave the section blank. Never claim a local or CI check that was not observed.

Scope-outs must be explicit in the session/issue/diff and still absent from the final diff. If their destination is unknown, say `未定`; delete stale or unrelated scope-outs.

## Final audit

1. **斜め読み・本質回収**: first lines reconstruct purpose, impact, decision, and verification; every material outcome is recoverable.
2. **コードから読める情報**: no file, helper, import, parameter, or implementation inventory remains unless it is the PR's subject.
3. **分量・重複・事実整合**: facts are not duplicated; scope-outs match the final diff; only requested sections exceed the default shape.
4. **私語彙・生成痕跡**: no plan-local labels, filler, mechanical phrasing, or invented evidence remains.
