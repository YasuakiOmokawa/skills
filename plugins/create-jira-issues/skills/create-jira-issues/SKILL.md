---
name: create-jira-issues
description: ユーザーストーリーマップやタスク分解プランからJiraチケットを一括作成する場合に使用。ストーリーマップ完成後のチケット化、プランファイルからの一括作成、計画済みストーリー・タスクのJiraへの移行が必要な場合にトリガーされる。
---

# create-jira-issues

## Quick Reference — APIパターン早見表

⚠️ **MCP プレフィックスは環境依存**: 以下の優先順位で取得
  1. `~/.claude/skills-config/jira.md` の `jira_mcp` / `atlassian_mcp` フィールド（`bash scripts/setup.sh` で生成）
  2. `ToolSearch("+jira")` または `ToolSearch("+atlassian")` で実環境のプレフィックスを確認

下表の `<jira-mcp>` / `<atlassian-mcp>` はプレースホルダー。実環境のプレフィックス例: `fdev-jira` / `atlassian` / `claude_ai_Atlassian`。

| 操作 | <jira-mcp> | Atlassian MCP (環境例) |
|------|-----------|---------------|
| チケット作成 | `mcp__<jira-mcp>__create_issue` | `mcp__<atlassian-mcp>__createJiraIssue` |
| チケット更新 | ❌ 権限エラーで失敗（CLAUDE.md既知問題） | `mcp__<atlassian-mcp>__editJiraIssue` (任意フィールド) |
| コメント追加 | `mcp__<jira-mcp>__add_comment` | `mcp__<atlassian-mcp>__addCommentToJiraIssue` |
| issueType一覧 | `mcp__<jira-mcp>__list_jira_issue_types` | `mcp__<atlassian-mcp>__getJiraProjectIssueTypesMetadata` |
| フィールドID取得 | — | `mcp__<atlassian-mcp>__getJiraIssueTypeMetaWithFields` |
| カスタムフィールド設定 | ❌ 不可 | ✅ editJiraIssue の fields で設定 |
| issueリンク作成 | ❌ 不可 | ❌ 専用ツール無し（手動設定リストへ） |
| cloudId取得 (Atlassian専用) | — | `mcp__<atlassian-mcp>__getAccessibleAtlassianResources` |

## ワークフロー

### Step 0: MCPプロバイダ検出

```
ToolSearch("+<jira-mcp>")
  → 見つかった場合: <jira-mcp>用フロー
  → 見つからなかった場合:
    ToolSearch("+atlassian jira")
      → 見つかった場合: Atlassian MCP用フロー
      → 見つからなかった場合:
        「エラーが発生しました。Jira MCPを利用可能にしてください」
        → 停止
```

⚠️ **2系統を無条件に混在使用しない**。検出結果に基づいて1系統のみ使用する。

### Step 1: プランファイル解析

入力プランファイルから以下をパース:

1. `## Phase N:` ヘッダー直下のMarkdownテーブル → US一覧
2. `## タスクリスト` ヘッダー直下の ` ```tsv ` コードフェンス → タスク一覧

**パース契約**:
- USテーブル必須カラム: `US_ID | ユーザー | ストーリー | 受入条件 | 依存US | Jira | 技術メモ`
- タスクTSV必須カラム: `US_ID	Task_ID	タスク名	やること	やらないこと	完了条件	依存タスク	Jira	備考`

「依存US」「依存タスク」列の `-` は空欄と同義（依存なし）として扱う。

パース失敗時: 「プランファイルのフォーマットが map-user-stories の出力契約と一致しません」 → 停止

### Step 2: Jira設定確認

以下を確認:
- **プロジェクトキー** (例: XPROJ)
- **Epic（親チケット）** (例: XPROJ-50)
- **issueType名** → 実環境で確認して選択

issueType 確認手順（必ず実行）:
1. **<jira-mcp> 経路**: `list_jira_issue_types` を呼ぶ。権限エラー/存在エラーなら skill のフォールバック値「ストーリー」「サブタスク」を採用し、ユーザーに「issueType 一覧取得失敗 → 既定値で継続してよいか」を1行で確認してから進む
2. **Atlassian 経路**: `getJiraProjectIssueTypesMetadata(projectKey=...)` を呼ぶ。同じくフォールバック値と確認プロンプト
3. **cloudId（Atlassian 経路のみ必須）**: `getAccessibleAtlassianResources` を呼んで取得。値はユーザー入力不要、以降の全 Atlassian 呼び出しに付ける
4. **customfield ID（Atlassian 経路のみ、Team 等を設定する場合）**: `getJiraIssueTypeMetaWithFields(projectKey, issueTypeId)` でフィールド ID を取得。取得失敗時は手動設定リストに回す

⚠️ **issueType名の罠**: 「タスク」はストーリーと同じhierarchyLevel → 親子関係を作れない。サブタスクには必ず「サブタスク」(hierarchyLevel: -1) を使う。

```
Epic (hierarchyLevel: 1)
  └── ストーリー (hierarchyLevel: 0)  ← issueType: "ストーリー"
        └── サブタスク (hierarchyLevel: -1)  ← issueType: "サブタスク"
