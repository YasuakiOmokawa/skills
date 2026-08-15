# Subagent dispatch prompts (Step 1 / Step 2 詳細)

Independent-executor prompt template。**Step 1 の dispatch は deep tier のみ** (standard は SKILL.md の standard inline 実行手順で main agent が実行し、本ファイルの Step 1 テンプレートを使わない)。Step 2 (Fresh Red Team) は standard の Critical 候補 ≥1 時と deep で使う。

全 prompt 末尾に「分析ファイル・プランファイルを含む一切のファイルを書き換えない。結果は最終メッセージで返す」を付ける。

## Step 1: 並列 Analyst 起動 (deep のみ)

BB / WB の independent executors を同時に起動する。両者とも `references/analyst-contract.md` を読み、指定された役割の節だけ適用する。

### BB Analyst

```
Dispatch an independent executor with this prompt:
以下の Analyst 契約を Read で読み込み、**BB (Black Box) 節** と共通規則に書かれた責務・情報源制約・出力フォーマットに従ってください (WB 節は適用しない):
${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/references/analyst-contract.md

リポジトリ: ${REPO_NAME}
プランファイル:
${PLAN_CONTENT}
受け入れ条件 (AC-ID 付き、検証ターゲット):
${ENUMERATED_AC}

WB Analyst と独立に動くため、互いの分析結果は参照しないこと。
分析ファイル・プランファイルを含む一切のファイルを書き換えないこと。結果は最終メッセージで返す (記録は main agent が行う)。
```

### WB Analyst

```
Dispatch an independent executor with this prompt:
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
```

## ファイルの責務マップ

| ファイル | 責務 | 情報源 |
|---|---|---|
| `references/analyst-contract.md` (BB 節) | 仕様情報源で AC 検証 | プラン + 一般知識 (コード参照禁止) |
| `references/analyst-contract.md` (WB 節) | コード情報源で AC 検証 | リポ内コード (仕様参照禁止) |
| `agents/fresh-red-team.md` | 取得済み BB / WB 出力のみで統合判定 | dispatch で渡された JSONL + 欠落ロール名のみ (plan / AC 本文を持たない) |

## AC 判定行数不一致のリカバリ (Step 1-2)

BB / WB の AC 判定は `${ENUMERATED_AC}` の各 ID をちょうど1回ずつ含むこと。未知 ID、欠落 ID、同一 ID の重複はいずれも不一致として扱う。

1. **1 回再取得**: 同じ AC リストを再送し、期待 AC-ID 集合を明記する。この再取得は下記 JSONL 抽出・構文・schema 検証失敗と共通で、各ロール合計1回まで
2. **なお不一致**: 期待 ID の行が1件以上あれば、未知 ID を除外して期待 ID 順に正規化する。期待 ID が1行だけならその行を採用し、0行または複数行なら `judgment:"言及なし", reason:"executor 不全により自動補完"` の1行へ置換する。欠落・未知・重複を異常一覧へ記録し、合成へ渡す判定は常に期待 ID 順・N行・一意にする。期待 ID の行が1件も無い、または JSONL 破損で正規化不能なら該当ロールを空入力とし、synthetic JSONL を作らず `MISSING_ROLES` に記録する。もう一方が使えれば [synthesis-and-errors.md](synthesis-and-errors.md) の `未取得` 合成で継続する。両ロールが空ならその pass を terminal とし、合成・書き込みをせず終了する。interactive capability があれば手動レビューか中断かを確認し、手動が明示選択された後に新しい manual pass として開始する。対話不能なら現状を最終報告する

異常一覧は最終結果に残った欠落・未知・重複だけを記録する。再取得で解消した初回 validation error は再取得 prompt には含めるが、成功後の分析へ履歴として残さない。

## Step 2: Fresh Red Team dispatch (取得済み JSONL + 欠落ロール名のみ送信)

**⚠️ 重要**: Red Team subagent の入力にプラン本文 / AC 本文を含めない (真の freshness 確保)。BB / WB の出力からは取得済み **JSONL ブロックと欠落ロール名だけ**を渡し、Markdown ボイラープレート (Self-report / 暗黙前提詳細) は dispatch に含めない。

### 入力抽出ルール (main agent が dispatch 前に実行)

> **standard inline の場合は抽出不要**: inline BB/WB の出力は main agent 自身が JSONL 契約で産出しているため、`${BB_JSONL}` / `${WB_JSONL}` を直接構成する。以下の正規表現抽出は deep の dispatch 結果 (`${BB_RESULT}` / `${WB_RESULT}`) に対してのみ実行する。

1. `${BB_RESULT}` / `${WB_RESULT}` から **正規表現 `/^\s*```jsonl\n(.*?)\n\s*```/ms` を 2 回マッチ** させて findings ブロックと AC 判定ブロックを抽出 (先頭 `\s*` で字下げフェンスもキャッチ)
2. 各非空行を JSON object として parse し、findings / AC 判定それぞれを [analyst-contract.md](analyst-contract.md) の必須 field・許容 enum・ID 形式で検証する
3. 検証済み 2 ブロックを **改行 1 つで連結** して単一文字列 `${BB_JSONL}` / `${WB_JSONL}` を生成 (Red Team が 1 prompt セクションで両方を一括 parse できる形)

### 抽出・検証失敗時

- block が 0 / 1 個、fence 破損、JSON 構文不正、必須 field / enum / ID 形式不正を初回結果でまとめて検出する
- 1 回再取得: 全エラーを明記して BB / WB に findings + AC 判定の正しい 2 JSONL blocks を再送する。AC-ID 集合不一致と failure class ごとに retry を重ねず、各ロール合計1回まで
- なお失敗: 該当ロールを空入力として Red Team に渡し、欠落ロールを注記する。両方欠落なら上記 terminal rule で合成・書き込みなしに終了する

### Red Team dispatch prompt

`agents/fresh-red-team.md` は起動時に必要な references を自前で Read するため、main agent から本文を渡す必要はない。

```
Dispatch an independent executor with this prompt:
以下の agent 定義を Read で読み込み、そこに書かれた責務・出力フォーマットに従ってください:
${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/agents/fresh-red-team.md

BB Analyst の findings + AC 判定 (JSONL のみ):
${BB_JSONL}

WB Analyst の findings + AC 判定 (JSONL のみ):
${WB_JSONL}

欠落ロール (なし / BB / WB):
${MISSING_ROLES}

統合評価レポートを `${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/references/red-team-checklist.md` の「統合評価レポートのフォーマット」に従って出力してください。
分析ファイル・プランファイルを含む一切のファイルを書き換えないこと。結果は最終メッセージで返す (記録は main agent が行う)。
```

### JSONL のみ保持 (Markdown 全文は保持しない)

分析ファイルに記録するのは取得済み findings + AC 判定の **JSONL と合成表のみ** (`references/output-format.md` の「各ロール出力 (JSONL)」)。欠落ロールは synthetic JSONL を作らず同ファイルの `未取得ロール` 行へ記録する。BB / WB の Markdown 部は JSONL 抽出後に破棄する。
