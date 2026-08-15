# Orchestrated モード (qa-ui)

## 発動条件

ファイル存在（escalation ledger の有無等）からの推測では判定しない。呼び出し側（オーケストレータ）が「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示の伝達経路は `Task` 起動プロンプトでも、メインコンテキストで本 skill の手順を実行する直前の明示宣言でもよい（判定するのは宣言の有無であり伝達経路ではない）。指示が無い単独起動では本ファイルを参照せず、SKILL.md 本文の現行動作（該当時は停止してユーザーの返答を待つ）のまま進む。

## escalation ledger 形式

ファイル名: `<プラン名>.escalation-ledger.md`（プランファイルと同じディレクトリに置く）。追記のみ（既存行は書き換えない）。記帳前に QA ledger の最新 `## QA source <digest>` を読み、escalation ledger の最新見出しと異なれば同じ見出しと表 header を追記する。同じなら現行節を継続する。これにより旧 generation の保留を現行 QA へ継承しない。

```markdown
## QA source <digest>

| 番号 | 出所 | 深刻度 (Critical/Major/Minor) | 内容 | 根拠 | 推奨アクション |
|---|---|---|---|---|---|
```

- 「番号」は記帳前に ledger を Read し、既存の最終番号 +1 から採番する (ファイルが無ければ 1 から)。
- 「出所」には QA-ID を書く（QA-G-NN もそのまま QA-ID として扱う）
- 「深刻度」は台帳の状態語彙のうち `FAIL(重大度)` の重大度、または `要人間確認`・ラウンド上限超過は判定材料から Critical/Major/Minor のいずれかに寄せて記入する（判定が付かない場合は安全側で Critical 扱いにする）

## qa-ui 固有の記帳規則

Orchestrated モード時、以下の状況は `SKILL.md` の「停止する」を「escalation ledger に記帳して続行する」に読み替える。該当 QA-ID は qa-ledger 側で `要人間確認`（審判再実行由来の Critical は `FAIL(Critical)`）のまま保留し、以後の検証・修正対象から除外する。他の QA-ID は継続する。

1. **Critical FAIL**
2. **ラウンド上限超過**（狭い追加ラウンド条件を満たさない）
3. **要人間確認**（Gotchas テーブル未カタログの検証不能）

`検証不能(真の制約)` は元々非ブロッキングであり、Orchestrated モードの有無に関わらず記帳のうえループを継続する（SKILL.md 本文どおり、上記 3 状況とは別扱い）。

**初回の手動 QA 依頼は記帳対象外**: 通常実行は人間の回答を待つ。委譲実行は手順書を返して終了し、呼び出し元が回答を得た後に台帳から再開する。

auto 判定の再実行は、escalation ledger へ記帳済みの保留 QA-ID を除いた残り全項目が修正ループを抜けた時点で行う。

## 完了判定への反映

完了判定の表示に、escalation ledger の集計結果を追記する: 「escalated N 件（うち Critical M 件）」。**Critical が 1 件でも含まれる場合、判定は「完了」を名乗らず「部分完了」を上限とする**（Critical 項目が保留のままである限り、機械集計が exit 0 を返しても「完了」表示はしない）。

**検証済み Bash**（現行 QA source 節だけを集計し、表では $4=深刻度）:

```bash
LEDGER="<plan>.escalation-ledger.md"
QA_LEDGER="<plan>.qa-ledger.md"
RUN_DIR=$(mktemp -d) || { echo "⚠️ 一時ディレクトリを作成できません。" >&2; exit 2; }
cleanup() { [ -d "$RUN_DIR" ] && rm -r -- "$RUN_DIR"; }
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
CURRENT_ESCALATION="$RUN_DIR/current_escalation.md"

CURRENT_SOURCE=$(awk '/^## QA source [0-9a-f]+$/ { line=$0 } END { print line }' "$QA_LEDGER" 2>/dev/null)
if [ -z "$CURRENT_SOURCE" ]; then
  echo "⚠️ current QA source generation がありません。" >&2; exit 2
fi
SOURCE_LINE=$(grep -nFx "$CURRENT_SOURCE" "$LEDGER" 2>/dev/null | tail -1 | cut -d: -f1)
if [ -z "$SOURCE_LINE" ]; then
  echo "escalated 0件"
else
  tail -n "+$SOURCE_LINE" "$LEDGER" | awk 'NR > 1 && /^## QA source [0-9a-f]+$/ { exit } { print }' > "$CURRENT_ESCALATION"
  TOTAL=$(awk -F'|' '/^\| *[0-9]+ *\|/{c++} END{print c+0}' "$CURRENT_ESCALATION")
  CRITICAL=$(awk -F'|' '/^\| *[0-9]+ *\|/{
    sev=$4; gsub(/^[ \t]+|[ \t]+$/,"",sev)
    if (sev=="Critical") c++
  } END{print c+0}' "$CURRENT_ESCALATION")
  echo "escalated ${TOTAL}件（うち Critical ${CRITICAL}件）"
fi
```

## 記帳の追記例

```
## QA source 0123456789abcdef

| 番号 | 出所 | 深刻度 (Critical/Major/Minor) | 内容 | 根拠 | 推奨アクション |
|---|---|---|---|---|---|
| 4 | QA-H-02 | Critical | ボタン押下後に決済が二重送信される | ui-evaluator ラウンド1報告 | 実装修正後に再検証。他QA-IDの検証は継続 |
```
