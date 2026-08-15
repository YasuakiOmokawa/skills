# Regression scenarios

## QA-ID source is authoritative

The plan assigns `QA-H-01` to manual QA and `QA-E-01` to an automatic shell command. The request says “browser automation / ui-evaluator で Orchestrated 実行” and supplies an escalation-ledger path. Return the next actions before and after the mapped human result arrives.

### Requirements checklist

1. [critical] Ignore execution-mode wording and the escalation-ledger path; initialize and follow the QA-ID ledger methods.
2. [critical] Call no browser tools for either ID and create no escalation ledger.
3. Return the complete human handoff for `QA-H-01`, request its mapped result, and stop.
4. After the human result resolves manual QA, execute only the planned shell command for `QA-E-01` through the automatic gate.

## Missing ledger with QA-ID instructions

The plan contains manual instructions for `QA-H-01` and `QA-H-02`; `<plan>.qa-ledger.md` does not exist. Preflight supplies a base URL and login guidance. Return the next action without browser access. On the next invocation, the human supplies only `QA-H-01=PASS`; `QA-H-02` remains pending. In an interrupted-write variant, the matching current generation contains its heading, table header, and only `QA-H-01`; the same plan source still assigns both IDs.

### Requirements checklist

1. [critical] Initialize the missing ledger from the QA-ID instructions; do not treat the missing file as the no-source browser fallback.
2. Return one complete handoff block per pending manual QA-ID, request a mapped result for each, then stop.
3. Do not invent login or test-data commands.
4. [critical] On the next invocation, append the mapped `QA-H-01` result and return a new handoff for still-pending `QA-H-02`; the later-round failed-and-fixed filter does not hide reportless pending IDs.
5. [critical] In the interrupted variant, reconcile expected `(QA-ID, method)` pairs and append only missing `QA-H-02=pending` under the same generation; a second initialization is idempotent.

## No QA-ID source fallback

The plan has no `手動QA手順` and no analysis file. Its `正本抽出結果` has `FIG-01=一致`, `FIG-02=差分`, and `FIG-03=未実装`. State the execution path and derived targets.

### Requirements checklist

1. [critical] Use the no-QA-ID-source browser fallback.
2. [critical] Select `FIG-02` and `FIG-03`; exclude `FIG-01`.
3. Assign stable `QA-F-NN` identities and state that no QA-ID ledger or ledger gate applies.
4. Do not replace the available canonical-result source with generic diff inference.

## No QA-ID source with explicit targets

The invocation supplies two visible UI requirements but no plan, analysis, or QA-ID source. A base URL and browser capability are available. One target fails Major twice, and the evaluator reports an unrelated Minor difference.

### Requirements checklist

1. [critical] Use the explicit requirements as `QA-F-01` and `QA-F-02`, pass each source text and expected result in `検証対象定義`, and create no ledger.
2. [critical] Count fixes and QA rounds per fallback target, not by nonexistent planned QA-ID.
3. Retry the failed target only, within the same two-fix/three-round bound.
4. Report the unrelated difference inline as an ordinary failure with overall result `FAIL`; do not create `QA-G`, a `generated` method, or a ledger.
5. If the evaluator sends no report, request it once before inline browser fallback; count the evidence-bearing result as one round, allow round 4 only as verification-only under the stated exception, and do not allow a third fix.

## Automatic gate and completion

Evaluate the automatic gate and completion scripts directly. The latest ledger has `QA-H-01=PASS`, `QA-H-02=pending`, and `QA-E-01=PASS (self-reported)`. The six-column matrix gives `QA-E-01` an exact source containing escaped `\|` and a command `` `bundle exec rspec spec/ui_spec.rb \| tee /tmp/qa.log` ``. After Markdown unescaping, that canonical command exits 0 but prints `0 examples, 0 failures`. Return the parsed command, appended rows, and completion status.

### Requirements checklist

1. [critical] Append `QA-E-01=要人間確認` with the zero-test evidence; do not overwrite history or accept exit 0 as PASS.
2. [critical] Do not declare completion while `QA-H-02` or the new `要人間確認` row remains.
3. Aggregate by the latest `(QA-ID, 手段)` row in the generation matching the current QA source marker; stale generations never satisfy current IDs.
4. [critical] Protect escaped pipes before six-column splitting, restore the command pipe, and execute the complete cell; do not truncate it to an earlier column or run source text.
5. [critical] Use a checked per-run `mktemp -d` for every intermediate/log, clean it on normal and signal exit, and stop with exit 2 if allocation fails; never share predictable `/tmp/qaui_*` paths.
6. [critical] A current generation with a source heading/header but zero QA state rows is not complete and exits 2.

## Automatic gate excludes terminal rows

The current generation has auto rows `QA-E-01=対象外(N/A)`, `QA-E-02=検証不能(真の制約)`, `QA-E-03=要人間確認`, `QA-E-04=FAIL(exit=1)`, and `QA-E-05=PASS`. An older generation has different states for the same IDs.

### Requirements checklist

1. [critical] Run only current `QA-E-04` and `QA-E-05`; do not run E-01 through E-03.
2. [critical] Derive eligibility from each current `(QA-ID, auto)` latest row, not any historical row.
3. Do not read or create an escalation ledger or held-ID list.

## Delegated manual handoff

A delegated run receives three pending manual QA-IDs plus a concrete preflight URL, login guidance, and seed status. It cannot wait synchronously.

### Requirements checklist

1. [critical] Return the complete per-ID handout and exit without browser tools or fabricated results.
2. Tell the caller to obtain mapped human results and resume from the append-only ledger.
3. The inability to wait changes only the handoff boundary; it does not select a separate mode.

## Holdout: short-lived toast evidence

During the no-QA-ID browser fallback, the evaluator misses a four-second success toast in two `click` → screenshot attempts, while a snapshot observed text insertion. State classification and next evidence attempt.

### Requirements checklist

1. [critical] Treat this as `workaround既知`, not FAIL, `初見`, or `真の制約`.
2. [critical] Use one evaluate-script operation to observe insertion, trigger the final action, await the toast, and pause it with related-target mouse movement before capture.
3. Return to ordinary PASS/FAIL judgment after applying the workaround.
4. Do not apply this workaround to a long-lived dismissible notification.
