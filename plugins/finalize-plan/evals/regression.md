# finalize-plan regression

Run each scenario with a fresh executor. All `[critical]` items must pass.

## Standard: coverage, ledger, preflight

Input: standard plan with duplicate stale `## 実装準備` sections, complete AC/MECE, and a structured-source table whose columns are reordered to `atom ID | 状態 | 期待値`. It has one uncovered atom, one matching atom whose expectation is `A \| 未実装 B`, an unrelated MECE table row containing `差分`, and an atom citation outside `## 実装準備`; no ledger/preflight.

1. [critical] QA-ID is enumerated once; manual and auto planners run in parallel without reclassification.
2. [critical] Reusing an existing manual QA preserves its AC source and adds exact `**正本出典: <atom>**` inside that QA block; a new QA uses the atom as its source. The rerun reaches zero diff.
3. [critical] Ledger contains every enumerated and supplemented QA-ID. Assignment is auto-first, then manual; orphan is `- / 要人間確認 / 担当手段未特定`; dual coverage yields one auto row.
4. [critical] Ledger creates a generation keyed by ordered QA-ID/method/exact-source data and writes the same plan marker; a changed/reordered AC starts current assignments pending instead of inheriting an ordinal ID's old PASS, while adding QA-G does not reset the generation.
5. [critical] Preflight has exactly six fields. Known values are copied, unknown values are `未定`, and one question covers all unknowns.
6. Auto coverage matrix has exactly six columns with QA-ID in `$2` and execution command in `$7`.
7. [critical] Coverage requires `atom ID` / `期待値` / `状態`, resolves them by header name after protecting escaped pipes, and accepts only the canonical state grammar, including reordered columns; exact QA-block source lines and rows under QA-ID coverage-matrix headings satisfy atoms, while prose, expectation text, MECE rows, and unrelated tables cannot create or satisfy them. A missing header or unknown FIG state returns structural error and terminally stops before ledger/preflight instead of producing an empty required set.
8. [critical] Output contains one `## 実装準備` and one associated separator. Repair runs once and the gate reruns once; a still-uncovered variant records exact atom IDs and remains incomplete without another repair loop.

## Lite

Input: four ACs including one MECE addition, complete AC/MECE, no `## 正本抽出結果` section.

1. [critical] No planner is dispatched; main reads the manual agent and writes QA-ID headings inline.
2. [critical] Auto section remains with `自動QA: lite tier のため対象外 (auto 0 件)`.
3. [critical] Coverage records `正本カバレッジ: skip (構造化正本なし、または分析ファイル空)` and performs no other source check.
4. All six category counts remain visible, including zeros.
5. Zero auto rows is valid; every QA-ID is manual or orphan.

## Input gate

Evaluate: (a) no analysis file, (b) one required section missing, (c) complete sections after any upstream route.

1. [critical] (a) and (b) stop with the canonical AC/MECE message; PoC or prototype context creates no exception.
2. [critical] (c) runs the same full workflow regardless of upstream route.
3. A Figma URL without `## 正本抽出結果` triggers the extraction proposal; delegated execution records it and continues.

## Preflight edge

Input: `{BASE_URL}` placeholder, known test-data command, known permission without purpose, unknown login/server command, branch `develop`.

1. [critical] Placeholder becomes `未定`; test data is copied; permission purpose may be derived only from a matching QA-ID; branch is copied as `develop`.
2. [critical] Login and server command remain `未定` and are asked together.
3. Secrets, email, and actual accounts are absent.
4. [critical] A changed source fingerprint regenerates all six current rows; an unchanged fingerprint preserves user-updated cells.

## Non-UI batch plan

Input: complete standard AC/MECE for a scheduled batch with no screen or endpoint. The plan documents a CLI trigger and a result log but no test-data command.

1. [critical] Manual QA uses the documented CLI and log observation without inventing UI or network steps.
2. [critical] Missing test data remains `未定`; no command is fabricated.
3. Every enumerated QA-ID is planned or reported unresolved.

## Delegated execution

Pattern A supplies an absolute plan path with AskUserQuestion unavailable. Pattern B supplies no path.

1. [critical] A resolves plugin paths absolutely, uses nested Task when available, never asks, and reports artifact paths, coverage, assignment counts, and unresolved items.
2. [critical] B neither searches nor writes; it immediately ends with `不足入力: プランファイルパス`.
3. Task absence alone selects in-context fallback; being a subagent does not.

## Deep delegated hold-out

Input: auth plan with three ACs, complete AC/MECE, Figma URL in a Read DD without source heading, explicit delegated path, Task available, AskUserQuestion unavailable, and an incomplete preflight with an old source fingerprint.

1. [critical] Risk forces deep and both planners run in parallel.
2. [critical] Figma extraction is reported as unresolved while execution continues.
3. [critical] The stale preflight is regenerated as exactly six current rows; unresolved values are saved as `未定`, and no question is attempted.
4. [critical] Final report includes three artifact paths, coverage, ledger assignment counts, and unresolved items.
5. Permission type/purpose reaches the final plan; secrets, email, and actual accounts do not.
