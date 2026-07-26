---
name: mece-plan-review
description: Verifies acceptance criteria for MECE coverage with parallel spec/code/wiki analysts and a fresh red-team judge, recording coverage gaps and duplicates in the analysis file. Use when AC is already defined in the analysis file via /define-acceptance-criteria and MECE verification is required before implementation, or when the user says "AC の網羅性を検証して" / "MECE 検証して". Not typically invoked during PoC / throwaway-validation phases (the assumption ledger substitutes there).
---

# MECE Plan Review

`## 受け入れ条件` を 4 視点で MECE 分析する。**BB Analyst (仕様)** + **WB Analyst (コード)** + **Wiki Researcher (Devin)** の 3 並列 → **Fresh Red Team** の統合判定、の 2 phase。結果は分析ファイルに全記録、プランファイルには 1 行サマリーだけ追記する。

## Quick start

1. Arguments: `$ARGUMENTS` (プランファイルパス)。無ければシステムプロンプトの `Plan File Info:` から取得
2. 上流は `/define-acceptance-criteria`。分析ファイルに `## 受け入れ条件` が無ければ**即中断** (検証ターゲット不在)
3. 出力先: 分析ファイル (全結果) + プランファイル (`## 品質検証` に 1 行)
4. TodoWrite で Step 0 / 1 / 2 / 3-1〜3-4 を進捗管理する (TodoWrite が利用可能ツール一覧に無い委譲実行では進捗管理を省略する。セッション共有の `TaskCreate` / `TaskUpdate` で代替しない — 呼び出し元の task list を汚染するため)

## Task complexity tier

`${ENUMERATED_AC}` の件数で tier を判定し、Analyst / Red Team の実行形態を変える:

| Tier | AC 件数 | Analyst | Fresh Red Team |
|---|---|---|---|
| **lite** | ≤5 件 | main agent 内で BB+WB を統合 inline 実行 (Wiki Researcher は非起動) | skip (Critical 候補 0 で確定) |
| **standard** (default) | 6-15 件 | 3 並列 Analyst (BB / WB / Wiki Researcher) | Critical 候補 ≥1 なら起動 |
| **deep** | >15 件 / auth / billing / payment / migration | 3 並列 Analyst | 必須起動 |

`<plan>.analysis.md` 冒頭の `### Tier` (define-AC が記録) を継承。リスク領域は AC 件数によらず強制的に **deep** — 上流の `### Tier` 記録 (lite / standard) と食い違う場合もリスク領域強制が優先し、上書きした旨と根拠を分析サマリーに記録する。リスク領域該当は**変更が書き換える対象**で判定する (例: billing = 請求金額を算出・永続化するコードパスに触れる変更。請求ドメインの表示のみの変更は非該当)。

> **ゲートの優先順位**: Wiki Researcher の起動可否は tier ではなく Step 0-4.5 の `${DEVIN_COVERAGE}` が決める (可用性ゲート > 規模ゲート)。`none` なら deep でも非起動 (BB + WB の 2 並列)。tier 表が規定するのは Fresh Red Team の起動条件 (Step 2) だけ。

**lite-mode inline 実行手順** (Step 1 / Step 2 の代替):
1. main agent が `${ENUMERATED_AC}` を inline review し、情報源を分けた 2 視点を統合した analysis を産出 (件数縛りは standard と同じくなし = Core rule 5)。inline 実行でも先に `agents/bb-analyst.md` / `agents/wb-analyst.md` を Read し、Critical 閾値と出力契約 (JSONL・AC 判定行) をそのまま適用する — dispatch を省くのは起動だけで、agent 定義が運ぶ契約は省かない。手順 4 の「Critical 候補」も閾値 4 類型に**現に該当**するもののみ (直感で昇格しない):
   - **BB 視点**: 仕様 / カレントリポ wiki / 一般知識 から欠落 use case を抽出 (コード参照禁止)
   - **WB 視点**: 変更ファイル diff を Read し技術ギャップを抽出 (仕様参照禁止)。**コードが未実装 / 不可読 (greenfield・plan mode) の場合**は AC 判定を `言及なし` 既定とし、plan からコード構造ギャップが積極的に導ける AC のみ `不十分` とする。低充足率は AC 不備でなくコード不可読が原因と明記し、機械合成 (一方充足 + 他方言及なし → 充足) に委ねる
2. Wiki Researcher / Fresh Red Team は skip。出力は標準と同じ Step 3 形式 (分析ファイル末尾セクション + プラン 1 行サマリー)
   - **0-4 (関連リポ取得) は skip** し `${RELATED_REPOS}="なし"` とする (Wiki Researcher が非起動で参照先が無いため)
   - **0-4.5 preflight は lite でも実行する**。lite で決めるのは Wiki Researcher の起動可否ではなく、inline BB がカレントリポ wiki を読めるか / 結果に `[Devin未使用]` タグを付けるかである
   - `${DEVIN_COVERAGE}` がどちらの値でも `${WIKI_RESULT}="[Wiki Researcher 非起動 (lite)]"` を確定値として保持する (Step 3-3 の `<details>` が未定義変数にならないようにする)
