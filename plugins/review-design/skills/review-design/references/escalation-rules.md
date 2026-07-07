# DA escalation / fatal criteria / mode tags

SKILL.md "Workflow" の本文と相互参照する canonical 定義集。SKILL.md には triggering 条件と短縮表のみを残す。

## Three execution modes — full table

| Mode | When | Final-report tag |
|---|---|---|
| **inline default** | DA escalation conditions NOT met (normal path) | none |
| **subagent dispatch** | DA escalation condition met | none |
| **in-context fallback** | Task tool unavailable (deferred / no dispatch perm) for reviewers OR DA | `(in-context fallback mode: <agent name>)` at report tail |

`inline default` ≠ `in-context fallback`. The tail tag is **only** for the environment-constraint fallback, never for normal inline DA.

## DA escalation conditions (machine-checkable)

Switch from `inline default` to `subagent dispatch` if **any** of:

1. Reviewers with `❌` ≥ 2 (across the 5 reviewer types)
2. **Single-trigger escalators** (any 1 hit forces escalation):
   - DB transaction boundary violation (external API in callback / multi-Aggregate write / missing saga)
   - Concurrency / idempotency defect (race condition / duplicate notify / multi-tab contention)
   - Security vulnerability (auth bypass / SQLi / XSS / CSRF / plaintext PII / IDOR / open redirect)
   - Existing contract breach (public API breaking change / SDK major version up)
3. `$ARGUMENTS` contains `--strict-da`

## Fatal vs single-trigger (separate concepts)

| Term | Used for | When |
|---|---|---|
| Single-trigger escalator | inline → subagent switch | after Parallel Review, before DA |
| **Fatal criteria** | DA classifying each finding as "fatal / acceptable" | during DA (inline or subagent) |

Fatal ⊇ single-triggers (4 above) **plus** `anti-pattern-checker` ❌ judgments. The latter is already surfaced by Step 3, so escalation handles it via the `❌ ≥ 2` route. Subjective preferences are "acceptable", not "fatal".
