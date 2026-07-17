# automation モード (qa-ui)

automation モードは「automation で実行して」「ブラウザで検証して」「ui-evaluator を使って」等、ブラウザ automation の使用を明示指示したときだけのオプション（Step 1 参照）。本ファイルは automation モードでのみ実施する手順を集約する。SKILL.md の各 Step が該当時点で本ファイルの対応節を読んで実行する。

## Contents

- [Step 1: ChromeDevTools MCP 接続確認](#step-1-chromedevtools-mcp-接続確認)
- [Step 2: 開発サーバー確認・ログイン（automation の続行手順）](#step-2-開発サーバー確認ログインautomation-の続行手順)
- [Step 4: ui-evaluator の Task 起動](#step-4-ui-evaluator-の-task-起動)
- [Step 5 判定 2.: automation（ui-evaluator）側の検証不能判定](#step-5-判定-2-automationui-evaluator側の検証不能判定)
- [${CLAUDE_PLUGIN_ROOT} の解決](#claude_plugin_root-の解決)

## Step 1: ChromeDevTools MCP 接続確認

`mcp__chrome-devtools-direct__list_pages` を呼び出す。

- 成功 → Step 2 へ
- 失敗 → 以下を表示して**停止**:
  「ChromeDevTools MCPに接続できません。Chromeが起動しているか確認してください。」

## Step 2: 開発サーバー確認・ログイン（automation の続行手順）

Step 2 の「検証対象 URL の決定」（1.）は両モード共通で SKILL.md 本文にある。automation モードのみ、URL 決定後に以下 2〜4 を続けて実施する（画面遷移・ログイン確認の自動操作）:

2. `mcp__chrome-devtools-direct__navigate_page` で決定した URL にアクセス
3. `mcp__chrome-devtools-direct__take_snapshot` で画面状態を確認
4. 判定:
   - ログイン済み（「でログイン中」の文字列がある） → そのまま進行
   - ログイン画面が表示された → 以下を表示して**停止し、ユーザーの返答を待つ**:
     「ブラウザで対象環境にログインしてから「ログインしました」と返答してください。検証はその後に再開します。」
     ユーザーから合図を受けたら `take_snapshot` で再確認し、ログイン済みなら進行。
   - 接続失敗（`net::ERR_CONNECTION_RESET` 等） → 以下を表示して**停止**:
     「対象サーバーに接続できません（{URL}）。サーバーが起動しているか、URL が正しいか確認してください。」
   - DB未起動（`ActiveRecord::ConnectionNotEstablished`） → 以下を表示して**停止**:
     「PostgreSQLが起動していません。DBを起動してから再実行してください。」
   - Pending Migration画面（`ActiveRecord::PendingMigrationError`） → 「Run pending migrations」ボタンを `click` して待機後にリロードして再確認

## Step 4: ui-evaluator の Task 起動

ユーザーが「automation で実行して」「ブラウザで検証して」「ui-evaluator を使って」等、ブラウザ automation の使用を明示指示した場合のみ実施する（Step 1 参照）。`Task` ツール (`subagent_type="general-purpose"`、本リポ標準の dispatch) で `ui-evaluator` を起動する（委譲実行で Task が使えない場合の扱いは [delegated-execution.md](delegated-execution.md) を参照）。初回・再検証とも同一テンプレートを使い、`{N}` 等のプレースホルダだけ差し替える:

```
Task:
  subagent_type: general-purpose
  prompt: |
    あなたはUI検証エージェントです。
    以下の指示ファイルを読み、その内容に厳密に従って検証を実行してください。

    指示ファイル: ${CLAUDE_PLUGIN_ROOT}/skills/qa-ui/agents/ui-evaluator.md

    ## 入力
    - QAプランファイルパス: {プランファイルパス（`## 実装準備 > 手動QA手順` を含む）or 分析ファイルパス（AC直接読込みフォールバック時）or プランファイルパス（`## 正本抽出結果` を含む、正本抽出結果直接読込みフォールバック時）or "なし（AC無しモード）"}
    - 変更ファイル一覧: {git diff --name-only の結果 (ブランチ全体、ラウンドを通じて維持)}
    - ラウンド番号: {N}
    - 前回の不合格理由: {初回は「なし（初回）」/ ラウンド2以降は前回の不合格詳細を転記}
    - 適用した修正: {初回は「なし（初回）」/ ラウンド2以降は変更ファイルごとに修正概要 1 行}
    - 手動確認済み: {なし / 検証不能エスカレートからの再開時、または `検証不能(真の制約)` を記帳済みの QA-ID がある場合に、除外した項目を 1 行}
    - 検証対象画面: {特定した画面URL一覧}

    指示ファイルのワークフローに従い、全QA-ID/AC項目を検証してください。
    結果は指示ファイルの「結果出力」フォーマットに厳密に従ってください。
```

**ui-evaluator が報告を返さないときの fallback**: 起動した ui-evaluator が完了 (idle) 通知を繰り返すだけで結果出力が届かない場合、結果の再送要求は 2 回まで。それでも届かなければ待ち続けず、main agent が ChromeDevTools MCP で対象 QA-ID を直接検証してよい。直接検証の観測結果を Step 5 の判定入力に使い、fallback した旨を最終レポートに 1 行明記する (理由: 実測 2026-07-15 — Task 起動した ui-evaluator が催促 2 回の後も最終報告を返さず、main agent の直接検証は数分で完了した。委譲実行の Task 不可時の縮退は起動自体ができない場合の規定で、この「起動できたが報告が届かない」障害はそれとは別に扱う)。

## Step 5 判定 2.: automation（ui-evaluator）側の検証不能判定

Step 5 の判定 2.（検証不能）で、automation（ui-evaluator）の場合は以下に従う:

- automation（ui-evaluator）の場合 → `ui-evaluator.md` の Gotchas テーブル（罠 | 分類 | 対処）でその項目の分類を確認する
  - `workaround既知` → workaround 適用後の再検証結果を確認し、通常の PASS/FAIL 判定に戻す（判定スキップ禁止）
  - `真の制約` → ui-evaluator が試行した代替検証（curl/API/ログ 1回）の結果を確認する。台帳がある場合は該当 QA-ID を `検証不能(真の制約)` として記帳し、**この項目だけを終端としてスキップし、他項目の検証・ループは止めない**。以後のラウンドでは Step 4 プロンプトの `手動確認済み:` 欄に含め、ui-evaluator の再検証対象から除外する（真の制約は代替検証で決着済みのため、ラウンドを跨いで再試行させない）
  - Gotchas テーブルに未カタログの検証不能（初見）→ デフォルト `要人間確認`（安全側）。台帳がある場合は該当 QA-ID を `要人間確認` として記帳したうえで、SKILL.md Step 5 の「検証不能エスカレート」に従い**停止する**（Orchestrated モード時の例外は [orchestrated-mode.md](orchestrated-mode.md) を参照）

## ${CLAUDE_PLUGIN_ROOT} の解決

Step 4 automation の Task 起動プロンプト中 `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま見える場合（`npx skills add` 経由で本 SKILL.md を直接 Read している場合）、この SKILL.md が置かれているディレクトリを skill root とみなし、`${CLAUDE_PLUGIN_ROOT}/skills/qa-ui/` をその skill root へ読み替えてから絶対パスを埋め込む。
