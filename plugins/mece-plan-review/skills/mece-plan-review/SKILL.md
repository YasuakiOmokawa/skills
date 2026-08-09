---
name: mece-plan-review
description: Use when AC is already defined in the analysis file via /define-acceptance-criteria and MECE verification is required before implementation, or when the user says "AC の網羅性を検証して" / "MECE 検証して". Not typically invoked during PoC / throwaway-validation phases (the assumption ledger substitutes there).
---

# MECE Plan Review

`## 受け入れ条件` を **BB (仕様)** / **WB (コード)** の 2 視点 + **Fresh Red Team** で MECE 分析する。既定 (standard) は main agent が BB+WB を **inline 実行**し、Critical 候補が出たときだけ Fresh Red Team を dispatch する。リスク領域・大規模 AC (deep) では BB / WB を並列 subagent で起動し Red Team を必須とする。結果は分析ファイルに全記録、プランファイルには 1 行サマリーだけ追記する。

## Quick start

1. Arguments: `$ARGUMENTS` (プランファイルパス)。無ければシステムプロンプトの `Plan File Info:` から取得
2. 上流は `/define-acceptance-criteria`。分析ファイルに `## 受け入れ条件` が無ければ**即中断** (検証ターゲット不在)
3. 出力先: 分析ファイル (全結果) + プランファイル (`## 品質検証` に 1 行)
4. TodoWrite で Step 0 / 1 / 2 / 3-1〜3-4 を進捗管理する (TodoWrite が利用可能ツール一覧に無い委譲実行では進捗管理を省略する。セッション共有の `TaskCreate` / `TaskUpdate` で代替しない — 呼び出し元の task list を汚染するため)

## Task complexity tier

リスク領域該当と `${ENUMERATED_AC}` の件数で tier を判定し、Analyst / Red Team の実行形態を変える:

| Tier | 条件 | Analyst | Fresh Red Team |
|---|---|---|---|
| **standard** (default) | AC ≤15 件 かつ 非リスク領域 | main agent 内で BB+WB を統合 inline 実行 (subagent dispatch なし) | Critical 候補 ≥1 なら起動 / 0 なら skip |
| **deep** | AC >15 件 / auth / billing / payment / migration | BB / WB の 2 並列 dispatch | 必須起動 |

`<plan>.analysis.md` 冒頭の `### Tier` (define-AC が記録) を継承。**`### Tier`=lite は standard として読み替える** (本 skill の lite tier は standard に統合済み。define-AC 側の lite は AC マトリクス規模を決める tier で現役のまま — 本 skill の実行形態 tier とは役割が別)。リスク領域は AC 件数によらず強制的に **deep** — 上流の `### Tier` 記録 (lite / standard) と食い違う場合もリスク領域強制が優先し、上書きした旨と根拠を分析サマリーに記録する。リスク領域該当は**変更が書き換える対象**で判定する (例: billing = 請求金額を算出・永続化するコードパスに触れる変更。請求ドメインの表示のみの変更は非該当)。「表示のみ」はプランの自己申告ではなく振る舞いで検算する — 確定済みの値をそのまま描画するだけなら非該当、金額・認証状態等を算出/生成する式や検査を新設するなら該当。

**standard inline 実行手順** (Step 1 / Step 2 の既定形態):
1. main agent が `${ENUMERATED_AC}` を inline review し、情報源を分けた 2 視点を統合した analysis を産出 (件数縛りなし = Core rule 4)。inline 実行でも先に [references/analyst-contract.md](references/analyst-contract.md) を Read し、BB 節 / WB 節の情報源制約・Critical 閾値・出力契約 (JSONL・AC 判定行) をそのまま適用する — dispatch を省くのは起動だけで、契約は省かない。手順 3 の「Critical 候補」も閾値 4 類型に**現に該当**するもののみ (直感で昇格しない):
   - **BB 視点**: 仕様 / 一般知識 から欠落 use case を抽出 (コード参照禁止)
   - **WB 視点**: 変更ファイル diff を Read し技術ギャップを抽出 (仕様参照禁止)。**コードが未実装 / 不可読 (greenfield・plan mode) の場合**は analyst-contract の「コード不可読時の既定」に従い AC 判定を `言及なし` 既定とする