3. Critical 候補 0 なら `Critical: 0` を確定値として 1 行サマリーに記載する
4. **inline BB/WB で Critical 候補が 1 件でも出たら lite 確定を破棄し格上げする**: tier=standard として Step 1 (BB/WB 並列 + 該当時 Wiki Researcher) と Step 2 Fresh Red Team を改めて実行し、lite サマリーは残さず standard 出力で上書きする (lite は Red Team を skip するため、Critical 候補を inline のまま確定させると MECE判定 の信頼性が崩れる)。格上げ先は standard とし、**finding が lite 分類時に見落とした auth / billing / payment / migration の関与を露呈した場合のみ deep へ格上げする** (リスク領域強制 deep が standard 格上げに優先)

## Core rules (守らないと検証設計が崩れる不変条件)

1. **分析ファイルへの記録は main agent のみ** (subagent は書かない — 並列 subagent が同一ファイルに書くと記録の競合・重複が起き、main agent の機械合成 (Step 3-1) の入力が壊れるため)
2. **情報源の完全分離**: BB は仕様 (カレントリポ wiki + Web + 一般知識) のみ・コード参照禁止 / WB はコードのみ・仕様 / wiki 参照禁止 / Wiki Researcher は判定なし / Red Team は plan/AC 本文を持たない
3. **Wiki 分担**: BB は `read_wiki_*` を **カレントリポ (`${REPO_NAME}`) のみ** に呼ぶ。関連リポ wiki は Wiki Researcher 専属
4. **Critical=0 なら「MECE OK」**、1 件以上で「要修正」(分析ファイルに記録、プラン本文は変更しない)。**MECE判定 (OK / 要修正) は Critical 件数のみで決まる** — 「不十分」AC や coverage 率は MECE判定 に影響せず、AC ブラッシュアップ (Step 3-2) の対象として別系統で扱う (Critical 0 + 不十分 AC 数件 = 「MECE OK」で正しい)。**Critical 認定は「その欠陥が *それ単独で* 害を成立させるか (hardening 不足は Important)」の決定規則で行う** — MECE判定 の信頼性はこの規則に依存する (詳細は各 agent / `references/red-team-checklist.md` の「Critical 閾値」節)
5. **指摘件数の縛りなし**: 該当時のみ指摘、0 件なら根拠 1 文

## Orchestrated モード

ファイル存在からの推測では判定しない。呼び出し側（将来のオーケストレータ）が Task 起動プロンプトで「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示が無い単独起動では現行動作（subagent 応答不能時に AskUserQuestion で確認）のまま進む。**Step 0 の即中断ゲート (0-2 AC 無し 等) はこのモードの対象外**で、宣言の有無によらず本文記載どおり決定的に処理し記帳しない。差分は Step 1 の AC 判定行数不一致リカバリ・[references/dispatch-prompts.md](references/dispatch-prompts.md) の AskUserQuestion 分岐・[references/synthesis-and-errors.md](references/synthesis-and-errors.md) の書き込み失敗系 AskUserQuestion 分岐で、詳細は [references/orchestrated-mode.md](references/orchestrated-mode.md) を参照。

## 委譲実行 (subagent として起動された場合)

Task で委譲起動された場合の読み替え。単独起動 (メイン会話でユーザーが直接起動) の現行動作は変えない。判定基準はすべて観測可能な条件 (利用可能ツール一覧・宣言の有無) であり、実行文脈の推測では判定しない。

