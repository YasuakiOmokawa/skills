# Regression scenarios

## Missing ledger with QA-ID instructions

The plan contains manual instructions for `QA-H-01` and `QA-H-02`; `<plan>.qa-ledger.md` does not exist. Preflight supplies a base URL and login guidance. The request says only “UI を確認して” and does not request automation. Return the next action without browser access. On the next invocation, the human supplies only `QA-H-01=PASS`; `QA-H-02` remains pending. In an interrupted-write variant, the matching current generation contains its heading, table header, and only `QA-H-01`; the same plan source still assigns both IDs.

### Requirements checklist

1. [critical] Select manual handoff and call no browser tools.
2. [critical] Initialize the missing ledger from the QA-ID instructions; do not treat the missing file as the no-source automation fallback.
3. Return one complete handoff block per pending manual QA-ID, request a mapped result for each, then stop.
4. Do not invent login or test-data commands.
5. [critical] On the next invocation, append the mapped `QA-H-01` result and return a new handoff for still-pending `QA-H-02`; the later-round failed-and-fixed filter does not hide reportless pending IDs.
6. [critical] In the interrupted variant, reconcile expected `(QA-ID, method)` pairs and append only missing `QA-H-02=pending` under the same generation; a second initialization is idempotent.

## No QA-ID source fallback

The plan has no `手動QA手順` and no analysis file. Its `正本抽出結果` has `FIG-01=一致`, `FIG-02=差分`, and `FIG-03=未実装`. State the mode and derived targets.

### Requirements checklist

1. [critical] Use the no-QA-ID-source automation fallback, not manual handoff.
2. [critical] Select `FIG-02` and `FIG-03`; exclude `FIG-01`.
3. State that no QA-ID ledger or ledger gate applies.
4. Do not replace the available canonical-result source with generic diff inference.

## No QA-ID source with explicit targets

The invocation supplies two visible UI requirements but no plan, analysis, or QA-ID source. A base URL and browser capability are available. One target fails Major twice.

### Requirements checklist

1. [critical] Use the explicit requirements as `QA-F-01` and `QA-F-02`, pass each source text and expected result in `検証対象定義`, and create no ledger.
2. [critical] Count fixes and QA rounds per fallback target, not by nonexistent QA-ID.
3. Retry the failed target only, within the same two-fix/three-round bound.
4. If the evaluator sends no report, request it once before inline browser fallback; count the evidence-bearing result as one round, allow round 4 only as verification-only under the stated exception, and do not allow a third fix.

## Automation: unknown constraint and Major failure

Automation is explicit. Round 1 reports three PASS results, one Major FAIL, and one unverifiable external-IdP redirect classified as `初見`. Describe ledger updates and continuation after a human later confirms the unknown item.

### Requirements checklist

1. [critical] Record the unknown item as `要人間確認` and stop before fixing the Major failure.
2. [critical] After the mapped human result arrives, exclude that item and apply only the smallest Major-scoped fix.
3. Rerun only the fixed QA-ID and keep the confirmed item in `手動確認済み`.
4. Preserve all concurrent results in the report.

## Automation: true constraint and unplanned differences

Automation is explicit. The plan has QA-ID instructions but no explicit `<!-- QA source: ... -->` marker, so initialization uses its source fingerprint. `QA-D-01` is a multipart upload classified as `真の制約`; a one-shot API alternative returned 200. All planned IDs pass, but the evaluator also reports a missing icon as Major and a color mismatch as Minor. Reinvoke after recording both generated items.

### Requirements checklist

1. [critical] Record `QA-D-01` as terminal `検証不能(真の制約)` without stopping other items, including the alternative evidence.
2. [critical] Add both observations as distinct `QA-G-NN` definitions and `generated` state rows under the current ledger generation; do not write either item into the plan QA source.
3. Preserve evaluator severity and send Major/Minor items through the ordinary bounded fix loop.
4. Exclude `QA-D-01` from later evaluator rounds.
5. [critical] Keep both items in the same active generation on reinvocation, preserve their `generated` method/result/fix-round history, rerun fixed items with browser evidence, and send them through neither the automatic command gate nor a manual handoff.

