# Orchestrated モード (qa-ui)

## 発動条件

ファイル存在（escalation ledger の有無等）からの推測では判定しない。呼び出し側（将来のオーケストレータ）が `Task` 起動プロンプトで「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示が無い単独起動では本ファイルを参照せず、SKILL.md 本文の現行動作（該当時は停止してユーザーの返答を待つ）のまま進む。

## escalation ledger 形式

ファイル名: `<プラン名>.escalation-ledger.md`（プランファイルと同じディレクトリに置く）。1 行 = 1 項目、追記のみ（既存行は書き換えない）。

| 番号 | 出所 | 深刻度 (Critical/Major/Minor) | 内容 | 根拠 | 推奨アクション |
|---|---|---|---|---|---|

- 「出所」には QA-ID を書く（QA-G-NN もそのまま QA-ID として扱う）
- 「深刻度」は台帳の状態語彙のうち `FAIL(重大度)` の重大度、または `要人間確認`・ラウンド上限超過は判定材料から Critical/Major/Minor のいずれかに寄せて記入する（判定が付かない場合は安全側で Critical 扱いにする）

## qa-ui 固有の記帳規則

Orchestrated モード時、以下の 3 つの状況は SKILL.md 本文の「停止する」を「escalation ledger に記帳して続行する」に読み替える。該当 QA-ID は qa-ledger 側で `要人間確認`（または `FAIL(Critical)`）のまま保留し、以後のラウンドの検証対象・修正対象からは除外するが、**他の独立した QA-ID の検証・修正ループは止めない**（全項目の検証が終わるまで完了とは呼ばない）。

1. **Critical FAIL** — Step 5「Critical が1件でも含まれる → 即エスカレート」
2. **ラウンド上限超過**（cap 超過の狭い例外に該当しない）— Step 5「ラウンド3でもFAIL → エスカレート」
3. **要人間確認**（Gotchas テーブル未カタログの検証不能）— Step 5 の判定 2. および「検証不能が1件でも含まれる場合」

`検証不能(真の制約)` は元々非ブロッキングであり、Orchestrated モードの有無に関わらず記帳のうえループを継続する（SKILL.md 本文どおり、上記 3 状況とは別扱い）。

## Step 6 完了判定への反映

完了判定の表示に、escalation ledger の集計結果を追記する: 「escalated N 件（うち Critical M 件）」。**Critical が 1 件でも含まれる場合、判定は「完了」を名乗らず「部分完了」を上限とする**（Critical 項目が保留のままである限り、機械集計が exit 0 を返しても「完了」表示はしない）。

**検証済み Bash**（`/tmp` fixture で $4=深刻度 の列位置を確認済み）:

```bash
LEDGER="<plan>.escalation-ledger.md"

if [ ! -s "$LEDGER" ]; then
  echo "escalated 0件"
else
  TOTAL=$(awk -F'|' '/^\| *[0-9]+ *\|/{c++} END{print c+0}' "$LEDGER")
  CRITICAL=$(awk -F'|' '/^\| *[0-9]+ *\|/{
    sev=$4; gsub(/^[ \t]+|[ \t]+$/,"",sev)
    if (sev=="Critical") c++
  } END{print c+0}' "$LEDGER")
  echo "escalated ${TOTAL}件（うち Critical ${CRITICAL}件）"
fi
```

## 記帳の追記例

```
| 4 | QA-H-02 | Critical | ボタン押下後に決済が二重送信される | ui-evaluator ラウンド1報告 | 実装修正後に再検証。他QA-IDの検証は継続 |
```
