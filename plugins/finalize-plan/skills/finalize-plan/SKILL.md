---
name: finalize-plan
description: Turns AC and MECE results from the analysis file into a branch strategy and manual/auto QA steps appended to the plan file, then gates QA-ID coverage against any structured source-of-truth atoms, initializes the QA execution ledger (`<plan>.qa-ledger.md`), and generates the preflight contract (`<plan>.preflight.md`) so QA input-waiting moves before the loop starts. Use when the user has completed `/define-acceptance-criteria` + `/mece-plan-review` and is about to move from plan mode into implementation, or says "実装準備を追記して" / "ブランチ戦略を決めて" / "QA 手順をプランに書いて".
---

# finalize-plan

分析ファイル (`<plan>.analysis.md`) から AC・MECE 結果を読み込み、プランファイル末尾に `## 実装準備` (ブランチ・QA 手順) を追記する。入力欠落時は即中断。`## 正本抽出結果` があれば QA-ID の正本カバレッジをゲートし、QA-ID ごとの実行台帳 (`<plan>.qa-ledger.md`) を初期化する。あわせて、QA 開始時に個別で尋ねる入力 (ベース URL・テストデータ準備・権限アカウント等) を事前に一括収集する preflight 契約 (`<plan>.preflight.md`) を生成する。

## Arguments

- `$ARGUMENTS`: プランファイルパス (省略時は会話コンテキストの `Plan File Info:` から取得、見つからなければ確認)

## Task complexity tier

`<plan>.analysis.md` 冒頭の `### Tier` を継承し、agent の起動範囲を変える:

| Tier | AC 件数 | branch-planner | manual-qa-planner | auto-qa-planner |
|---|---|---|---|---|
| **lite** | ≤5 | ✓ (簡略) | inline (1 セクション統合) | skip |
| **standard** (default) | 6-15 | ✓ | ✓ | ✓ |
| **deep** | >15 / auth / billing / payment / migration | ✓ (詳細) | ✓ | ✓ |

リスク領域は AC 件数によらず **deep**。lite では Step 1.7 の QA-ID enumerate を簡略形 (`QA-N-01`, `QA-N-02`... の通し番号) に縮約してよい。

**PR 分割は行わない**: 実装単位の事前梱包 (PR を何本に切るか) は欠陥検出に寄与しない — 実案件 2 回の実測で、欠陥検出の実体は QA-ID カバレッジマトリクス・実装後の diff 突き合わせ・qa-ledger 審判再実行の 3 層であり、PR 分割固有の検出は 0 件だった一方、帳簿ずれのノイズ指摘と割当漏れ事故の発生源になっていた。PR 梱包の判断は出荷時に `/create-pr` が行う (利用者決定 2026-07-06)。ブランチ戦略は起点ブランチから単一の作業ブランチ 1 本に簡素化し、branch-planner は起点確認とブランチ命名のみを担う。

**agent 省略が sanctioned なのは lite tier の skip 列のみ** — deep tier で「文脈が十分だから直接書ける」という判断での省略はしない (planner agent を通さない直接策定は QA-ID トレーサビリティの独立検証を欠く)。

## Quick start

1. **Step 1**: プランファイルパスを特定
2. **Step 1.5**: 分析ファイルから `## 受け入れ条件` と `## MECE分析結果` を抽出 (両方必須、片方欠落で中断)。`## 正本抽出結果` があれば追加入力として読む
3. **Step 1.7**: main agent が AC を QA-ID 形式で 1 回だけ enumerate (`${ENUMERATED_QA_AC}`)
4. **Step 2A**: branch-planner でブランチ戦略 (起点ブランチ・単一の作業ブランチ名) を策定
5. **Step 2B** (並列、同一メッセージ): manual-qa-planner + auto-qa-planner
6. **Step 3**: 結果を統合してプランファイルに `## 実装準備` を追記
7. **Step 3.5**: 正本カバレッジ・ゲート (Step 3 の Write 後、プランファイル自体を対象に実行)
8. **Step 4**: QA 実行台帳 `<plan>.qa-ledger.md` を初期化
9. **Step 5**: プラン内容と branch-planner (Step 2A) の結果から `<プラン名>.preflight.md` を生成 (既存なら不足項目のみ補完、`未定` は AskUserQuestion 1 回にまとめて確認)

## Workflows

### Step 1.5: 分析ファイル抽出 (片方欠落で即中断)

分析ファイルパス = プランファイルの拡張子前に `.analysis` を挿入 (例: `feature-xxx.md` → `feature-xxx.analysis.md`)。`## 受け入れ条件` と `## MECE分析結果` の**両方**が必要。片方でも欠落なら次のメッセージを表示して中断:

```
⛔ 分析ファイル（{パス}）にACまたはMECE分析結果が見つかりません。
先に /define-acceptance-criteria → /mece-plan-review を実行してください。
```

