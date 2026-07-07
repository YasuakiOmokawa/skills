# Orchestrated モード (mece-plan-review)

## 発動条件

ファイル存在からの推測では判定しない。呼び出し側（オーケストレータ）が「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示の伝達経路は `Task` 起動プロンプトでも、メインコンテキストで本 skill の手順を実行する直前の明示宣言でもよい（判定するのは宣言の有無であり伝達経路ではない）。指示が無い単独起動では本ファイルを参照せず、SKILL.md 本文の現行動作（subagent 応答不能時に AskUserQuestion で確認）のまま進む。

## escalation ledger 形式

ファイル名: `<プラン名>.escalation-ledger.md`。1 行 = 1 項目、追記のみ（既存行は書き換えない）。

| 番号 | 出所 | 深刻度 (Critical/Major/Minor) | 内容 | 根拠 | 推奨アクション |
|---|---|---|---|---|---|

- 「番号」は記帳前に ledger を Read し、既存の最終番号 +1 から採番する (ファイルが無ければ 1 から)。

## mece-plan-review 固有の記帳規則

Orchestrated モード時、以下 4 箇所の AskUserQuestion 分岐を読み替える。a/b は BB/WB 3 連続失敗 (または全欠落) 型、c/d はファイル I/O 失敗型で、読み替え後の記録先が異なる:

a. **Step 1-2 の AC 判定行数不一致**（[references/dispatch-prompts.md](dispatch-prompts.md) 「AC 判定行数不一致のリカバリ」点 3）: 3 連続失敗または全 AC 欠落の場合、判定できなかった AC を `judgment:"言及なし"` で補完したうえで、当該 AC を Critical 扱いとして escalation ledger に記帳し、Step 2 (Fresh Red Team) 以降へ進む
b. **Step 2 の JSONL 抽出失敗**（同ファイル「抽出失敗時」点 3）: 3 連続失敗または BB/WB 両方の JSONL 欠落の場合、欠落側の分析結果が無いまま MECE 判定を確定させず、影響を受ける AC 範囲を Critical 扱いとして escalation ledger に記帳し、判明している範囲で Step 3 の出力へ進む
c. **プランファイル書き込み失敗**（[references/synthesis-and-errors.md](synthesis-and-errors.md) 「プランファイル書き込み失敗」）: 分析ファイルへの記録は完了させたうえで、プランファイル 1 行サマリーは「未反映」として escalation ledger に Critical 扱いで記帳し、最終メッセージに分析ファイルの絶対パスを明記する (人間が事後に手動反映できるようにする)
d. **分析ファイル lock / non-git リポジトリでの書込み失敗**（同ファイル「分析ファイル lock / non-git リポジトリ」）: 1 回リトライしても失敗する場合、分析ファイルへの書込みは断念し、Step 3 の全内容 (AC カバレッジ表・4 分類クロスリファレンス・MECE 分析結果) を最終メッセージにそのまま埋め込んで返す。escalation ledger には書込み失敗自体を Critical 扱いで記帳する

a/b は BB/WB 分析失敗型で、Step 3 の出力ルール（分析ファイルへの全記録・プランファイルへの 1 行サマリー）自体は変更しない。c/d はファイル I/O 失敗型で記録先そのものを切り替える（c はプランファイル側のみ迂回、d は分析ファイル側を放棄し最終メッセージへ退避する）。いずれも「AskUserQuestion で確認」を「Critical 扱いで記帳して続行」に置き換える点は共通する。3-4 の 1 行サマリーには escalation ledger 記帳分を Critical 件数に算入する（安全側に倒した分を「MECE OK」に混入させないため）。

## 記帳例

```
| 7 | AC-12 | Critical | BB/WB が 3 回連続で AC 判定行数不一致、AC-12 の判定不能 | Step 1-2 リトライ 3 回失敗 | 手動 MECE レビューで AC-12 を再確認 |
| 8 | プランファイル | Critical | プランファイル書き込み権限エラーでサマリー行が未反映 | Step 3-4 書き込み時に Permission denied | 分析ファイル（絶対パス記載済み）を基に手動でサマリー行を追記 |
```

## Gotchas

- 上記 a〜d に該当しない中断・エラー分岐 (例: SKILL.md 0-2 の「分析ファイル / AC 無し」による即中断) は、Orchestrated モード宣言の有無によらず SKILL.md 本文の記載通り決定的に処理する (記帳対象ではない)。fresh executor が 2 回とも「a〜d のどれにも該当しないので記帳しない」と正しく判断できたが、都度この一覧を読んで自力で除外を導出する負荷が発生した。
