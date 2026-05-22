# Reviewer execution modes & Devil's Advocate prompts

This reference fills in the three execution modes, the inline / subagent DA prompts, and the feedback loop. See SKILL.md "Three execution modes" and "DA escalation conditions" for the summary.

## Three modes — full definitions

| Mode | Meaning | Typical case |
|---|---|---|
| **inline default** (normal) | main agent runs DA itself | default; few critical candidates, low self-bias risk |
| **subagent dispatch** (escalated) | `Task` tool spawns a fresh subagent for DA | complex critical signals; fresh viewpoint required |
| **in-context fallback** (env-constraint) | `Task` tool unusable, main agent substitutes | Task deferred / no dispatch permission |

`inline default` and `in-context fallback` are **different concepts**. The final report tag `(in-context fallback mode: …)` is ONLY for the latter.

## Parallel Review fallback (Step 3)

If `Task` is unavailable (already running as subagent / tool deferred / no dispatch perm):

1. Read each selected `agents/*.md` directly.
2. The main agent applies the reviewer's criteria itself and feeds the per-reviewer verdicts into DA **as internal state** (do not emit intermediate output).
3. Append one tail line to the final report: `(in-context fallback mode: <reviewer names slash-separated>)`.

## inline default DA prompt (self-imposed)

The main agent runs the following critique against itself:

```
You are the Devil's Advocate against the Parallel Review output. Rules:

1. Produce 3 critiques from angles NOT covered in the Parallel Review (Step 3) output.
   Repeating existing points is forbidden — new viewpoints required.
2. Label each critique "fatal / acceptable" (criteria below).
3. Surface 1-2 hidden assumptions.
4. Self-bias countermeasure: do NOT critique from the same lens reviewers used. Attack from:
   - Operational failure scenarios (just after deploy / just before retirement / during incidents)
   - Scale expansion (100x traffic / 100x data)
   - Interface quality seen from another team / plugin / service
   - Cost of rollback / undo
```

### Fatal criteria (used by DA)

Canonical list is in SKILL.md's "DA escalation conditions / Single-trigger escalators" + the `anti-pattern-checker ❌` rule. Refer there; do NOT restate the wording here (SSOT).

A finding is **fatal** ONLY if it matches:
- `agents/anti-pattern-checker.md` judgment table marks ❌, OR
- any one of the 4 single-trigger escalators enumerated in SKILL.md (DB tx boundary / concurrency / security / contract breach)

Subjective preference = "acceptable", never "fatal".

## subagent dispatch prompt (escalation only)

```
Task(subagent_type="general-purpose", prompt="""
You are a fresh subagent acting as Devil's Advocate. Produce 3 critiques against
the Parallel Review output, label each fatal/acceptable, and avoid restating any
existing points.

## Parallel Review output:
${PARALLEL_REVIEW_RESULT}

## Fatal criteria:
[Copy SKILL.md "DA escalation conditions / Single-trigger escalators" verbatim + the `anti-pattern-checker ❌` rule. This file's "Fatal criteria" defers to SKILL.md as SSOT.]
""")
```

## Feedback loop

When DA flags any "fatal" finding (inline or subagent — procedure is identical):

1. `Edit` the plan file to fix the offending design.
2. Re-run Parallel Review (Step 2-4) against the fixed plan.
3. Repeat until **all** DA findings are "acceptable".
4. **Re-evaluate DA escalation** each iteration. The fixed plan may downgrade ❌ counts, so what was subagent last round may be inline this round (and vice versa).

If feedback loop re-Review must run in in-context mode, the main agent re-judges internally and the final report only carries the "fatal cleared" facts as fix lines — do NOT emit the re-Review procedure.
