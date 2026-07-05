# Orchestrated モード (mece-plan-review)

## 発動条件

ファイル存在からの推測では判定しない。呼び出し側（将来のオーケストレータ）が `Task` 起動プロンプトで「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示が無い単独起動では本ファイルを参照せず、SKILL.md 本文の現行動作（subagent 応答不能時に AskUserQuestion で確認）のまま進む。

## escalation ledger 形式

ファイル名: `<プラン名>.escalation-ledger.md`。1 行 = 1 項目、追記のみ（既存行は書き換えない）。

| 番号 | 出所 | 深刻度 (Critical/Major/Minor) | 内容 | 根拠 | 推奨アクション |
|---|---|---|---|---|---|

## mece-plan-review 固有の記帳規則

Orchestrated モード時、以下 2 箇所の BB/WB 3 連続失敗 (または全欠落) による AskUserQuestion 分岐は、ユーザーへの確認を待たず**安全側 (Critical 扱い) に倒して続行する**に読み替える:

1. **Step 1-2 の AC 判定行数不一致**（[references/dispatch-prompts.md](dispatch-prompts.md) 「AC 判定行数不一致のリカバリ」点 3）: 3 連続失敗または全 AC 欠落の場合、判定できなかった AC を `judgment:"言及なし"` で補完したうえで、当該 AC を Critical 扱いとして escalation ledger に記帳し、Step 2 (Fresh Red Team) 以降へ進む
2. **Step 2 の JSONL 抽出失敗**（同ファイル「抽出失敗時」点 3）: 3 連続失敗または BB/WB 両方の JSONL 欠落の場合、欠落側の分析結果が無いまま MECE 判定を確定させず、影響を受ける AC 範囲を Critical 扱いとして escalation ledger に記帳し、判明している範囲で Step 3 の出力へ進む

いずれも「AskUserQuestion で確認」を「Critical 扱いで記帳して続行」に置き換えるだけで、Step 3 の出力ルール（分析ファイルへの全記録・プランファイルへの 1 行サマリー）自体は変更しない。3-4 の 1 行サマリーには escalation ledger 記帳分を Critical 件数に算入する（安全側に倒した分を「MECE OK」に混入させないため）。

## 記帳例

```
| 7 | AC-12 | Critical | BB/WB が 3 回連続で AC 判定行数不一致、AC-12 の判定不能 | Step 1-2 リトライ 3 回失敗 | 手動 MECE レビューで AC-12 を再確認 |
```
