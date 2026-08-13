# Source coverage gate

`## 実装準備` の Write 後、プラン自体へ実行する。固定 `/tmp` 作業名を使うため、同一環境では直列実行する。

```bash
ANALYSIS_FILE="<plan>.analysis.md"
PLAN_FILE="<plan>.md"   # Step 4 で Write 済みの実ファイル

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
}' "$ANALYSIS_FILE" | sort -u > /tmp/atoms_required.txt

# manual / auto の引用 atom
grep -oE '出典: *[A-Z]+-[0-9]+' "$PLAN_FILE" | grep -oE '[A-Z]+-[0-9]+' > /tmp/cited_manual.txt || true
grep -oE '^\| *QA-[A-Z]+-[0-9]+ *\| *[A-Z]+-[0-9]+' "$PLAN_FILE" | grep -oE '[A-Z]+-[0-9]+ *$' > /tmp/cited_auto.txt || true
cat /tmp/cited_manual.txt /tmp/cited_auto.txt | sort -u > /tmp/atoms_cited.txt

# 真の集合差分
comm -23 /tmp/atoms_required.txt /tmp/atoms_cited.txt > /tmp/atoms_uncovered.txt
if [ -s /tmp/atoms_uncovered.txt ]; then
  echo "正本カバレッジ: 未カバー $(wc -l < /tmp/atoms_uncovered.txt) 件"
  cat /tmp/atoms_uncovered.txt
  exit 1
else
  echo "正本カバレッジ: 差分 0 件 (要対応 $(wc -l < /tmp/atoms_required.txt) 件 / 引用 $(wc -l < /tmp/atoms_cited.txt) 件)"
  exit 0
fi
```
