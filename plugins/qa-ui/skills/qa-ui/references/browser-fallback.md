# Browser fallback

Use this file only when `SKILL.md` finds no QA-ID source.

## Connect, navigate, and authenticate

Call `mcp__chrome-devtools-direct__list_pages`. On failure, report that ChromeDevTools MCP is unavailable and stop.

Navigate to the URL resolved by `SKILL.md`, take a snapshot, then handle the observed state:

- logged in: continue;
- login page: ask the user to log in, wait for their confirmation, then verify with another snapshot;
- connection failure: report the URL and ask the user to check the server and URL;
- `ActiveRecord::ConnectionNotEstablished`: report that PostgreSQL must be started;
- `ActiveRecord::PendingMigrationError`: click `Run pending migrations`, wait, reload, and verify.

## Run the evaluator

Dispatch an independent `ui-evaluator` when available. Otherwise follow [delegated-execution.md](delegated-execution.md). Use the same inputs for initial and repeated verification:

```text
UI evaluator input:
あなたはUI検証エージェントです。以下の指示ファイルを読み、その内容に従って検証してください。

指示ファイル: ${CLAUDE_PLUGIN_ROOT}/skills/qa-ui/agents/ui-evaluator.md

## 入力
- QAプランまたは分析ファイル: {パス、または なし}
- 変更ファイル一覧: {ブランチ全体の変更ファイル}
- ラウンド番号: {N}
- 検証対象: {初回は全 QA-F、以後は修正した FAIL 項目}
- 検証対象定義: {各 QA-F-ID → 出典原文と期待結果}
- 前回の不合格理由: {初回はなし}
- 適用した修正: {初回はなし}
- 検証済み除外: {検証不能(真の制約) またはなし}
- 検証対象画面: {URL一覧}

「検証対象定義」を正本として「検証対象」を全て検証し、指示ファイルの結果形式で返してください。
```

If no report arrives, request it once, then run the same evaluator contract inline when browser capability is available. Dispatch, retry, and inline fallback belong to the same QA round; count only an evidence-bearing result.

## Classify unverifiable results

Use the `ui-evaluator.md` Gotchas table:

- `workaround既知`: apply the workaround and return to ordinary PASS/FAIL judgment;
- `真の制約`: confirm one attempted alternative using curl, API, or logs; report the target as terminal and continue with other targets;
- uncatalogued: report `要人間確認` and stop.

Resolve a literal `${CLAUDE_PLUGIN_ROOT}` by treating the directory containing `SKILL.md` as the skill root and replacing `${CLAUDE_PLUGIN_ROOT}/skills/qa-ui/` with that absolute path.
