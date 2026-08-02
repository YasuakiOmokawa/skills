# regression eval (empirical-prompt-tuning 収束時保存)
再実行記録: 2026-07-26 (v0.29.0 PR / Claude 5 世代ガイドライン適合)。selection-rules.md の flat 規定「下限 3 / 上限 5」(lite=1 軸と矛盾) を SKILL.md の Quantitative scaffolding 表 (canonical) への委譲に修正し、6 軸実効上限・「3-5 個」表現も tier 語彙へ統一。merge-gate 4 シナリオ + lite/deep 追加 probe を fresh executor で再実行し全 [critical] ○ (lite 1 軸 / standard 3 軸 / deep 5 軸+obs の 3 点すべてで canonical 表への解決を実証、旧 flat 規則を引いた executor 0)。

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: standard tier / 複数主種別 (api_change + service_change)

plan mode (git 実行不能) の委譲実行。事前準備: run dir に `plan-csv-export.md` を作成する — CSV エクスポート API (`GET /api/exports/users.csv`) に列 1 つ追加、変更ファイル予定 = controller + service + spec を明記し、本文に「認可は既存のまま変更しない (管理者のみ閲覧可の既存 policy を流用)」と書く。分析ファイルとプラン末尾サマリーは run dir に実ファイルとして書かせ、conductor が実ファイルで突き合わせる (self-report だけで採点しない)。

### Requirements checklist
1. [critical] 分析ファイルが作成され、必須セクション (`## 受け入れ条件` / `### 正常系` / `### 異常系` / `### エッジケース` / `### 不変条件` / `### 非影響確認`) が揃い、必須 3 カテゴリの AC 行がすべて `- [ ] <controlled label>: ...` 形式 (不変条件は `[不変条件: <パターン>]` 行頭、非影響確認は label 不要)
1b. [critical] 不変条件のトリガー (期間跨ぎ / 集計値 / 状態遷移 / 二重書き込み / 再実行) はいずれも観測できないため **0 件で通し**、`### 検討観点` に見送り理由が 1 文ある (トリガー非該当なのに QA-I を捏造していない)
2. [critical] tier = standard、主軸 3 軸 × 必須 3 カテゴリ = 9 セル全充填
3. 複数主種別のため主軸確定手順 (候補プール → 除外 → 優先度列 → 採用) を適用し、根拠を `### 検討観点` に明記
4. 既存認可 (存在するが不変) を主軸から外した場合、非影響確認に認可の regression 1 行が残る
5. 技術リスク 3 件 (3 点セット、散文は各 1 文、検証はコマンド入り)
6. `### Tier` 見出しの次行に判定結果と理由が独立 1 行 (見出し行に結合しない)
7. `## 品質検証` の M 算出が実 AC 行数と一致

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
2. [critical] 必須セクション構成 (`### 不変条件` を含む 5 カテゴリ) と AC 行頭 controlled label 形式 (不変条件・非影響確認は例外) が維持されている
3. tier 判定 (このシナリオでは standard) が `### Tier` に理由付きで1行記録されている
4. 技術リスク3件が3点セットで記述されている
5. `## 品質検証` の M 算出が実カウントと一致

## シナリオ: 不変条件トリガー該当 (期間跨ぎの台帳 / deep tier)

**追加日: 2026-08-02 (v0.30.0 / 不変条件カテゴリ新設)。**

収束記録: 2026-08-02 (v0.31.0)。fresh executor 1 走行で **checklist 9 項目すべて ○ (GREEN)**。成果物 2 件 (分析ファイル + プラン末尾サマリー) を conductor が実ファイル Read で突き合わせ済み。tier=deep / N=5 / M=22 (必須15 + 不変条件3 + 非影響確認4) で `M == N×3 + I + K` が成立し、不変条件が N・必須セル数のいずれにも加算されていないことを実ファイルで確認。**RED/GREEN の対比が同一成果物内で観測できた**: 同じ「表示対象会計期間」の論点に対し、正常系 (`caller`) は DD 未記載を理由に `(仕様確定要)` で保留した一方、不変条件は `当期モードの期末簿価 == 翌期プレビューモードの期首時点簿価` として仕様確定を待たずに書けている。executor は指示外の判断として「保存」の観測を CSV 経路と画面経路の 2 経路突合に置いた (外部オラクル突合に相当)。

