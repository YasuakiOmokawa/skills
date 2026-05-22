---
name: mece-plan-review
description: 分析ファイル内の受け入れ条件（AC）に対し BB (仕様) / WB (コード) / Wiki Researcher / Fresh Red Team の 4 視点で MECE 完全性検証を実施し、ユースケース漏れ・技術的対応漏れ・お見合いを検出して分析ファイルに記録する。分析ファイルに AC が定義済みで実装前に MECE 検証が必要な時に使用。事前に /define-acceptance-criteria で AC を定義しておくこと。
---

# MECE Plan Review

プランファイルを **BB Analyst (仕様) + WB Analyst (コード) + Wiki Researcher (Devin) + Fresh Red Team** の 4 役割で MECE 分析し、結果を分析ファイルに記録する。プランファイル本文には品質検証サマリー 1 行のみ追記。

## Wiki 探索の分担

- BB は `read_wiki_*` を **カレントリポ (`${REPO_NAME}`) のみ** に呼ぶ
- 関連リポ (`${RELATED_REPOS}`) の wiki は Wiki Researcher 専属 (BB は読まない)
- main agent が後段で BB + Wiki Researcher 結果を統合

## 重要ルール

1. **分析ファイルへの記録はメインエージェント（あなた）のみ**が行う
2. **Critical=0なら「MECE OK」**、1件以上なら「要修正」→ 分析ファイルに記録（プラン本文は変更しない）
3. **BB / WB Analyst は情報源を完全に分離**: BB はコード参照禁止、WB は仕様 / wiki 参照禁止 (独立性の構造保証)
4. **Fresh Red Team はプラン / AC を持たない**: BB+WB+Wiki 出力のみが入力 (真のクロスリファレンス確保)
5. **指摘件数の縛りなし**: 該当時のみ指摘、0件なら根拠 1 文

## 進捗チェックリスト

TodoWrite で以下のステップを記録すること:
- Step 0: 初期化 (プラン読み込み、AC抽出、リポ取得)
- Step 1: 3 並列 Analyst 起動 (BB + WB + Wiki Researcher)
- Step 1: 3 役の結果受信
- Step 2: Fresh Red Team subagent 起動
- Step 2: Red Team 結果受信
- Step 3-1: 全指摘の分析ファイル記録
- Step 3-2: ACブラッシュアップ (分析ファイル)
- Step 3-3: MECE 分析結果セクション追記 (分析ファイル)
- Step 3-4: プランファイルにサマリー1行追記

## Arguments

- `$ARGUMENTS`: プランファイルのパス
  - パス指定なし時: システムプロンプトの Plan File Info から取得
  - 例: `/mece-plan-review path/to/plan.md`

## Step 0: 初期化

### 0-1: 共通初期化 (引数パース、ファイル特定、リポ取得)

`/define-acceptance-criteria` と共通の初期化手順を実施: [references/init-common.md](references/init-common.md) を参照し、以下を実行:
- プランファイル特定 (`$ARGUMENTS` or システムプロンプト `Plan File Info:`)
- プランファイル全文を Read
- 分析ファイルパス導出 (拡張子前に `.analysis` 挿入)
- リポジトリ名取得 (`git remote get-url origin`)

### 0-2: 分析ファイルから受け入れ条件（AC）の抽出【必須】

mece-plan-review 固有の処理。分析ファイルから `## 受け入れ条件` セクションを抽出する。

- **ACあり**: 検証ターゲットとして §0-3 (enumerate) に進む
- **分析ファイルが存在しない or ACなし**: 以下のメッセージを表示して**即座に中断** (§0-3 以降は実行しない):

```
⛔ 受け入れ条件（AC）が見つかりません。

分析ファイル（{分析ファイルパス}）にACが定義されている必要があります。
MECEは「何に対して漏れがないか」を検証するプロセスです。
検証ターゲットなしでは分析の精度が保証できないため、先にACを定義してください。

👉 /define-acceptance-criteria を実行してACを定義した後、再度 /mece-plan-review を実行してください。
```

### 0-3: AC の enumerate (AC-ID 付与)

抽出した AC セクションを行単位でパースし、`- [ ]` で始まる項目に AC-ID (`AC-1, AC-2, ...`) を機械的に付与する。各項目のカテゴリ (正常系/異常系/エッジケース/非影響確認) と観点ラベル (controlled label) も保持する。

**正規化ルール**:
- 元の `- [ ] permission: ...` 行を `- AC-N (カテゴリ): permission: ...` に変換
- エッジケースの場合は `- [ ] permission [境界値: 本人]: ...` を `- AC-N (エッジケース, 観点: permission, 境界値: 本人): ...` に変換 (タグを内部メタデータとして展開)
- チェックボックス `[ ]` は除去、AC-ID は連番

