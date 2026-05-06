---
name: qa-ui
description: 実装完了後にChromeDevTools MCPでUI検証を行う。ACがあればAC項目ごとに画面操作・スクリーンショット・pass/fail判定。FAILなら自動修正→再QAを最大3回ループ。
argument-hint: [確認したい画面やURL（省略可）]
---

# UI QA Loop

ChromeDevTools MCPを使い、独立コンテキストのQAエージェントでUI検証を行う。
Generator-Evaluator分離: 実装した自分自身ではなく、別エージェントが画面を見て判定する。

## Arguments

- `$ARGUMENTS`: 確認したい画面やURL（省略可）
  - 指定あり: 指定された画面を優先的に検証
  - 指定なし: ACファイルまたはgit diffから自動特定

## ワークフロー

### Step 1: ChromeDevTools MCP接続確認

`mcp__chrome-devtools-direct__list_pages` を呼び出す。

- 成功 → Step 2 へ
- 失敗 → 以下を表示して**停止**:
  「ChromeDevTools MCPに接続できません。Chromeが起動しているか確認してください。」

### Step 2: 開発サーバー確認 + ログイン

1. `mcp__chrome-devtools-direct__navigate_page` で `http://localhost:3250/` にアクセス
2. `mcp__chrome-devtools-direct__take_snapshot` で画面状態を確認
3. 判定:
   - ログイン画面（ドロップダウンがある） → `evaluate_script` でselect値を変更してログイン:
     ```
     evaluate_script function: |
       () => {
         const select = document.querySelector('select');
         const option = Array.from(select.options).find(o => o.text === 'corporate-advance-admin@example.com');
         if (!option) return 'not found';
         select.value = option.value;
         select.dispatchEvent(new Event('change', { bubbles: true }));
         return 'selected: ' + option.text;
       }
     ```
     注: `click` でのoption選択はタイムアウトするため `evaluate_script` を使うこと
   - ログイン済み（「でログイン中」の文字列がある） → そのまま進行
   - 接続失敗（`net::ERR_CONNECTION_RESET` 等） → 以下を表示して**停止**:
     「開発サーバー（localhost:3250）が起動していません。」
   - DB未起動（`ActiveRecord::ConnectionNotEstablished`） → 以下を表示して**停止**:
     「PostgreSQLが起動していません。DBを起動してから再実行してください。」
   - Pending Migration画面（`ActiveRecord::PendingMigrationError`） → 「Run pending migrations」ボタンを `click` して待機後にリロードして再確認

**テストユーザー:**
| 用途 | メールアドレス |
|------|---------------|
| ADMIN画面確認 | `corporate-advance-admin@example.com` |
| 一般画面確認 | プラン別に適切なユーザーを選択 |

### Step 3: AC検証項目の特定

#### ACファイルがある場合

1. `~/.claude/plans/` 配下の `*.md`（`*.analysis.md` を除く）を検索
2. 各プランファイル内で `git checkout -b` の引数とカレントブランチ名を照合
3. 一致するプランファイルに対応する `*.analysis.md` を読み込む
4. UI関連のAC項目を抽出（「画面」「表示」「クリック」「遷移」「フォーム」等のキーワード）
5. UI関連のAC項目が0件 → AC無しモードにフォールバック

#### AC無しモード

1. `git diff --name-only origin/develop...HEAD` で変更ファイル取得
2. 変更ファイルが0件 → 以下を表示して**完了**:
   「UI検証対象の変更ファイルがありません。フロントエンド変更を含むブランチで実行してください。」
3. `.tsx`, `.jsx`, `.slim`, `.erb`, `.scss`, `.css` の変更を特定
4. フロントエンド関連の変更が0件 → 以下を表示して**完了**:
   「フロントエンド関連の変更がありません。UI検証は不要です。」
5. 変更されたView/Componentから対象画面URLを推論
6. 最低限の検証項目: 「画面が正常に表示されるか」「JSエラーが出ていないか」

#### $ARGUMENTS が指定された場合

上記のいずれかで特定した検証項目に加え、指定されたURLや画面を優先的に検証対象に含める。

### Step 4: UI検証エージェント起動（ラウンド1）

`Agent` ツールで `ui-evaluator` を起動する。

```
Agent tool:
  subagent_type: general-purpose
  prompt: |
    あなたはUI検証エージェントです。
    以下の指示ファイルを読み、その内容に厳密に従って検証を実行してください。

    指示ファイル: ~/.claude/skills/qa-ui/agents/ui-evaluator.md

    ## 入力
    - ACファイルパス: {ACファイルパス or "なし（AC無しモード）"}
    - 変更ファイル一覧: {git diff --name-only の結果}
    - ラウンド番号: 1
    - 前回の不合格理由: なし（初回）
    - 検証対象画面: {特定した画面URL一覧}

    指示ファイルのワークフローに従い、全AC項目を検証してください。
    結果は指示ファイルの「結果出力」フォーマットに厳密に従ってください。
```

### Step 5: 結果判定

QAエージェントの結果を読み取り、判定する。

#### 総合PASS の場合
以下を表示して**完了**:

```
## UI QA 完了

全AC項目がPASSしました。

### スクリーンショット
[QAエージェントが撮影したスクリーンショット一覧]
```

#### 総合FAIL の場合

不合格項目の重大度を確認:

**Critical が1件でも含まれる → 即エスカレート:**
```
## UI QA エスカレート

Criticalな不合格が検出されました。人間の判断が必要です。

### 不合格項目
[QAエージェントの不合格詳細をそのまま表示]
```

**Major/Minor のみ、かつラウンド3未満 → 自動修正:**
1. QAエージェントの「修正の示唆」に基づいてコードを修正
2. Step 4 に戻り、ラウンド番号をインクリメントして再度QAエージェント起動

ラウンド2以降のAgent起動時は `前回の不合格理由` にQAエージェントの不合格詳細を含める。

#### ラウンド3でもFAIL → エスカレート:
```
## UI QA エスカレート

3回修正しましたが解消できません。

### 解消できなかった項目
[残りの不合格項目]

### 修正履歴
- ラウンド1: [何を修正したか]
- ラウンド2: [何を修正したか]
- ラウンド3: [何を修正したか]
```