本走行の不明点 9 件のうち、**本カテゴリ由来の 4 件のみを修正**し 5 件は既存 gap として見送った (下記)。修正はいずれも追加ではなく統合・削除・既存句の精緻化で行い、新規セクションは足していない。

- **Issue 6 (修正済み・最重要)**: パターン「保存」の説明文が「集計値と明細の合計一致」(同時点の内部整合) と「変更前後で総数が保たれる」(リリース前後の回帰) の 2 概念を同居させており、後者が切り分け表の「既存が変更前と同じ挙動 → 非影響確認」と正面衝突した。executor は実際に Retry 3 でこの判断をやり直している。**後者の句を削除**して解決 (定義を 1 概念に戻す)。
- **Issue 4 (修正済み)**: 「期待値を仕様書から引かずに書けるか」の判定基準は期待値のみを見ており、**観測対象の同定**に未確定仕様が要る場合 (「翌期プレビューが指すのは期首か期末か」) が無規定だった。切り分け節に 1 段落追加し、この場合も不変条件のまま `(仕様確定要)` を付す運用に統一 (カテゴリを移すと確定待ちの間に関係が失われるため)。
- **Issue 3 (修正済み)**: 「実装に依存しない観測方法」を要求しているが**観測点の実在**は要求しておらず、executor は実在未確認の「台帳画面の合計欄」を観測点に採った。書式ルールの既存句に `[観測点未確認]` マークの義務を追記。
- **件数の部分該当 (修正済み)**: tier 別件数 (数量制約) とトリガー該当 (構造制約) の併記に対し、不足時・過剰時の分岐が無かった。失敗パターン台帳の既存 General Fix Rule (「数量制約と構造制約を併記する指示では、衝突時の優先順・不足時の埋め方・過剰時の削り方を対で書く」) をそのまま適用し、**件数を上限と再定義**して両方向を 1 文で規定。あわせて「1 トリガーから複数パターンが出ることはある」(本走行で executor が自力で気づいた点) を明記。

**見送り (既存 gap・本カテゴリ非由来)**: Issue 1 (tier の `multi-domain` が観測可能な述語で定義されていない — deep/standard の分岐で観点軸数・必須セル数・不変条件件数が丸ごと変わる) / Issue 2 (候補プール < tier 軸数時の充足手順。台帳に「クラスとして残存」と既記) / Issue 5 (定型文の placeholder に完成例が無い) / Issue 7 (M 算出式の変数のうち K だけ tier 別 SSOT に載っていない) / Issue 8 (不採用候補の記録先が observability とドロップ軸で不統一) / Issue 9 (見出しの必須性と項目の必須性が同じ語で書かれている)。いずれも本走行の [critical] 合否に影響していない。

**申し送り (M 算出のインセンティブ)**: executor が自己申告で「簡略式 `M == N×3 + I + K` が使える形を先に狙い、エッジケースの `data_volume` セルに空件数と大量件数の両方を書きたかったが 1 項目に削って成立させた」と報告した。規則違反ではない (SKILL.md は簡略式・完成形どちらも許容) が、**簡略式の存在が AC の粒度を歪める方向に働く**証拠。閉じるには簡略式の廃止か「粒度を優先し式は後から選ぶ」の明文化が要り、いずれも挙動変更のため本 PR の対象外。

**上記 4 修正後の再走は未実施** (修正はいずれも本走行で観測された不明点への直接対応で、[critical] 不合格の修正ではない)。次回 regression 時に本シナリオを再走し、Issue 6 の Retry が消えること・`[観測点未確認]` マークが機能することを確認する。

このシナリオは不変条件カテゴリの **positive path** を検証する (既存 4 シナリオはいずれもトリガー非該当なので negative path しか踏まない)。

