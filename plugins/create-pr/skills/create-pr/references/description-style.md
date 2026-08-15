# PR body contract

Before drafting, list the material reader-visible outcomes and operational facts. Do not enforce a minimum. If the template has an essence-list section such as `このPRでやること`, place them there as a numbered list; otherwise compress them across the existing sections without adding a heading.

## Default shape

- Preserve every template heading, order, and HTML comment. Do not add headings.
- Except template checklists/revert blocks, essence lists, and multiple explicit scope-outs, each section is one physical line by default.
- Expand only the section the user explicitly named. Keep its summary as the first line, then use prose for rationale, rejected alternatives, tradeoffs, or measured detail.
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

For performance evidence, summarize `before → after` with the decisive condition in one line unless detail was requested. For trivial verification with no observed result, use `目視確認のみ` or leave blank. Never claim a local or CI check that was not observed.

Scope-outs must be explicit in the session/issue/diff and still absent from the final diff. If their destination is unknown, say `未定`; delete stale or unrelated scope-outs.

## Final audit

1. Reading only each first line reconstructs the PR's purpose, impact, decision, and verification.
2. Every pre-draft outcome is recoverable from the body.
3. No plan-local labels, duplicate facts, invented evidence, or diff inventory remains.
4. Only user-requested sections exceed the default shape, and expanded prose retains rejected alternatives/reasons when supplied.
