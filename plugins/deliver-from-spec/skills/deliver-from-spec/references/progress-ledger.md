# `<PRD>.progress-ledger.md` 契約

## 置き場・命名

仕様文書 (PRD) と同ディレクトリ、拡張子前に `.progress-ledger` を挿入する (例: `add-role-field.md` → `add-role-field.progress-ledger.md`)。

## 目的

PRD を要求単位に分解し、各要求がどのスライス/プランでどこまで進んだかを 1 台帳に集約する。実装漏れ (PRD/AC にあるのに実装されていない要求) を PRD 全体の粒度で機械検出できるようにする (適応度関数の主指標「欠陥率」のうち実装漏れクラスへの対応、利用者決定 2026-07-06 の決定 1)。

## 形式

追記型。既存の qa-ledger / orchestration-status.md と同じ「1 行 1 件・最新行が勝つ」規約を流用する (新しい記法は作らない)。

```markdown
| 要求ID (PRD節番号) | 要求の要旨 | スライス/プラン | 状態 (未着手/計画中/実装中/QA中/完了/対象外) | 記録時刻 |
|---|---|---|---|---|
```

- 「要求ID (PRD節番号)」は PRD の節/項番号をそのまま使う (例: `3.2`, `4-a`)。PRD 側に番号が無い場合は起票時に見出し順で採番し、以後プラン側にも同じ ID で書き戻す
- 「状態」は 6 値の閉じた集合のみを使う: `未着手` (初期値) / `計画中` / `実装中` / `QA中` / `完了` / `対象外` (PRD には書かれているが今回スコープ外と明示合意された要求)
- 同一「要求ID」に複数行が追記された場合、最新行 (ファイル内で最後に出現する行) が現在状態を表す。既存行は書き換えない

## Phase 0: 起票

Phase 0 ([references/preflight.md](preflight.md) の「PRD 分解と進捗台帳の起票」節) で、仕様文書を `Read` して要求単位を列挙し、PRD 全体について台帳へ 1 行ずつ起票する。今回の対象スライス以外も含めて全件起票する (全件起票しないと後述の実装漏れゲートが PRD 全体を見たことにならない)。今回の対象スライスに含まれない要求は `未着手` のまま残す。

## Phase 4: 完了時の追記

該当スライスの実装が Phase 4 (出荷ゲート pass) に達した時点で、そのスライスに対応する要求 ID の行を `完了` として追記する。

**単一スライス完了時の挙動**: 当該スライスに含まれない要求 (他スライスや将来対応分) が未完了のままでも、このタイミングでは停止しない。残要求を一覧表示するだけに留める (下記の実装漏れゲートとは目的が異なる — 単一スライスの Phase 4 は「このスライスが完了したか」だけを見る):

```bash
LEDGER="<PRD>.progress-ledger.md"
if [ -s "$LEDGER" ]; then
  awk -F'|' '
    /^\|/ {
      if ($0 ~ /^\|---/ || $0 ~ /要求ID/) next
      id=$2; gsub(/^[ \t]+|[ \t]+$/,"",id)
      state=$5; gsub(/^[ \t]+|[ \t]+$/,"",state)
      if (id != "") row[id]=state
    }
    END { for (id in row) if (row[id]!="完了" && row[id]!="対象外") print id": "row[id] }
  ' "$LEDGER"
fi
```

## 実装漏れゲート (PRD 全体の完了判定、検証済み Bash)

単一スライスの Phase 4 とは別に、「PRD 全体を完了と呼べるか」を判定したいときに実行する。全要求行が終端状態 (`完了` または `対象外`) に達しているかを集計し、未完了の要求 ID を列挙する。このゲートは deliver-from-spec の Phase 0〜4 の自動遷移には組み込まない (1 回の deliver-from-spec 実行は 1 スライスが対象のため) — 複数スライスにまたがる PRD 全体の完了を確認したいタイミングで人間・オーケストレータが明示的に実行する。

**検証済み Bash**（scratchpad fixture 3 種 — 全件終端状態・未完了行が残る・台帳未生成 — で pass/fail/fail の判定を確認済み。「最新行が勝つ」規約どおり、同一要求IDの古い行 (例: `計画中`) が新しい行 (`完了`) に正しく上書きされることも確認済み）:

```bash
LEDGER="<PRD>.progress-ledger.md"

if [ ! -s "$LEDGER" ]; then
  echo "progress-ledger 未生成 → PRD 全体の完了は判定できない"
  exit 1
fi

UNRESOLVED=$(awk -F'|' '
  /^\|/ {
    if ($0 ~ /^\|---/ || $0 ~ /要求ID/) next
    id=$2; gsub(/^[ \t]+|[ \t]+$/,"",id)
    state=$5; gsub(/^[ \t]+|[ \t]+$/,"",state)
    if (id != "") row[id]=state
  }
  END { for (id in row) if (row[id]!="完了" && row[id]!="対象外") print id }
' "$LEDGER")

if [ -n "$UNRESOLVED" ]; then
  echo "PRD 全体は未完了。以下の要求が未完了のまま:"
  echo "$UNRESOLVED"
  exit 1
else
  echo "PRD 全体の全要求が 完了/対象外 → 完了と判定してよい"
  exit 0
fi
```