事前準備: `$RUN/plan-asset-carryover.md` を新規作成する — 固定資産台帳の **CSV エクスポート項目に「期末簿価」「除売却フラグ」を追加**する plan。本文に次を含める:
- 表示対象は「当期」「翌期プレビュー」「年度締め後」の 3 モードがある
- 減損の計上方式が 3 択 (直接減額 / 間接控除 / 併用) で、選択により簿価の算出が変わる
- 変更ファイル予定 = `app/services/fixed_assets/csv_builder.rb` / `app/models/fixed_asset.rb` / `spec/services/fixed_assets/csv_builder_spec.rb`
- **DD には「どの会計期間を表示するか」の記載が無い**ことをメモとして残す (仕様の穴を意図的に作る)

成果物は run dir に実ファイルで書かせ、conductor が実ファイルで採点する。

### Requirements checklist
1. [critical] `### 不変条件` に AC が **deep tier の 3 件**あり、各行が `- [ ] [不変条件: <パターン>]: <関係> (検証: <観測方法>)` 形式
2. [critical] 各不変条件が**等式または順序関係**で書かれている (「〜が正しく保たれる」等の関係が消えた表現がゼロ)。かつ**期待値をプラン本文・DD から引いていない** (DD に会計期間の記載が無いにもかかわらず書けている)
3. [critical] 採用パターンに **連続** (前期末 == 翌期期首) または **凍結** (確定済み過去データが後続操作で不変) の少なくとも一方が含まれる — これが実案件で見逃された 2 件の Major に対応する軸
4. `### 検討観点` に、該当したトリガー名 (期間・世代をまたぐ / 状態遷移 等) と採用パターンが 1 文ずつ記録されている
5. `(検証: ...)` が**実装に依存しない観測方法** (DB 値 / API レスポンス / 画面表示) になっている — 変更対象クラスのメソッドを呼んで比べる書き方になっていない
6. tier = deep と判定されている (multi-domain + 会計ロジック)
7. `## 品質検証` の M 算出に `不変条件3件` が内訳として現れ、実 AC 行数と一致
8. 不変条件が必須セル数 (deep = 15 セル) に**加算されていない** (N は観点軸数のまま)

### 期待する failure mode (RED の想定)
本カテゴリ導入前の baseline では、この plan に対して生成される AC は「当期の CSV に期末簿価列が出る」「除売却済み資産で除売却フラグが true」といった**単一状態の期待値**に留まり、`期 N の期末簿価 == 期 N+1 の期首簿価` のような 2 状態の突合は出ない。同型の実案件 (会計台帳の CSV 出力項目追加) の不具合分析で Major 2 件がこの形で見逃されており、「DD 未記載でも不変条件テストなら検出可能だった」と結論されている。**RED は実測済み**とみなし、GREEN の確認が本シナリオの目的。

収束記録: 2026-07-11 (M 算出の N 定義明確化)。委譲実行シナリオ A を fresh executor で再実行し全 [critical] ○。M 算出の N 定義について「裁量追加した副作用軸 (compat 等) を N に数えるか」が不明点として出たため、N をセル充填基準 (必須 3 カテゴリのセルを充填した軸は N に数え、matrix 外別表記の observability 等のみ除外) で明確化した。机上再確認で迷いなく一意適用できることを確認し収束。

収束記録: 2026-07-17 (v0.27.0 / SKILL.md スリム化)。Step 2 の低頻度・相互排他な分岐 (deterministic classifier / 主軸超過ドロップ規則 / cross-cutting label / observability 6 軸上限) を SKILL.md から references/selection-rules.md へ **verbatim 退避** (1 hop)。SKILL.md 171 行 → 163 行 (17,488 → 15,563 byte)。median path (単一主種別・inline 表) は SKILL.md 内で自己完結を維持し、「存在するが不変の横断機能をドロップ→非影響確認に regression 1 行」の point-of-use 要約は SKILL.md に残置。上記 4 シナリオを fresh executor (blank slate, Task dispatch) で 2 ラウンド実行し、全 [critical] ○ / accuracy ~100% を 2 連続達成。複数主種別シナリオ (1 / リファクタ) は退避先 selection-rules.md へ 1 hop 到達し classifier + ドロップ規則 + 認可 regression を正しく適用できることを確認 (退避による劣化なし)。挙動変更・ルール統合はなく、消失ルール 0 (git 突き合わせ済み)。修正 diff は 0 のため過学習リスクなし (hold-out は不要)。

