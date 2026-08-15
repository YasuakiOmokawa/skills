# Reviewer fallback and Devil's Advocate dispatch

Mode selection and failure classification are defined in [escalation-rules.md](escalation-rules.md).

## Parallel Review fallback (Step 3)

If independent dispatch falls back under [escalation-rules.md](escalation-rules.md):

1. Read each selected `agents/*.md` directly.
2. The main agent applies the reviewer's criteria itself and feeds the per-reviewer verdicts into DA **as internal state** (do not emit intermediate output).
3. Append one tail line to the final report: `(in-context fallback mode: <reviewer names slash-separated>)`.

## subagent dispatch prompt (escalation only)

`${FATAL_CRITERIA}` を [escalation-rules.md](escalation-rules.md) の4つの single-trigger category と `anti-pattern-checker` ❌ で置換する。`${REVIEW_TARGET}` は plan path と対象設計節、plan が無ければ feature description。`${GROUNDING_SOURCES}` は対象 code path と、Step 0 で解決した PoC ledger / mapping path・該当 status。存在しない source を発明しない。次の fence 内だけを independent executor へ渡す。

```
You are a fresh subagent acting as Devil's Advocate. Produce up to 3 grounded critiques against
the Parallel Review output, label each fatal/acceptable, and avoid restating any
existing points. Surface up to 2 grounded hidden assumptions. Zero is valid.

Review each of these lenses: operations, 100x scale, interface for other teams,
and rollback cost. Before labeling, Read the cited target/source paths or Grep for
a concrete counterexample. If the premise is absent, label the critique acceptable;
do not make it fatal. A PoC item recorded as addressed, intentionally deferred, or
killed with a destination is not fatal solely because it is absent from the design.

## Review target:
${REVIEW_TARGET}

## Grounding sources:
${GROUNDING_SOURCES}

## Parallel Review output:
${PARALLEL_REVIEW_RESULT}

## Fatal criteria:
${FATAL_CRITERIA}
```

After an edit, re-run selected reviewers and DA, recalculating the DA escalation conditions. Preserve invocation-sticky permanent dispatch failures from `escalation-rules.md`; those targets go directly to inline fallback without another dispatch attempt. Repeat only while a reviewer ❌ / fatal has a new grounded edit; a reviewer ❌ / fatal with no new grounded edit uses the unresolved route. A repeated ⚠️ / Unknown / acceptable item uses the normal residual-risk route instead. Keep intermediate state internal.
