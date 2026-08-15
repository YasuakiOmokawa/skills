---
name: qa-ui
description: Use to verify implemented UI. With QA-ID instructions, manual handoff is default and a missing ledger file is initialized. Browser automation requires explicit opt-in unless no QA-ID source exists and fallback is required.
---

## Mode

- Explicit `automation`, browser execution, or `ui-evaluator` request: automation.
- Otherwise: manual handoff. Do not call browser tools.
- Orchestrated behavior applies only when the caller explicitly supplies an escalation ledger; use [references/orchestrated-mode.md](references/orchestrated-mode.md).
- Delegated execution uses [references/delegated-execution.md](references/delegated-execution.md), including split manual handoff and missing-input termination.

## Resolve inputs

Resolve the URL in order: complete argument URL; non-placeholder preflight base URL plus argument path; concrete plan URL. If only a path or no base remains, ask once; a noninteractive run returns `不足入力: ベース URL` without later steps. Never hardcode or auto-login. Use preflight login guidance and ask once for unresolved role-specific accounts.

Resolve the current plan from an explicit path, then current non-delegated session. Read `## 実装準備 > 手動QA手順` as the QA-ID source. If absent, warn and fall back in this order:

1. explicit UI requirements in the invocation;
2. UI-related AC from `<plan>.analysis.md`;
3. `差分`/`未実装` rows in `## 正本抽出結果` (`一致` is excluded);
4. UI files in the branch diff, with minimum render and console-error checks.

These source fallbacks do not use a QA-ID ledger and run in automation mode. Assign targets `QA-F-01...` in source order for evaluator and rerun identity only. If no UI target exists, report that QA is unnecessary.

Before execution, prepare only test data commands explicitly documented in preflight, plan, README, or tests. Do not invent commands. Ask once for remaining QA-ID-specific states/data; unavailable items become unverifiable.

## Ledger

When QA-ID instructions exist, use `<plan>.qa-ledger.md` and run [references/ledger-gates.md](references/ledger-gates.md) generation initialization on every invocation before reading state. Preserve all generations; only the generation matching the current `<!-- QA source: ... -->` marker is active, and its latest row for `(QA-ID, 手段)` wins. Allowed states are:

`pending`, `PASS`, `FAIL(Critical|Major|Minor|exit=N)`, `検証不能(真の制約)`, `要人間確認`, `対象外(N/A)`.

Methods are `auto` (plan の shell command gate), `manual` (human handoff), and `generated` (automation が発見した QA-G の browser/evidence 再検証)。`generated` は shell gate と manual handoff のどちらにも流さない。

Do not infer result-to-ID mappings or change an existing method. Record only results explicitly mapped to a QA-ID; ask for missing mappings.

## Execute

### Manual default

After applying every explicitly mapped human result, return one block for (a) each `pending` manual QA-ID, including IDs omitted from the preceding report, and (b) each Major/Minor manual QA-ID fixed after its latest FAIL. Include source, URL/login/data prerequisites, numbered operations, and checkbox expectations. Request `PASS`, `FAIL + observed behavior`, or `検証不能 + reason` per included ID and stop. Do not resend terminal IDs or an unfixed FAIL. A delegated run returns the complete handout and exits so the parent can obtain the human answer and resume from the ledger.

### Automation

Use [references/automation-mode.md](references/automation-mode.md) and the `ui-evaluator` contract. Evidence—not intuition—determines status:

- PASS: the expected outcome is observed with required evidence;
- FAIL: contrary behavior is observed;
- unverifiable: required evidence cannot be obtained.

## Judge and iterate

Apply results to the explicitly named IDs and process in this order:

1. Critical FAIL: report all concurrent failures and escalate without editing.
2. Unverifiable: known workaround evidence is retried normally; a true external/environment constraint becomes terminal `検証不能(真の制約)`; unclear evidence becomes `要人間確認` and escalates. Human-delegated reasons use the same distinction without automation gotchas.
3. Automation-only unplanned differences: add every observed item as `QA-G-NN` to the **current ledger generation** with method `generated`, source, expected result, evaluator severity, and its observed state. Number from the highest QA-G suffix in that generation. Store its definition as a non-table bullet under `### Generated QA` in the ledger; do not edit the plan's fingerprinted `## 実装準備` QA source or its marker. Keep `generated` on later browser or explicitly mapped human evidence rows; after a fix, browser automation reruns that ID directly. A Critical item escalates; Major/Minor joins the normal loop. Without a ledger, report it as an ordinary failure.
4. Major/Minor: make only the smallest failure-scoped fix, then rerun that QA-ID or fallback target. Before a repeated fix, verify whether the previous change disappeared or was not built. Per QA-ID or fallback target, run at most two fixes and three QA rounds. One extra verification round is allowed only for a single proven one-line root cause with measured confirmation; it does not authorize a third fix. Otherwise escalate.

Never refactor outside the failed behavior. When a ledger exists, append each round; otherwise report the evidence inline. Restore QA-created data when possible and report anything left behind.

## Automatic gate and completion

When a QA-ID ledger exists and manual/automation failures are resolved, run the auto commands once using [references/ledger-gates.md](references/ledger-gates.md). The coverage matrix has exactly six columns; protect Markdown-escaped `\|` before splitting, then read QA-ID from cell 2 and command from cell 7 and restore the pipe. A zero-test result is not PASS. Without a ledger, skip this gate and report the automation result directly.

For a ledger run, use the same reference to aggregate latest rows:

- all `PASS`/`対象外(N/A)`: complete;
- any `検証不能(真の制約)`: partial completion with those rows listed;
- any pending, `要人間確認`, or FAIL: not complete; report remaining rows and follow the matching judgment above.

Include screenshots only for automation-verified IDs. In orchestrated mode, replace eligible stops with escalation-ledger append/continue and cap the final status at partial completion when Critical escalation remains.
