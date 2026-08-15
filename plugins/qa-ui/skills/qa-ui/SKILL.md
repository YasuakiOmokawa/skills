---
name: qa-ui
description: Use to verify implemented UI. Manual handoff is default; browser automation requires explicit opt-in. Without a QA-ID ledger, use automation fallback.
argument-hint: "[screen or URL]"
---

## Mode

- Explicit `automation`, browser execution, or `ui-evaluator` request: automation.
- Otherwise: manual handoff. Do not call browser tools.
- Orchestrated behavior applies only when the caller explicitly supplies an escalation ledger; use [references/orchestrated-mode.md](references/orchestrated-mode.md).
- Delegated execution uses [references/delegated-execution.md](references/delegated-execution.md), including split manual handoff and missing-input termination.

## Resolve inputs

Resolve the URL in order: complete argument URL; non-placeholder preflight base URL plus argument path; concrete plan URL. If only a path or no base remains, ask once; a noninteractive run returns `不足入力: ベース URL` without later steps. Never hardcode or auto-login. Use preflight login guidance and ask once for unresolved role-specific accounts.

Resolve the current plan from an explicit path, then current non-delegated session. Read `## 実装準備 > 手動QA手順` as the QA-ID source. If absent, warn and fall back in this order:

1. UI-related AC from `<plan>.analysis.md`;
2. `差分`/`未実装` rows in `## 正本抽出結果` (`一致` is excluded);
3. UI files in the branch diff, with minimum render and console-error checks.

All three fallbacks have no ledger and use automation regardless of the default mode. If no UI target exists, report that QA is unnecessary.

Before execution, prepare only test data commands explicitly documented in preflight, plan, README, or tests. Do not invent commands. Ask once for remaining QA-ID-specific states/data; unavailable items become unverifiable.

## Ledger

When QA-ID instructions exist, use `<plan>.qa-ledger.md`. Initialize or evaluate it with [references/ledger-gates.md](references/ledger-gates.md). Preserve all history; the latest row for `(QA-ID, 手段)` wins. Allowed states are:

`pending`, `PASS`, `FAIL(Critical|Major|Minor|exit=N)`, `検証不能(真の制約)`, `要人間確認`, `対象外(N/A)`.

Do not infer result-to-ID mappings or change an existing method. Record only results explicitly mapped to a QA-ID; ask for missing mappings.

## Execute

### Manual default

For each nonterminal `manual` QA-ID, return one block containing source, URL/login/data prerequisites, numbered operations, and checkbox expectations. Then request `PASS`, `FAIL + observed behavior`, or `検証不能 + reason` per QA-ID and stop. On later rounds, include only Major/Minor IDs fixed after the preceding result. A delegated run returns the complete handout and exits so the parent can obtain the human answer and resume from the ledger.

### Automation

Use [references/automation-mode.md](references/automation-mode.md) and the `ui-evaluator` contract. Evidence—not intuition—determines status:

- PASS: the expected outcome is observed with required evidence;
- FAIL: contrary behavior is observed;
- unverifiable: required evidence cannot be obtained.

## Judge and iterate

Apply results to the explicitly named IDs and process in this order:

1. Critical FAIL: report all concurrent failures and escalate without editing.
2. Unverifiable: known workaround evidence is retried normally; a true external/environment constraint becomes terminal `検証不能(真の制約)`; unclear evidence becomes `要人間確認` and escalates. Human-delegated reasons use the same distinction without automation gotchas.
3. Automation-only unplanned differences: add every observed item as `QA-G-NN`, with source and evaluator severity, to ledger and manual-QA plan section. A Critical item escalates; Major/Minor joins the normal loop. Without a ledger, report it as an ordinary failure.
4. Major/Minor: make only the smallest failure-scoped fix, then rerun that QA-ID. Before a repeated fix, verify whether the previous change disappeared or was not built. Per QA-ID, run at most two fixes and three QA rounds. One extra round is allowed only for a single proven one-line root cause with measured confirmation; otherwise escalate.

Never refactor outside the failed behavior. Record each round by appending. Restore QA-created data when possible and report anything left behind.

## Automatic gate and completion

After manual/automation failures are resolved, run the auto commands once using [references/ledger-gates.md](references/ledger-gates.md). The coverage matrix has exactly six columns; QA-ID is awk `$2` and command is `$7`. A zero-test result is not PASS.

Then use the same reference to aggregate latest ledger rows:

- all `PASS`/`対象外(N/A)`: complete;
- any `検証不能(真の制約)`: partial completion with those rows listed;
- any pending, `要人間確認`, or FAIL: not complete; report remaining rows and follow the matching judgment above.

Include screenshots only for automation-verified IDs. In orchestrated mode, replace eligible stops with escalation-ledger append/continue and cap the final status at partial completion when Critical escalation remains.
