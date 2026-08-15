---
name: qa-ui
description: Use to verify implemented UI from finalized QA-ID instructions, or through browser fallback when no QA-ID source exists.
---

## Resolve the verification path

Resolve the current plan from an explicit path, then the current non-delegated session. When `## 実装準備 > 手動QA手順` exists, its QA-ID methods are authoritative: `manual` means human handoff and `auto` means the planned shell command. Ignore caller-supplied alternate execution strategies, ledger paths, browser execution, or `ui-evaluator` wording.

If that QA-ID source is absent, warn and derive browser targets in this order:

1. explicit UI requirements in the invocation;
2. UI-related AC from `<plan>.analysis.md`;
3. `差分`/`未実装` rows in `## 正本抽出結果` (`一致` is excluded);
4. UI files in the branch diff, with minimum render and console-error checks.

Assign `QA-F-01...` in source order. This browser fallback uses [references/browser-fallback.md](references/browser-fallback.md), not a ledger. If no UI target exists, report that QA is unnecessary.

For any handoff or browser target, resolve the URL in order: complete argument URL; non-placeholder preflight base URL plus argument path; concrete plan URL. If only a path or no base remains, ask once; a noninteractive run returns `不足入力: ベース URL` without later steps. Never hardcode or auto-login. Use preflight login guidance and ask once for unresolved role-specific accounts.

Prepare only test data commands explicitly documented in preflight, plan, README, or tests. Do not invent commands. Ask once for remaining QA-ID-specific states/data; unavailable items become unverifiable.

## QA-ID ledger

Use `<plan>.qa-ledger.md` and run [references/ledger-gates.md](references/ledger-gates.md) initialization on every invocation before reading state. Preserve all generations; only the generation matching the current `<!-- QA source: ... -->` marker is active, and its latest row for `(QA-ID, 手段)` wins.

Allowed states are `pending`, `PASS`, `FAIL(Critical|Major|Minor|exit=N)`, `検証不能(真の制約)`, `要人間確認`, and `対象外(N/A)`. Methods are `manual` and `auto`; preserve any source row with method `-` as `要人間確認`. Never infer result-to-ID mappings or change an existing method. Record only results explicitly mapped to a QA-ID; ask for missing mappings.

Apply every explicitly mapped human result. For each pending manual QA-ID, and each Major/Minor manual QA-ID fixed after its latest FAIL, return a complete block with source, URL/login/data prerequisites, numbered operations, and checkbox expectations. Request `PASS`, `FAIL + observed behavior`, or `検証不能 + reason` per ID and stop. Do not resend terminal IDs or an unfixed FAIL. Under delegated execution, follow [references/delegated-execution.md](references/delegated-execution.md).

After manual items and failure handling are resolved, run planned `auto` commands once through the reference gate. The coverage matrix has exactly six columns; protect Markdown-escaped `\|` before splitting, read QA-ID from cell 2 and command from cell 7, then restore the pipe. A zero-test result is not PASS.

## Judge, retry, and complete

Evidence—not intuition—determines status. Process results in this order:

1. Critical FAIL: report all concurrent failures and stop without editing.
2. Unverifiable: retry known workaround evidence; record a true external/environment constraint as terminal `検証不能(真の制約)`; record unclear evidence as `要人間確認` and stop.
3. Other FAIL: make only the smallest failure-scoped fix, then repeat that QA-ID's handoff or command. Per QA-ID, run at most two fixes and three QA rounds. One extra verification-only round is allowed for a single proven one-line root cause with measured confirmation; it does not authorize a third fix.

Never refactor outside the failed behavior. Append each ledger round, restore QA-created data when possible, and report anything left behind.

Use [references/ledger-gates.md](references/ledger-gates.md) to aggregate latest rows:

- all `PASS`/`対象外(N/A)`: complete;
- any `検証不能(真の制約)`: partial completion with those rows listed;
- any pending, `要人間確認`, or FAIL: not complete; report remaining rows and follow the matching judgment above.

Without a QA-ID source, report browser evidence and unplanned differences inline without creating a ledger. Apply the same Critical/unverifiable/bounded-fix rules per `QA-F` target. Include screenshots only for browser-verified fallback targets.
