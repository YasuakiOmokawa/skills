# DA escalation / fatal criteria / mode tags

## Three execution modes — full table

| Mode | When | Final-report tag |
|---|---|---|
| **inline default** | DA escalation conditions NOT met (normal path) | none |
| **subagent dispatch** | DA escalation condition met | none |
| **in-context fallback** | independent dispatch unavailable for reviewers or DA | `(in-context fallback mode: <agent name>)` at report tail |

`inline default` ≠ `in-context fallback`. The tail tag is **only** for the environment-constraint fallback, never for normal inline DA.

**Permanent vs temporary dispatch failure** (decides whether fallback applies at all):

- **Permanent** → in-context fallback + tail tag: dispatch capability absent, permission denied, or spawn budget exhausted. 対象 agent / capability の permanent 判定は invocation 終了まで sticky とし、feedback loop の再実行でも dispatch を再試行せず直接 fallback する。
- **Temporary** → 1回だけ再試行し、再失敗なら in-context fallback + tag: concurrent-subagent limit, rate limit.
- **Hung** → dispatch から最大15分だけ待ち、結果がなければ1回だけ re-ping する。re-ping 後は最大60秒を deadline とし、結果がなければ in-context fallback + tag。追加の ping / wait は行わない。
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
4. Row 4 territory (auth / billing / payment / migration / security)。reviewer 全 ✅ でも dispatch する

Escalators select the DA execution mode before critique. DA classification uses the four single-trigger categories plus `anti-pattern-checker` ❌ as the fatal set; subjective preferences are `acceptable`.