```

### Step 3: USストーリー一括作成

全USを**順次**作成し、作成されたキーを**即時記録**:

description は **「Issue description テンプレート（厳守）」セクション** の **USストーリー用テンプレート** に沿って構成する。テンプレート外の情報を入れない。

```
【<jira-mcp>】
  mcp__<jira-mcp>__create_issue(
    project_key, issue_type: "ストーリー",
    summary: "US-XXX: {ストーリー要約}",
    description: "{USストーリー用テンプレートに沿って構成}",
    parent_issue_key: {Epic}
  )
  → 返却キーを記録
  → Teamフィールド設定不可 → 以下 2 つの処理は **どちらか一方** を選ぶ:
    (a) add_commentで "Team: {チーム名}" を残す（将来の検索用、任意）
    (b) 手動設定リスト 1 行に追記（推奨、ユーザーが Jira UI で設定できる）
    ※ 両方同時には書かない（二重管理を避ける）。本 skill の既定は (b) のみ。

【Atlassian MCP (例: mcp__<atlassian-mcp>__)】
  # 前提: Step 2 で cloudId と Team customfield ID は取得済み
  createJiraIssue(
    cloudId: {取得済み},
    projectKey, issueTypeName: "ストーリー",
    summary: "US-XXX: {ストーリー要約}",
    description: "{USストーリー用テンプレートに沿って構成}",
    parent: {Epic}
  )
  → 返却キーを記録
  → Team を customfield で設定する場合:
    editJiraIssue(cloudId, issueIdOrKey, fields: { "{team_customfield_id}": "{チーム名}" })
    ※ customfield ID が未取得なら手動設定リストに回す（擬似 ID を仮置きしない）
```

### Step 4: サブタスク一括作成

全タスクを**順次**作成（parent: 対応するUSストーリーのキー）:

description は **「Issue description テンプレート（厳守）」セクション** の **サブタスク用テンプレート** に沿って構成する。テンプレート外の情報を入れない。

```
【<jira-mcp>】
  mcp__<jira-mcp>__create_issue(
    project_key, issue_type: "サブタスク",
    summary: "{タスク名}",
    description: "{サブタスク用テンプレートに沿って構成}",
    parent_issue_key: {USストーリーのキー}
  )

【Atlassian MCP (例: mcp__<atlassian-mcp>__)】
  createJiraIssue(
    cloudId: {取得済み},
    projectKey, issueTypeName: "サブタスク",
    summary, description: "{サブタスク用テンプレートに沿って構成}",
    parent: {USストーリーのキー}
  )
```

各作成後に**プランファイルのJira列を即時更新**（インクリメンタル記録）。

⚠️ **プラン書き戻しを忘れない**。

### Step 5: 手動設定リスト出力

MCPで自動設定できない項目を明確なリストとして出力:

```
【<jira-mcp> の場合】

## 手動設定が必要な項目

### Teamフィールド設定（{N}件）
以下のチケットにTeamフィールドを手動設定してください:
- XPROJ-501 (US-001)
- XPROJ-502 (US-002)
- ...

