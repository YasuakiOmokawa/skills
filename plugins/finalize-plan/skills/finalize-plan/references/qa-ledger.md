# QA ledger contract

プランと同じディレクトリで拡張子前へ `.qa-ledger` を挿入する。append-only。同じ `(QA-ID, 手段)` は最後の行が現在値。

```markdown
| QA-ID | 手段 | 状態 | ラウンド | 備考 |
|---|---|---|---|---|
| QA-H-01 | manual | pending | 0 | - |
| QA-E-01 | auto | pending | - | - |
| QA-X-01 | - | 要人間確認 | - | 担当手段未特定 |
```

状態語彙は `pending`、`PASS`、`FAIL(<重大度orexit>)`、`検証不能(真の制約)`、`要人間確認`、`対象外(N/A)` のみ。完了を許すのは `PASS` / `検証不能(真の制約)` / 理由付き `対象外(N/A)`。

割当は auto matrix → manual 見出し → orphan の優先順。dual coverage は auto のみ。manual の初期 round は `0`、それ以外は `-`。
lite は auto 割当0件を有効とし、全 ID を manual または orphan に割り当てる。

```bash
test -n "$RUN_DIR" || exit 2
ENUMERATED_IDS="$RUN_DIR/enumerated_qa_ids.txt"
PLAN_FILE="<plan>.md"
test -s "$ENUMERATED_IDS" && test -s "$PLAN_FILE" || exit 2
awk -F'|' '/^\| *QA-[A-Z]+-[0-9]+ *\|/{id=$2;gsub(/^[ \t]+|[ \t]+$/,"",id);print id}' "$PLAN_FILE" | sort -u > "$RUN_DIR/auto_qa_ids.txt"
grep -oE '^\*\*QA-[A-Z]+-[0-9]+' "$PLAN_FILE" | tr -d '*' | sort -u > "$RUN_DIR/manual_qa_ids_all.txt"
cat "$ENUMERATED_IDS" "$RUN_DIR/auto_qa_ids.txt" "$RUN_DIR/manual_qa_ids_all.txt" | sort -u > "$RUN_DIR/all_qa_ids.txt"
ALL_IDS="$RUN_DIR/all_qa_ids.txt"
comm -12 "$RUN_DIR/all_qa_ids.txt" "$RUN_DIR/auto_qa_ids.txt" > "$RUN_DIR/assign_auto.txt"
comm -23 "$RUN_DIR/manual_qa_ids_all.txt" "$RUN_DIR/auto_qa_ids.txt" | comm -12 "$RUN_DIR/all_qa_ids.txt" - > "$RUN_DIR/assign_manual.txt"
cat "$RUN_DIR/assign_auto.txt" "$RUN_DIR/assign_manual.txt" | sort -u > "$RUN_DIR/assigned.txt"
comm -23 "$RUN_DIR/all_qa_ids.txt" "$RUN_DIR/assigned.txt" > "$RUN_DIR/assign_orphan.txt"
```
