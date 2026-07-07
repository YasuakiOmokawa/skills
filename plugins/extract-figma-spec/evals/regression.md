# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-07-07 (委譲実行契約 対応 PR)。用途: **regression 検出器** (capability 改善の信号としては使わない)。
本 skill を変更する PR では fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

baseline (Iter1) では委譲実行時の入力解決順位・ドリルダウン選定基準・完了報告フォーマットが未規定で、
出力先プランファイルパスの受け取り方自体が無かった。`## 委譲実行（subagent として起動された場合）` 節の新設と
Step 1 の 4 項目再構成 (ToolSearch 前提の接続確認 → 対象ノード確定 → 対象ノードの診断呼び出し → 複数ノード列挙) を経て、
Iter5・Iter6 で fresh executor 4 本 (シナリオ A/B 各 2 回) が全 [critical] ○ / accuracy 100% / tool_uses 4-6 / duration 125-170 秒を記録した。
ただし「新規不明点 0 が 2 ラウンド連続」という収束条件は厳密には満たしていない。Iter4-6 を通じて、フレッシュな実行者が
毎回異なる粒度の軽微な文書精度の指摘 (診断メッセージの再試行方針・ドリルダウンの照合粒度・完了報告の early-stop 分岐の文言) を
新たに見つけ続けたため、tuner-instructions.md の発散規則に従い追加の構造修正は打ち切り、最終報告でエスカレーションした。
critical 項目の合否自体は Iter5 以降 4 回 + hold-out 1 回の計 5 回で一度も崩れておらず、regression 検出用途としての採用に支障はない。

追記 (2026-07-07, Step 5 分岐対応 PR): Step 5 に「AC/MECE/finalize 等の計画装備を通常伴う文脈では `/define-acceptance-criteria` を実行、PoC・使い捨て検証では呼ばずプランの反映チェックリスト転記のみ」という分岐を追加した際の regression。
median (PoC 文脈) / edge (出荷文脈) の両シナリオで fresh executor 計 4 本が全 [critical] ○ / accuracy 100% を 3 ラウンド連続で記録。
文脈が曖昧で PoC/通常のどちらとも明示されない hold-out シナリオでは、初回は executor が自力で「通常経路をデフォルト」と推論した (根拠の宣言はあり critical は通過)。
これを明文規則として Step 5.2 に追記 (「文脈から判定できない場合は通常経路をデフォルトとし、判定根拠を明記する」) した上で再実行し、fresh executor が推論でなく本文の規則を直接引用する形に変わったことを確認 (tool_uses・duration とも悪化なし)。
Step 5.1 の「AC（またはプランの反映チェックリスト）」が AC 化後も併存可能かは明文化されておらず、executor は毎回両方作成して自己解決していた (checklist 合否には影響しない長期未解決点。Gotchas 参照)。

## シナリオ: 委譲実行 A (Figma URL + 出力先プランパス付きで抽出を委譲する)

Task dispatch で以下の委譲プロンプトを与える (`$RUN` は毎回新規作成する run dir):

```
あなたは extract-figma-spec skill の実行を委譲されました。以下の SKILL.md を Read し、その内容に厳密に従って実行してください。

対象 SKILL.md: plugins/extract-figma-spec/skills/extract-figma-spec/SKILL.md (リポジトリ root からの相対パス)

## 背景
todo アプリの UI を Figma デザイン通りに実装する作業の一部です。

## 入力
- 対象 Figma URL: `https://www.figma.com/design/AbCdEf123/todo-app?node-id=1-234`
- 出力先プランファイル: $RUN/plans/plan-priority-final.md