2. **Critical 候補 0** → Fresh Red Team は skip。`Critical: 0` を確定値として 1 行サマリーに記載する。分析サマリーの漏れ件数は `0件 (Red Team skip のため未検出)` と表記する (構造的 0 を「検証済み 0」と誤読させない)。出力は標準と同じ Step 3 形式 (分析ファイル末尾セクション + プラン 1 行サマリー)。Red Team が不在のため、Red Team が供給するはずだった Step 3 入力は main agent が代替する — 4 分類クロスリファレンス表の `分類` は red-team-checklist の 4 分類定義を main agent が適用して付与し、お見合い表・純技術リスク表は空のまま「Red Team skip のため未検出」と明記する
3. **Critical 候補 ≥1** → inline BB/WB 出力 (JSONL 契約は dispatch と同一) から `${BB_JSONL}` / `${WB_JSONL}` を構成し、Step 2 の Fresh Red Team を dispatch して統合判定させる (inline のまま Critical を確定しない — Red Team の閾値再適用が MECE判定 の信頼性を担保する)。ただし **finding が standard 分類時に見落とした auth / billing / payment / migration の関与を露呈した場合は standard 確定を破棄して deep へ格上げ**: Step 1 の BB/WB 並列 dispatch と Step 2 必須 Red Team を改めて実行し、inline サマリーは残さず deep 出力で上書きする (リスク領域の Critical 候補を inline 分析のまま確定させると情報源分離の強制が効かず MECE判定 の信頼性が崩れる)

## Core rules (守らないと検証設計が崩れる不変条件)

1. **分析ファイルへの記録は main agent のみ** (subagent は書かない — 並列 subagent が同一ファイルに書くと記録の競合・重複が起き、main agent の機械合成 (Step 3-1) の入力が壊れるため)
2. **情報源の完全分離**: BB は仕様 (プラン + 一般知識) のみ・コード参照禁止 / WB はコードのみ・仕様参照禁止 / Red Team は plan/AC 本文を持たない
3. **Critical=0 なら「MECE OK」**、1 件以上で「要修正」(分析ファイルに記録、プラン本文は変更しない)。**MECE判定 (OK / 要修正) は Critical 件数のみで決まる** — 「不十分」AC や coverage 率は MECE判定 に影響せず、AC ブラッシュアップ (Step 3-2) の対象として別系統で扱う (Critical 0 + 不十分 AC 数件 = 「MECE OK」で正しい)。**Critical 認定は「その欠陥が *それ単独で* 害を成立させるか (hardening 不足は Important)」の決定規則で行う** — MECE判定 の信頼性はこの規則に依存する (詳細は [references/analyst-contract.md](references/analyst-contract.md) / [references/red-team-checklist.md](references/red-team-checklist.md) の「Critical 閾値」節)
4. **指摘件数の縛りなし**: 該当時のみ指摘、0 件なら根拠 1 文

## 委譲実行 (subagent として起動された場合)

Task で委譲起動された場合の入力解決・AskUserQuestion 読み替え・Task 不可 fallback・`${CLAUDE_PLUGIN_ROOT}` 解決・完了報告契約は [references/delegated-execution.md](references/delegated-execution.md) に従う。単独起動の動作は変えない。

## Workflow

### Step 0: 初期化

**0-1 共通初期化**: [references/init-common.md](references/init-common.md) に従い、プランファイル特定 / Read / 分析ファイルパス導出 (拡張子前に `.analysis` 挿入) / `${REPO_NAME}` 取得。併せて `date +%s` で開始時刻 `${T_START}` を記録する (Step 3-3 の実行メタ用)。

`${REPO_NAME}` と、WB がコードを探す起点 `${CODE_ROOT}` (絶対パス) は、**レビュー対象コードを含むリポジトリ**で解決する。skill を起動した cwd がそれと別リポの場合、cwd のリポジトリ名を使わない。対象コードが cwd から辿れない場合は `${CODE_ROOT}="(対象コード不在)"` とし、WB 判定を `言及なし` 既定にする。

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

**0-4 Step 0 保持変数** (Step 1 以降の inline 実行 / dispatch prompt にそのまま使う):
`${PLAN_CONTENT}` / `${ANALYSIS_PATH}` / `${ENUMERATED_AC}` / `${REPO_NAME}` / `${CODE_ROOT}` / `${T_START}`

### Step 1: Analyst 実行

- **standard** → 「standard inline 実行手順」に従い main agent が BB / WB を inline 実行する (subagent dispatch なし)
- **deep** → **同一メッセージ内に Task 呼び出しを並べる** (並列化のため単一メッセージ必須)。**BB / WB の 2 並列**

deep の dispatch は `subagent_type="general-purpose"`、prompt 内で [references/analyst-contract.md](references/analyst-contract.md) の絶対パスと適用する役割 (BB 節 / WB 節) を示し subagent に Read させる。完全な dispatch prompt template は [references/dispatch-prompts.md](references/dispatch-prompts.md)。**Task ツールが利用不可な場合 (nested 実行で subagent dispatch 不可)**: deep でも BB / WB を main agent が情報源分離を自制しつつ inline 実行する (standard inline 手順を流用)。`TaskCreate` / `TaskList` 等の todo 管理ツールは dispatch 用 Task ではない。