例外: `/iterate-with-prototypes` の step 4-5 (doc 逆生成 + AC/MECE) 自体を省略し、分析ファイルが一度も作られていない **ledger 駆動** セッションでは、本 skill を起動せず iterate-with-prototypes step 6 の ledger 追記代替 (ブランチ戦略 + QA 手順を ledger に書く) に従う。上の中断メッセージは「分析ファイルが本来あるべきなのに無い」場合のみ表示する。

`/iterate-with-prototypes` の step 5 (`/define-acceptance-criteria` → `/mece-plan-review`) を経て `## 受け入れ条件` `## MECE分析結果` を備えた分析ファイルが既に作られている場合、この例外にはあたらない — design-first 経由の分析ファイルと同じ入力として扱い、本 skill を通常どおり起動する。Step 1.7 以降 (QA-ID enumerate・Step 3.5 の正本カバレッジ・ゲート・Step 4 の QA-ID 台帳・Step 5 の preflight 契約) は分析ファイルの起源 (design-first / プロトタイプ先行) を区別せず同一に動作する。

分析ファイルに `## 正本抽出結果` (extract-figma-spec Step5 等が生成する "atom ID + 期待値 + 状態" のテーブル) があれば追加入力として読む。無くてもエラーにはしない (Step 3.5 が skip として扱うフォールバックを維持する)。

### Step 1.7: QA-ID enumerate (main agent が 1 回だけ実行)

`${AC_CONTENT}` の各 `- [ ]` 項目を以下の prefix で連番付与し `${ENUMERATED_QA_AC}` として両 planner に渡す:

```
正常系       → QA-H-01, QA-H-02, ...  (Happy)
異常系       → QA-E-01, QA-E-02, ...  (Error)
エッジケース → QA-D-01, QA-D-02, ...  (eDge)
非影響確認   → QA-R-01, QA-R-02, ...  (Regression)
[MECE追加]   → QA-M-01, QA-M-02, ...  (Mece)
```

**0 件カテゴリは ID を発行しない** が Step 3 の対象 AC 行では `0/0` 件数表記を必ず残す (詳細・生成例・fallback は [references/qa-id-enumeration.md](references/qa-id-enumeration.md))。

**[MECE追加] のカウント**: `[MECE追加]` / `[MECE追加 変更]` タグ付き AC は base 4 カテゴリ (正常系 / 異常系 / エッジケース / 非影響確認) **とは別に** QA-M-NN を採番し、`対象AC` 件数の総数に**加算**して扱う。**タグ優先**: AC 本文が `### 正常系` 等のセクション内にインライン配置されていても、`[MECE追加]` タグが section 見出しより優先し QA-M を採番する。例: base 8 件 (3/2/2/1) + MECE追加 1 件 → 対象AC `9項目 (正常系3 / 異常系2 / エッジケース2 / 非影響1 / MECE追加1)`。

### Step 2A → 2B: Agent 実行 (1 単独 + 2 並列)

- **Step 2A**: `branch-planner` を起動しブランチ戦略 (起点ブランチ・単一の作業ブランチ名) を策定
- **Step 2B 並列**: `manual-qa-planner` + `auto-qa-planner` を**同一メッセージ内**で並列起動。両 planner は再分類せず `${ENUMERATED_QA_AC}` の QA-ID を信頼する
- **lite tier の縮約**: tier 表に従い auto-qa-planner は起動しない (skip)。manual-qa-planner も dispatch せず、main agent 自身が手動 QA 手順を 1 セクションに統合して書く (= 表の「inline」の意味)

3 agent はいずれも `Task(subagent_type="general-purpose")` で起動し、prompt 冒頭で agent 定義ファイルを Read させる (repo 制約上 typed subagent_type は使わない)。最小レシピ:

```
Task(subagent_type="general-purpose", prompt="""
${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/<agent>.md を読み込み、以下を基に <成果物> を策定:
## プラン:
${PLAN_CONTENT}
## Enumerated AC:
${ENUMERATED_QA_AC}      # qa planner が QA-ID の対応付けに使う
## MECE 分析結果:
${MECE_CONTENT}          # qa planner のみ
""")
```

各 agent 固有 prompt の全文・Task ツール利用不可時の in-context fallback は [references/agent-orchestration.md](references/agent-orchestration.md) 参照。

### Step 3: プランファイルに `## 実装準備` 追記

```markdown
---

## 実装準備

### ブランチ戦略
git checkout -b feature/xxx
命名理由: [理由] / 既存ブランチ確認: [重複なし | 連番付与]

### 手動QA手順
**環境**: {BASE_URL}（QA 実行時にユーザーから取得）
**対象AC**: N項目（正常系X / 異常系Y / エッジケースZ / 非影響W / MECE追加V）（カテゴリ名・0件表記は output-template.md SSOT 準拠）
[Chrome DevTools MCP で実行可能な手順]

### 自動QA（テストコード仕様）
[RSpec / Vitest 仕様]
```