上記を対象に抽出を実行してください。
```

事前準備: `$RUN/plans/` を作成し、fixtures-template の `plans/plan-priority-final.md`（todo アプリの優先度機能プラン、Figma とは無関係な既存内容）を配置してから実行する。

### Requirements checklist
1. [critical] Figma MCP への接続確認 (`get_metadata` 相当) を試み、失敗した場合は「Figma Dev Mode MCP に接続できません」相当のメッセージで明確に停止している (推測データを捏造して先に進んでいない)
2. [critical] 接続失敗時、出力先プランファイル (`$RUN/plans/plan-priority-final.md`) に `## 正本抽出結果` 等の架空データを書き込んでいない (未接続の事実が最終メッセージで明確に報告される)
3. 固定 MCP ツール名で失敗した場合、ToolSearch 等で類似名を探す試行、またはその試行結果 (見つからなかった旨) が報告に含まれている
4. 対象ノード (`node-id` を `1-234` → `1:234` へ変換したもの) が URL から正しく抽出され、報告に反映されている (実行はできなくても対象特定は行われている)
5. 最終メッセージが「未接続」の事実と対処法 (Figma デスクトップアプリの起動・対象ファイルを開く) を含んでいる

## シナリオ: 委譲実行 B (出力先プランパスなしで同じ抽出を委譲する)

Task dispatch で以下の委譲プロンプトを与える (`$RUN` は毎回新規作成する run dir):

```
あなたは extract-figma-spec skill の実行を委譲されました。以下の SKILL.md を Read し、その内容に厳密に従って実行してください。

対象 SKILL.md: plugins/extract-figma-spec/skills/extract-figma-spec/SKILL.md (リポジトリ root からの相対パス)

## 背景
todo アプリの UI を Figma デザイン通りに実装する作業の一部です。

## 入力
- 対象 Figma URL: `https://www.figma.com/design/AbCdEf123/todo-app?node-id=1-234`

上記を対象に抽出を実行してください。
```

事前準備: シナリオ A と同じく `$RUN/plans/plan-priority-final.md` を配置する (出力先パス自体は起動プロンプトに与えない)。

### Requirements checklist
1. [critical] Step 1 の MCP 接続確認が失敗した場合、その事実 (Figma デスクトップ未接続、または接続済みだが対象ノード未検出) を停止理由として明確に報告している (出力先プランパスが無いことを停止理由と混同・誤帰属していない)
2. [critical] 出力先プランファイルパスが与えられていないことを、接続失敗とは別の懸念点として言及しているか、または (接続さえできればの前提で) チェックリストを最終メッセージで全文返す方針であることを明示している
3. 存在しないプランファイルへの書き込みや、架空の抽出結果 (`FIG-NN` 行) を捏造していない
4. 対象ノード (`node-id` を `1-234` → `1:234` へ変換したもの) が URL から正しく抽出され、報告に含まれている
5. 最終メッセージが「未接続」の事実と対処法を含んでいる

## シナリオ: 委譲実行 C (node-id / URL 不明でドリルダウンが必要な委譲、hold-out)

収束判定時の過学習チェック用に自作した hold-out シナリオ。A/B が通る①経路 (URL 直接指定) ではなく、
委譲実行のドリルダウン選定基準 (Step 1-2 の③経路) を初めて踏む。実測では accuracy 100% で、
A/B からの精度低下は観測されなかった (過学習の兆候なし)。

Task dispatch で以下の委譲プロンプトを与える (`$RUN` は毎回新規作成する run dir):

```
あなたは extract-figma-spec skill の実行を委譲されました。以下の SKILL.md を Read し、その内容に厳密に従って実行してください。

対象 SKILL.md: plugins/extract-figma-spec/skills/extract-figma-spec/SKILL.md (リポジトリ root からの相対パス)

## 背景
todo アプリの UI を Figma デザイン通りに実装する作業の一部です。優先度表示まわりのタブ UI を担当しています。

## 入力
- 対象 Figma ファイル: `todo-app` プロジェクトのデザインファイル（具体的な node-id や URL は未確定です）
- 出力先プランファイル: $RUN/plans/plan-priority-final.md

