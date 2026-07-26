# DA escalation / fatal criteria / mode tags

SKILL.md "Workflow" の本文と相互参照する canonical 定義集。SKILL.md には triggering 条件と短縮表のみを残す。

## Three execution modes — full table

| Mode | When | Final-report tag |
|---|---|---|
| **inline default** | DA escalation conditions NOT met (normal path) | none |
| **subagent dispatch** | DA escalation condition met | none |
| **in-context fallback** | Task dispatch **permanently** unavailable for reviewers OR DA | `(in-context fallback mode: <agent name>)` at report tail |

`inline default` ≠ `in-context fallback`. The tail tag is **only** for the environment-constraint fallback, never for normal inline DA.

**Permanent vs temporary dispatch failure** (decides whether fallback applies at all):

- **Permanent** → in-context fallback + tail tag: `Task` absent from the available-tools list, dispatch permission denied, spawn budget exhausted (e.g. `spawn limit reached (200 of 200)`).
- **Temporary** → retry the failed dispatches, no fallback and no tag: concurrent-subagent limit, rate limit. Running as a subagent is not a failure at all — nested `Task` dispatch from a subagent works.
- **Hung** (dispatch succeeded but no result within a bounded wait) → treat as permanent: wait at most ~15 minutes with 1 re-ping, then run in-context fallback + tail tag. Do not poll indefinitely — without this bound the taxonomy has a non-terminating state (実測: reviewer 5 体が spawn 成功のまま 55 分無応答).
- A DA whose escalation condition is met but whose dispatch is permanently unavailable runs inline **and** carries the tail tag (escalation met + fallback are independent facts).

## DA escalation conditions (machine-checkable)

Switch from `inline default` to `subagent dispatch` if **any** of:

1. Reviewers with `❌` ≥ 2 (across the 5 reviewer types)
2. **Single-trigger escalators** (any 1 hit forces escalation):
   - DB transaction boundary violation (external API in callback / multi-Aggregate write / missing saga)
   - Concurrency / idempotency defect (race condition / duplicate notify / multi-tab contention)
   - Security vulnerability (auth bypass / SQLi / XSS / CSRF / plaintext PII / IDOR / open redirect)
   - Existing contract breach (public API breaking change / SDK major version up)
3. `$ARGUMENTS` contains `--strict-da`
4. Row 4 territory (auth / billing / payment / migration / security) に該当 — SKILL.md の tier 表・task-tier-boundaries.md と同一規則の転記 (本リストが機械判定の canonical であるため、reviewer 全 ✅ でも Row 4 単独で dispatch する)

## Fatal vs single-trigger (separate concepts)

| Term | Used for | When |
|---|---|---|
| Single-trigger escalator | inline → subagent switch | after Parallel Review, before DA |
| **Fatal criteria** | DA classifying each finding as "fatal / acceptable" | during DA (inline or subagent) |

Fatal ⊇ single-triggers (4 above) **plus** `anti-pattern-checker` ❌ judgments. The latter is already surfaced by Step 3, so escalation handles it via the `❌ ≥ 2` route. Subjective preferences are "acceptable", not "fatal".
