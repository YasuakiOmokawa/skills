# finalize-plan regression

Run each scenario with a fresh executor. All `[critical]` items must pass.

## Standard: coverage, ledger, preflight

Input: standard plan, complete AC/MECE, one uncovered structured-source atom, no ledger/preflight.

1. [critical] QA-ID is enumerated once; manual and auto planners run in parallel without reclassification.
2. [critical] The uncovered atom is added to manual QA with original expectation and `出典: <atom>`; the rerun reaches zero diff and records `補完 N 件 (再実行で差分 0 件)`.
3. [critical] Ledger contains every enumerated and supplemented QA-ID. Assignment is auto-first, then manual; orphan is `- / 要人間確認 / 担当手段未特定`; dual coverage yields one auto row.
4. [critical] Preflight has exactly six fields. Known values are copied, unknown values are `未定`, and one question covers all unknowns.
5. Auto coverage matrix has exactly six columns with QA-ID in `$2` and execution command in `$7`.

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

## Delegated execution

Pattern A supplies an absolute plan path with AskUserQuestion unavailable. Pattern B supplies no path.

1. [critical] A resolves plugin paths absolutely, uses nested Task when available, never asks, and reports artifact paths, coverage, assignment counts, and unresolved items.
2. [critical] B neither searches nor writes; it immediately ends with `不足入力: プランファイルパス`.
3. Task absence alone selects in-context fallback; being a subagent does not.

## Deep delegated hold-out

Input: auth plan with three ACs, complete AC/MECE, Figma URL in a Read DD without source heading, explicit delegated path, Task available, AskUserQuestion unavailable, and an existing preflight missing two rows.

1. [critical] Risk forces deep and both planners run in parallel.
2. [critical] Figma extraction is reported as unresolved while execution continues.
3. [critical] Existing preflight values remain; only missing rows are added, unresolved values are saved as `未定`, and no question is attempted.
4. [critical] Final report includes three artifact paths, coverage, ledger assignment counts, and unresolved items.
5. Permission type/purpose reaches the final plan; secrets, email, and actual accounts do not.