上記を対象に、タブ UI に関連するノードを特定した上で抽出を実行してください。
```

事前準備: シナリオ A と同じく `$RUN/plans/plan-priority-final.md` を配置する。

### Requirements checklist
1. [critical] Step 1-1 (`get_metadata`、nodeId なし) で接続確認を行い、ページ一覧を取得している
2. [critical] 対象ページ / ノードが一意に決まらない場合 (該当ページが無い、または複数の候補があり一意に絞れない場合)、AskUserQuestion が使えないことを理由に質問せず、候補一覧 (または該当なしの事実) を最終メッセージに含めて停止している (推測でノードを決め打ちして先に進んでいない)
3. 出力先プランファイルに架空の抽出結果 (`FIG-NN` 行や `## 正本抽出結果`) を書き込んでいない
4. 最終メッセージに、どのページ名を候補として検討したか (または該当ページが無いと判断した根拠) が示されている
5. 最終メッセージが対処法 (人間による対象ノードの明示指定、または Figma デスクトップで対象ファイルを開くこと) を含んでいる

## シナリオ: Step 5 分岐判断 (文脈が PoC とも出荷とも明示されない、hold-out)

Step 1-4 は完了済みとして与える (実 Figma MCP 接続を伴わない、Step 5 単体の分岐検証)。Task dispatch で以下を与える (`$RUN` は毎回新規作成する run dir):

```
あなたは extract-figma-spec skill の実行を委譲されました。以下の SKILL.md を Read し、その内容に厳密に従って実行してください。

対象 SKILL.md: plugins/extract-figma-spec/skills/extract-figma-spec/SKILL.md (リポジトリ root からの相対パス)

## シナリオ
todo アプリの優先度表示タブ UI を、Figma デザインに合わせて調整する作業です。

Figma からの抽出作業のうち Step 1 (MCP 接続確認・対象ノード確定) と Step 2-4 (構造化データ取得・チェックリスト化・実装との照合) はすでに完了しています。やり直す必要はありません。対象ノードは `1:234` (優先度タブ UI コンポーネント) で、Step 3-4 で確定した照合結果は以下の通りです (この内容は検証済みとして扱ってください):

| atom ID | 期待値 | 状態 |
|---------|--------|------|
| FIG-01 | タブ全体固定幅 92px | 一致 |
| FIG-02 | タブ間 gap 8px | 一致 |
| FIG-03 | 選択タブ背景色 #eef7e2 (YG2) | 差分 (現状 #f0f0f0) |
| FIG-04 | 選択タブ文字色 #333333 (GY7) | 一致 |
| FIG-05 | 非選択タブ font-weight Regular | 一致 |
| FIG-06 | 選択タブ font-weight Bold | 差分 (現状 Regular) |
| FIG-07 | IconOnlyButton は枠なし | 差分 (現状 1px 枠あり) |
| FIG-08 | タブ全体の中央寄せ | 一致 |

出力先プランファイル: $RUN/plans/plan-tabs.md

それ以外の文脈情報 (PoC か出荷実装かなど) はこれ以上与えられていません。SKILL.md の指示に従って Step 5 以降を実行してください。
```

事前準備: `$RUN/plans/plan-tabs.md` に「# 優先度タブ UI 対応」「## 背景」「優先度表示のタブ UI を Figma デザインに合わせて調整する。」のみの最小プランを配置する (PoC・出荷いずれの語も含めない)。

### Requirements checklist
1. [critical] `/define-acceptance-criteria` を呼ぶかどうかのどちらかの分岐を選択し、その選択根拠 (SKILL.md Step 5.2 のデフォルト規則を含む) を成果物または self-report に明示している (文脈が曖昧なままなのに根拠を示さず分岐している場合は×)
2. [critical] 差分 3 件 (FIG-03, FIG-06, FIG-07) が「プランの反映チェックリスト」として atom ID 付きでプランファイルへ転記されている
3. `## 正本抽出結果` セクションが全 8 行 atom ID 付きで書き出されている
4. 選んだ分岐と矛盾する行動をしていない (AC 化しないと述べつつ `/define-acceptance-criteria` を呼ぶ、逆も不可)
5. 出力先ファイルへの書き込みが実際に行われている