**申し送り (本 slim の対象外・既存の capability 課題)**: Iter2 のリファクタ executor が「deterministic classifier の『各 type 最も中心的な 1 label』を厳守すると 2 主種別で 2 軸しか出ず、standard = 3 軸に 1 本足りない。3 本目の補充規則が明示されていない」と指摘。これは退避前から存在する記述上のギャップ (selection-rules.md の「複数種別該当時は union を 3-5 に絞る」で実質補えるが、classifier の 1-per-type 表現と併読しないと解消しない) で、slim が新たに生んだものではなく、[critical] 不合格にもつながっていない。閉じるには補充規則の新設 = 挙動変更が必要なため本スリム化 PR の対象外とし、capability 改善として別途検討する。

収束記録: 2026-07-25 (Opus 5 / Fable 5 向け最適化)。上記シナリオ 1 (CSV エクスポート) / シナリオ 3 (薄いプラン) を median + edge として round 1-5 を fresh executor で実行し、**全 11 executor 走行で全 [critical] ○ / accuracy 100% / 成果物を実ファイルで突き合わせ済み**。hold-out (リファクタ、シナリオ 4) は round 4 で accuracy 100% (過学習なし)。steps 11-14 / duration 252-308s で rounds 3-5 は閾値内。Iter 0 で description が技術リスクとプラン末尾サマリーを謳っていない gap、Quick start の「auth 文脈の role 更新を 3 主軸」= 強制 deep 規則との矛盾、Step 4 の「リスク 3 件固定」= tier 表 (lite 0-1 / deep 3-5) との矛盾を修正。iter 2-4 で観測された不明点 (observability の N カウント / `### Tier` 直後の空行可否 / `(仕様確定要)` のリテラル性 / 推定入力時の tier 規則 / M 実数表記の分岐後の完成形 / 異常系定型の適用範囲) を明示化し、**output-template.md の例示見出し `### エッジケース (境界値チェックリストより)` を bare 見出しへ修正** (mece-plan-review の契約表は完全一致を要求し、suffix 付きは `カテゴリ:不明` へ劣化する経路が実在。round 1-2 の executor は実際に suffix 付きで書き出していた)。iter 5 では新規不明点が「規則同士の衝突」に集中したためパッチを止め、selection-rules.md の主軸確定を **候補プール → 除外 → 優先度列 → 採用 → 外した関心の regression** の 1 手順へ構造統合 (増やす方向と減らす方向で同じ優先度列を使う形にし、リファクタ文脈で「不変」根拠が全軸を消す衝突も閉じた)。

**申し送り (未クローズ・capability 改善として別扱い)**:
- 「そのカテゴリに実観測点が構造的に存在しないセル」(read-only エンドポイントの `compat` / `caller` 軸の異常系など) の代替書式が未定義。round 2 / 3 / 5 の executor が同じ趣旨を指摘し、いずれも framework 例外を発明して埋めた ([critical] 不合格には至っていない)。閉じるには「セル単位の代替書式」= 挙動追加が必要なため本 PR の対象外。
- 「0 新規不明点 2 ラウンド連続」は最後まで成立しなかった (新規不明点は 7 → 9 → 6 → 8 → 6 と減らず、内容は毎回異なる周辺境界ケース)。accuracy は全ラウンド 100% で飽和し steps / duration も閾値内のため、方法論の resource cutoff で打ち切った。Opus 5 / Fable 5 は規則の穴を必ず 1 つは見つけて報告するため、この残差は defect ではなく密度の高い規則系の性質として扱う。
- selection-rules.md 手順 3(b) の「type をまたぐ比較も表の行順」の 1 句は **最終ラウンド後に追加**したため fresh executor 未検証 (round 5 の executor 2 名が独立に同じ解決 = ファイル全体の行順を選んだのを成文化したもの)。次回 regression 実行時に確認する。

