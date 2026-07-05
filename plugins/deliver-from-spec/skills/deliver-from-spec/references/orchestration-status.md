# `<plan>.orchestration-status.md` 契約

## 置き場・命名

プランファイルと同ディレクトリ、拡張子前に `.orchestration-status` を挿入する (例: `feature-xxx.md` → `feature-xxx.orchestration-status.md`)。

## 形式

追記型 (QA-ID 台帳と同じ「最新行が勝つ」)。フェーズ列をキーとして、そのフェーズの最新行が現在状態を表す。

```markdown
| フェーズ | 状態 (running/done/blocked) | 再突入回数 | 成果物パス | 記録時刻 |
|---|---|---|---|---|
```

- フェーズ列は `0` / `1a` / `1b` / `1c` / `1d` / `2` / `2.5` / `3` / `4` の固定値を使う。Phase 2 は PR 単位の内訳を残すため、`2-PR1` / `2-PR2` のような枝番フェーズ名を追加で使ってよい (再開判定は固定 9 フェーズのみを見るため、枝番行は無視されて安全に共存する)
- 「再突入回数」は当該フェーズを最初に開始した時点を 0 とし、フェーズ全体をやり直すたびに 1 加算する
- 「成果物パス」は当該フェーズの完了条件が参照する成果物ファイルのパス、または実行中/停止中の場合は `-`
- オーケストレータは各 phase の開始時・完了時 (running → done、または running → blocked) に必ず 1 行追記する

## 追記の検証済み Bash

SKILL.md 本文「status ファイルへの追記」節を参照 (重複掲載しない)。

## 再開判定の検証済み Bash

再開時はこのファイルだけ読めば現在地が分かる。固定順のフェーズを走査し、`done` でない最初のフェーズを再開点とする。再開点が `blocked` かつ再突入回数が 1 以上 (= 再突入を既に使い切って再び失敗した) の場合、機械再開せず人間確認を要求する (thin 版の再突入上限は固定 1 回)。

**検証済み Bash**（scratchpad fixture で「正常遷移時に done でない最初のフェーズを返す」「再突入 1 回消費後に再度 blocked なら exit 1」の両方を確認済み）:

```bash
STATUS="<plan>.orchestration-status.md"
PHASES="0 1a 1b 1c 1d 2 2.5 3 4"

if [ ! -s "$STATUS" ]; then
  echo "status ファイル未初期化 → Phase 0 から開始"
  exit 0
fi

declare -A ST RE ART
while IFS='|' read -r _ phase state reentry artifact _; do
  phase=$(echo "$phase" | xargs)
  [ -z "$phase" ] && continue
  case "$phase" in フェーズ|---*) continue ;; esac
  ST["$phase"]=$(echo "$state" | xargs)
  RE["$phase"]=$(echo "$reentry" | xargs)
  ART["$phase"]=$(echo "$artifact" | xargs)
done < "$STATUS"

RESUME=""
for p in $PHASES; do
  state="${ST[$p]:-未着手}"
  if [ -z "$RESUME" ] && [ "$state" != "done" ]; then
    RESUME="$p"
  fi
done

if [ -z "$RESUME" ]; then
  echo "全フェーズ done → Phase 4 完了済み"
  exit 0
fi

echo "再開フェーズ: ${RESUME}"

if [ "${ST[$RESUME]}" = "blocked" ] && [ "${RE[$RESUME]:-0}" -ge 1 ]; then
  echo "再突入上限 (1回) 超過 → 機械再開せず人間確認を要求"
  exit 1
fi

exit 0
```

## ハンドオフ規則

フェーズ間のハンドオフは常にファイルパス (成果物パス列、および各成果物ファイル自身) で行う。要約して次フェーズに渡すことは禁止する (長寿命実行での compaction 後も、このファイルと各成果物ファイルを読めば復元できる状態を保つため)。