完全なテンプレ・0 件カテゴリ表記ルール・in-context fallback 時の備考挿入位置は [references/output-template.md](references/output-template.md) 参照。

### Step 3.5: 正本カバレッジ・ゲート

Step 3 でプランファイルへ `## 実装準備` を **Write した後** に実行する (出典欄は Write 済みのプランファイル上にしか実在しないため、Step 3 の Write 前には検査できない)。

**`## 正本抽出結果` が無い場合**: `## 実装準備` に次の 1 行を残して終了する (下記「検証済み Bash」の echo 文言と一致させる)。AC 行数と QA-ID 数の突き合わせのような追加検査はしない。

```
正本カバレッジ: skip (構造化正本なし、または分析ファイル空)
```

**ある場合**: 分析ファイルの `## 正本抽出結果` から「差分」「未実装」状態の atom (対応不要な「一致」は除外) を集め、プランファイル出典欄で引用済みの atom と `comm -23` で真の集合差分を取る。**検証済み Bash** (fixture で実行検証済み):

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

未カバー atom が出た場合、分析ファイルから該当 atom 行 (期待値原文) を引き、QA-M-NN として手動QA手順へ「出典: <atom ID>」付きで Edit 追記する (原文引用・「自動補完」である旨を明記)。既存の QA 項目と検証内容が実質同一なら、新規 QA-M を作らず既存項目の出典へ atom ID を追加併記してよい (重複手順を増やさないため)。併記は `出典: AC原文 / 出典: FIG-09` のように「出典:」を atom ごとに繰り返す — カンマ区切り列挙 (`出典: AC原文, FIG-09`) はゲートの grep に拾われず未カバーのまま残る。追記後にゲートを再実行し差分ゼロを確認する。ゲート結果 (`skip` / `差分 0 件` / `補完 N 件`) は `## 実装準備` に残す。**`## 実装準備` に既存の `正本カバレッジ:` 行がある場合は最新の結果で置換する（重複追記しない）**（再実行・Step 3.5 のやり直しで行が積み重なると、どれが最新か機械判定できなくなるため）。

補完しても「対象AC」件数 (Step 1.7 由来の集計) は書き換えない — 補完分はゲート結果行にのみ計上する別集計。なお本ゲートが検査するのは正本 atom のカバレッジだけで、QA-ID 全体が manual/auto のどちらかに載っているかの網羅性は Step 4 の孤児検出が担う。

### Step 4: QA 実行台帳の初期化

`<plan>.qa-ledger.md` (プランファイルと同ディレクトリ、拡張子前に `.qa-ledger` を挿入) を、Step 1.7 で enumerate した全 QA-ID に **Step 3.5 で追記した QA-M-NN を合流させた集合**を対象に初期化する (合流しないと補完分がゲートを通した意味を失う)。Step 1.7 の結果が同一セッションに無い場合は、分析ファイル `## 受け入れ条件` の QA-ID ラベルとプランファイルの追記分から再構成する (例: `grep -oE 'QA-[A-Z]+-[0-9]+' "$ANALYSIS_FILE" | sort -u`)。手段は QA-ID ごとに 1 つだけ割り当てる: auto-qa-planner の QA-ID カバレッジマトリクスに載っていれば `auto`、それ以外で manual-qa-planner の見出しに載っていれば `manual`、両方に載っている (dual coverage) 場合は `auto` を正として manual 行は作らない (auto 側でカバー済みなのに manual 側にも pending 行が残って完了しない状態を防ぐ)。どちらにも載っていない QA-ID は `対象外(N/A)` (備考「担当手段未特定、要人間確認」)。**検証済み Bash** (fixture で実行検証済み):

```bash
ALL_IDS="/tmp/enumerated_qa_ids.txt"   # Step 1.7 の enumerate 結果 + Step 3.5 補完分 (QA-ID 1行1件)
PLAN_FILE="<plan>.md"

if [ ! -s "$ALL_IDS" ] || [ ! -s "$PLAN_FILE" ]; then
  echo "⚠️ 入力が空/不存在: ALL_IDS=$ALL_IDS PLAN_FILE=$PLAN_FILE — 台帳初期化を実行不可。" >&2
  exit 2
fi

sort -u "$ALL_IDS" > /tmp/all_qa_ids.txt
awk -F'|' '/^\| *QA-[A-Z]+-[0-9]+ *\|/{id=$2;gsub(/^[ \t]+|[ \t]+$/,"",id);print id}' "$PLAN_FILE" | sort -u > /tmp/auto_qa_ids.txt
grep -oE '^\*\*QA-[A-Z]+-[0-9]+' "$PLAN_FILE" | tr -d '*' | sort -u > /tmp/manual_qa_ids_all.txt

comm -12 /tmp/all_qa_ids.txt /tmp/auto_qa_ids.txt > /tmp/assign_auto.txt              # auto優先
comm -23 /tmp/manual_qa_ids_all.txt /tmp/auto_qa_ids.txt > /tmp/manual_candidate.txt   # dualは除外
comm -12 /tmp/all_qa_ids.txt /tmp/manual_candidate.txt > /tmp/assign_manual.txt
cat /tmp/assign_auto.txt /tmp/assign_manual.txt | sort -u > /tmp/assigned.txt
comm -23 /tmp/all_qa_ids.txt /tmp/assigned.txt > /tmp/assign_na.txt                    # どちらにも無い→対象外
```

