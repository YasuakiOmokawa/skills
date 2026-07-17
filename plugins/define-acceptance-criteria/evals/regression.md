# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: standard tier / 複数主種別 (api_change + service_change)

plan mode (git 未着手) の plan: CSV エクスポート API (GET /api/exports/users.csv) に列 1 つ追加、変更ファイル予定 = controller + service + spec、「認可は既存のまま変更しない」。分析ファイル全文と `## 品質検証` サマリーをインラインで出させる。

### Requirements checklist
1. [critical] 必須セクション構成 (## 受け入れ条件 / ### 正常系 / 異常系 / エッジケース / 非影響確認) と AC 行頭 `- [ ] <controlled label>:` を遵守
2. [critical] tier = standard、主軸 3 軸 × 必須 3 カテゴリ = 9 セル全充填
3. 複数主種別のため deterministic classifier + ドロップ規則を使い根拠を `### 検討観点` に明記。既存認可 (存在するが不変) のドロップ時は非影響確認に regression 1 行
4. 技術リスク 3 件 (3 点セット、各 1 文、検証はコマンド入り)
5. `## 品質検証` の M 算出が実カウントと一致
6. `### Tier` 行を分析ファイル冒頭に記録

## シナリオ: 委譲実行 A (プランファイル明示、分析ファイル無しからの AC 定義委譲)

収束記録: 2026-07-07 (delegation-execution 対応 PR)。baseline (Iter1) は両 critical とも ○ だったが、Step 6 後の最終報告規定が無く分析ファイルパス/Tier が返却されない項目が課題だった。SKILL.md に「## 委譲実行 (subagent として起動された場合)」節を追加し、init-common.md のプランファイル特定を 4 項目の優先順位 (`$ARGUMENTS` → 委譲プロンプト本文の明示パス → 単独起動時のみ `Plan File Info:` → 不足入力なら即終了) へ改修した後、Iter2/Iter3 で fresh executor が全 [critical] ○ / accuracy 100% を 2 ラウンド連続で達成し収束。hold-out シナリオ (プランファイル自体が存在しない委譲) でも accuracy 100% で overfitting なしを確認済み。

Task dispatch で以下の委譲プロンプトを与える (`$RUN` は毎回新規作成する run dir):

```
あなたは define-acceptance-criteria の実行を委譲されたエージェントです。次の SKILL.md を Read し、その指示に厳密に従って実行してください。

対象 SKILL.md: リポジトリ root からの相対パス plugins/define-acceptance-criteria/skills/define-acceptance-criteria/SKILL.md

## 入力
- プランファイル: $RUN/plan-search.md
- 分析ファイルはまだ存在しません

このプランに対する受け入れ条件を定義し、完了したら結果を報告してください。
```

事前準備: `$SCRATCH/fixtures-template/plans/plan-search.md` を `$RUN/` にコピーしてから実行する。

### Requirements checklist
1. [critical] `$RUN/plan-search.analysis.md` が新規作成され、`## 受け入れ条件` の 正常系/異常系/エッジケース 全カテゴリの全セルに ≥1 項目が埋まっている
2. [critical] 変更ファイル抽出や観点選定の過程で確認待ち (AskUserQuestion 相当) に陥らず、Step 6 まで完遂して最終メッセージを返している
3. 各 AC 行が controlled label (references/perspectives.md 準拠) で始まっている (非影響確認カテゴリを除く)
4. `$RUN/plan-search.md` 末尾の `## 品質検証` に AC 件数サマリーの1行が追記されている
5. 最終メッセージに分析ファイルの絶対パスと Tier 判定結果 (lite/standard/deep) が含まれている

## シナリオ: 委譲実行 B (変更ファイル記載が薄い + git 管理外ディレクトリでの委譲)

baseline (Iter1) は変更ファイル抽出フォールバック末尾の AskUserQuestion 分岐について item 5 (要人間判断の明記) のみ partial だった。同じ GREEN fix (AskUserQuestion が利用可能ツールに無い場合は `(推定)` を付けて最善推測のまま続行し、完了報告に要人間判断項目として明記) で Iter2 以降 accuracy 100% に収束。

Task dispatch で以下の委譲プロンプトを与える (`$RUN` は毎回新規作成する run dir、git 管理外):

```
あなたは define-acceptance-criteria の実行を委譲されたエージェントです。次の SKILL.md を Read し、その指示に厳密に従って実行してください。

対象 SKILL.md: リポジトリ root からの相対パス plugins/define-acceptance-criteria/skills/define-acceptance-criteria/SKILL.md

## 入力
- プランファイル: $RUN/plan-thin.md

このプランに対する受け入れ条件を定義し、完了したら結果を報告してください。
```

事前準備: `$RUN/plan-thin.md` に変更対象ファイルへの言及が一切ない薄いプラン (例:「システムの動作を良くする」) を新規作成してから実行する。

### Requirements checklist
1. [critical] 変更ファイル一覧が `git diff` からも取得できず (このディレクトリは git 管理下にない)、プラン本文にも記載が無い状況で、自然言語類推による最善推測に `(推定)` 相当の注記を付けたうえで AC 生成を継続している
2. [critical] AskUserQuestion 相当の確認待ちで停止し AC が0件のまま終了する、ということが起きておらず、最終メッセージまで到達している
3. `$RUN/plan-thin.analysis.md` が作成され、必須3カテゴリの全セルが埋まっている
4. 分析ファイル冒頭の `### Tier` に判定結果と根拠が1行記録されている
5. 最終メッセージに「変更ファイルが推測に基づく」旨が要人間判断項目として明記されている

## シナリオ: standard tier / 振る舞い不変のリファクタ (controller → service 抽出)

収束記録: 2026-07-07 (prototype-flow 最適化 PR)。SKILL.md Step 3 に「振る舞いを変えないリファクタ等では、各カテゴリを『変更前と同じ入出力を維持すること』を検証する回帰確認として書く」の箇条書きを追加した後、Iter1/Iter2 で fresh executor が全 [critical] ○ / accuracy 100% を 2 ラウンド連続で達成し収束 (steps 14→13, duration 276s→286s)。hold-out シナリオ (lite tier の pure 関数リファクタ) でも accuracy 100% で overfitting なしを確認済み。

Task dispatch で以下の委譲プロンプトを与える (`$RUN` は毎回新規作成する run dir):

```
あなたは define-acceptance-criteria の実行を委譲されたエージェントです。次の SKILL.md を Read し、その指示に厳密に従って実行してください。

対象 SKILL.md: リポジトリ root からの相対パス plugins/define-acceptance-criteria/skills/define-acceptance-criteria/SKILL.md

## 入力
- プランファイル: $RUN/plan-ranking-refactor.md
- 分析ファイルはまだ存在しません

このプランに対する受け入れ条件を定義し、完了したら結果を報告してください。
```

事前準備: `$RUN/plan-ranking-refactor.md` に、既存 API エンドポイント (例: `GET /api/search/ranking`) のコントローラ内ロジックを service 層へ抽出するだけの、入出力仕様を一切変更しないリファクタ plan (変更ファイル予定 2 件以上、git 管理外ディレクトリ) を新規作成してから実行する。

### Requirements checklist
1. [critical] 正常系・異常系・エッジケースの3必須カテゴリ全セルが「変更前と同じ入出力を維持することを検証する回帰確認」の形式で埋まっている (空欄・曖昧文言・新機能であるかのような記述になっていない)
2. [critical] 必須セクション構成と AC 行頭 controlled label 形式 (非影響確認は例外) が維持されている
3. tier 判定 (このシナリオでは standard) が `### Tier` に理由付きで1行記録されている
4. 技術リスク3件が3点セットで記述されている
5. `## 品質検証` の M 算出が実カウントと一致

収束記録: 2026-07-11 (M 算出の N 定義明確化)。委譲実行シナリオ A を fresh executor で再実行し全 [critical] ○。M 算出の N 定義について「裁量追加した副作用軸 (compat 等) を N に数えるか」が不明点として出たため、N をセル充填基準 (必須 3 カテゴリのセルを充填した軸は N に数え、matrix 外別表記の observability 等のみ除外) で明確化した。机上再確認で迷いなく一意適用できることを確認し収束。

収束記録: 2026-07-17 (v0.27.0 / SKILL.md スリム化)。Step 2 の低頻度・相互排他な分岐 (deterministic classifier / 主軸超過ドロップ規則 / cross-cutting label / observability 6 軸上限) を SKILL.md から references/selection-rules.md へ **verbatim 退避** (1 hop)。SKILL.md 171 行 → 163 行 (17,488 → 15,563 byte)。median path (単一主種別・inline 表) は SKILL.md 内で自己完結を維持し、「存在するが不変の横断機能をドロップ→非影響確認に regression 1 行」の point-of-use 要約は SKILL.md に残置。上記 4 シナリオを fresh executor (blank slate, Task dispatch) で 2 ラウンド実行し、全 [critical] ○ / accuracy ~100% を 2 連続達成。複数主種別シナリオ (1 / リファクタ) は退避先 selection-rules.md へ 1 hop 到達し classifier + ドロップ規則 + 認可 regression を正しく適用できることを確認 (退避による劣化なし)。挙動変更・ルール統合はなく、消失ルール 0 (git 突き合わせ済み)。修正 diff は 0 のため過学習リスクなし (hold-out は不要)。

**申し送り (本 slim の対象外・既存の capability 課題)**: Iter2 のリファクタ executor が「deterministic classifier の『各 type 最も中心的な 1 label』を厳守すると 2 主種別で 2 軸しか出ず、standard = 3 軸に 1 本足りない。3 本目の補充規則が明示されていない」と指摘。これは退避前から存在する記述上のギャップ (selection-rules.md の「複数種別該当時は union を 3-5 に絞る」で実質補えるが、classifier の 1-per-type 表現と併読しないと解消しない) で、slim が新たに生んだものではなく、[critical] 不合格にもつながっていない。閉じるには補充規則の新設 = 挙動変更が必要なため本スリム化 PR の対象外とし、capability 改善として別途検討する。
