# 台帳・ゲートの検証済み Bash (qa-ui)

QA 実行台帳の初期化 (Step 3.5)・auto 判定の再実行ゲート (Step 5.5)・完了判定 (Step 6) の検証済み Bash ブロックと、それぞれの注意点を集約する。いずれも台帳がある場合のみ実施する（フォールバック時・AC無しモードは skip）。実施条件・判定ロジック・出力書式は SKILL.md 本文が正で、本ファイルはそのまま実行する Bash を保持する。

## Contents

- [Step 3.5: 台帳初期化](#step-35-台帳初期化)
- [Step 5.5: auto 判定の再実行ゲート](#step-55-auto-判定の再実行ゲート)
- [Step 6: 完了判定](#step-6-完了判定)

## Step 3.5: 台帳初期化

台帳が存在しない場合、Step 3 で読み込んだ QA-ID から初期化する。**検証済み Bash**（担当手段の割当順は finalize-plan 側 references/qa-ledger.md の手段割当規則と同一の auto優先・dual coverageはautoが正。プランファイル自身から拾える QA-ID の集合に限定するフォールバックのため、finalize-plan Step4 が別途保持する enumerate 済み全 QA-ID とは突き合わせず、孤児 QA-ID の `対象外(N/A)` 検出は行わない）:

```bash
LEDGER="<plan>.qa-ledger.md"
PLAN_FILE="<plan>.md"

if [ -s "$LEDGER" ]; then
  echo "台帳: 既存を使用 ($LEDGER)"
else
  awk -F'|' '/^\| *QA-[A-Z]+-[0-9]+ *\|/{id=$2;gsub(/^[ \t]+|[ \t]+$/,"",id);print id}' "$PLAN_FILE" | sort -u > /tmp/qaui_auto_ids.txt
  grep -oE '^\*\*QA-[A-Z]+-[0-9]+' "$PLAN_FILE" | tr -d '*' | sort -u > /tmp/qaui_manual_ids_all.txt
  comm -23 /tmp/qaui_manual_ids_all.txt /tmp/qaui_auto_ids.txt > /tmp/qaui_manual_only.txt  # dual coverage は auto が正、manual 行は作らない

  {
    echo "| QA-ID   | 手段   | 状態    | ラウンド | 備考 |"
    echo "|---------|--------|---------|----------|------|"
    while read -r id; do [ -n "$id" ] && echo "| $id | auto   | pending | -        | - |"; done < /tmp/qaui_auto_ids.txt
    while read -r id; do [ -n "$id" ] && echo "| $id | manual | pending | 0        | - |"; done < /tmp/qaui_manual_only.txt
  } > "$LEDGER"
fi
```

## Step 5.5: auto 判定の再実行ゲート

**マトリクス列レイアウト (canonical)**: 列は `| QA-ID | 手段 | 出典 | AC | 環境 | 実行コマンド |` の **6 列固定** で、下記 awk は列位置 (`$2 = QA-ID`, `$7 = 実行コマンド`) を決め打ちで参照する (`|` で区切ると先頭にダミー欄が入り実質列は `$2` から始まる)。列を追加・並べ替える場合は `実行コマンド` を最終列 = `$7` の位置に保つこと。列位置がずれると審判は `実行コマンド未定義` と誤検出し全 auto 行が `要人間確認` に落ちる (finalize-plan Step 3 の自動 QA planner が出力するマトリクスは既定でこの列順)。**検証済み Bash**:

```bash
LEDGER="<plan>.qa-ledger.md"; PLAN_FILE="<plan>.md"

if [ ! -s "$LEDGER" ] || [ ! -s "$PLAN_FILE" ]; then
  echo "⚠️ 入力が空/不存在: LEDGER=$LEDGER PLAN_FILE=$PLAN_FILE — 再実行ゲートを実行不可。" >&2
  exit 2
fi

awk -F'|' '/^\|/ && $2 !~ /QA-ID/ && $2 !~ /^[ \t]*-+[ \t]*$/{
  id=$2;gsub(/^[ \t]+|[ \t]+$/,"",id); m=$3;gsub(/^[ \t]+|[ \t]+$/,"",m)
  if (m=="auto") print id
}' "$LEDGER" | sort -u > /tmp/auto_ids_in_ledger.txt

if [ ! -s /tmp/auto_ids_in_ledger.txt ]; then
  echo "再実行ゲート: auto 行なし (skip)"; exit 0
fi

while read -r id; do
  [ -z "$id" ] && continue
  CMD=$(awk -F'|' -v t="$id" '/^\| *QA-[A-Z]+-[0-9]+ *\|/{i=$2;gsub(/^[ \t]+|[ \t]+$/,"",i); if(i==t){c=$7;gsub(/^[ \t]+|[ \t]+$/,"",c);print c}}' "$PLAN_FILE")
  if [ -z "$CMD" ]; then
    echo "| $id | auto | 要人間確認 | -        | 実行コマンド未定義 (QA-IDカバレッジマトリクスに該当行なし) |" >> "$LEDGER"
    continue
  fi
  CMD_CLEAN=$(echo "$CMD" | sed -e 's/^`//' -e 's/`$//')
  if bash -c "$CMD_CLEAN" </dev/null >/tmp/reexec_out_"$id".log 2>&1; then EXIT=0; else EXIT=$?; fi
  # rspec は -e 不一致でも exit 0 を返すことがある (実機確認済み)。出力を見て0件実行を検出する。
  if grep -qE '(^|[^0-9])0 examples|No test files found|no tests' /tmp/reexec_out_"$id".log; then
    STATE="要人間確認"; NOTE="テスト0件を検出 (exit=$EXIT、コマンド不一致の疑い) $(date -Iseconds)"
  elif [ "$EXIT" -eq 0 ]; then
    STATE="PASS"; NOTE="審判再実行 $(date -Iseconds) exit=$EXIT"
  else
    STATE="FAIL(exit=$EXIT)"; NOTE="審判再実行 $(date -Iseconds) exit=$EXIT"
  fi
  echo "| $id | auto | $STATE | -        | $NOTE |" >> "$LEDGER"
done < /tmp/auto_ids_in_ledger.txt
```

**注意点**:
- 実行出力に `0 examples`（RSpec）/ `No test files found`・`no tests`（Vitest）のいずれかを検出したら、exit 0 でも `PASS` にはせず `要人間確認` を記帳する（コマンドの `-e`/`-t` 指定が QA-ID と一致していない疑いのため）
- `bash -c` への `</dev/null` は削らない（理由: docker/dip 等 stdin を消費するコマンドが while ループの ID リストを飲み込み、2 件目以降を実行しないまま正常終了する — 実測で 23 件中 1 件だけ実行されるループ早期終了が発生した）。テストコマンドを環境に合わせて読み替える場合もこの構造は維持する
- 0 件検出の正規表現は `(^|[^0-9])0 examples` の形を維持する（理由: `0 examples` 単体は「10 examples」「20 examples」にも部分一致し、正常 pass を `要人間確認` へ誤判定する — 10 examples 全 pass の QA-ID が誤判定された実測あり）
- プランファイルの QA-ID カバレッジマトリクスにコマンドが定義されていない QA-ID は `要人間確認` を記帳する
- `CMD_CLEAN` はプランファイルのバッククォート除去のみで、シェルメタ文字のエスケープ処理は行わない。`bash -c` にそのまま渡すため、プランファイルの実行コマンド列に不正な文字列が書かれていると意図しないコマンドが実行されるリスクがある（プランファイルは信頼できる入力という前提で運用する）

## Step 6: 完了判定

台帳の最新行（同一 QA-ID・手段は最後の行）を集計し、全行が終端状態（`PASS` / `検証不能(真の制約)` / `対象外(N/A)`）かどうかで判定する。**検証済み Bash**:

```bash
LEDGER="<plan>.qa-ledger.md"
if [ ! -s "$LEDGER" ]; then
  echo "⚠️ 台帳が空/不存在: $LEDGER — 完了判定を実行不可。台帳初期化を先に実行してください。" >&2
  exit 2
fi

awk -F'|' '
  /^\|/ && $2 !~ /QA-ID/ && $2 !~ /^[ \t]*-+[ \t]*$/ {
    id = $2; gsub(/^[ \t]+|[ \t]+$/, "", id)
    method = $3; gsub(/^[ \t]+|[ \t]+$/, "", method)
    key = id "::" method
    row[key] = $0
  }
  END { for (k in row) print row[k] }
' "$LEDGER" | sort > /tmp/ledger_latest.txt

grep -vE '\| *(PASS|検証不能\(真の制約\)|対象外\(N/A\)) *\|' /tmp/ledger_latest.txt > /tmp/ledger_incomplete.txt || true

if [ -s /tmp/ledger_incomplete.txt ]; then
  echo "## UI QA 部分完了 (人間確認事項あり) または未完了"
  cat /tmp/ledger_incomplete.txt
  exit 1
fi

# 全行が終端状態でも、検証不能(真の制約) が1件でも残る場合は人間の目が必要なため「完了」と呼ばない。
grep -E '\| *検証不能\(真の制約\) *\|' /tmp/ledger_latest.txt > /tmp/ledger_unverifiable.txt || true
if [ -s /tmp/ledger_unverifiable.txt ]; then
  echo "## UI QA 部分完了 (人間確認事項あり)"
  cat /tmp/ledger_unverifiable.txt
  exit 0
else
  echo "## UI QA 完了"
  exit 0
fi
```