## Automatic gate and completion

The latest ledger has `QA-H-01=PASS`, `QA-H-02=pending`, and `QA-E-01=PASS (self-reported)`. The six-column matrix gives `QA-E-01` an exact source containing escaped `\|` and a command `` `bundle exec rspec spec/ui_spec.rb \| tee /tmp/qa.log` ``. After Markdown unescaping, that canonical command exits 0 but prints `0 examples, 0 failures`. Return the parsed command, appended rows, and completion status.

### Requirements checklist

1. [critical] Append `QA-E-01=要人間確認` with the zero-test evidence; do not overwrite history or accept exit 0 as PASS.
2. [critical] Do not declare completion while `QA-H-02` or the new `要人間確認` row remains.
3. Aggregate by the latest `(QA-ID, 手段)` row in the generation matching the current QA source marker; stale generations never satisfy current IDs.
4. [critical] Protect escaped pipes before six-column splitting, restore the command pipe, and execute the complete cell; do not truncate it to an earlier column or run source text.
5. [critical] Use a checked per-run `mktemp -d` for every intermediate/log, clean it on normal and signal exit, and stop with exit 2 if allocation fails; never share predictable `/tmp/qaui_*` paths.
6. [critical] A current generation with a source heading/header but zero QA state rows is not complete and exits 2.

## Automatic gate excludes terminal and held IDs

The current generation has auto rows `QA-H-01=対象外(N/A)`, `QA-H-02=検証不能(真の制約)`, `QA-H-03=要人間確認`, `QA-H-04=FAIL(Critical)` recorded in the escalation ledger, and `QA-H-05=PASS`. An older generation also escalated `QA-H-06`, but its current row is `pending`.

### Requirements checklist
1. [critical] Run only `QA-H-05` and current `QA-H-06`; do not run H-01 through H-04.
2. [critical] Derive eligibility from each current `(QA-ID, auto)` latest row, not any historical row.
3. [critical] Scope held IDs to the escalation section whose `## QA source` matches the current QA-ledger generation; do not let an old-generation escalation suppress the current `pending` identity.

## Orchestrated Critical isolation

The caller explicitly supplies an escalation-ledger path and requests automation. Round 1 reports `QA-H-01=Critical FAIL`, `QA-H-02=PASS`, and `QA-H-03=PASS`.

### Requirements checklist

1. [critical] Append `QA-H-01` to the escalation ledger and keep it on hold without stopping independent IDs.
2. [critical] Exclude held `QA-H-01` from automatic gates while continuing gates and aggregation for the remaining IDs.
3. Cap the outcome at partial completion and report total/Critical escalation counts.
4. Preserve the six-column escalation-ledger contract under the current `## QA source` generation heading.

## Delegated manual handoff

A delegated run receives three pending manual QA-IDs plus a concrete preflight URL, login guidance, and seed status. It cannot wait synchronously and automation was not requested.

### Requirements checklist

1. [critical] Use manual mode without browser tools.
2. [critical] Return the complete per-ID handout and exit without fabricating results.
3. Tell the caller to obtain mapped human results and resume from the append-only ledger.
4. An orchestrated declaration does not turn the initial handoff into an escalation.

## Holdout: short-lived toast evidence

The evaluator misses a four-second success toast in two `click` → screenshot attempts, while a snapshot observed text insertion. State classification and next evidence attempt.

### Requirements checklist

1. [critical] Treat this as `workaround既知`, not FAIL, `初見`, or `真の制約`.
2. [critical] Use one evaluate-script operation to observe insertion, trigger the final action, await the toast, and pause it with related-target mouse movement before capture.
3. Return to ordinary PASS/FAIL judgment after applying the workaround.
4. Do not apply this workaround to a long-lived dismissible notification.