収束記録: 2026-07-25 (残作業検証 / 修正 diff 0 / **収束確定**)。上記 2026-07-25 申し送りの残作業 1・2 を hold-out C (振る舞い不変リファクタ) の fresh executor 1 走行で検証し、checklist 5 項目すべて ○ / accuracy 100% (tool_uses 11 / duration 278s / retry 0 = rounds 3-5 の閾値内)。成果物は実ファイル 2 件 (分析ファイル + プラン末尾サマリー) を conductor が Read で突き合わせた。**残作業 1 (iter 5 の主軸確定 1 手順化を C で再走)**: リファクタ文脈でも主軸は全滅せず、手順 2 の除外範囲 (「変更対象レイヤーが触れない横断機能だけ」) が意図どおり効いて `permission` のみドロップ → 手順 5 の regression 1 行が非影響確認に残った。主軸 3 軸 (`req_form` / `caller` / `compat`) は維持。**残作業 2 (手順 3(b) の type をまたぐ行順)**: (a) で api_change から `req_form`・service_change から `caller` を採った後、残候補 `compat` (api_change 行) と `error_prop` (service_change 行) を **type をまたいで表の行順で比較**し `compat` を採用、`error_prop` を枠外ドロップして異常系 caller セルで代替回収。停止・確認待ちなし。rounds 4・5 の全 [critical] ○ + 本走行をもって収束確定とする (「新規不明点 0 が 2 連続」は成立せず = 申し送りどおり resource cutoff を踏襲。本走行の新規不明点 5 件も周辺境界ケースで、うち最有力は「1 つの type 内で複数 label がいずれも plan 明示関心のときのタイブレーク未定義」— executor は 3(b) と同じ解決 (表の行順) を自力で選び [critical] に影響なし。**追加ではなく統合で応じる**方針のため本走行の修正 diff は 0)。

収束記録: 2026-07-18 (regression 再検証 / 修正 diff 0)。上記 4 シナリオを fresh executor (blank slate, Task dispatch) で 1 ラウンド再実行し、全シナリオで全 [critical] ○ / accuracy ~100% (○ のみ、partial/× なし)。tool_uses 7-11 / duration 256-315s。書き出された分析ファイル 3 件 (委譲 A / B / リファクタ) を実ファイル Read で突き合わせ、self-report と一致することを確認 (必須セクション構成・controlled label 行頭・全セル充填・Tier 冒頭記録・M 算出一致をすべて実検証)。過去の収束記録が直前ラウンドのクリアとして先行するため 2 連続クリアが成立し収束確定。新規不明点 0 — executor が挙げた不明点は (a) eval scaffolding 由来 (シナリオ 1 の plan パス未提示)、(b) 意図どおりの domain-thin 処理 (薄いプランの変更ファイル推定・データ取得経路不明を技術リスク + `(仕様確定要)` へ正しくルーティング)、(c) 上記 2026-07-17 申し送りの既知 gap (複数主種別で classifier が tier 軸数未満の主軸しか出さない件) のいずれかに分類され、いずれも新規ではない。(c) はシナリオ 2 (委譲 A) と 4 (リファクタ) で再度表面化したが、両 executor とも Gotcha「type ごと均等配分不要」を根拠に api_change の 2 本目 label (`compat`) を採って正しく 3 軸を確定し、[critical] 不合格には至っていない。既知 gap の解消は挙動変更を要するため引き続き capability 改善として別扱いとし、本ラウンドの skill 修正 diff は 0。

---

# tuning 進行状態 (2026-07-25 / Opus 5・Fable 5 向け最適化)

セッションの subagent spawn 上限 (200) 到達で打ち切ったため、再開に必要な状態をここに残す。**skill 側の修正は完了・全ラウンド合格済み**で、残っているのは下記「残作業」の検証のみ。

## このラウンドで使った凍結シナリオ (fixture は session scratchpad にあり消滅するため内容を記録)

いずれも **委譲実行** (Task dispatch)。run dir は git 管理外に毎回新規作成し、executor には run dir 配下のみ書き込みを許可、リポジトリは Read のみ、`gh` / 外部 MCP / push を禁止する。成果物は self-report ではなく **conductor が実ファイルを Read / grep して採点**する。