### タスク間依存リンク（{N}件）
以下の "is blocked by" リンクを手動設定してください:
- XPROJ-510 is blocked by XPROJ-508
- XPROJ-511 is blocked by XPROJ-508, XPROJ-509
- ...
```

⚠️ **手動設定リストを省略しない**。description内埋込ではなく、コピペ可能なリスト形式で出力する。

### Step 6: 結果レポート

```
## 作成結果

### 作成済みチケット（{N}件）
| US_ID/Task_ID | Jiraキー | summary |
|...|...|...|

### 未作成（{N}件）
| US_ID/Task_ID | 理由 |
|...|...|

### 手動設定が必要な項目
（Step 5の内容を再掲）
```

プランファイルのJira列を最終更新。

## Issue description テンプレート（厳守）

⚠️ **description は冗長になりがち**。以下の **4セクションのみ** で構成する。それ以外（ブランチ名、Epic リンク、DesignDoc URL、PSIRT 番号、ロードマップ、ファイル数目安、概要文、リリースレベル等のメタ情報）は **入れない**。

### 共通ルール

- セクション順は **着手条件 → やること → やらないこと → 完了条件** で固定。順序変更・追加見出し禁止
- 各セクションは箇条書きを基本（1セクション1項目でも箇条書き）
- 値が無いセクションは **「（なし）」または「（特になし）」** と明示。セクション自体を省略しない
- 親 Epic / 親 US は Jira の親子リンク (`parent`) で表現済み → description に再掲しない
- 依存リンク (`is blocked by`) は Step 5 の手動設定リストへ → description には Jiraキーのみ箇条書きで残す
- メタ情報（ブランチ、PSIRT、DesignDoc 等）の **退避先既定 = プランファイルに残置のまま**。Jira へ転記（コメント / カスタムフィールド）はユーザー明示要求がある場合のみ。description には絶対入れない。**Step 5 の手動設定リストにも「メタ情報」サブセクションを作らない**（プラン残置のため転記不要）
- **プレフィックス剥離**: US の「技術メモ」列から「やらないこと」を抽出する際、`やらない: ` `対象外: ` の各プレフィックスを除去し、本文のみを箇条書き化する（プレフィックス保持禁止）。タスク側は「やらないこと」「完了条件」の専用列をそのまま転記するため、プレフィックス剥離は不要
- **抽出値優先**: サブタスクの完了条件は、「完了条件」列に記入があれば **それのみ** を採用。空欄の場合**のみ**「親US {Jiraキー} の AC に準拠」固定文言を使う。**両方併記禁止**（冗長回避）
- **「やること」分解粒度（Decision Table）**:
  - 入力が **単一動詞句**（例:「移行する」「ログインする」）→ **1 項目**（無理に分解しない）
  - 入力に **「+」「、」または独立した複数動詞**（例:「gem追加 + Application 設定」「セッション管理 + ログイン/ログアウト」）→ **その記号 / 動詞境界で分解**
  - 入力が **30文字以下の短文** → 原則 1 項目（短文を機械的に分割しない。接続助詞のみで結ばれた一文が複数動詞を含んでいても、明示記号「+」「、」が無ければこの文字数ルールを優先する）
  - 入力が **30文字超 かつ 複数動詞** → 句点 / 「+」/ 「、」で分解。これらの明示記号が原文に無い場合は接続助詞（て形・連用形「〜し」「〜して」）の動詞境界を分解点として用いる。1動詞 1 項目目安
- **summary 表記規則**: US は `US-XXX: {体言止め30文字目安}` 形式（「〜したい」を漢語名詞化）。サブタスクは「タスク名」列を**そのまま**採用（変形・要約禁止、`#` や英記号も保持）。US 体言化の正規例:
  - 「メールアドレスでログインしたい」→「メールアドレスでログイン」
  - 「パスワードを忘れたらリセットしたい」→「パスワードリセット」
  - 「ユーザー一覧を見たい」→「ユーザー一覧表示」
  - 「旧APIから新クライアントに移行したい」→「新クライアントへ移行」
