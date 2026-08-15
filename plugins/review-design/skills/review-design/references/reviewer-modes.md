# Reviewer execution modes & Devil's Advocate prompts

This reference fills in the three execution modes, the inline / subagent DA prompts, and the feedback loop. See SKILL.md "Three execution modes" and "DA escalation conditions" for the summary.

## Three modes — full definitions

| Mode | Meaning | Typical case |
|---|---|---|
| **inline default** (normal) | main agent runs DA itself | default; few critical candidates, low self-bias risk |
| **subagent dispatch** (escalated) | independent-executor capability provides a fresh DA | complex critical signals; fresh viewpoint required |
| **in-context fallback** (env-constraint) | independent dispatch is permanently unavailable, main agent substitutes | no capability / no permission / exhausted budget |

`inline default` and `in-context fallback` are **different concepts**. The final report tag `(in-context fallback mode: …)` is ONLY for the latter.

## Parallel Review fallback (Step 3)

If independent dispatch is **permanently** unavailable (classification: escalation-rules.md "Permanent vs temporary dispatch failure" — a temporary concurrency/rate limit is retried, not fallen back):

1. Read each selected `agents/*.md` directly.
2. The main agent applies the reviewer's criteria itself and feeds the per-reviewer verdicts into DA **as internal state** (do not emit intermediate output).
3. Append one tail line to the final report: `(in-context fallback mode: <reviewer names slash-separated>)`.

## inline default DA prompt (self-imposed)

The main agent runs the following critique against itself:

```
You are the Devil's Advocate against the Parallel Review output. Rules:

1. Produce up to 3 grounded critiques from angles NOT covered in the Parallel Review output. Zero is valid.
   Repeating existing points is forbidden — new viewpoints required.
2. Label each critique "fatal / acceptable" (criteria below).
3. Surface up to 2 grounded hidden assumptions. Zero is valid.
4. Self-bias countermeasure: do NOT critique from the same lens reviewers used. Attack from:
   - Operational failure scenarios (just after deploy / just before retirement / during incidents)
   - Scale expansion (100x traffic / 100x data)
   - Interface quality seen from another team / plugin / service
   - Cost of rollback / undo
```

### Fatal criteria (used by DA)

Canonical list is in references/escalation-rules.md ("DA escalation conditions / Single-trigger escalators" + the `anti-pattern-checker ❌` rule). Read that file when classifying findings as fatal / acceptable; do NOT restate the wording here (SSOT).

## subagent dispatch prompt (escalation only)

```
Dispatch an independent executor with this prompt:
You are a fresh subagent acting as Devil's Advocate. Produce up to 3 grounded critiques against
the Parallel Review output, label each fatal/acceptable, and avoid restating any
existing points. Surface up to 2 grounded hidden assumptions. Zero is valid.

## Parallel Review output:
${PARALLEL_REVIEW_RESULT}

## Fatal criteria:
[Copy the "Single-trigger escalators" + `anti-pattern-checker ❌` rule from references/escalation-rules.md verbatim. That file is the SSOT.]
```

## Feedback loop

After any Step 4 edit, re-run the selected Parallel Review and DA. When DA flags any "fatal" finding (inline or subagent — procedure is identical):

1. `Edit` the plan file to fix the offending design.
2. Re-run Parallel Review (Step 3-4) against the fixed plan.
3. Repeat until **all** DA findings are "acceptable".
4. **Re-evaluate DA escalation** each iteration. The fixed plan may downgrade ❌ counts, so what was subagent last round may be inline this round (and vice versa).

If feedback loop re-Review must run in in-context mode, the main agent re-judges internally and the final report only carries the "fatal cleared" facts as fix lines — do NOT emit the re-Review procedure.