```
${ENUMERATED_AC} の生成例:
- AC-1 (正常系): permission: 既存ユーザが /auth/login → 200 + JWT
- AC-2 (正常系): permission: 新規ユーザが /auth/saml/login → IdP リダイレクト → callback → ユーザ作成 + JWT + /dashboard
- AC-3 (異常系): permission: SAML 有効ユーザが /auth/login → 403
- AC-4 (エッジケース, 観点: permission, 境界値: 本人): 本人が PATCH /api/users/self → 422
- ...
```

subagent (BB / WB / Red Team) はこの正規化済み文字列を AC-ID ソースとして使う (元の `- [ ]` 行を再パースしない)。

BB / WB Analyst には `${ENUMERATED_AC}` を渡し、各 AC-ID に対する判定 (充足 / 不十分 / 言及なし) を返してもらう (output-format.md「ACカバレッジ機械合成」参照)。

### 0-4: 関連リポジトリ取得（オプション、Wiki Researcher 用）

**GitHub org の解決手順** (必ずこの順序で試行):

1. `~/.claude/skills-config/mece-plan-review.md` を Read し、`github_org:` フィールドを取得
2. 未設定 / ファイル無し → `git remote get-url origin` から `<org>/<repo>` を抽出し、`<org>` 部分を採用
3. ステップ 1-2 いずれも失敗 → 関連リポ収集を**スキップ**し、`${RELATED_REPOS}="なし (org 未解決のため関連リポ調査スキップ)"` リテラルで確定して §0-5 へ進む (以下の gh コマンドは実行しない)

**org 解決成功時のみ** 以下を実行:

```bash
gh repo list ${GITHUB_ORG} --limit 200 --json name,description --jq '.[] | "\(.name)\t\(.description)"'
```

取得したリポジトリ一覧とプラン内容を照合し、関連性の高いリポジトリを 5〜10 件選定。**選定基準**: プラン本文の固有名詞 (サービス名 / モデル名 / API 名) と repo description のキーワード一致を優先。

**⚠️ 重要**: 選定したリポジトリ名は `${GITHUB_ORG}/<リポジトリ名>` 形式で保持する (Devin wiki の `repoName` 引数にそのまま渡す)。

**`${RELATED_REPOS}` の最終フォーマット**:

| 状態 | `${RELATED_REPOS}` の値 |
|---|---|
| gh 成功 + 1 件以上選定 | `${GITHUB_ORG}/<repo1>\n${GITHUB_ORG}/<repo2>\n...` (改行区切り) |
| gh 成功 + 0 件選定 | `"なし"` リテラル (Wiki Researcher dispatch 時はカレントリポのみ) |
| org 解決失敗 (gh 未実行) | `"なし (org 未解決のため関連リポ調査スキップ)"` リテラル |

### 0-5: Step 0 完了時の保持変数 (Step 1 以降で参照)

Step 0 を抜ける時点で以下を変数として保持していること。Step 1-2 の dispatch prompt にそのまま埋め込む:

- `${PLAN_CONTENT}`: プランファイル全文 (Step 0-1 で Read)
- `${ANALYSIS_PATH}`: 分析ファイルの絶対パス (Step 0-1 で導出)
- `${ENUMERATED_AC}`: AC-ID 付きの enumerate 結果 (Step 0-3)
- `${REPO_NAME}`: `<org>/<repo>` 形式 (Step 0-1 / init-common)
- `${RELATED_REPOS}`: 改行区切り or `"なし"` (Step 0-4)
- `${GITHUB_ORG}`: org 部分単独 (Step 0-4)

### 上流 skill との AC 出力フォーマット契約

`/define-acceptance-criteria` の出力に依存するため、本 skill は以下を契約として仮定する。違反時の挙動も明記:

| 期待フォーマット | 違反時の挙動 |
|---|---|
| 分析ファイルに `## 受け入れ条件` (見出しレベル `##`) | セクション無し → Step 0-2 のエラーメッセージで中断 |
| カテゴリは `### 正常系` / `### 異常系` / `### エッジケース` / `### 非影響確認` の `###` 見出し | カテゴリ見出し無し → 全項目を `カテゴリ:不明` で進める |
| AC 行は `- [ ]` 行頭 (チェックボックス必須) | `- ` のみ (チェックボックスなし) → 同様に enumerate (`- [ ]` `- ` 両方を許容) |
| エッジケース行は `[観点ラベル] [境界値: カテゴリ名]:` 形式 | 形式違反 → `観点:不明` でカテゴリ保持し進める |

