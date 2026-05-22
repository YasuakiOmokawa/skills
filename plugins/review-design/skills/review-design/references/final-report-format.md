# Final report format (Step 6)

The final report has two routes depending on whether the plan was edited.

## Problem-free route

Conditions: Parallel Review all ✅ **AND** Devil's Advocate fatal count = 0.

```
設計レビュー完了。問題なし。
```

## Problem-found route

Conditions: any reviewer returned ❌/⚠️, OR DA flagged ≥1 fatal finding and Edit was executed.

```
設計レビュー完了。以下を修正しました:
- <what → how it was fixed (1 issue = 1 line)>
- <...>
```

The plan file body must contain the corrected design itself, never an analysis summary or report dump.

### "1 issue = 1 line" granularity

- Same logical issue rippling across multiple files / spots → **one line** (collapse to the root issue).
- Independent issues (e.g. transaction boundary violation **and** God Class avoidance) → **separate lines**.

## In-context fallback notation

This tag is added ONLY when the environment forced fallback for at least one of:

- Parallel Review reviewers (Step 3)
- Devil's Advocate (Step 5, subagent dispatch attempt failed due to env constraint)

It is **NOT** added when DA simply ran in `inline default` mode (the normal path) — that is not an environment-constraint fallback. Readers must not confuse "ran inline by design" with "ran inline because Task was unavailable".

Tail format (append exactly one line at the very end of the final report):

```
(in-context fallback mode: <agent names slash-separated>)
```

### Examples

DA only fell back:

```
(in-context fallback mode: devil's-advocate)
```

All reviewers + DA fell back:

```
(in-context fallback mode: anti-pattern-checker / ddd-reviewer / hexagonal-reviewer / clean-architecture-reviewer / devil's-advocate)
```

## What NOT to include

The final report must **not** include:

- Per-reviewer verdict dumps
- Devil's Advocate critique details
- Feedback-loop re-Review procedure or per-iteration state

These remain internal. The user-facing report stays in the two templates above plus the optional fallback tail.
