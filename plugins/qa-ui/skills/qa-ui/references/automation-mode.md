# Browser automation

Use this file only for explicit browser-automation requests or the no-QA-ID-source fallback defined in `SKILL.md`.

## Connect

`mcp__chrome-devtools-direct__list_pages` を呼び出す。

- 成功 → URL 解決へ
- 失敗 → 以下を表示して**停止**:
  「ChromeDevTools MCPに接続できません。Chromeが起動しているか確認してください。」

## Navigate and authenticate

`SKILL.md` の `Resolve inputs` で URL を決定した後に実行する:

1. `mcp__chrome-devtools-direct__navigate_page` で決定した URL にアクセス
2. `mcp__chrome-devtools-direct__take_snapshot` で画面状態を確認
3. 判定:
   - ログイン済み（「でログイン中」の文字列がある） → そのまま進行
   - ログイン画面が表示された → 以下を表示して**停止し、ユーザーの返答を待つ**:
     「ブラウザで対象環境にログインしてから「ログインしました」と返答してください。検証はその後に再開します。」
     ユーザーから合図を受けたら `take_snapshot` で再確認し、ログイン済みなら進行。
   - 接続失敗（`net::ERR_CONNECTION_RESET` 等） → 以下を表示して**停止**:
     「対象サーバーに接続できません（{URL}）。サーバーが起動しているか、URL が正しいか確認してください。」
   - DB未起動（`ActiveRecord::ConnectionNotEstablished`） → 以下を表示して**停止**:
     「PostgreSQLが起動していません。DBを起動してから再実行してください。」
   - Pending Migration画面（`ActiveRecord::PendingMigrationError`） → 「Run pending migrations」ボタンを `click` して待機後にリロードして再確認

## Run ui-evaluator

automation が明示指示または no-QA-ID-source fallback で選択された場合に実施する。独立 executor が利用できれば `ui-evaluator` を dispatch し、できなければ [delegated-execution.md](delegated-execution.md) の inline 規則に従う。初回・再検証とも同一入力を使う:

```
UI evaluator input:
あなたはUI検証エージェントです。以下の指示ファイルを読み、その内容に従って検証してください。

指示ファイル: ${CLAUDE_PLUGIN_ROOT}/skills/qa-ui/agents/ui-evaluator.md

## 入力
- QAプランファイルパス: {プランファイルパス、分析ファイルパス、または なし}
- 変更ファイル一覧: {ブランチ全体の変更ファイル}
- ラウンド番号: {N}
- 検証対象 QA-ID: {初回は全 UI 項目、以後は修正した FAIL 項目}
- 検証対象定義: {各 QA-ID / QA-F-ID → 出典原文と期待結果}
- 前回の不合格理由: {初回はなし}
- 適用した修正: {初回はなし}
- 手動確認済み: {除外済み QA-ID またはなし}
- 検証対象画面: {URL一覧}

「検証対象定義」を正本として「検証対象 QA-ID」を全て検証し、指示ファイルの結果形式で返してください。
```

**報告なし fallback**: 1回再送要求しても届かなければ main agent が browser capability で直接検証し、fallback を報告する。結果が届くまでの dispatch・再送・inline fallback は同じ QA round とし、証拠を得た評価だけを round に数える。

## Classify unverifiable results

`SKILL.md` の `Judge and iterate` で検証不能を処理するときは以下に従う:

- automation（ui-evaluator）の場合 → `ui-evaluator.md` の Gotchas テーブル（罠 | 分類 | 対処）でその項目の分類を確認する
  - `workaround既知` → workaround 適用後の再検証結果を確認し、通常の PASS/FAIL 判定に戻す（判定スキップ禁止）
  - `真の制約` → ui-evaluator が試行した代替検証（curl/API/ログ 1回）の結果を確認する。台帳がある場合は該当 QA-ID を `検証不能(真の制約)` として記帳し、**この項目だけを終端としてスキップし、他項目の検証・ループは止めない**。以後のラウンドでは ui-evaluator 入力の `手動確認済み:` 欄に含め、再検証対象から除外する
  - Gotchas テーブルに未カタログの検証不能（初見）→ 台帳があれば `要人間確認` として記帳し、なければ同じ状態を報告する。`Judge and iterate` に従い停止する（Orchestrated モード時の例外は [orchestrated-mode.md](orchestrated-mode.md)）

## ${CLAUDE_PLUGIN_ROOT} の解決

ui-evaluator 入力中 `${CLAUDE_PLUGIN_ROOT}` が生文字列なら、この SKILL.md のディレクトリを skill root とみなし、`${CLAUDE_PLUGIN_ROOT}/skills/qa-ui/` をその root へ読み替えて絶対パスを埋め込む。