- **入力解決の優先順位**: ① `$ARGUMENTS` → ② 起動プロンプト本文で明示されたプランファイルパス (Task 委譲時はこれが `$ARGUMENTS` 相当) → ③ セッション文脈・システムプロンプトの `Plan File Info:` (単独起動時のみ有効)。①〜③のいずれでも解決できない場合、「不足入力: プランファイルパス」を最終メッセージで返し、返答を待たず終了する。
- **AskUserQuestion 分岐の読み替え**: AskUserQuestion が利用可能ツール一覧に無い場合 (= subagent 実行)、(a) orchestrated モード宣言があれば [references/orchestrated-mode.md](references/orchestrated-mode.md) の記帳規則に従って続行する、(b) 宣言が無ければ確認したかった内容と現状を最終メッセージに含めて終了する (呼び出し元が人間へ中継し、回答を添えて再起動する)。対話承認者がいるかの判定基準は AskUserQuestion の利用可否そのもの。
- **Task 不可時の fallback**: Task (Agent) ツールが利用可能ツール一覧に無い場合のみ、Step 1 は本文記載の inline 実行 (lite-mode 手順流用) に切り替える。Step 2 (Fresh Red Team) は [references/synthesis-and-errors.md](references/synthesis-and-errors.md) の「Red Team subagent 失敗」節のフォールバックに従う。
- **`${CLAUDE_PLUGIN_ROOT}` の解決**: 本文・agents/*.md 中に生文字列で残っている場合、この SKILL.md が置かれているディレクトリを skill root とみなし `${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/` をそこへ読み替える。nested Task へ埋め込む全パス ([references/dispatch-prompts.md](references/dispatch-prompts.md) のテンプレート含む) は読み替え後の絶対パスにする。
- **完了報告**: Step 3 完了時の最終メッセージに、3-4 の 1 行サマリーに加えて (a) 分析ファイルの絶対パス、(b) MECE判定 (OK/要修正) と Critical 件数、を明記する。

## Workflow

### Step 0: 初期化

**0-1 共通初期化**: [references/init-common.md](references/init-common.md) に従い、プランファイル特定 / Read / 分析ファイルパス導出 (拡張子前に `.analysis` 挿入) / `${REPO_NAME}` 取得。

`${REPO_NAME}` と、WB がコードを探す起点 `${CODE_ROOT}` (絶対パス) は、**レビュー対象コードを含むリポジトリ**で解決する。skill を起動した cwd がそれと別リポの場合、cwd のリポジトリ名を使わない (無関係リポが Devin 収録済みだと preflight が誤って `covered` になり、BB に別プロジェクトの wiki を渡してしまう)。対象コードが cwd から辿れない場合は `${CODE_ROOT}="(対象コード不在)"` とし、WB 判定を `言及なし` 既定にする。

**0-2 AC 抽出 (必須)**: 分析ファイルから `## 受け入れ条件` セクションを抽出。

- AC あり → 0-3 へ
- 分析ファイル無し or AC 無し → 以下を表示して**即中断** (0-3 以降を実行しない):

```
⛔ 受け入れ条件（AC）が見つかりません。
分析ファイル（{分析ファイルパス}）にACが定義されている必要があります。
MECEは「何に対して漏れがないか」を検証するプロセスです。
👉 /define-acceptance-criteria を実行してACを定義した後、再度 /mece-plan-review を実行してください。
```

`{分析ファイルパス}` は絶対パスに置換する (委譲実行の完了報告と同じ規約)。

**0-3 AC enumerate**: 全カテゴリ統一形式で AC-ID を付与する。詳細ルールと出力例は [references/ac-enumerate.md](references/ac-enumerate.md)。

形式: `- AC-N (カテゴリ, 観点: <ラベル>[, 境界値: <値>]): 本文`
非対称扱い禁止 (subagent パース分岐を増やすため)。

**0-4 関連リポ取得** (オプション、Wiki Researcher 用): [references/related-repos.md](references/related-repos.md) に従い `${RELATED_REPOS}` を確定。3 状態 (改行区切り / `"なし"` / `"なし (org 未解決のため関連リポ調査スキップ)"`) の意味区別を必ず保つ。

**0-4.5 Devin 収録 preflight (Wiki Researcher 起動可否)**: Wiki Researcher を起動する前に main agent が **軽量 probe を 1 回だけ** 実行し `${DEVIN_COVERAGE}` を確定する。probe は規模・価値判断で省略しない (遅延源は `ask_question` のみで、下記 2 呼び出しは軽量):

0. `${REPO_NAME}` が対象リポジトリで解決できない (non-git 等で `unknown-repo`) → probe を打たず `${DEVIN_COVERAGE}=none` を即確定する (probe 必須規則は価値判断による省略を禁じるもので、引数となる repoName が構成不能な場合は前提不成立としてこの分岐が正)
1. `ToolSearch("+fdev-devin")` 失敗 → `${DEVIN_COVERAGE}=none`
2. 成功時は `read_wiki_structure(repoName=${REPO_NAME})` を **1 回だけ** 叩く。`ask_question` は preflight に使わない (Devin 調査セッション起動で分単位の遅延を招く)
   - wiki 構造が返る → `${DEVIN_COVERAGE}=covered`
   - "Repository not found" / error / 空 → `${DEVIN_COVERAGE}=none` (リトライ・別ツール再確認をしない)

`${DEVIN_COVERAGE}=none` の場合:
- Step 1 で **Wiki Researcher を dispatch しない** (BB + WB の 2 並列のみ)
- `${WIKI_RESULT}="[Devin未使用] (preflight でカレントリポ未収録/MCP 不可を確認、Wiki Researcher 非起動)"` を確定値として保持
- BB dispatch prompt に「Devin 未収録のため Phase 0 (wiki 調査) をスキップし `[Devin未使用]` で進める」と明記し、BB の重複 probe を防ぐ

**0-5 Step 0 保持変数** (Step 1 以降の dispatch prompt にそのまま埋め込む):
`${PLAN_CONTENT}` / `${ANALYSIS_PATH}` / `${ENUMERATED_AC}` / `${REPO_NAME}` / `${CODE_ROOT}` / `${RELATED_REPOS}` / `${GITHUB_ORG}` / `${DEVIN_COVERAGE}`

### Step 1: 並列 Analyst 起動

`${DEVIN_COVERAGE}` (0-4.5) に応じて **同一メッセージ内に Task 呼び出しを並べる** (並列化のため単一メッセージ必須):
- `covered` → **3 並列** (BB / WB / Wiki Researcher)
- `none` → **2 並列** (BB / WB のみ)。Wiki Researcher は **起動せず**、0-4.5 で確定した `${WIKI_RESULT}` (`[Devin未使用]`) をそのまま後段で使う (遅延防止)

`subagent_type="general-purpose"`、prompt 内で agent ファイル絶対パスを示し subagent に Read させる。各 agent の完全な dispatch prompt template と責務マップは [references/dispatch-prompts.md](references/dispatch-prompts.md)。**Task ツールが利用不可な場合 (nested 実行で subagent dispatch 不可)**: tier によらず BB / WB (covered なら Wiki も) を main agent が情報源分離を自制しつつ inline 実行する (lite-mode 手順を流用)。`TaskCreate` / `TaskList` 等の todo 管理ツールは dispatch 用 Task ではない。

**1-2 結果受信**: `${BB_RESULT}` / `${WB_RESULT}` / `${WIKI_RESULT}` を保持。AC 判定行数が `${ENUMERATED_AC}` と不一致なら 1 回リトライ → 不足 AC を「言及なし」で補完 → 3 連続失敗で AskUserQuestion（Orchestrated モード時は安全側 (該当 AC を Critical 扱い) に倒して escalation ledger に記帳し続行する。[references/orchestrated-mode.md](references/orchestrated-mode.md) 参照）。

### Step 2: Fresh Red Team 起動

- **⚠️ Red Team の入力に plan 本文 / AC 本文を含めない** (真の freshness 確保)
- main agent は dispatch 前に `${BB_RESULT}` / `${WB_RESULT}` から findings + AC 判定の JSONL ブロックのみを抽出して `${BB_JSONL}` / `${WB_JSONL}` を生成する (`${WIKI_RESULT}` は Markdown のまま渡す)。抽出の正規表現・2 ブロック連結手順・抽出失敗時のリカバリ・dispatch prompt template は [references/dispatch-prompts.md](references/dispatch-prompts.md) の Step 2 節 (SSOT)
- **二重用途**: BB / WB の元 Markdown 全文は main agent 側で別途保持する (Step 3-3 で `<details>` 埋め込み用)
- **2-2 結果受信**: `${RED_TEAM_RESULT}`。**Task ツールが利用不可な場合**は Red Team subagent を dispatch できないため [references/synthesis-and-errors.md](references/synthesis-and-errors.md) の「Red Team subagent 失敗」節のフォールバックに従う

### Step 3: 出力

**ルール**: 全分析結果は分析ファイルに記録、プランファイルにはサマリー 1 行のみ追記、プラン本文は一切変更しない。指摘をプラン本文へ反映する後続作業でも finding ID (`BB-N` / `WB-N` / `IM-N` 等) をプラン本文に持ち込まない ([references/output-format.md](references/output-format.md) 修正ルール参照)。

- **3-1** AC カバレッジ表機械合成 + Critical / Important / Nice-to-have を分析ファイルに記録
- **3-2** AC ブラッシュアップ (`[MECE追加]` / `[MECE追加 変更]` タグ、補足は無タグ)
- **3-3** MECE 分析結果セクションを分析ファイル末尾に追記 ([references/output-format.md](references/output-format.md))
- **3-4** プランファイル `## 品質検証` に 1 行追記:
  `- MECE判定: [OK (Critical: 0) or 要修正（Critical N件）] / ACカバレッジ [N]/[M] (うち[MECE追加] [X]件) / 漏れ [Y]件 / 重複 [Z]件 → [分析ファイル名]`

Red Team 出力の Markdown 部に「判定不能 (Unknown)」がある場合: 3-3 の MECE 分析結果セクションに理由ごと転記し、3-4 の 1 行サマリーの `→ [分析ファイル名]` の直前に ` / 判定不能 [U]件` を挿入する (受け皿が無いと棄権項目が黙って落ち、誤った「MECE OK」になるため。0 件なら転記・付記とも省略)。

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
