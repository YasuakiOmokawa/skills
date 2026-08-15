# Source coverage gate

`## 実装準備` の Write 後、プラン自体へ実行する。Step 2 の `RUN_DIR` を使う。

```bash
ANALYSIS_FILE="<plan>.analysis.md"
PLAN_FILE="<plan>.md"   # Step 4 で Write 済みの実ファイル
test -n "$RUN_DIR" || exit 2

if [ ! -s "$ANALYSIS_FILE" ] || ! grep -q '^## 正本抽出結果' "$ANALYSIS_FILE"; then
  echo "正本カバレッジ: skip (構造化正本なし、または分析ファイル空)"
  exit 0
fi
if [ ! -s "$PLAN_FILE" ]; then
  echo "⚠️ プランファイルが空/不存在: $PLAN_FILE — Step4 の Write を先に実行してください。" >&2
  exit 2
fi

# 要対応 atom は1列目だけから取る。
awk -F'|' '/^\|/ && ($0 ~ /差分/ || $0 ~ /未実装/) {
  id = $2; gsub(/^[ \t]+|[ \t]+$/, "", id)
  if (id ~ /^[A-Z]+-[0-9]+$/) print id
}' "$ANALYSIS_FILE" | sort -u > "$RUN_DIR/atoms_required.txt"

# manual / auto の引用 atom
grep -oE '出典: *[A-Z]+-[0-9]+' "$PLAN_FILE" | grep -oE '[A-Z]+-[0-9]+' > "$RUN_DIR/cited_manual.txt" || true
grep -oE '^\| *QA-[A-Z]+-[0-9]+ *\| *[A-Z]+-[0-9]+' "$PLAN_FILE" | grep -oE '[A-Z]+-[0-9]+ *$' > "$RUN_DIR/cited_auto.txt" || true
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