**1-2 結果受信** (deep の dispatch 時のみ): `${BB_RESULT}` / `${WB_RESULT}` を保持。AC 判定行数が `${ENUMERATED_AC}` と不一致なら 1 回リトライ → 不足 AC を「言及なし」で補完 → 3 連続失敗で AskUserQuestion (委譲実行時の読み替えは [references/delegated-execution.md](references/delegated-execution.md))。

### Step 2: Fresh Red Team 起動 (standard は Critical 候補 ≥1 のとき / deep は必須)

- **⚠️ Red Team の入力に plan 本文 / AC 本文を含めない** (真の freshness 確保)
- **deep (dispatch 結果あり)**: main agent は dispatch 前に `${BB_RESULT}` / `${WB_RESULT}` から findings + AC 判定の JSONL ブロックのみを抽出して `${BB_JSONL}` / `${WB_JSONL}` を生成する。抽出の正規表現・2 ブロック連結手順・抽出失敗時のリカバリ・dispatch prompt template は [references/dispatch-prompts.md](references/dispatch-prompts.md) の Step 2 節 (SSOT)
- **standard (inline 結果)**: `${BB_JSONL}` / `${WB_JSONL}` は inline BB/WB 出力から main agent が直接構成する (出力契約が dispatch と同一のため正規表現抽出は不要)
- **JSONL のみ保持**: BB / WB の Markdown 部 (Self-report 等) を Step 3 まで保持・転記する義務は無い。分析ファイルへ記録するのは JSONL と合成表のみ ([references/output-format.md](references/output-format.md))
- **2-2 結果受信**: `${RED_TEAM_RESULT}`。**Task ツールが利用不可な場合**は Red Team subagent を dispatch できないため [references/synthesis-and-errors.md](references/synthesis-and-errors.md) の「Red Team subagent 失敗」節のフォールバックに従う

### Step 3: 出力

**ルール**: 全分析結果は分析ファイルに記録、プランファイルにはサマリー 1 行のみ追記、プラン本文は一切変更しない。指摘をプラン本文へ反映する後続作業でも finding ID (`BB-N` / `WB-N` / `IM-N` 等) をプラン本文に持ち込まない ([references/output-format.md](references/output-format.md) 修正ルール参照)。

- **3-1** AC カバレッジ表機械合成 + Critical / Important / Nice-to-have を分析ファイルに記録
- **3-2** AC ブラッシュアップ (`[MECE追加]` / `[MECE追加 変更]` タグ、補足は無タグ)
- **3-3** MECE 分析結果セクションを分析ファイル末尾に追記 ([references/output-format.md](references/output-format.md))。Red Team 出力の Markdown 部に「判定不能 (Unknown)」がある場合は理由ごとこのセクションへ転記する (受け皿が無いと棄権項目が黙って落ち、誤った「MECE OK」になるため。0 件なら省略)
- **3-4** プランファイル `## 品質検証` に 1 行追記:
  `- MECE判定: [OK (Critical: 0) or 要修正（Critical N件）] / Important [I]件 (うちAC反映 [R]件) → [分析ファイル名]`
  (`I` / `R` の定義は [references/synthesis-and-errors.md](references/synthesis-and-errors.md) の「サマリー値の定義 (SSOT)」。Critical 0 でも Important が実価値を持つ運用実態をサマリーに露出させるための列。カバレッジ・漏れ・重複などの詳細集計は分析ファイルの分析サマリーにのみ記録する)

各 step の合成ロジック・タグ判定・「補足」と「書き換え」の境界は [references/synthesis-and-errors.md](references/synthesis-and-errors.md)。

## Advanced

References:
- [references/analyst-contract.md](references/analyst-contract.md) — BB / WB の責務・情報源制約・Critical 閾値・出力契約 (統合定義)
- [references/ac-enumerate.md](references/ac-enumerate.md) — AC-ID 正規化ルール / 全カテゴリ統一形式 / 上流契約違反時の挙動
- [references/dispatch-prompts.md](references/dispatch-prompts.md) — Step 1 / Step 2 dispatch prompt 全文 / JSONL 抽出 / 失敗リカバリ
- [references/synthesis-and-errors.md](references/synthesis-and-errors.md) — Step 3 合成ロジック / Error Handling
- [references/init-common.md](references/init-common.md) — 初期化 (define-AC と共通)
- [references/red-team-checklist.md](references/red-team-checklist.md) — Red Team チェックリスト (agents/fresh-red-team.md が Read)
- [references/output-format.md](references/output-format.md) — 分析ファイル / プラン修正フォーマット
- [references/delegated-execution.md](references/delegated-execution.md) — 委譲実行時の読み替え契約

Agents:
- [agents/fresh-red-team.md](agents/fresh-red-team.md) — Red Team (BB/WB 出力のみで統合判定、plan/AC を持たない)

## 併用推奨 skill

- `/define-acceptance-criteria` — 前段で AC を定義
- `/finalize-plan` — MECE 結果を反映して実装準備へ
