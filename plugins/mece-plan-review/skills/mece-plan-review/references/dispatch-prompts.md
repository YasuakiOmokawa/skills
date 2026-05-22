# Subagent dispatch prompts (Step 1 / Step 2 詳細)

`subagent_type="general-purpose"` の Task ツールで起動する prompt template。Step 1 は 3 並列、Step 2 は単独。

## Step 1: 3 並列 Analyst 起動

Task ツールを **同一メッセージ内に 3 つ並べて** 起動する (並列化のため単一メッセージ必須)。

### BB Analyst

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
```

### WB Analyst

```
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
```

### Wiki Researcher

```
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

## agents/ ファイルの責務マップ

| agent | 責務 | 情報源 |
|---|---|---|
| `agents/bb-analyst.md` | 仕様情報源で AC 検証 | カレントリポ wiki + Web + 一般知識 (コード参照禁止) |
| `agents/wb-analyst.md` | コード情報源で AC 検証 | リポ内コード (仕様 / wiki 参照禁止) |
| `agents/wiki-researcher.md` | Devin wiki から事実情報を収集 | カレントリポ + 関連リポ wiki (判定なし) |
| `agents/fresh-red-team.md` | BB / WB / Wiki 出力のみで統合判定 | dispatch で渡された JSONL のみ (plan / AC 本文を持たない) |

※ general-purpose subagent は frontmatter `tools` が harness レベルで強制されないため、情報源の分離は agent 本文の禁止記述に依存する self-control。

## AC 判定行数不一致のリカバリ (Step 1-2)

BB / WB が `${ENUMERATED_AC}` の AC 数と異なる行数で AC 判定を返した場合:

1. **1 回リトライ**: 同じ AC リストを再送して再 dispatch。指示に「AC-1 から AC-N まで漏れなく判定行を返す」旨を強調
2. **2 回目も不一致**: 不足分の AC-ID を `judgment:"言及なし", reason:"subagent 不全により自動補完"` として手動補完し、`[subagent部分結果]` タグを Self-report に付与して進行
3. **3 回連続失敗** または **全 AC 欠落**: AskUserQuestion で「subagent が応答不能。手動 MECE レビューに切り替えるか中断するか」をユーザに確認

## Step 2: Fresh Red Team dispatch (JSONL のみ送信)

**⚠️ 重要**: Red Team subagent の入力にプラン本文 / AC 本文を含めない (真の freshness 確保)。BB / WB の出力からは **JSONL ブロックのみ抽出** し、Markdown ボイラープレート (Self-report / 確信度 / 暗黙前提詳細) は dispatch に含めない。

### 入力抽出ルール (main agent が dispatch 前に実行)

1. `${BB_RESULT}` / `${WB_RESULT}` から **正規表現 `/^\s*```jsonl\n(.*?)\n\s*```/ms` を 2 回マッチ** させて findings ブロックと AC 判定ブロックを抽出 (先頭 `\s*` で字下げフェンスもキャッチ)
2. 2 ブロックの中身を **改行 1 つで連結** して単一文字列 `${BB_JSONL}` / `${WB_JSONL}` を生成 (Red Team が 1 prompt セクションで両方を一括 parse できる形)
3. `${WIKI_RESULT}` は Markdown のまま渡してよい (短い箇条書きで Red Team が事実補強に参照)

### 抽出失敗時 (JSONL ブロックが 0 個 / 1 個 / フェンス破損)

- 1 回リトライ: BB / WB に「findings + AC 判定の 2 jsonl ブロックを必ず返してください」と明示し再送
- 2 回目も失敗: 該当ロールを `${BB_JSONL}=""` または `${WB_JSONL}=""` (空文字) で Red Team に渡し、Red Team の prompt に「⚠️ <ロール名> の JSONL 出力が欠落しています。残りの入力 + チェックリストでお見合い検出を強化してください」と注釈追加
- 3 回連続失敗または BB/WB 両方 JSONL 欠落: AskUserQuestion で「手動 MECE レビューに切り替えるか中断するか」を確認

### Red Team dispatch prompt

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

### 二重用途の注意 (Markdown を捨てない)

BB / WB の Markdown 部分 (Self-report 等) は分析ファイルに記録する用途で main agent 側に保持しておくこと。Step 3-3 で `references/output-format.md` の「各ロール分析詳細」セクション (3 つの `<details>` ブロック) に `${BB_RESULT}` / `${WB_RESULT}` / `${WIKI_RESULT}` の **元 Markdown 全文** をそのまま埋め込む。Red Team dispatch では JSONL のみだが、分析ファイルでは Markdown 全文を保持する二重用途を main agent が担う。