## Step 1: 3 並列 Analyst 起動

### 1-1: 3 つの Task subagent を同一メッセージ内で並列起動

Task ツール (`subagent_type="general-purpose"`) で同一メッセージ内に 3 つの Task 呼び出しを並べて起動 (並列化のため単一メッセージ必須)。各 agent ファイル (`agents/<role>.md`) の絶対パスを示し、main agent が dispatch 時に**入力データ (AC / プラン / リポ情報) と agent ファイルパス**を渡す。subagent は agent ファイルを Read してから分析を開始する。

`${CLAUDE_PLUGIN_ROOT}` は plugin install 先 (`plugins/mece-plan-review/`) に解決される。npx skills add 経由でも `~/.claude/skills/mece-plan-review/` に skills 配下が展開されるため、相対パスは同じ。

```
Task(subagent_type="general-purpose", prompt="""
以下の agent 定義を Read で読み込み、そこに書かれた責務・情報源制約・出力フォーマットに従ってください:
${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/agents/bb-analyst.md

カレントリポジトリ (BB が wiki 読み可能な唯一の対象): ${REPO_NAME}
関連リポジトリ (参考、BB は読まない / Wiki Researcher が担当):
${RELATED_REPOS}
プランファイル:
${PLAN_CONTENT}
受け入れ条件 (AC-ID 付き、検証ターゲット):
${ENUMERATED_AC}

WB Analyst と独立に動くため、互いの分析結果は参照しないこと。Wiki Researcher と並列起動されるが、BB Analyst は `read_wiki_*` をカレントリポ (${REPO_NAME}) に対してのみ呼ぶこと (関連リポ wiki は Wiki Researcher 専属)。
""")

Task(subagent_type="general-purpose", prompt="""
以下の agent 定義を Read で読み込み、そこに書かれた責務・情報源制約・出力フォーマットに従ってください:
${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/agents/wb-analyst.md

リポジトリ: ${REPO_NAME}
プランファイル:
${PLAN_CONTENT}
受け入れ条件 (AC-ID 付き、検証ターゲット):
${ENUMERATED_AC}

BB Analyst と独立に動くため、互いの分析結果は参照しないこと。
""")

Task(subagent_type="general-purpose", prompt="""
以下の agent 定義を Read で読み込み、そこに書かれた責務・出力フォーマットに従ってください:
${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/agents/wiki-researcher.md

リポジトリ: ${REPO_NAME}
関連リポジトリ:
${RELATED_REPOS}
プランファイル:
${PLAN_CONTENT}
""")
```

**agents/ ファイルの責務マップ**:

| agent ファイル | 責務 | frontmatter `tools` (※) |
|---|---|---|
| `agents/bb-analyst.md` | 仕様情報源で AC 検証 | Read, Grep, Glob, ToolSearch, WebFetch |
| `agents/wb-analyst.md` | コード情報源で AC 検証 | Read, Grep, Glob |
| `agents/wiki-researcher.md` | Devin wiki から事実情報を収集 | ToolSearch |

※ general-purpose subagent は frontmatter `tools` が harness レベルで強制されないため、情報源の分離は agent 本文の禁止記述に依存する self-control。

### 1-2: 3 つの結果を受信

Task の戻り値として自動的に取得。変数 `${BB_RESULT}` / `${WB_RESULT}` / `${WIKI_RESULT}` として保持。

**AC 判定行数の不一致検知 (BB / WB が `${ENUMERATED_AC}` の AC 数と異なる行数で AC 判定を返した場合)**:

1. **1 回リトライ**: 同じ AC リストを再送して再 dispatch。指示に「AC-1 から AC-N まで漏れなく判定行を返す」旨を強調
2. **2 回目も不一致**: 不足分の AC-ID を `judgment:"言及なし", reason:"subagent 不全により自動補完"` として手動補完し、`[subagent部分結果]` タグを Self-report に付与して進行
3. **3 回連続失敗** または **全 AC 欠落**: AskUserQuestion で「subagent が応答不能。手動 MECE レビューに切り替えるか中断するか」をユーザに確認

## Step 2: Fresh Red Team subagent 起動

### 2-1: Fresh Red Team subagent dispatch (JSONL のみ送信)

