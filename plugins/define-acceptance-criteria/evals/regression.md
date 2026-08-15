# define-acceptance-criteria regression

Run each fixed scenario with a fresh blank-context executor in an isolated fixture. Score the written plan and analysis files, not self-report. All `[critical]` items must pass. Run the hold-out only after tuning and do not tune against its result.

## Standard: API and service change

Input: a CSV export adds one column through an existing controller and service. The plan lists both implementation files and a spec, and states that existing admin authorization is unchanged. Git is unavailable.

1. [critical] The analysis contains `### Tier` and all required acceptance-criteria headings, including `### 不変条件` and `### 非影響確認`.
2. [critical] Tier is standard; three selected axes fill all nine normal/error/edge cells with controlled-label checkbox rows.
3. [critical] No invariant trigger is observable, so invariant rows are zero and the analysis records the reason instead of inventing one.
4. The multi-type selection rules are applied, and unchanged authorization is retained as a non-impact regression check.
5. Exactly three technical risks contain the unknown, worst impact, and executable verification. Punctuation count is not graded.
6. The plan quality summary uses actual `N`, `I`, `K`, `R`, and `M` counts.

## Delegated thin plan

Input: an absolute plan path is supplied in the delegation prompt. The plan says only that search behavior will improve, contains no file list, and is outside a Git repository. Synchronous questions are unavailable.

1. [critical] The explicit path is used and `<plan>.analysis.md` is created without waiting for confirmation.
2. [critical] The executor continues with a best-effort inferred file list marked `(推定)` and fills every required acceptance-criteria cell.
3. The tier and inference basis are recorded in the analysis.
4. The final report contains the absolute analysis path, tier, AC count summary, and inferred-input risk.

## Deep: period-crossing ledger

Input: a migration changes an existing fixed-asset ledger schema and CSV output across current-period, next-period preview, and closed-period states. The plan exposes continuity, freeze, and aggregate relationships but leaves the displayed period unspecified.

1. [critical] Risk forces deep; five main axes fill fifteen required cells.
2. [critical] Observable invariant triggers produce only supportable equality/order relations, including continuity or freeze, with independent observation methods.
3. Invariant rows do not increase the axis count or required-cell count, and their number does not exceed the deep cap.
4. Unspecified expectations outside the invariant relation carry `(仕様確定要)` rather than invented facts.
5. The quality-summary arithmetic matches the written rows.

## Standard: behavior-preserving refactor

Input: two existing files move ranking logic from a controller to a service without changing the endpoint's inputs, outputs, errors, or authorization.

1. [critical] The normal, error, and edge rows assert the corresponding pre-change input/output behavior remains unchanged; they do not invent a new feature.
2. [critical] Tier is standard and only the adjacent unchanged authorization appears as a non-impact regression check; primary endpoint behavior is not duplicated there.
3. Technical risks concern the refactor boundary or verification, not speculative product behavior.

## Hold-out: added file only

Input: a lite plan adds one isolated formatter file; no other file is added, modified, or deleted.

1. [critical] Tier is lite and one axis fills three required cells.
2. [critical] `### 非影響確認` remains present, contains no checkbox AC rows, and states why checks were omitted.
3. The analysis records the added-only classification; the plan summary reports `K=0` through the canonical count format.
4. No unrelated existing feature is invented as a non-impact target.

## Structured-source atom transfer

Input: the analysis has a reordered `期待値 | 状態 | atom ID` table with `FIG-01=一致` whose expectation contains `未実装` and an escaped pipe, `FIG-02=差分` with an exact visible expectation, `FIG-03=未実装`, and one unresolved icon item.

1. [critical] Add one controlled-label AC each for `FIG-02` and `FIG-03`, retaining the atom IDs and exact expectations.
2. [critical] Resolve all three columns by header name, restore the escaped pipe in the expectation, and add no AC for `FIG-01` or the unresolved icon. A missing required header or FIG row outside the canonical state grammar stops before AC/plan edits with the canonical input-invalid status.
3. [critical] A rerun keeps one owned AC/risk/tier block, updates existing `[FIG-NN]` rows without duplication, and preserves the source table; atom rows increase X/M but not N.
4. [critical] After MECE exists, a normal rerun stops without erasing additions; only explicit `--reset-mece` removes old MECE additions/result/summary and reports the required rerun.