- **A (median)** = 上記「standard tier / 複数主種別」シナリオ。fixture `plan-csv-export.md`: ユーザー CSV エクスポート API (`GET /api/exports/users.csv`) の出力に `last_signed_in_at` 列を末尾追加。列順は既存 6 列を動かさない (既存取り込みスクリプト保護)、値は既存 `created_at` と同じ JST 書式、**「認可は既存のまま変更しない (管理者のみ閲覧可の既存 policy を流用)」を明記**。変更ファイル予定 = `app/controllers/api/exports_controller.rb` / `app/services/exports/user_csv_builder.rb` / `spec/requests/api/exports_spec.rb`。未確定事項として nil 時の出力 (空文字 or `-`) を残す。対象コードベースは環境に不在 = git 抽出不能。checklist は同シナリオの 7 項目 ([critical] は 1, 2)。
- **B (edge)** = 上記「委譲実行 B」シナリオ。fixture `plan-thin.md`: 「検索のもっさり感を改善する」— 背景は「検索が重い」の社内声のみ、やることは「検索まわりの動作を良くする」「待たされないように」、メモに「まだどこを直すかは決めていない」。**変更ファイルへの言及ゼロ**。checklist は同シナリオの 5 項目に次の 1 項目を加えた 6 項目で運用した: 「プランファイル末尾 `## 品質検証` に 1 行サマリー追記」「最終メッセージに分析ファイル絶対パス・Tier・M 値」([critical] は 1, 2)。
- **C (hold-out)** = 上記「振る舞い不変のリファクタ」シナリオ。fixture `plan-ranking-refactor.md`: `GET /api/search/ranking` のランキング算出ロジック (controller のプライベートメソッド 4 つ・約 120 行) を `app/services/search/ranking_calculator.rb` へ抽出。**入出力仕様・並び順・HTTP status・エラー挙動 (不正 `period` は 400 / 未ログインは 401) をすべて維持**、spec は期待値変更なし。同点タイブレークが id 昇順だが意図か不明とメモ。checklist は同シナリオの 5 項目 ([critical] は 1, 2)。

## ラウンド別結果 (fresh executor / 全走行で全 [critical] ○ / accuracy 100%)

| Round | 適用した修正テーマ | A steps/dur/retry | B steps/dur/retry | C steps/dur/retry | 新規不明点 |
|---|---|---|---|---|---|
| 1 | baseline (Iter 0 + 最適化パス後) | 12 / 260s / 1 | 18 / 300s / 1 | — | 7 |
| 2 | 数量・マーカー contract の一意化 (5 件) | 11 / 308s / 0 | 12 / 297s / 1 | — | 9 |
| 3 | 分岐・例外経路を完成形で閉じる (6 件) | 11 / 260s / 2 | 12 / 253s / 1 | — | 6 |
| 4 | 規則の適用範囲・両面・入力参照を閉じる (5 件) | 14 / 261s / 1 | 13 / 274s / 1 | **12 / 270s / 1 (100%)** | 8 |
| 5 | selection-rules.md の主軸確定を 1 手順へ構造統合 | 11 / 253s / 2 | 12 / 253s / 1 | dispatch 不可 (上限到達) | 6 |
| 6 | 修正なし (残作業 1・2 の検証のみ) | — | — | **11 / 278s / 0 (100%)** | 5 |

weak phase は全 11 走行で `Trace: all OK` (Understanding / Planning / Execution / Formatting のいずれも stuck なし)。

## 失敗パターン台帳 (最終状態)

