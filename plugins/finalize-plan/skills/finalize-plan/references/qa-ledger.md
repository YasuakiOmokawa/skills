# QA ledger contract

プランと同じディレクトリで拡張子前へ `.qa-ledger` を挿入する。append-only。Step 5 後の ordered `(QA-ID, 手段, exact source)` を SHA-256 fingerprint にし、プランへ `<!-- QA source: <digest> -->`、ledger へ generation 見出しを記録する。`QA-G` は同 generation に追記し、この fingerprint を変えない。最新 generation 内だけが現行で、同じ `(QA-ID, 手段)` は最後の行が現在値。

```markdown
## QA source 0123456789abcdef...

| QA-ID | 手段 | 状態 | ラウンド | 備考 |
|---|---|---|---|---|
| QA-H-01 | manual | pending | 0 | - |
| QA-E-01 | auto | pending | - | - |
| QA-X-01 | - | 要人間確認 | - | 担当手段未特定 |
```

fingerprint が前 generation と異なるか既存 ledger に generation が無ければ、新しい見出しと全 current assignments の初期行を追記する。これにより、並べ替えや本文変更で同じ序数 QA-ID が再利用されても旧 PASS を継承しない。同じ fingerprint なら履歴を継続し、新規 `(QA-ID, 手段)` だけ初期化する。

状態語彙は `pending`、`PASS`、`FAIL(<重大度orexit>)`、`検証不能(真の制約)`、`要人間確認`、`対象外(N/A)` のみ。完了を許すのは `PASS` / `検証不能(真の制約)` / 理由付き `対象外(N/A)`。

割当は auto matrix → manual 見出し → orphan の優先順。dual coverage は auto のみ。manual の初期 round は `0`、それ以外は `-`。
lite は auto 割当0件を有効とし、全 ID を manual または orphan に割り当てる。

```bash
test -n "$RUN_DIR" || exit 2
ENUMERATED_IDS="$RUN_DIR/enumerated_qa_ids.txt"
PLAN_FILE="<plan>.md"
test -s "$ENUMERATED_IDS" && test -s "$PLAN_FILE" || exit 2
PLAN_QA="$RUN_DIR/ledger_plan_implementation_ready.txt"
awk '
  /^## 実装準備[[:space:]]*$/ { active = 1 }
  active && seen && /^## / { exit }
  active { print; seen = 1 }
' "$PLAN_FILE" > "$PLAN_QA"
awk -F'|' '
  /^#### QA-ID カバレッジマトリクス[[:space:]]*$/ { matrix=1; next }
  matrix && /^#{1,4} / { matrix=0 }
  matrix && /^\| *QA-[A-Z]+-[0-9]+ *\|/ { id=$2; gsub(/^[ \t]+|[ \t]+$/,"",id); print id }
' "$PLAN_QA" | sort -u > "$RUN_DIR/auto_qa_ids.txt"
grep -E '^\*\*QA-[A-Z]+-[0-9]+[[:space:]]+\|[[:space:]]+出典:.*\*\*$' "$PLAN_QA" | grep -oE '^\*\*QA-[A-Z]+-[0-9]+' | tr -d '*' | sort -u > "$RUN_DIR/manual_qa_ids_all.txt"
cat "$ENUMERATED_IDS" "$RUN_DIR/auto_qa_ids.txt" "$RUN_DIR/manual_qa_ids_all.txt" | sort -u > "$RUN_DIR/all_qa_ids.txt"
ALL_IDS="$RUN_DIR/all_qa_ids.txt"
comm -12 "$RUN_DIR/all_qa_ids.txt" "$RUN_DIR/auto_qa_ids.txt" > "$RUN_DIR/assign_auto.txt"
comm -23 "$RUN_DIR/manual_qa_ids_all.txt" "$RUN_DIR/auto_qa_ids.txt" | comm -12 "$RUN_DIR/all_qa_ids.txt" - > "$RUN_DIR/assign_manual.txt"
cat "$RUN_DIR/assign_auto.txt" "$RUN_DIR/assign_manual.txt" | sort -u > "$RUN_DIR/assigned.txt"
comm -23 "$RUN_DIR/all_qa_ids.txt" "$RUN_DIR/assigned.txt" > "$RUN_DIR/assign_orphan.txt"
```