`assign_auto.txt` → 手段=auto pending、`assign_manual.txt` → 手段=manual pending、`assign_na.txt` → 状態=対象外(N/A) (備考「担当手段未特定、要人間確認」) として台帳の行を生成する。フォーマット・状態語彙・「最新行が勝つ」規則・実装フェーズでの追記例は [references/qa-ledger.md](references/qa-ledger.md) 参照。

### Step 5: Preflight 契約の生成

ループ開始前に一括収集する入力 (`<プラン名>.preflight.md`) を、プラン内容 (Step 3 で書いた手動QA手順) と branch-planner (Step 2A) の結果から生成する。置き場・項目表・セキュリティ規則は [references/preflight.md](references/preflight.md) が SSOT。既に存在する場合は不足項目のみ補完する (既存記載は上書きしない)。

1. ベース URL・テストデータ準備手順・権限アカウント一覧は Step 3 の手動QA手順に記載があればそこから転記する。埋まらなければ `未定`。
2. ログイン手段は既定で `未定` とする (自動ログインは行わないため、記載が無い限り推測で埋めない)。
3. 起点ブランチは Step 2A (branch-planner) が確定した値をそのまま転記する。
4. サーバ・DB 起動コマンドはプラン・README 等に既記載があれば転記、なければ `未定`。
5. 生成・補完後も `未定` が残る項目があれば、それらをまとめて **AskUserQuestion 1 回**でユーザーに確認する (項目ごとに個別に停止しない)。

## Quality standards

- **実行可能性**: Chrome DevTools MCP で実行可能な手動 QA 手順
- **QA-ID トレーサビリティ**: QA-H/E/D/R/M 全項目が手動 QA または自動 QA のいずれかでカバーされている。Step 3.5 の機械 ID 差分結果 (`skip` / `差分 0 件` / `補完 N 件`) を成果物に残す (目視確認ではなく機械判定の結果を残す。skip 時もその理由を残す)
- **0 件カテゴリ可視化**: 対象 AC 行は 0 件カテゴリも件数を明示 (例 `非影響0`、省略禁止)。書式・canonical カテゴリ名・禁止理由は output-template.md を SSOT とする

## Advanced

- [references/qa-id-enumeration.md](references/qa-id-enumeration.md) — QA-ID 採番ルール詳細・生成例・Step 1.7 失敗時の `QA-X-NN` fallback
- [references/agent-orchestration.md](references/agent-orchestration.md) — 各 agent への Task prompt / 並列メッセージ構成 / Task ツール不可時の in-context 代替モード
- [references/output-template.md](references/output-template.md) — Step 3 出力テンプレ全文 / 0 件カテゴリ表記 / fallback 時の備考行
- [references/qa-ledger.md](references/qa-ledger.md) — QA 実行台帳のフォーマット・状態語彙・「最新行が勝つ」規則・手段割当規則・実装フェーズでの追記例
- [references/preflight.md](references/preflight.md) — preflight 契約 (`<plan>.preflight.md`) の置き場・項目表・セキュリティ規則・未定項目の扱い

## 併用推奨 skill

- `/define-acceptance-criteria` — 入力となる AC を定義する (前段)
- `/mece-plan-review` — AC の網羅性を検証してから本スキルに引き継ぐ (前段)
- `/iterate-with-prototypes` — プロトタイプ先行経路で進めたスライスも、step 5 (AC/MECE) 完走後の分析ファイルを渡せば本スキルに合流できる (前段、design-first と同格)
- `/review-plan-diff` — 実装完了後、本スキルが確定したプラン・QA-ID マトリクスと実 diff を突き合わせて実装漏れ・計画外差異を検出する (後段)
- `/qa-ui` — 実装完了後、本スキルが定めた QA 手順・`<plan>.qa-ledger.md`・`<plan>.preflight.md` を使って UI 検証する (後段)
- `/create-pr` — 実装完了後、PR 梱包 (何本に切るか) を判断して PR を作成する (後段。PR 分割は finalize-plan では行わない)
