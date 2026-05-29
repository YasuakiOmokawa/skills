---
name: mece-plan-review
description: Use when AC is already defined in the analysis file via /define-acceptance-criteria and MECE verification is required before implementation.
---

# MECE Plan Review

`## 受け入れ条件` を 4 視点で MECE 分析する。**BB Analyst (仕様)** + **WB Analyst (コード)** + **Wiki Researcher (Devin)** の 3 並列 → **Fresh Red Team** の統合判定、の 2 phase。結果は分析ファイルに全記録、プランファイルには 1 行サマリーだけ追記する。

## Quick start

1. Arguments: `$ARGUMENTS` (プランファイルパス)。無ければシステムプロンプトの `Plan File Info:` から取得
2. 上流は `/define-acceptance-criteria`。分析ファイルに `## 受け入れ条件` が無ければ**即中断** (検証ターゲット不在)
3. 出力先: 分析ファイル (全結果) + プランファイル (`## 品質検証` に 1 行)
4. TodoWrite で Step 0 / 1 / 2 / 3-1〜3-4 を進捗管理する

## Task complexity tier

`${ENUMERATED_AC}` の件数で tier を判定し、Analyst / Red Team の実行形態を変える:

| Tier | AC 件数 | Analyst | Fresh Red Team |
|---|---|---|---|
| **lite** | ≤5 件 | main agent 内で BB+WB を統合 inline 実行 (Wiki Researcher 省略可) | skip (Critical 候補 0 で確定) |
| **standard** (default) | 6-15 件 | 3 並列 Analyst (BB / WB / Wiki Researcher) | Critical 候補 ≥1 なら起動 |
| **deep** | >15 件 / auth / billing / payment / migration | 3 並列 Analyst | 必須起動 |

`<plan>.analysis.md` 冒頭の `### Tier` (define-AC が記録) を継承。リスク領域は AC 件数によらず強制的に **deep**。

> **ゲートの優先順位 (Wiki Researcher 起動可否)**: tier 表の Analyst 列「3 並列」は **Devin 収録時の上限**を表すに過ぎない。Wiki Researcher を起動するかは tier ではなく Step 0-4.5 の `${DEVIN_COVERAGE}` が決める (**可用性ゲート > 規模ゲート**)。`${DEVIN_COVERAGE}=none` なら **deep でも Wiki Researcher は非起動** (BB + WB の 2 並列)。tier が規定するのは Fresh Red Team の起動条件 (Step 2) であり、Wiki Researcher の起動条件ではない。

**lite-mode inline 実行手順** (Step 1 / Step 2 の代替):
1. main agent が `${ENUMERATED_AC}` を inline review し、以下 2 視点を統合した analysis を産出:
   - **BB 視点**: 仕様 / カレントリポ wiki / 一般知識 から欠落 use case を 1-3 件抽出 (コード参照禁止)
   - **WB 視点**: 変更ファイル diff を Read し技術ギャップを 1-3 件抽出 (仕様参照禁止)
2. Wiki Researcher / Fresh Red Team は skip (Critical 候補 0 で確定する設計)
3. 出力は標準と同じ Step 3 形式 (分析ファイル末尾セクション + プラン 1 行サマリー) を採用
4. lite 報告では `Critical: 0` を確定値として 1 行サマリーに記載 (Critical ≥1 が出現したら自動的に standard tier へ格上げ判定)

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

**0-4.5 Devin 収録 preflight (Wiki Researcher 起動可否、遅延防止の要)**: Wiki Researcher を起動する前に main agent が **軽量 probe を 1 回だけ** 実行し `${DEVIN_COVERAGE}` を確定する:

1. `ToolSearch("+fdev-devin")` 失敗 → `${DEVIN_COVERAGE}=none`
2. 成功時は `read_wiki_structure(repoName=${REPO_NAME})` を **1 回だけ** 叩く。`ask_question` は preflight に使わない (Devin 調査セッション起動で分単位の遅延を招くため厳禁)
   - wiki 構造が返る → `${DEVIN_COVERAGE}=covered`
   - "Repository not found" / error / 空 → `${DEVIN_COVERAGE}=none` (リトライ・別ツール再確認をしない)

`${DEVIN_COVERAGE}=none` の場合:
- Step 1 で **Wiki Researcher を dispatch しない** (BB + WB の 2 並列のみ)
- `${WIKI_RESULT}="[Devin未使用] (preflight でカレントリポ未収録/MCP 不可を確認、Wiki Researcher 非起動)"` を確定値として保持
- BB dispatch prompt に「Devin 未収録のため Phase 0 (wiki 調査) をスキップし `[Devin未使用]` で進める」と明記し、BB の重複 probe を防ぐ

**0-5 Step 0 保持変数** (Step 1 以降の dispatch prompt にそのまま埋め込む):
`${PLAN_CONTENT}` / `${ANALYSIS_PATH}` / `${ENUMERATED_AC}` / `${REPO_NAME}` / `${RELATED_REPOS}` / `${GITHUB_ORG}` / `${DEVIN_COVERAGE}`

### Step 1: 並列 Analyst 起動

`${DEVIN_COVERAGE}` (0-4.5) に応じて **同一メッセージ内に Task 呼び出しを並べる** (並列化のため単一メッセージ必須):
- `covered` → **3 並列** (BB / WB / Wiki Researcher)
- `none` → **2 並列** (BB / WB のみ)。Wiki Researcher は **起動せず**、0-4.5 で確定した `${WIKI_RESULT}` (`[Devin未使用]`) をそのまま後段で使う (遅延防止)

`subagent_type="general-purpose"`、prompt 内で agent ファイル絶対パスを示し subagent に Read させる。各 agent の完全な dispatch prompt template と責務マップは [references/dispatch-prompts.md](references/dispatch-prompts.md)。**Task ツールが利用不可な場合 (nested 実行で subagent dispatch 不可)**: tier によらず BB / WB (covered なら Wiki も) を main agent が情報源分離を自制しつつ inline 実行する (lite-mode 手順を流用)。`TaskCreate` / `TaskList` 等の todo 管理ツールは dispatch 用 Task ではない。

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

References:
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