- **Step 5 のゼロ件表現**: 「Team フィールド設定」「タスク間依存リンク」各サブセクションは **0 件でも見出しを残し**、見出し直下に **「（なし）」のみ 1 行**（リード文「以下のチケットに〜」は **書かない**、箇条書きも **出さない**）。サブセクション自体の省略禁止
- **依存リンク網羅範囲**: Step 5 の依存リンクには **US 間依存と サブタスク間依存の両方** を含める（プランの「依存US」「依存タスク」列の値を全て Jira キーで列挙）

### USストーリー用テンプレート

```markdown
## 着手条件
- {依存US の Jiraキー（複数可）}
- もしくは「（なし）」

## やること
- {「ストーリー」列の本文を 1〜数項目に分解}

## やらないこと
- {スコープ外項目}
- もしくは「（特になし）」

## 完了条件
- {「受入条件」列の各項目を箇条書きで}
```

### サブタスク用テンプレート

```markdown
## 着手条件
- {依存タスク の Jiraキー（複数可）}
- もしくは「（なし）」

## やること
- {「やること」列の内容を 1〜数項目に分解}

## やらないこと
- {「やらないこと」列の内容}
- もしくは「（特になし）」

## 完了条件
- {「完了条件」列の内容。空欄なら「親US {US-Jiraキー} の AC に準拠」}
```

### プランファイル列とのマッピング

| description セクション | USストーリー（プラン列） | サブタスク（プラン列） |
|---|---|---|
| 着手条件 | 「依存US」→ Jiraキーに展開 | 「依存タスク」→ Jiraキーに展開 |
| やること | 「ストーリー」 | 「やること」列から転記（他列からの抽出はしない。1〜数項目への分解のみ「やること」分解粒度の Decision Table に従い、分解で生じる活用形・助詞の調整 — 連用形「〜し」→終止形「〜する」、並列助詞「も」→「を」等、意味を変えない範囲の文法補正 — は許容する） |
| やらないこと | 「技術メモ」内の `やらない:` / `対象外:` 行を抽出（プレフィックス剥離後）。なければ「（特になし）」 | 「やらないこと」列をそのまま転記。空欄なら「（特になし）」 |
| 完了条件 | 「受入条件」 | 「完了条件」列をそのまま転記。空欄なら「親US の AC に準拠」 |

### 禁止パターン例（NG）

以下のような description は **作らない**:

```markdown
## 概要
freee Sign のプラン同期を…  ← 概要セクション禁止

## やること
- ...

## ファイル数目安
4ファイル ← 禁止

## ブランチ
refactor/license-... ← 禁止

## 関連
- Epic: XPROJ-663 ← 親リンクで表現済み、再掲禁止
- DesignDoc: https://... ← 親 Epic / プランへ
- PSIRT: PSIRT-... ← 専用フィールド or 親 Epic へ
```

OK パターン:

```markdown
## 着手条件
- （なし）

## やること
- LicenseProvider Strategy パターンを導入し、PublicApi Provider を新設
- Freee::Client をプロバイダ委譲の薄い形に縮退

## やらないこと
- nil 許容 / ガード撤去（PR4-b で対応）
- OptionFilter 抽出（PR4-a で対応）

## 完了条件
- 既存の Freee::Client メソッド挙動が変わらない（機能変更ゼロ）
- spec/models/freee/ が全 green
- public_api_spec.rb が新設されカバレッジを維持
```

## エラーハンドリング

```
◆ Jira MCP利用不可
  → 「エラーが発生しました。Jira MCPを利用可能にしてください」と出力して停止
  → フォールバックなし

◆ 作成途中で失敗
  → 「エラーが発生しました」と出力して停止
  → 作成済みチケット一覧をプランファイルのJira列に記録済み（インクリメンタル記録のため）
  → ユーザーが問題解決後、未作成分のみ手動で再指示
```


## 併用推奨 skill

- `/map-user-stories` — チケット化前のユーザーストーリー分解に使う
- `/set-jira-story-points` — 作成済み Jira チケットに Story Points を一括設定する