**⚠️ 重要**: Red Team subagent の入力にプラン本文 / AC 本文を含めない (真の freshness 確保)。BB / WB の出力からは **JSONL ブロック (findings + AC 判定) のみ抽出** して渡し、Markdown ボイラープレート (Self-report / 確信度 / コード参照したくなった場面 / 使った情報源 / 暗黙前提詳細) は dispatch に含めない (Red Team の判定に不要、入力トークン削減)。

**入力抽出ルール** (main agent が dispatch 前に実行):
1. `${BB_RESULT}` / `${WB_RESULT}` から **正規表現 `/^\s*```jsonl\n(.*?)\n\s*```/ms` を 2 回マッチ** させて findings ブロックと AC 判定ブロックを抽出する (先頭の `\s*` で subagent が字下げした場合のフェンスもキャッチ)
2. 2 ブロックの中身 (フェンス内 JSONL 行のみ) を **改行 1 つで連結** して単一文字列 `${BB_JSONL}` / `${WB_JSONL}` を生成する (Red Team が 1 つの prompt セクションで両方を一括 parse できる形)
3. `${WIKI_RESULT}` は Markdown のまま渡してよい (短い箇条書きであり、Red Team が事実情報として参照する補強として有用)
4. **抽出失敗時 (JSONL ブロックが 0 個 / 1 個のみ / フェンスが破損)**:
   - 1 回リトライ: BB / WB に対して同じ AC リストを再送し、「findings (jsonl fence) + AC 判定 (jsonl fence) の 2 ブロックを必ず返してください」と明示
   - 2 回目も失敗: 該当 ロールを `${BB_JSONL}=""` または `${WB_JSONL}=""` (空文字) で Red Team に渡し、Red Team の prompt に「⚠️ <ロール名> の JSONL 出力が欠落しています。残りの入力 + チェックリストでお見合い検出を強化してください」と注釈を追加
   - 3 回連続失敗または BB/WB の両方が JSONL 欠落: AskUserQuestion で「subagent が JSONL 形式を返せない。手動 MECE レビューに切り替えるか中断するか」を確認

`agents/fresh-red-team.md` は起動時に `references/red-team-checklist.md` を自前で Read する設計のため、main agent からチェックリストを渡す必要はない。

