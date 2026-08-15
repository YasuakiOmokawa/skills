# Source coverage gate

`## 実装準備` の Write 後、プラン自体へ実行する。Step 2 の `RUN_DIR` を使う。

```bash
ANALYSIS_FILE="<plan>.analysis.md"
PLAN_FILE="<plan>.md"   # Step 4 で Write 済みの実ファイル
test -n "$RUN_DIR" || exit 2

if [ ! -s "$ANALYSIS_FILE" ] || ! grep -Eq '^## 正本抽出結果[[:space:]]*$' "$ANALYSIS_FILE"; then
  echo "正本カバレッジ: skip (構造化正本なし、または分析ファイル空)"
  exit 0
fi
if [ ! -s "$PLAN_FILE" ]; then
  echo "⚠️ プランファイルが空/不存在: $PLAN_FILE — Step4 の Write を先に実行してください。" >&2
  exit 2
fi

# `## 正本抽出結果` の必須 header を解決し、canonical 状態の要対応 atom を取る。
ATOMS_RAW="$RUN_DIR/atoms_required_raw.txt"
if ! awk '
  /^## 正本抽出結果[[:space:]]*$/ { in_source = 1; next }
  in_source && /^## / { in_source = 0 }
  in_source && /^\|/ {
    row = $0; gsub(/\\[|]/, "\034", row); count = split(row, cell, "|")
    if (!header_seen) {
      for (i = 1; i <= count; i++) {
        header = cell[i]
        gsub(/^[ \t]+|[ \t]+$/, "", header)
        if (tolower(header) == "atom id") id_col = i
        if (header == "期待値") expectation_col = i
        if (header == "状態") state_col = i
      }
      header_seen = 1
      if (!id_col || !expectation_col || !state_col) exit 3
      next
    }
    id = cell[id_col]; state = cell[state_col]
    gsub(/^[ \t]+|[ \t]+$/, "", id)
    gsub(/^[ \t]+|[ \t]+$/, "", state)
    if (id ~ /^:?-+:?$/) next
    if (id !~ /^FIG-[0-9]+$/ || state !~ /^(一致|差分|未実装)([ (]|$)/) exit 3
    if (id ~ /^FIG-[0-9]+$/ && state ~ /^(差分|未実装)([ (]|$)/) print id
  }
  END { if (!header_seen || !id_col || !expectation_col || !state_col) exit 3 }
' "$ANALYSIS_FILE" > "$ATOMS_RAW"; then
  rm -f -- "$ATOMS_RAW"
  echo "⚠️ 正本抽出結果の構造が不正です (必須 header: atom ID / 期待値 / 状態、状態: 一致 / 差分 / 未実装)。" >&2
  exit 2
fi
sort -u "$ATOMS_RAW" > "$RUN_DIR/atoms_required.txt"
rm -f -- "$ATOMS_RAW"

# manual QA 見出しと auto coverage matrix の出典だけを数える。
awk '
  /^## 実装準備[[:space:]]*$/ { in_ready = 1; next }
  in_ready && /^## / { exit }
  in_ready { print }
' "$PLAN_FILE" > "$RUN_DIR/implementation_ready.txt"
awk '
  /^\*\*QA-[A-Z]+-[0-9]+[[:space:]]+\|[[:space:]]+出典:.*\*\*$/ {
    in_qa = 1
    if ($0 ~ /出典:[[:space:]]*FIG-[0-9]+[[:space:]]*\*\*$/) { line=$0; sub(/^.*出典:[[:space:]]*/, "", line); sub(/[[:space:]]*\*\*$/, "", line); print line }
    next
  }
  /^### / { in_qa = 0 }
  in_qa && /^\*\*正本出典:[[:space:]]*FIG-[0-9]+[[:space:]]*\*\*$/ {
    line=$0; sub(/^\*\*正本出典:[[:space:]]*/, "", line); sub(/[[:space:]]*\*\*$/, "", line); print line
  }
' "$RUN_DIR/implementation_ready.txt" > "$RUN_DIR/cited_manual.txt"
awk -F'|' '
  /^#### QA-ID カバレッジマトリクス[[:space:]]*$/ { in_matrix = 1; next }
  in_matrix && /^#{1,4} / { in_matrix = 0 }
  in_matrix && /^\| *QA-[A-Z]+-[0-9]+ *\|/ {
    source = $3; gsub(/^[ \t]+|[ \t]+$/, "", source)
    if (source ~ /^FIG-[0-9]+$/) print source
  }
' "$RUN_DIR/implementation_ready.txt" > "$RUN_DIR/cited_auto.txt"
cat "$RUN_DIR/cited_manual.txt" "$RUN_DIR/cited_auto.txt" | sort -u > "$RUN_DIR/atoms_cited.txt"

# 真の集合差分
comm -23 "$RUN_DIR/atoms_required.txt" "$RUN_DIR/atoms_cited.txt" > "$RUN_DIR/atoms_uncovered.txt"
if [ -s "$RUN_DIR/atoms_uncovered.txt" ]; then
  echo "正本カバレッジ: 未カバー $(wc -l < "$RUN_DIR/atoms_uncovered.txt") 件"
  cat "$RUN_DIR/atoms_uncovered.txt"
  exit 1
else
  echo "正本カバレッジ: 差分 0 件 (要対応 $(wc -l < "$RUN_DIR/atoms_required.txt") 件 / 引用 $(wc -l < "$RUN_DIR/atoms_cited.txt") 件)"
  exit 0
fi
```
