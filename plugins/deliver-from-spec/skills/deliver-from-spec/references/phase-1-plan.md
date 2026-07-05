# Phase 1a-1d: プラン確定

起動方法の通則 (2 経路パス解決・メインコンテキスト実行・Orchestrated モード宣言) は SKILL.md 本文を参照。本ファイルは各 Phase の手順・完了条件・ループ上限を扱う。

## Phase 1a: プラン起案 → review-design

1. 仕様文書 (`$ARGUMENTS`) を基に、通常の plan mode 手順でプランファイルを起案する（本 skill が代行するのはこの後の review-design 起動のみで、起案そのものは主エージェントの既存の plan mode 能力を使う）
2. `/review-design` の SKILL.md を Read し、手順どおりプランファイルをレビューする

**完了条件**: `<plan>.design-review.md` が存在し、fatal 0 件。

**前提部品への依存**: この完了条件は review-design が Step 6 の最終レポートを `<plan>.design-review.md` へ固定ファイル名で保存することに依存する。本 skill の実装時点でこの保存処理が review-design 側に無い場合、Phase 1a は機械判定できない (詳細は SKILL.md 冒頭の依存関係の注記を参照)。

**再突入**: fatal が残る場合、プランを修正し review-design を再実行する。フェーズ再突入は 1 回まで（SKILL.md 本文の一般規則どおり）。

## Phase 1b: AC 定義 → MECE 検証

1. `/define-acceptance-criteria` の SKILL.md を Read し、手順どおり AC マトリクスを `<plan>.analysis.md` に書き出す
2. `/mece-plan-review` を Orchestrated モードで起動する（起動直前に発動フレーズを宣言し、escalation ledger パスを `<plan>.escalation-ledger.md` として渡す）

**完了条件**: 分析ファイルの Critical 0 件（mece-plan-review 既存のゲート判定をそのまま使う）。

**AC 修正ループの上限 (design 文書の明示的な例外)**: Critical が残る場合、define-acceptance-criteria で AC を修正し mece-plan-review を再実行するループは **2 周まで**。これは SKILL.md 本文の一般規則（フェーズ再突入 1 回まで）に対する Phase 1b 固有の例外であり、2 周を超えて Critical が残る場合は Phase 1c の仕様判断バッチへ持ち越さず、そのまま人間確認へエスカレートする（AC の土台が固まらないまま後続フェーズに進めると手戻りが大きいため、記帳続行には倒さない）。

## Phase 1c: 仕様判断バッチ (自前、既存 skill 委譲なし)

MECE 完了 (Phase 1b 完了) の直後、finalize-plan 起動 (Phase 1d) の直前に置く、プランニング段で唯一許容された停止点。

### 収集対象

1. Phase 1a/1b で `(仕様確定要)` 付き AC として残った項目（define-acceptance-criteria の記法規則により、プラン本文に仕様が欠落する箇所は AC 側にこの印が付く）
2. Phase 0 で `未定` のまま残った preflight 項目（権限アカウント一覧・テストデータ準備手順。[references/preflight.md](preflight.md) 参照）

### 判定・実行

1. 上記 1・2 を合算した「未決仕様判断」件数を数える
2. **0 件なら停止しない**（Phase 1d へそのまま進む）
3. 1 件以上ある場合、`<plan>.preflight.md` の「仕様判断の扱い」欄を確認する:
   - `停止して確認` (既定): 1 回の `AskUserQuestion` で全件をまとめて確認し、回答をプランファイル・preflight ファイルへ反映する
   - `推奨案で続行し escalation 記帳`: 停止せず、各項目について推奨案 (define-acceptance-criteria が AC に残した仮置き値、または preflight 項目ならプロジェクト既定値からの推測) を採用し、`<plan>.escalation-ledger.md` に 1 件 1 行で記帳して続行する。深刻度は Major を既定とする（実装方針を左右しうるが、致命的な機能欠落ではないため）

**完了条件**: 未決仕様判断 0 件（人間の回答またはフルオート記帳のいずれかで解消済み）。

## Phase 1d: finalize

1. `/finalize-plan` の SKILL.md を Read し、手順どおりブランチ・PR 分割・QA 手順を確定する
2. finalize-plan の Step 5 (preflight 補完) は、Phase 1c で残項目が既に解消済みのため、通常は追加の `AskUserQuestion` を発火させない (0 件確認は無停止)

**完了条件** (3 点、いずれも既存/追加ゲートの機械判定):
1. カバレッジゲート pass (finalize-plan 既存)
2. qa-ledger 初期化済み (finalize-plan 既存)
3. **全 auto QA-ID が PR 割当済み** — finalize-plan 側に追加予定のゲート bash（QA-ID→PR 割当列の必須化、計測知見 7 対応）に依存する。本 skill の実装時点でこのゲートが finalize-plan 側に無い場合、Phase 1d は機械判定できない (詳細は SKILL.md 冒頭の依存関係の注記を参照)

**再突入**: いずれか未達なら finalize-plan を再実行する。フェーズ再突入は 1 回まで。
