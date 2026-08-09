# Subagent dispatch prompts (Step 1 / Step 2 詳細)

`subagent_type="general-purpose"` の Task ツールで起動する prompt template。**Step 1 の dispatch は deep tier のみ** (standard は SKILL.md の standard inline 実行手順で main agent が実行し、本ファイルの Step 1 テンプレートを使わない)。Step 2 (Fresh Red Team) は standard の Critical 候補 ≥1 時と deep で使う。

> **全 dispatch 共通 (Core rule 1 の防波堤)**: 本ファイルの全テンプレートの prompt 末尾に「**分析ファイル・プランファイルを含む一切のファイルを書き換えないこと。結果は最終メッセージで返す (記録は main agent が行う)**」を必ず付ける。general-purpose subagent は frontmatter `tools` が harness レベルで強制されないため、この 1 行が並列書き込み衝突を防ぐ唯一の手段。

## Step 1: 並列 Analyst 起動 (deep のみ)

Task ツールを **同一メッセージ内に並べて** 起動する (並列化のため単一メッセージ必須)。BB / WB の 2 並列。両者とも `references/analyst-contract.md` を Read し、指定された役割の節のみ適用する。

### BB Analyst

```
Task(subagent_type="general-purpose", prompt="""
以下の Analyst 契約を Read で読み込み、**BB (Black Box) 節** と共通規則に書かれた責務・情報源制約・出力フォーマットに従ってください (WB 節は適用しない):
${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/references/analyst-contract.md

リポジトリ: ${REPO_NAME}
プランファイル:
${PLAN_CONTENT}
受け入れ条件 (AC-ID 付き、検証ターゲット):
${ENUMERATED_AC}

WB Analyst と独立に動くため、互いの分析結果は参照しないこと。
分析ファイル・プランファイルを含む一切のファイルを書き換えないこと。結果は最終メッセージで返す (記録は main agent が行う)。
""")
```

### WB Analyst

```
Task(subagent_type="general-purpose", prompt="""
以下の Analyst 契約を Read で読み込み、**WB (White Box) 節** と共通規則に書かれた責務・情報源制約・出力フォーマットに従ってください (BB 節は適用しない):
${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/references/analyst-contract.md

リポジトリ: ${REPO_NAME}
コード探索の起点 (絶対パス、この配下だけを読む): ${CODE_ROOT}
プランファイル:
${PLAN_CONTENT}
受け入れ条件 (AC-ID 付き、検証ターゲット):
${ENUMERATED_AC}

BB Analyst と独立に動くため、互いの分析結果は参照しないこと。
分析ファイル・プランファイルを含む一切のファイルを書き換えないこと。結果は最終メッセージで返す (記録は main agent が行う)。
""")
```

## ファイルの責務マップ

| ファイル | 責務 | 情報源 |
|---|---|---|
| `references/analyst-contract.md` (BB 節) | 仕様情報源で AC 検証 | プラン + 一般知識 (コード参照禁止) |
| `references/analyst-contract.md` (WB 節) | コード情報源で AC 検証 | リポ内コード (仕様参照禁止) |
| `agents/fresh-red-team.md` | BB / WB 出力のみで統合判定 | dispatch で渡された JSONL のみ (plan / AC 本文を持たない) |

※ general-purpose subagent は frontmatter `tools` が harness レベルで強制されないため、情報源の分離は契約本文の禁止記述に依存する self-control。

## AC 判定行数不一致のリカバリ (Step 1-2)

BB / WB が `${ENUMERATED_AC}` の AC 数と異なる行数で AC 判定を返した場合:

1. **1 回リトライ**: 同じ AC リストを再送して再 dispatch。指示に「AC-1 から AC-N まで漏れなく判定行を返す」旨を強調
2. **2 回目も不一致**: 不足分の AC-ID を `judgment:"言及なし", reason:"subagent 不全により自動補完"` として手動補完し、`[subagent部分結果]` タグを付与して進行 (欠落が一部 AC に限られ補完で進行できる場合はここでリカバリ完了とし、点 3 へは進まない)
3. **3 回連続失敗** (補完自体が成立しない出力破損が続く場合) または **全 AC 欠落**: AskUserQuestion で「subagent が応答不能。手動 MECE レビューに切り替えるか中断するか」をユーザに確認 (委譲実行時の読み替えは [delegated-execution.md](delegated-execution.md))

## Step 2: Fresh Red Team dispatch (JSONL のみ送信)

**⚠️ 重要**: Red Team subagent の入力にプラン本文 / AC 本文を含めない (真の freshness 確保)。BB / WB の出力からは **JSONL ブロックのみ抽出** し、Markdown ボイラープレート (Self-report / 暗黙前提詳細) は dispatch に含めない。

### 入力抽出ルール (main agent が dispatch 前に実行)

> **standard inline の場合は抽出不要**: inline BB/WB の出力は main agent 自身が JSONL 契約で産出しているため、`${BB_JSONL}` / `${WB_JSONL}` を直接構成する。以下の正規表現抽出は deep の dispatch 結果 (`${BB_RESULT}` / `${WB_RESULT}`) に対してのみ実行する。

1. `${BB_RESULT}` / `${WB_RESULT}` から **正規表現 `/^\s*```jsonl\n(.*?)\n\s*```/ms` を 2 回マッチ** させて findings ブロックと AC 判定ブロックを抽出 (先頭 `\s*` で字下げフェンスもキャッチ)
2. 2 ブロックの中身を **改行 1 つで連結** して単一文字列 `${BB_JSONL}` / `${WB_JSONL}` を生成 (Red Team が 1 prompt セクションで両方を一括 parse できる形)

### 抽出失敗時 (JSONL ブロックが 0 個 / 1 個 / フェンス破損)

- 1 回リトライ: BB / WB に「findings + AC 判定の 2 jsonl ブロックを必ず返してください」と明示し再送
- 2 回目も失敗: 該当ロールを `${BB_JSONL}=""` または `${WB_JSONL}=""` (空文字) で Red Team に渡し、Red Team の prompt に「⚠️ <ロール名> の JSONL 出力が欠落しています。残りの入力 + チェックリストでお見合い検出を強化してください」と注釈追加
- 3 回連続失敗または BB/WB 両方 JSONL 欠落: AskUserQuestion で「手動 MECE レビューに切り替えるか中断するか」を確認 (委譲実行時の読み替えは [delegated-execution.md](delegated-execution.md))

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

統合評価レポートを `${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/references/red-team-checklist.md` の「統合評価レポートのフォーマット」に従って出力してください。
分析ファイル・プランファイルを含む一切のファイルを書き換えないこと。結果は最終メッセージで返す (記録は main agent が行う)。
""")
```

### JSONL のみ保持 (Markdown 全文は保持しない)

分析ファイルに記録するのは findings + AC 判定の **JSONL と合成表のみ** (`references/output-format.md` の「各ロール出力 (JSONL)」)。BB / WB の Markdown 部 (Self-report 等) は JSONL 抽出後に破棄してよく、Step 3 まで全文を保持・転記する義務は無い (元 Markdown 全文の `<details>` 転記は分析ファイル肥大と main agent のコンテキスト保持コストの主因だったため廃止済み)。
