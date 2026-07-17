# 正本カバレッジ・ゲートの検証済み Bash (Step 3.5)

SKILL.md の Step 3.5 (正本カバレッジ・ゲート) が `## 正本抽出結果` **ある場合**に実行する検証済み Bash (fixture で実行検証済み)。判定ロジック・出力文言・未カバー atom の追記手順は SKILL.md Step 3.5 が SSOT。本ファイルは Step 3 でプランファイルへ `## 実装準備` を Write した**後**に、プランファイル自体を対象に実行する。

```bash
ANALYSIS_FILE="<plan>.analysis.md"
PLAN_FILE="<plan>.md"   # Step 3 で Write 済みの実ファイル

if [ ! -s "$ANALYSIS_FILE" ] || ! grep -q '^## 正本抽出結果' "$ANALYSIS_FILE"; then
  echo "正本カバレッジ: skip (構造化正本なし、または分析ファイル空)"
  exit 0
fi
if [ ! -s "$PLAN_FILE" ]; then
  echo "⚠️ プランファイルが空/不存在: $PLAN_FILE — Step3 の Write を先に実行してください。" >&2
  exit 2
fi

# 1. 要対応 atom: テーブルの1列目 (atom ID列) のみ見る。期待値列に atom ID 風の文字列
#    (例 HTTP-404) が混ざっても誤って拾わないようにするため。
awk -F'|' '/^\|/ && ($0 ~ /差分/ || $0 ~ /未実装/) {
  id = $2; gsub(/^[ \t]+|[ \t]+$/, "", id)
  if (id ~ /^[A-Z]+-[0-9]+$/) print id
}' "$ANALYSIS_FILE" | sort -u > /tmp/atoms_required.txt

# 2. 引用 atom: manual形式 (太字見出し "出典: FIG-NN") + auto形式 (テーブル列)
grep -oE '出典: *[A-Z]+-[0-9]+' "$PLAN_FILE" | grep -oE '[A-Z]+-[0-9]+' > /tmp/cited_manual.txt || true
grep -oE '^\| *QA-[A-Z]+-[0-9]+ *\| *[A-Z]+-[0-9]+' "$PLAN_FILE" | grep -oE '[A-Z]+-[0-9]+ *$' > /tmp/cited_auto.txt || true
cat /tmp/cited_manual.txt /tmp/cited_auto.txt | sort -u > /tmp/atoms_cited.txt

# 3. 真のID集合差分
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
