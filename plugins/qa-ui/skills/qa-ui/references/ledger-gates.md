# 台帳・ゲートの検証済み Bash (qa-ui)

QA 実行台帳の初期化、auto 判定の再実行、完了集計に使う Bash を保持する。QA-ID instructions が無い source fallback では実行しない。plan の QA source marker が変わるたび新 generation を追記し、gate は最新 generation だけを読む。実施条件・判定・出力は `SKILL.md` が正とする。

## Contents

- [台帳初期化](#台帳初期化)
- [auto 判定の再実行ゲート](#auto-判定の再実行ゲート)
- [完了判定](#完了判定)

## 台帳初期化

毎回 plan の QA source marker と ledger の最新 generation を比較する。不在・不一致ならプランから読んだ QA-ID で新 generation を追記し、一致なら継続する。auto を優先し、dual coverage は auto のみを作る。この初期化ではプランから拾える QA-ID だけを扱い、孤児 QA-ID の `対象外(N/A)` 検出は行わない。

```bash
LEDGER="<plan>.qa-ledger.md"
PLAN_FILE="<plan>.md"
RUN_DIR=$(mktemp -d) || { echo "⚠️ 一時ディレクトリを作成できません。" >&2; exit 2; }
cleanup() { [ -d "$RUN_DIR" ] && rm -r -- "$RUN_DIR"; }
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

PLAN_QA="$RUN_DIR/plan_implementation_ready.md"
AUTO_IDS="$RUN_DIR/auto_ids.txt"
MANUAL_IDS="$RUN_DIR/manual_ids.txt"
MANUAL_ONLY="$RUN_DIR/manual_only.txt"
EXPECTED_PAIRS="$RUN_DIR/expected_pairs.tsv"
CURRENT_SECTION="$RUN_DIR/current_section.md"
CURRENT_PAIRS="$RUN_DIR/current_pairs.tsv"
MISSING_PAIRS="$RUN_DIR/missing_pairs.tsv"
awk '
  /^## 実装準備[[:space:]]*$/ { active = 1 }
  active && seen && /^## / { exit }
  active { print; seen = 1 }
' "$PLAN_FILE" > "$PLAN_QA"
if [ ! -s "$PLAN_QA" ]; then
  echo "⚠️ ## 実装準備 が空/不存在: $PLAN_FILE" >&2; exit 2
fi
SOURCE_DIGEST=$(sed -nE 's/^<!-- QA source: ([0-9a-f]+) -->$/\1/p' "$PLAN_QA" | tail -1)
if [ -z "$SOURCE_DIGEST" ]; then
  if command -v sha256sum >/dev/null 2>&1; then SOURCE_DIGEST=$(sha256sum "$PLAN_QA" | awk '{print $1}')
  elif command -v shasum >/dev/null 2>&1; then SOURCE_DIGEST=$(shasum -a 256 "$PLAN_QA" | awk '{print $1}')
  else echo "⚠️ QA source marker and SHA-256 command unavailable" >&2; exit 2; fi
fi
CURRENT_SOURCE="## QA source $SOURCE_DIGEST"
LAST_SOURCE=$(awk '/^## QA source [0-9a-f]+$/ { line=$0 } END { print line }' "$LEDGER" 2>/dev/null)

awk -F'|' '
  /^#### QA-ID カバレッジマトリクス[[:space:]]*$/ { matrix=1; next }
  matrix && /^#{1,4} / { matrix=0 }
  matrix && /^\| *QA-[A-Z]+-[0-9]+ *\|/ { id=$2; gsub(/^[ \t]+|[ \t]+$/,"",id); print id }
' "$PLAN_QA" | sort -u > "$AUTO_IDS"
grep -E '^\*\*QA-[A-Z]+-[0-9]+[[:space:]]+\|[[:space:]]+出典:.*\*\*$' "$PLAN_QA" | grep -oE '^\*\*QA-[A-Z]+-[0-9]+' | tr -d '*' | sort -u > "$MANUAL_IDS"
comm -23 "$MANUAL_IDS" "$AUTO_IDS" > "$MANUAL_ONLY"  # dual coverage は auto が正、manual 行は作らない
{
  awk '{print $0 "\tauto"}' "$AUTO_IDS"
  awk '{print $0 "\tmanual"}' "$MANUAL_ONLY"
} | sort -u > "$EXPECTED_PAIRS"
if [ ! -s "$EXPECTED_PAIRS" ]; then
  echo "⚠️ 現行 QA source に割当可能な QA-ID がありません。" >&2; exit 2
fi

if [ "$LAST_SOURCE" = "$CURRENT_SOURCE" ]; then
  SOURCE_LINE=$(grep -nFx "$CURRENT_SOURCE" "$LEDGER" | tail -1 | cut -d: -f1)
  tail -n "+$SOURCE_LINE" "$LEDGER" > "$CURRENT_SECTION"
  awk -F'|' '/^\| *QA-[A-Z]+-[0-9]+ *\|/ {
    id=$2; method=$3
    gsub(/^[ \t]+|[ \t]+$/, "", id); gsub(/^[ \t]+|[ \t]+$/, "", method)
    if (method=="auto" || method=="manual") print id "\t" method
  }' "$CURRENT_SECTION" | sort -u > "$CURRENT_PAIRS"
  comm -23 "$EXPECTED_PAIRS" "$CURRENT_PAIRS" > "$MISSING_PAIRS"
  if [ -s "$MISSING_PAIRS" ]; then
    if ! grep -qE '^\|[[:space:]]*QA-ID[[:space:]]*\|' "$CURRENT_SECTION"; then
      {
        echo
        echo "| QA-ID   | 手段   | 状態    | ラウンド | 備考 |"
        echo "|---------|--------|---------|----------|------|"
      } >> "$LEDGER"
    fi
    while IFS=$'\t' read -r id method; do
      [ -z "$id" ] && continue
      if [ "$method" = "auto" ]; then round=-; else round=0; fi
      echo "| $id | $method | pending | $round | - |" >> "$LEDGER"
    done < "$MISSING_PAIRS"
  fi
  echo "台帳: current generation を使用 ($LEDGER)"
else
  {
    echo
    echo "$CURRENT_SOURCE"
    echo
    echo "| QA-ID   | 手段   | 状態    | ラウンド | 備考 |"
    echo "|---------|--------|---------|----------|------|"
    while read -r id; do [ -n "$id" ] && echo "| $id | auto   | pending | -        | - |"; done < "$AUTO_IDS"
    while read -r id; do [ -n "$id" ] && echo "| $id | manual | pending | 0        | - |"; done < "$MANUAL_ONLY"
  } >> "$LEDGER"
fi
```

## auto 判定の再実行ゲート

**マトリクス列レイアウト (canonical)**: `| QA-ID | 出典 | カテゴリ | テストファイル | テストケース | 実行コマンド |` の6列固定。Markdown-escaped `\|` を一時退避してから分割した cell では QA-ID が2、実行コマンドが7。command の pipe は復元する。追加・並べ替えは禁止する。

```bash
LEDGER="<plan>.qa-ledger.md"; PLAN_FILE="<plan>.md"

if [ ! -s "$LEDGER" ] || [ ! -s "$PLAN_FILE" ]; then
  echo "⚠️ 入力が空/不存在: LEDGER=$LEDGER PLAN_FILE=$PLAN_FILE — 再実行ゲートを実行不可。" >&2
  exit 2
fi

RUN_DIR=$(mktemp -d) || { echo "⚠️ 一時ディレクトリを作成できません。" >&2; exit 2; }
cleanup() { [ -d "$RUN_DIR" ] && rm -r -- "$RUN_DIR"; }
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
CURRENT_LEDGER="$RUN_DIR/current_ledger.md"
PLAN_QA="$RUN_DIR/plan_implementation_ready.md"
AUTO_LATEST="$RUN_DIR/auto_latest.tsv"
AUTO_IDS="$RUN_DIR/auto_ids.txt"
RUN_LOG="$RUN_DIR/reexec.log"
SOURCE_LINE=$(grep -nE '^## QA source [0-9a-f]+$' "$LEDGER" | tail -1 | cut -d: -f1)
if [ -z "$SOURCE_LINE" ]; then
  echo "⚠️ current QA source generation がありません。台帳初期化を先に実行してください。" >&2; exit 2
fi
tail -n "+$SOURCE_LINE" "$LEDGER" > "$CURRENT_LEDGER"
awk '
  /^## 実装準備[[:space:]]*$/ { active = 1 }
  active && seen && /^## / { exit }
  active { print; seen = 1 }
' "$PLAN_FILE" > "$PLAN_QA"

awk -F'|' '/^\|/ && $2 !~ /QA-ID/ && $2 !~ /^[ \t]*-+[ \t]*$/{
  id=$2; gsub(/^[ \t]+|[ \t]+$/,"",id)
  method=$3; gsub(/^[ \t]+|[ \t]+$/,"",method)
  state=$4; gsub(/^[ \t]+|[ \t]+$/,"",state)
  if (method=="auto") latest[id]=state
} END {
  for (id in latest) print id "\t" latest[id]
}' "$CURRENT_LEDGER" | sort > "$AUTO_LATEST"

awk -F'\t' '$2!="対象外(N/A)" && $2!="検証不能(真の制約)" && $2!="要人間確認" { print $1 }' \
  "$AUTO_LATEST" | sort -u > "$AUTO_IDS"

if [ ! -s "$AUTO_IDS" ]; then
  echo "再実行ゲート: auto 行なし (skip)"; exit 0
fi

while read -r id; do
  [ -z "$id" ] && continue
  CMD=$(awk -v t="$id" '
    /^#### QA-ID カバレッジマトリクス[[:space:]]*$/ { matrix=1; next }
    matrix && /^#{1,4} / { matrix=0 }
    matrix && /^\| *QA-[A-Z]+-[0-9]+ *\|/ {
      row=$0; gsub(/\\[|]/, "\034", row); n=split(row, cell, "|")
      if (n != 8) next
      i=cell[2]; gsub(/^[ \t]+|[ \t]+$/,"",i)
      if (i==t) {
        c=cell[7]; gsub(/^[ \t]+|[ \t]+$/,"",c); gsub(/\034/, "|", c)
        print c; exit
      }
    }
  ' "$PLAN_QA")
  if [ -z "$CMD" ]; then
    echo "| $id | auto | 要人間確認 | -        | 実行コマンド未定義 (QA-IDカバレッジマトリクスに該当行なし) |" >> "$LEDGER"
    continue
  fi
  CMD_CLEAN=$(echo "$CMD" | sed -e 's/^`//' -e 's/`$//')
  if bash -c "$CMD_CLEAN" </dev/null >"$RUN_LOG" 2>&1; then EXIT=0; else EXIT=$?; fi
  # rspec は -e 不一致でも exit 0 を返すことがある (実機確認済み)。出力を見て0件実行を検出する。
  if grep -qE '(^|[^0-9])0 examples|No test files found|no tests' "$RUN_LOG"; then
    STATE="要人間確認"; NOTE="テスト0件を検出 (exit=$EXIT、コマンド不一致の疑い) $(date -Iseconds)"
  elif [ "$EXIT" -eq 0 ]; then
    STATE="PASS"; NOTE="審判再実行 $(date -Iseconds) exit=$EXIT"
  else
    STATE="FAIL(exit=$EXIT)"; NOTE="審判再実行 $(date -Iseconds) exit=$EXIT"
  fi
  echo "| $id | auto | $STATE | -        | $NOTE |" >> "$LEDGER"
done < "$AUTO_IDS"
```

**注意点**:
- 対象は current generation の各 auto QA-ID の最新行だけ。`対象外(N/A)` / `検証不能(真の制約)` / `要人間確認` は再実行しない
- 実行出力に `0 examples`（RSpec）/ `No test files found`・`no tests`（Vitest）のいずれかを検出したら、exit 0 でも `PASS` にはせず `要人間確認` を記帳する（コマンドの `-e`/`-t` 指定が QA-ID と一致していない疑いのため）
- `bash -c` への `</dev/null` は削らない（理由: docker/dip 等 stdin を消費するコマンドが while ループの ID リストを飲み込み、2 件目以降を実行しないまま正常終了する — 実測で 23 件中 1 件だけ実行されるループ早期終了が発生した）。テストコマンドを環境に合わせて読み替える場合もこの構造は維持する
- 0 件検出の正規表現は `(^|[^0-9])0 examples` の形を維持する（理由: `0 examples` 単体は「10 examples」「20 examples」にも部分一致し、正常 pass を `要人間確認` へ誤判定する — 10 examples 全 pass の QA-ID が誤判定された実測あり）
- プランファイルの QA-ID カバレッジマトリクスにコマンドが定義されていない QA-ID は `要人間確認` を記帳する
- `CMD_CLEAN` はプランファイルのバッククォート除去のみで、シェルメタ文字のエスケープ処理は行わない。`bash -c` にそのまま渡すため、プランファイルの実行コマンド列に不正な文字列が書かれていると意図しないコマンドが実行されるリスクがある（プランファイルは信頼できる入力という前提で運用する）

## 完了判定

台帳の最新行（同一 QA-ID・手段は最後の行）を集計し、全行が終端状態（`PASS` / `検証不能(真の制約)` / `対象外(N/A)`）かどうかで判定する。**検証済み Bash**:

```bash
LEDGER="<plan>.qa-ledger.md"
if [ ! -s "$LEDGER" ]; then
  echo "⚠️ 台帳が空/不存在: $LEDGER — 完了判定を実行不可。台帳初期化を先に実行してください。" >&2
  exit 2
fi

RUN_DIR=$(mktemp -d) || { echo "⚠️ 一時ディレクトリを作成できません。" >&2; exit 2; }
cleanup() { [ -d "$RUN_DIR" ] && rm -r -- "$RUN_DIR"; }
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
CURRENT_LEDGER="$RUN_DIR/current_ledger.md"
LEDGER_LATEST="$RUN_DIR/ledger_latest.md"
LEDGER_INCOMPLETE="$RUN_DIR/ledger_incomplete.md"
LEDGER_UNVERIFIABLE="$RUN_DIR/ledger_unverifiable.md"
SOURCE_LINE=$(grep -nE '^## QA source [0-9a-f]+$' "$LEDGER" | tail -1 | cut -d: -f1)
if [ -z "$SOURCE_LINE" ]; then
  echo "⚠️ current QA source generation がありません。台帳初期化を先に実行してください。" >&2; exit 2
fi
tail -n "+$SOURCE_LINE" "$LEDGER" > "$CURRENT_LEDGER"

awk -F'|' '
  /^\|/ && $2 !~ /QA-ID/ && $2 !~ /^[ \t]*-+[ \t]*$/ {
    id = $2; gsub(/^[ \t]+|[ \t]+$/, "", id)
    method = $3; gsub(/^[ \t]+|[ \t]+$/, "", method)
    key = id "::" method
    row[key] = $0
  }
  END { for (k in row) print row[k] }
' "$CURRENT_LEDGER" | sort > "$LEDGER_LATEST"

if [ ! -s "$LEDGER_LATEST" ]; then
  echo "⚠️ current generation に QA 状態行がありません。完了扱いにしません。" >&2; exit 2
fi

grep -vE '\| *(PASS|検証不能\(真の制約\)|対象外\(N/A\)) *\|' "$LEDGER_LATEST" > "$LEDGER_INCOMPLETE" || true

if [ -s "$LEDGER_INCOMPLETE" ]; then
  echo "## UI QA 部分完了 (人間確認事項あり) または未完了"
  cat "$LEDGER_INCOMPLETE"
  exit 1
fi

# 全行が終端状態でも、検証不能(真の制約) が1件でも残る場合は人間の目が必要なため「完了」と呼ばない。
grep -E '\| *検証不能\(真の制約\) *\|' "$LEDGER_LATEST" > "$LEDGER_UNVERIFIABLE" || true
if [ -s "$LEDGER_UNVERIFIABLE" ]; then
  echo "## UI QA 部分完了 (人間確認事項あり)"
  cat "$LEDGER_UNVERIFIABLE"
  exit 0
else
  echo "## UI QA 完了"
  exit 0
fi
```
