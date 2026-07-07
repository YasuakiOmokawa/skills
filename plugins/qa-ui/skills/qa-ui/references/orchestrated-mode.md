# Orchestrated モード (qa-ui)

## 発動条件

ファイル存在（escalation ledger の有無等）からの推測では判定しない。呼び出し側（オーケストレータ）が「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示の伝達経路は `Task` 起動プロンプトでも、メインコンテキストで本 skill の手順を実行する直前の明示宣言でもよい（判定するのは宣言の有無であり伝達経路ではない）。指示が無い単独起動では本ファイルを参照せず、SKILL.md 本文の現行動作（該当時は停止してユーザーの返答を待つ）のまま進む。

## escalation ledger 形式

ファイル名: `<プラン名>.escalation-ledger.md`（プランファイルと同じディレクトリに置く）。1 行 = 1 項目、追記のみ（既存行は書き換えない）。

| 番号 | 出所 | 深刻度 (Critical/Major/Minor) | 内容 | 根拠 | 推奨アクション |
|---|---|---|---|---|---|

- 「番号」は記帳前に ledger を Read し、既存の最終番号 +1 から採番する (ファイルが無ければ 1 から)。
- 「出所」には QA-ID を書く（QA-G-NN もそのまま QA-ID として扱う）
- 「深刻度」は台帳の状態語彙のうち `FAIL(重大度)` の重大度、または `要人間確認`・ラウンド上限超過は判定材料から Critical/Major/Minor のいずれかに寄せて記入する（判定が付かない場合は安全側で Critical 扱いにする）

## qa-ui 固有の記帳規則

Orchestrated モード時、以下の 3 つの状況は SKILL.md 本文の「停止する」を「escalation ledger に記帳して続行する」に読み替える。該当 QA-ID は qa-ledger 側で保留し (Step 5 由来は `要人間確認`、Step 6 の審判再実行由来は `FAIL(Critical)` のまま — 状態語彙は SKILL.md 本文を正とする)、以後のラウンドの検証対象・修正対象からは除外するが、**他の独立した QA-ID の検証・修正ループは止めない**（全項目の検証が終わるまで完了とは呼ばない）。

1. **Critical FAIL** — Step 5「Critical が1件でも含まれる → 即エスカレート」
2. **ラウンド上限超過**（cap 超過の狭い例外に該当しない）— Step 5「ラウンド3でもFAIL → エスカレート」
3. **要人間確認**（Gotchas テーブル未カタログの検証不能）— Step 5 の判定 2. および「検証不能が1件でも含まれる場合」

`検証不能(真の制約)` は元々非ブロッキングであり、Orchestrated モードの有無に関わらず記帳のうえループを継続する（SKILL.md 本文どおり、上記 3 状況とは別扱い）。

**人間委譲モードの QA 依頼（Step 4）は記帳対象外**: 人間委譲モード（既定）の Step 4 で実行手順書を提示し人間の回答を待つことは、上記の「停止する」を「記帳して続行する」に読み替える対象に含まれない。QA 実行を人間に委譲する設計（利用者決定3・4）であり、調整コスト由来の同期待ちではなく判断価値由来の工程だからである。Orchestrated モードであっても Step 4 の人間からの回答待ちはそのまま維持し、escalation ledger には記帳しない。委譲実行（subagent 起動）では「待つ」こと自体が構造的にできないため、SKILL.md の「## 委譲実行」節が定める分割実行契約（手順書を返して終了 → 呼び出し元が回答を得て台帳から再開）に従う。この往復は escalation ledger と無関係であり、記帳対象外の扱いを変えない。

Step 5.5 (auto 判定の再実行ゲート) の起動条件「Critical / 未解消エスカレートも無い状態」は、Orchestrated モード時は「escalation ledger へ記帳済みの保留 QA-ID を除いた残り全項目が修正ループを抜けた状態」と読み替える (保留 Critical があっても他項目の審判・完了集計を止めない)。

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