```
Task(subagent_type="general-purpose", prompt="""
以下の agent 定義を Read で読み込み、そこに書かれた責務・出力フォーマットに従ってください:
${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/agents/fresh-red-team.md

BB Analyst の findings + AC 判定 (JSONL のみ):
${BB_JSONL}

WB Analyst の findings + AC 判定 (JSONL のみ):
${WB_JSONL}

Wiki Researcher の参考情報 (事実情報のみ、判定なし。BB の補強として使う):
${WIKI_RESULT}

統合評価レポートを `${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/references/red-team-checklist.md` の「統合評価レポートのフォーマット」に従って出力してください。
""")
```

**注意**: BB / WB の Markdown 部分 (Self-report 等) は分析ファイルに記録する用途で main agent 側に保持しておくこと。具体的には Step 3-3 で [references/output-format.md](references/output-format.md) の「各ロール分析詳細」セクション (3 つの `<details>` ブロック) に `${BB_RESULT}` / `${WB_RESULT}` / `${WIKI_RESULT}` の **元 Markdown 全文** をそのまま埋め込む。Red Team dispatch では JSONL のみだが、分析ファイルでは Markdown 全文を保持する二重用途を main agent が担う。

### 2-2: Red Team 結果受信

`${RED_TEAM_RESULT}` として保持。

## Step 3: 分析結果出力

**出力先ルール**: 全分析結果は **分析ファイル** に記録する。プランファイルにはサマリー 1 行のみ追記。プラン本文は一切変更しない。

### 3-1: AC カバレッジ表を機械合成 + 全指摘の分析ファイル記録

**AC カバレッジ表の機械合成** (main agent):
1. BB が返した「AC 判定」テーブルと WB が返した「AC 判定」テーブルを AC-ID で join
2. 各 AC-ID について [references/red-team-checklist.md](references/red-team-checklist.md) の「AC カバレッジ機械合成」ルールで総合判定を決定:
   - どちらか「不十分 / ❌」 → 不十分
   - 両方「言及なし」 → 不十分 (お見合い検出対象)
   - 少なくとも一方「充足 / ✅」+ 他方「充足」or「言及なし」 → 充足
3. 元 AC 文の「カテゴリ」(正常系/異常系/エッジ/非影響) を分析ファイルの AC セクションから補完
4. [references/output-format.md](references/output-format.md) のフォーマットで分析ファイルに記録

**指摘の記録**:
Red Team の統合 Critical / Important / Nice-to-have を **分析ファイル** に記録する。

- **🔴 Critical**: プラン内の該当箇所 (セクション名・内容) と推奨修正内容を併記
- **🟡 Important / 🟢 Nice-to-have**: 簡潔に記録

### 3-2: AC ブラッシュアップ

Red Team の 4 分類結果から AC 改善点を統合:

- **実装漏れ** (BB ✓ WB —) → 該当 AC を強調 + Critical 指摘
- **仕様漏れ** (BB — WB ✓) → AC 追加 (`[MECE追加]` タグ)
- **お見合い** (両者言及なし、Red Team 検出) → AC 追加 (`[MECE追加]` タグ)

分析ファイルの受け入れ条件セクションに対して (output-format.md の 3 ケース表と整合):

| 操作 | タグ | 例 |
|---|---|---|
| 新規 AC 項目を追加 (仕様漏れ・お見合いから) | `[MECE追加]` | 該当カテゴリ内に新規行追加 |
| 既存 AC を **補足のみ** (元の文意を変えずカッコ書きで追記) | タグ不要 | 元の行末尾に `(...)` |
| 既存 AC を **書き換え** (元の文意を変える、実現不可能 / 曖昧 / 不十分の修正) | `[MECE追加 変更]` | 修正後の行頭にタグ + 修正理由併記 |

**「補足」と「書き換え」の境界**: 元の文の主述が変わるかで判定する。主述が同じで限定句や境界値だけが追加されるなら「補足」、主述や HTTP ステータス / I/O 値が変わるなら「書き換え」。

### 3-3: MECE分析結果を分析ファイルに追記

[references/output-format.md](references/output-format.md) のフォーマットに従い、**分析ファイル**末尾に追記。

### 3-4: プランファイルにサマリーを追記

プランファイルの `## 品質検証` セクションに以下を追記する（セクションがなければ作成）:

```markdown
- MECE判定: [OK or 要修正（Critical N件）] / ACカバレッジ [N]/[M] (うち[MECE追加] [X]件) / 漏れ [Y]件 / 重複 [Z]件 → [分析ファイル名]
```

**[MECE追加] [X]件** は品質指標 (詳細は [references/output-format.md](references/output-format.md))。

## Error Handling

### Devin MCP 利用不可

```
ToolSearch("+fdev-devin") → 失敗
  → BB Analyst と Wiki Researcher は wiki なしで継続 (BB はローカル仕様 + 一般知識でフォールバック)
  → 結果に [Devin未使用] タグ付与
```

### Analyst subagent 失敗

```
Task の戻り値がエラーまたはタイムアウト:
  → 該当ロールを [未取得] として記録
  → Red Team に「BB or WB のいずれかが取得できなかった」旨を伝え、残りの結果のみで Step 2 を継続
```

### Red Team subagent 失敗

```
Red Team が失敗した場合:
  → メインエージェントが手動で BB+WB の結果を統合 (フォールバック)
  → 結果に [Red Team フォールバック] タグ付与
```

### プランファイル書き込み失敗

AskUserQuestion でパス確認を依頼。

### 分析ファイルが他プロセスで lock 中 / non-git リポジトリ

- 分析ファイル書込み時に lock 検出 → 1 回リトライ、それでも失敗なら AskUserQuestion で対応確認
- non-git リポ (`git remote get-url origin` が失敗) → `${REPO_NAME}` を「unknown-repo」として継続、Wiki Researcher は `[non-git: Devin 未使用]` で skip

## Agents

- [agents/bb-analyst.md](agents/bb-analyst.md) - Black Box Analyst (仕様情報源限定)
- [agents/wb-analyst.md](agents/wb-analyst.md) - White Box Analyst (コード情報源限定、`tools` から ToolSearch / WebFetch を除外して構造的に分離)
- [agents/wiki-researcher.md](agents/wiki-researcher.md) - Wiki Researcher (Devin wiki 事実収集、判定なし)
- [agents/fresh-red-team.md](agents/fresh-red-team.md) - Fresh Red Team Reviewer (BB / WB / Wiki 出力のみで統合判定)

## References

- [references/init-common.md](references/init-common.md) - 初期化処理 (define-AC と共通)
- [references/red-team-checklist.md](references/red-team-checklist.md) - Fresh Red Team クロスリファレンスチェックリスト (`agents/fresh-red-team.md` から Read される)
- [references/output-format.md](references/output-format.md) - プラン修正・追記フォーマット

## 併用推奨 skill

- `/define-acceptance-criteria` — MECE 検証の対象となる AC を事前に定義する
- `/finalize-plan` — MECE 検証結果を反映してプランを実装フェーズに進める