| パターン | 代表 Issue | General Fix Rule | Seen in | 状態 |
|---|---|---|---|---|
| undefined-boundary-case delegation | classifier の 1-per-type で 2 主種別 → 2 軸、standard 3 軸に 1 足りず補充規則がない | 数量制約と構造制約を併記する指示では、衝突時の優先順・不足時の埋め方・過剰時の削り方を対で書く | iter 1-5 (表層は毎回異なる) | 個別事例は都度クローズ。クラスとしては残存 |
| branch-output-partial-form | M 実数表記に切り替えたとき簡略式の他要素 (`<N>観点×...`) の去就が不明 | 出力形式に分岐があるときは各分岐の完成した 1 行を並記する | iter 2 | **closed** (iter 3 修正 → round 4/5 で再発なし) |
| one-directional-selection-rule | ドロップ規則が「残す」側だけを規定し、補充規則は行順だけで plan 明示関心が効かない | 軸集合を決める規則は増やす方向・減らす方向で同一の優先度列を参照させる | iter 3, 4 | **closed** (iter 5 で構造統合)。type 次元の tie-break のみ未検証 |
| structurally-absent-cell | read-only GET の `compat` / `caller` 軸の異常系に置くエラー条件がなく framework 例外を発明して埋めた | セル単位の代替書式を 1 つ定義する (軸単位のドロップ規則では拾えない) | iter 2, 3, 5 (**3 回以上**) | **未クローズ** — 挙動追加を要するため申し送り |
| template-example-vs-canonical-divergence | output-template.md 本文の例示が `### エッジケース (境界値チェックリストより)`、規約リストと contract 表は bare | 下流が文字列一致で拾う見出しは規約リスト側を canonical とし、例示はそこから転記する | iter 2 | **closed** (iter 3 修正 → round 4/5 の成果物が bare であることを実ファイル確認) |
| shared-file-unconsumed-step | init-common.md のリポジトリ名取得は mece-plan-review 用でこの skill に消費先がない | 共有初期化ファイルの各手順は消費先を明記し、消費先のない skill では省略可と宣言する | iter 1 | **closed** (SKILL.md 側に「省略可」明記。cross-plugin sync 義務のため共有ファイルは不変) |
| multi-concept-in-one-definition | パターン「保存」の 1 行に「同時点の内部整合」と「変更前後の回帰」が同居し、後者が切り分け表と正面衝突。executor が判断をやり直した | 分類語彙の定義行に複数概念を同居させない。カテゴリ定義と切り分け表を併記する指示では、衝突する側の定義句を**削る** (切り分け表に例外を足さない) | 2026-08-02 (不変条件 round 1) | **closed** (「変更前後で総数が保たれる」句を削除) |
| observability-vs-existence | 「実装に依存しない観測方法」だけを要求し、その観測点が実在するかを問わなかったため、存在未確認の画面要素を検証手段に採った | 観測手段を書かせる指示は「実装非依存」と「実在」を別要件として両方課し、未確認時のマーク書式を与える | 2026-08-02 (不変条件 round 1) | **closed** (`[観測点未確認]` マーク義務化) |
| expectation-vs-identification | 「期待値を仕様書から引かずに書けるか」の判定が期待値のみを見ており、比較 2 点の**同定**に未確定仕様が要る場合が無規定 | 「仕様への依存」を判定軸にする指示は、期待値への依存と対象同定への依存を分けて扱う (前者はカテゴリを決め、後者はマークで済ませる) | 2026-08-02 (不変条件 round 1) | **closed** (同定依存は `(仕様確定要)` を付して不変条件のまま) |

## 残作業 (2026-07-25 の round 6 で全件クローズ済み — 収束確定)

1. ~~**hold-out C を iter 5 後の SKILL.md で 1 回再走**する~~ → **完了** (round 6 / accuracy 100%)。リファクタ文脈で主軸は全滅せず、除外は `permission` の 1 軸のみ + 非影響確認に regression 1 行。
2. ~~**selection-rules.md 手順 3(b) の「type をまたぐ比較も perspectives.md の表の行順で決める」1 句は fresh executor 未検証**~~ → **完了** (round 6)。`compat` (api_change 行) と `error_prop` (service_change 行) の type をまたぐ比較を行順で解決し停止なし。
3. rounds 4・5 の全 [critical] ○ + round 6 の hold-out 100% をもって**収束確定**。**「新規不明点 0 が 2 連続」は本ラウンドでは成立しておらず** (7→9→6→8→6)、内容は毎回異なる周辺境界ケース・品質面の失敗ゼロ・accuracy 100% 飽和・steps/duration 閾値内であることを根拠に方法論の resource cutoff で打ち切った判断を踏襲する。次回も 0 を狙って規則を足し続けると iter 2-4 で観測したとおり「足した規則同士の衝突」が次の不明点を生むため、**追加ではなく統合で応じる**こと。
