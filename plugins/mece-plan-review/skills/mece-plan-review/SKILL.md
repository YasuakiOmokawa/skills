---
name: mece-plan-review
description: Validates MECE completeness of acceptance criteria in an analysis file from 4 viewpoints — BB Analyst (spec), WB Analyst (code), Wiki Researcher (Devin), Fresh Red Team — to detect missing use cases, technical gaps, and stand-offs. Use when AC is already defined in the analysis file via /define-acceptance-criteria and MECE verification is required before implementation.
---

# MECE Plan Review

`## 受け入れ条件` を 4 視点で MECE 分析する。**BB Analyst (仕様)** + **WB Analyst (コード)** + **Wiki Researcher (Devin)** の 3 並列 → **Fresh Red Team** の統合判定、の 2 phase。結果は分析ファイルに全記録、プランファイルには 1 行サマリーだけ追記する。

## Quick start

1. Arguments: `$ARGUMENTS` (プランファイルパス)。無ければシステムプロンプトの `Plan File Info:` から取得
2. 上流は `/define-acceptance-criteria`。分析ファイルに `## 受け入れ条件` が無ければ**即中断** (検証ターゲット不在)
3. 出力先: 分析ファイル (全結果) + プランファイル (`## 品質検証` に 1 行)
4. TodoWrite で Step 0 / 1 / 2 / 3-1〜3-4 を進捗管理する

## Core rules (絶対に守る)

1. **分析ファイルへの記録は main agent のみ** (subagent は書かない)
2. **情報源の完全分離**: BB は仕様 (カレントリポ wiki + Web + 一般知識) のみ・コード参照禁止 / WB はコードのみ・仕様 / wiki 参照禁止 / Wiki Researcher は判定なし / Red Team は plan/AC 本文を持たない
3. **Wiki 分担**: BB は `read_wiki_*` を **カレントリポ (`${REPO_NAME}`) のみ** に呼ぶ。関連リポ wiki は Wiki Researcher 専属
4. **Critical=0 なら「MECE OK」**、1 件以上で「要修正」(分析ファイルに記録、プラン本文は変更しない)
5. **指摘件数の縛りなし**: 該当時のみ指摘、0 件なら根拠 1 文

## Workflow

### Step 0: 初期化

**0-1 共通初期化**: [references/init-common.md](references/init-common.md) に従い、プランファイル特定 / Read / 分析ファイルパス導出 (拡張子前に `.analysis` 挿入) / `${REPO_NAME}` 取得。

**0-2 AC 抽出 (必須)**: 分析ファイルから `## 受け入れ条件` セクションを抽出。

- AC あり → 0-3 へ
- 分析ファイル無し or AC 無し → 以下を表示して**即中断** (0-3 以降を実行しない):

```
⛔ 受け入れ条件（AC）が見つかりません。
分析ファイル（{分析ファイルパス}）にACが定義されている必要があります。
MECEは「何に対して漏れがないか」を検証するプロセスです。
👉 /define-acceptance-criteria を実行してACを定義した後、再度 /mece-plan-review を実行してください。
```

**0-3 AC enumerate**: 全カテゴリ統一形式で AC-ID を付与する。詳細ルールと出力例は [references/ac-enumerate.md](references/ac-enumerate.md)。

形式: `- AC-N (カテゴリ, 観点: <ラベル>[, 境界値: <値>]): 本文`
非対称扱い禁止 (subagent パース分岐を増やすため)。

**0-4 関連リポ取得** (オプション、Wiki Researcher 用): [references/related-repos.md](references/related-repos.md) に従い `${RELATED_REPOS}` を確定。3 状態 (改行区切り / `"なし"` / `"なし (org 未解決のため関連リポ調査スキップ)"`) の意味区別を必ず保つ。

**0-5 Step 0 保持変数** (Step 1 以降の dispatch prompt にそのまま埋め込む):
`${PLAN_CONTENT}` / `${ANALYSIS_PATH}` / `${ENUMERATED_AC}` / `${REPO_NAME}` / `${RELATED_REPOS}` / `${GITHUB_ORG}`

### Step 1: 3 並列 Analyst 起動

