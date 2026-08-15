# 委譲実行 (qa-ui)

Use these adaptations only when the executor cannot wait synchronously; delegation itself does not change the verification path.

## Resolve inputs

Resolve the base URL from the invocation, the non-delegated session, then the plan. If none exists, return `不足入力: ベース URL`. Resolve the plan from an explicit path or the non-delegated session; if absent, continue through the no-QA-ID browser fallback.

## Return a manual handoff

For planned manual QA, return the complete per-ID handout as the final message and exit without waiting. Tell the caller to obtain mapped human results and invoke `qa-ui` again; the next run resumes from the append-only `<plan>.qa-ledger.md` state.

## Run browser fallback inline

When no independent evaluator is available but browser capability exists, read `agents/ui-evaluator.md` and apply the same contract inline. If browser capability itself is unavailable, report each fallback target as `検証不能(真の制約)` and continue through the remaining targets.