**同一メッセージ内に 3 つの Task 呼び出しを並べる** (並列化のため単一メッセージ必須)。`subagent_type="general-purpose"`、prompt 内で agent ファイル絶対パスを示し subagent に Read させる。3 agent (BB / WB / Wiki Researcher) の完全な dispatch prompt template と責務マップは [references/dispatch-prompts.md](references/dispatch-prompts.md)。

**1-2 結果受信**: `${BB_RESULT}` / `${WB_RESULT}` / `${WIKI_RESULT}` を保持。AC 判定行数が `${ENUMERATED_AC}` と不一致なら 1 回リトライ → 不足 AC を「言及なし」で補完 → 3 連続失敗で AskUserQuestion。

### Step 2: Fresh Red Team 起動

**⚠️ Red Team の入力に plan 本文 / AC 本文を含めない** (真の freshness 確保)。**入力抽出** (main agent が dispatch 前に実行):

1. `${BB_RESULT}` / `${WB_RESULT}` から **正規表現 `/^\s*```jsonl\n(.*?)\n\s*```/ms` を 2 回マッチ** で findings + AC 判定の 2 ブロックを抽出 (字下げフェンスもキャッチ)
2. 2 ブロックの中身を**改行 1 つで連結** して `${BB_JSONL}` / `${WB_JSONL}` を生成
3. `${WIKI_RESULT}` は Markdown のまま渡す (短い箇条書きで事実補強用)

抽出失敗時のリカバリと dispatch prompt template は [references/dispatch-prompts.md](references/dispatch-prompts.md)。**二重用途**: BB / WB の元 Markdown 全文は main agent 側で別途保持 (Step 3-3 で `<details>` 埋め込み用)。**2-2 結果受信**: `${RED_TEAM_RESULT}`。

### Step 3: 出力

**ルール**: 全分析結果は分析ファイルに記録、プランファイルにはサマリー 1 行のみ追記、プラン本文は一切変更しない。

- **3-1** AC カバレッジ表機械合成 + Critical / Important / Nice-to-have を分析ファイルに記録
- **3-2** AC ブラッシュアップ (`[MECE追加]` / `[MECE追加 変更]` タグ、補足は無タグ)
- **3-3** MECE 分析結果セクションを分析ファイル末尾に追記 ([references/output-format.md](references/output-format.md))
- **3-4** プランファイル `## 品質検証` に 1 行追記:
  `- MECE判定: [OK or 要修正（Critical N件）] / ACカバレッジ [N]/[M] (うち[MECE追加] [X]件) / 漏れ [Y]件 / 重複 [Z]件 → [分析ファイル名]`

各 step の合成ロジック・タグ判定・「補足」と「書き換え」の境界は [references/synthesis-and-errors.md](references/synthesis-and-errors.md)。

## Advanced

References (one level deep):
- [references/ac-enumerate.md](references/ac-enumerate.md) — AC-ID 正規化ルール / 全カテゴリ統一形式 / 上流契約違反時の挙動
- [references/related-repos.md](references/related-repos.md) — GitHub org 解決手順 / `${RELATED_REPOS}` 3 状態表
- [references/dispatch-prompts.md](references/dispatch-prompts.md) — Step 1 / Step 2 dispatch prompt 全文 / JSONL 抽出 / 失敗リカバリ
- [references/synthesis-and-errors.md](references/synthesis-and-errors.md) — Step 3 合成ロジック / Error Handling
- [references/init-common.md](references/init-common.md) — 初期化 (define-AC と共通)
- [references/red-team-checklist.md](references/red-team-checklist.md) — Red Team チェックリスト (agents/fresh-red-team.md が Read)
- [references/output-format.md](references/output-format.md) — 分析ファイル / プラン修正フォーマット

Agents:
- [agents/bb-analyst.md](agents/bb-analyst.md) — Black Box (仕様限定、カレントリポ wiki のみ)
- [agents/wb-analyst.md](agents/wb-analyst.md) — White Box (コード限定)
- [agents/wiki-researcher.md](agents/wiki-researcher.md) — Devin wiki 事実収集 (判定なし)
- [agents/fresh-red-team.md](agents/fresh-red-team.md) — Red Team (BB/WB/Wiki 出力のみで統合判定、plan/AC を持たない)

併用推奨: `/define-acceptance-criteria` (前段で AC 定義) → `/finalize-plan` (MECE 結果反映で実装フェーズへ)
