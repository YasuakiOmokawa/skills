---
name: deliver-from-spec
description: Takes a spec document path and drives the existing plan-driven skill chain (review-design → define-acceptance-criteria → mece-plan-review → spec-judgment batch → finalize-plan → implementation → plan-diff review → review-code-quality → polish-before-commit → qa-ui → create-pr) end to end via file-path handoffs and machine gates, writing progress to an orchestration-status file so long runs survive context compaction. Use when the user wants to run the full spec-to-PR chain in one pass, or says things like "仕様からPRまで流して" / "フェーズ連鎖で自動で進めて".
---

# deliver-from-spec

仕様文書 1 本を入力に、Phase 0 (preflight) から Phase 4 (出荷ゲート → create-pr → 監査パック) までの既存 skill 連鎖を、ファイルパスのハンドオフと機械ゲートで遷移させる薄いオーケストレータ。要約を渡すハンドオフは行わない — 各 Phase の受け渡しは常に成果物ファイルのパスであり、これにより長時間実行でコンテキストが要約された後も `<plan>.orchestration-status.md` と各成果物ファイルを読めば再開できる。

## 薄い版のスコープ

**入れる**: Phase 0〜4 の連鎖 / `<plan>.orchestration-status.md` への制御状態書き出し / 出荷ゲート (escalation 台帳の Critical 行 > 0 なら create-pr を起動せず機械停止) / 監査パック生成 (`<plan>.audit-pack.md`) / 開始時の skill 版数確認 (警告どまり)。

**入れない** (硬化フェーズ = dogfood 後の課題): 複雑度/リスク軸によるフェーズ省略判定 / 停滞検知の調整・フェーズ間往復上限の精緻化 (本 skill は「同一フェーズ再突入は 1 回まで」の固定値のみを使う) / 並列実装の worktree 分離 (PR チェーンは直列実装のみ) / 別系統モデルによる judge。

## 依存関係の注記

Phase 1a と Phase 1d の完了条件は、本 skill と同時期に着手された次の 3 点の周辺修正を前提にしている:

1. `/review-design` が Step 6 の最終レポートを `<plan>.design-review.md` へ固定ファイル名で保存すること (Phase 1a の完了条件、および監査パック (3) の前提部品)
2. `/finalize-plan` の PR 分割出力に「QA-ID → PR 割当」列があり、全 auto QA-ID の割当を検証するゲートがあること (Phase 1d の完了条件の 1 つ)
3. `/iterate-with-prototypes` の完了手順に「step 5 (post-code の AC/MECE カバレッジ検証) を完走させて分析ファイルを揃えてから `/finalize-plan` を通常起動する」合流手順があること (Phase 0 のスライス可逆性判定で iwp 経路に分岐したスライスが Phase 1d へ合流するための前提。finalize-plan Step 1.5 の即中断ゲートには手を入れず、入力側を要件に合わせる方式)。未更新の環境では、finalize-plan 起動前に分析ファイルへ `## 受け入れ条件` / `## MECE分析結果` が揃っていることを人間が確認する

いずれかが未着手のリポジトリでは、該当する完了条件を機械判定できない。その場合は該当条件を人間が目視確認したうえで次 Phase へ進めること。

## Arguments

`$ARGUMENTS`: 仕様文書パス (既にプランファイルがある場合はそのパスでもよい)

## 既存 skill の起動方法 (全 Phase 共通)

- **パス解決**: `~/.claude/skills/<name>/SKILL.md` を先に試し、無ければ plugin install 形 (`${CLAUDE_PLUGIN_ROOT}` の兄弟 plugin、`plugins/<name>/skills/<name>/SKILL.md`) を試す 2 経路フォールバック
- **実行形態**: 見つかった SKILL.md を `Read` し、その手順をメインコンテキストでそのまま実行する。**skill 全体を `Task` で丸ごと起動しない** (既存 skill は内部で自ら subagent を Task 起動する。これを外側からも `Task` で包むと二重の入れ子になり、内側の subagent から Task/Skill の可用性が保証されなくなるため)
- **Orchestrated モード宣言**: 4 skill (`mece-plan-review` / `review-code-quality` / `polish-before-commit` / `qa-ui`) の手順を読み始める直前に、各 plugin の `references/orchestrated-mode.md` 所定の発動フレーズを宣言する: 「orchestrated モードで実行。escalation は `<plan>.escalation-ledger.md` に記帳して続行せよ」。発動条件はファイル存在からの推測ではなく明示宣言の有無で判定され、伝達経路は `Task` プロンプトでもメインコンテキストの直前宣言でもよい（各 orchestrated-mode.md の発動条件節に明記済み）

## Phase 一覧

| Phase | 内容 | 起動する skill / agent | 完了条件 | 詳細 |
|---|---|---|---|---|
| 0 | preflight 収集 + PRD分解/進捗台帳起票 + スライス可逆性判定 + 版数確認 + status 初期化 | (自前) | preflight 環境系 4 項目確定 | [references/preflight.md](references/preflight.md) |
| 1a | プラン起案 → 設計レビュー (可逆スライスは `/iterate-with-prototypes` へ分岐) | `/review-design` または `/iterate-with-prototypes` | `<plan>.design-review.md` 存在 + fatal 0 (iwp 経路は ledger 確定) | [references/phase-1-plan.md](references/phase-1-plan.md) |
| 1b | AC 定義 → MECE 検証 | `/define-acceptance-criteria` → `/mece-plan-review` | 分析ファイルの Critical 0 (AC 修正ループ 2 周まで) | 同上 |
| 1c | 仕様判断バッチ | (自前 `AskUserQuestion`、常に停止して確認) | 未決仕様判断 0 件 | 同上 |
| 1d | finalize | `/finalize-plan` | カバレッジゲート pass + qa-ledger 初期化済み + 全 auto QA-ID が PR 割当済み | 同上 |
| 2 | PR チェーン直列実装 | `Task(general-purpose)` × PR 数 | 各 PR: テスト green + lint クリーン | [references/phase-2-implementation.md](references/phase-2-implementation.md) |
| 2.5 | diff × プラン突き合わせ | `Task(general-purpose)` + `agents/plan-diff-reviewer.md` | 指摘の Critical 0 (Major 以下は記帳して続行) | 同上 |
| 3 | 品質ループ + QA | `/review-code-quality` → `/polish-before-commit` → `/qa-ui` (Orchestrated モード) | quality ledger 収束 + qa-ledger 完了判定 exit 0 | [references/phase-3-4-quality-and-ship.md](references/phase-3-4-quality-and-ship.md) |
| 4 | 出荷ゲート → create-pr → 監査パック | ゲート bash → `/create-pr` | escalation 台帳 Critical 0 + 監査パック生成済み | 同上 |

同期タッチ (人間の応答を要する箇所) は **preflight (1 回目、調整コスト由来)** + **仕様判断バッチ (出た場合のみ、判断価値由来 — 仕様判断は削減対象ではなく設計された人間の工程)** + **QA ログイン (認証案件のみ、判断価値由来 — QA 実行は人間委譲)** + **最終監査 (監査パック提示、判断価値由来 — 出荷判断)** の **2〜4 回**。同期タッチの削減は調整コスト由来 (入力待ち・環境準備・確認の往復) にのみ適用し、判断価値由来の同期タッチは削減対象にしない (利用者決定 2026-07-06)。

## status ファイルへの追記 (検証済み Bash)

各 Phase の開始時・完了時 (running → done、または running → blocked) に `<plan>.orchestration-status.md` へ 1 行追記する。形式・再開判定ロジックの詳細は [references/orchestration-status.md](references/orchestration-status.md) を参照。

**検証済み Bash**（scratchpad fixture で、ファイル未作成時のヘッダ生成・既存ファイルへの追記・追記後の再開判定 (次フェーズへ正しく進む) を確認済み）:

```bash
STATUS="<plan>.orchestration-status.md"; PHASE="<フェーズ名>"; STATE="<running|done|blocked>"; REENTRY="<再突入回数>"; ARTIFACT="<成果物パスまたは->"
TS="$(date -Iseconds)"

if [ ! -f "$STATUS" ]; then
  {
    echo "| フェーズ | 状態 (running/done/blocked) | 再突入回数 | 成果物パス | 記録時刻 |"
    echo "|---|---|---|---|---|"
  } > "$STATUS"
fi

echo "| ${PHASE} | ${STATE} | ${REENTRY} | ${ARTIFACT} | ${TS} |" >> "$STATUS"
```

Phase 2 は PR ごとに `2-PR1` / `2-PR2` のような枝番フェーズ名でも追記してよい (再開判定は固定 9 フェーズのみを見るため、枝番行があっても再開先の判定を妨げない)。

## Phase 0: preflight + PRD分解/進捗台帳起票 + スライス可逆性判定 + 版数確認 + status 初期化

preflight 契約 (finalize-plan の既存契約をそのまま使用)、PRD 分解と進捗台帳 (`<PRD>.progress-ledger.md`) の起票、スライス単位の可逆性判定 (design-first か `/iterate-with-prototypes` か)、版数確認、Phase 0 固有の完了ゲートは [references/preflight.md](references/preflight.md) を参照。進捗台帳の契約詳細・実装漏れゲートは [references/progress-ledger.md](references/progress-ledger.md) を参照。

## Phase 1a-1d: プラン確定

プラン起案 → review-design → AC 定義 → MECE 検証 → 仕様判断バッチ → finalize の手順・完了条件・ループ上限は [references/phase-1-plan.md](references/phase-1-plan.md) を参照。

## Phase 2 / 2.5: 実装 + diff 突き合わせ

PR チェーン直列実装 (express-intent-in-code 生成時経路をプロンプトに組込み) と、diff × 確定プランの突き合わせレビューの起動テンプレート・完了条件は [references/phase-2-implementation.md](references/phase-2-implementation.md) を参照。

## Phase 3: 品質ループ + QA

review-code-quality → polish-before-commit → qa-ui を Orchestrated モードで連鎖させる手順・完了条件は [references/phase-3-4-quality-and-ship.md](references/phase-3-4-quality-and-ship.md) を参照。

## Phase 4: 出荷ゲート → create-pr → 監査パック

### 出荷ゲート (検証済み Bash)

escalation 台帳 (`<plan>.escalation-ledger.md`) の Critical 行数を判定する。Critical が 1 件でもあれば `/create-pr` を起動せず機械停止する。

**検証済み Bash**（scratchpad fixture 3 種 — Critical 0件・Critical 1件・台帳未生成 — で pass/blocked/pass の判定を確認済み。この escalation 台帳集計は `qa-ui` の `references/orchestrated-mode.md` に既出の集計と同一形式を再利用する）:

```bash
LEDGER="<plan>.escalation-ledger.md"

if [ ! -s "$LEDGER" ]; then
  echo "escalated 0件 → 出荷ゲート pass (create-pr 起動可)"
  exit 0
fi

TOTAL=$(awk -F'|' '/^\| *[0-9]+ *\|/{c++} END{print c+0}' "$LEDGER")
CRITICAL=$(awk -F'|' '/^\| *[0-9]+ *\|/{
  sev=$4; gsub(/^[ \t]+|[ \t]+$/,"",sev)
  if (sev=="Critical") c++
} END{print c+0}' "$LEDGER")

echo "escalated ${TOTAL}件（うち Critical ${CRITICAL}件）"

if [ "$CRITICAL" -gt 0 ]; then
  echo "出荷ゲート blocked → create-pr を起動せず機械停止"
  exit 1
else
  echo "出荷ゲート pass (create-pr 起動可)"
  exit 0
fi
```

Critical が残る場合の扱い (再突入・人間による上書き) は [references/phase-3-4-quality-and-ship.md](references/phase-3-4-quality-and-ship.md) を参照。

### create-pr

出荷ゲート pass 後、`/create-pr` を起動する (base branch は preflight の起点ブランチ)。

### 監査パック生成 (検証済み Bash)

3 台帳 (qa-ledger / quality-ledger / escalation-ledger) の集計・escalated 全行転記・design-review 転記・PR 一覧・Minor 無作為抽出・トークン消費概算・工程別欠陥検出サマリを `<plan>.audit-pack.md` にまとめる。収録内容の詳細は [references/audit-pack.md](references/audit-pack.md) を参照。

**検証済み Bash**（scratchpad fixture で 5 台帳 + analysis.md の計 6 ファイルが揃っているケースと、全て未生成のケースの両方で例外なく完走することを確認済み。実行時、途中で見つけた `$4`/`$5` 列インデックスの取り違え — orchestration-status.md の成果物パス列は 5 列目であり 4 列目ではない — を fixture 実行で検出し修正済み。(7) 工程別欠陥検出サマリ追加時も同じ 2 ケース (全ファイル有り/全ファイル無し) で再検証済み）:

```bash
QA_LEDGER="<plan>.qa-ledger.md"; QUALITY_LEDGER="<plan>.quality-ledger.md"
ESCALATION_LEDGER="<plan>.escalation-ledger.md"; DESIGN_REVIEW="<plan>.design-review.md"
STATUS="<plan>.orchestration-status.md"; ANALYSIS="<plan>.analysis.md"

echo "## (1) 台帳集計"; echo
echo "### qa-ledger"
if [ ! -s "$QA_LEDGER" ]; then
  echo "qa-ledger: 記帳なし"
else
  awk -F'|' '
    /^\| *QA-/ {
      id=$2; gsub(/^[ \t]+|[ \t]+$/,"",id)
      method=$3; gsub(/^[ \t]+|[ \t]+$/,"",method)
      state=$4; gsub(/^[ \t]+|[ \t]+$/,"",state)
      key = id "::" method; row[key] = state
    }
    END {
      pass=0; fail=0; pending=0; unverifiable=0; needhuman=0; na=0
      for (k in row) {
        s = row[k]
        if (s == "PASS") pass++
        else if (s ~ /^FAIL/) fail++
        else if (s == "pending") pending++
        else if (s == "検証不能(真の制約)") unverifiable++
        else if (s == "要人間確認") needhuman++
        else if (s == "対象外(N/A)") na++
      }
      printf "PASS %d / FAIL %d / pending %d / 検証不能(真の制約) %d / 要人間確認 %d / 対象外(N/A) %d\n", pass, fail, pending, unverifiable, needhuman, na
    }
  ' "$QA_LEDGER"
fi

echo; echo "### quality-ledger"
if [ ! -s "$QUALITY_LEDGER" ]; then
  echo "quality-ledger: 記帳なし"
else
  awk -F'|' '
    /^\| *[0-9]+ *\|/ {
      sev=$4; gsub(/^[ \t]+|[ \t]+$/,"",sev); st=$5; gsub(/^[ \t]+|[ \t]+$/,"",st)
      key = $2 "::" $3; rowsev[key]=sev; rowst[key]=st
    }
    END { for (k in rowsev) { c[rowsev[k]"::"rowst[k]]++ } for (k in c) printf "%s: %d件\n", k, c[k] }
  ' "$QUALITY_LEDGER" | sort
fi

echo; echo "### escalation-ledger"
if [ ! -s "$ESCALATION_LEDGER" ]; then
  echo "escalated 0件"
else
  TOTAL=$(awk -F'|' '/^\| *[0-9]+ *\|/{c++} END{print c+0}' "$ESCALATION_LEDGER")
  CRITICAL=$(awk -F'|' '/^\| *[0-9]+ *\|/{sev=$4;gsub(/^[ \t]+|[ \t]+$/,"",sev); if(sev=="Critical")c++} END{print c+0}' "$ESCALATION_LEDGER")
  MAJOR=$(awk -F'|' '/^\| *[0-9]+ *\|/{sev=$4;gsub(/^[ \t]+|[ \t]+$/,"",sev); if(sev=="Major")c++} END{print c+0}' "$ESCALATION_LEDGER")
  MINOR=$(awk -F'|' '/^\| *[0-9]+ *\|/{sev=$4;gsub(/^[ \t]+|[ \t]+$/,"",sev); if(sev=="Minor")c++} END{print c+0}' "$ESCALATION_LEDGER")
  echo "escalated ${TOTAL}件（うち Critical ${CRITICAL}件 / Major ${MAJOR}件 / Minor ${MINOR}件）"
fi

echo; echo "## (2) escalated 全行"
if [ -s "$ESCALATION_LEDGER" ]; then cat "$ESCALATION_LEDGER"; else echo "なし"; fi

echo; echo "## (3) design-review の内容 (acceptable 残存リスクを含む)"
if [ -s "$DESIGN_REVIEW" ]; then cat "$DESIGN_REVIEW"; else echo "design-review.md 未生成"; fi

echo; echo "## (4) 変更サマリー (PR一覧)"
if [ -s "$STATUS" ]; then
  awk -F'|' '/^\| *2-PR/{path=$5; phase=$2; gsub(/^[ \t]+|[ \t]+$/,"",phase); gsub(/^[ \t]+|[ \t]+$/,"",path); print phase": "path}' "$STATUS"
else
  echo "status ファイル未生成"
fi

echo; echo "## (5) Minor 無作為抽出 (quality台帳, n=2)"
if [ -s "$QUALITY_LEDGER" ]; then
  awk -F'|' '
    /^\| *[0-9]+ *\|/ { sev=$4; gsub(/^[ \t]+|[ \t]+$/,"",sev); key=$2"::"$3; if (sev=="Minor") row[key]=$0 }
    END { for (k in row) print row[k] }
  ' "$QUALITY_LEDGER" | shuf -n 2
else
  echo "quality-ledger: 記帳なし"
fi

echo; echo "## (6) トークン消費概算"
if [ -s "$STATUS" ]; then
  N=$(awk -F'|' '/^\| *[0-9.]+(-PR[0-9]+)? *\|/{c++} END{print c+0}' "$STATUS")
  echo "phase遷移記録 ${N} 行 (詳細な subagent 起動数は未計測、概算のみ)"
else
  echo "status ファイル未生成"
fi

echo; echo "## (7) 工程別欠陥検出サマリ"
echo "この集計は各工程が下流に流す前に検出した欠陥件数を表す。下流・本番で見つかった欠陥 (漏出) はこの表ではなく次回 dogfood 計測の対象。"

echo; echo "### mece-plan-review (Phase 1b)"
if [ ! -s "$ANALYSIS" ]; then
  echo "analysis.md: 記帳なし"
else
  MECE_CRITICAL=$(grep -oE '要修正（Critical [0-9]+件）' "$ANALYSIS" | tail -1 | grep -oE '[0-9]+')
  [ -z "$MECE_CRITICAL" ] && MECE_CRITICAL=0
  MECE_IMPORTANT=$(awk '
    /^### Important \/ Nice-to-have/ { insection=1; next }
    /^###/ { insection=0 }
    insection && /^\| *[0-9]+ *\|/ && /🟡/ { c++ }
    END { print c+0 }
  ' "$ANALYSIS")
  echo "Critical ${MECE_CRITICAL}件 / Important ${MECE_IMPORTANT}件"
fi

echo; echo "### review-design (Phase 1a)"
if [ ! -s "$DESIGN_REVIEW" ]; then
  echo "design-review.md: 未生成"
else
  DR_FATAL=$(grep -oE 'fatal 残存件数: *[0-9]+' "$DESIGN_REVIEW" | tail -1 | grep -oE '[0-9]+')
  [ -z "$DR_FATAL" ] && DR_FATAL=0
  DR_ACCEPTABLE=$(awk '
    /^## Acceptable 残存リスク/ { insection=1; next }
    /^## / { insection=0 }
    insection && /^\|/ {
      if ($0 ~ /指摘元/ || $0 ~ /^\|-+/ || $0 ~ /該当なし/) next
      c++
    }
    END { print c+0 }
  ' "$DESIGN_REVIEW")
  echo "fatal ${DR_FATAL}件 / acceptable残存リスク ${DR_ACCEPTABLE}件"
fi

echo; echo "### review-code-quality + polish-before-commit (Phase 3)"
if [ ! -s "$QUALITY_LEDGER" ]; then
  echo "quality-ledger: 記帳なし"
else
  awk -F'|' '
    /^\| *[0-9]+ *\|/ {
      sev=$4; gsub(/^[ \t]+|[ \t]+$/,"",sev)
      key=$2"::"$3; rowsev[key]=sev
    }
    END { for (k in rowsev) c[rowsev[k]]++; for (s in c) printf "%s %d件\n", s, c[s] }
  ' "$QUALITY_LEDGER" | sort
fi

echo; echo "### qa-ui (Phase 3)"
if [ ! -s "$QA_LEDGER" ]; then
  echo "qa-ledger: 記帳なし"
else
  awk -F'|' '
    /^\| *QA-/ {
      id=$2; gsub(/^[ \t]+|[ \t]+$/,"",id)
      method=$3; gsub(/^[ \t]+|[ \t]+$/,"",method)
      state=$4; gsub(/^[ \t]+|[ \t]+$/,"",state)
      key=id"::"method; row[key]=state
    }
    END { for (k in row) if (row[k] ~ /^FAIL/) c++; print "FAIL " c+0 "件" }
  ' "$QA_LEDGER"
fi

echo; echo "### escalation (工程横断、深刻度別)"
if [ ! -s "$ESCALATION_LEDGER" ]; then
  echo "escalated 0件"
else
  echo "escalated ${TOTAL}件（うち Critical ${CRITICAL}件 / Major ${MAJOR}件 / Minor ${MINOR}件） — escalation-ledger の「出所」列は記帳元スキルにより QA-ID/AC-ID/スキル名のいずれかで書式が異なるため、工程別ではなく深刻度別の集計に留める"
fi
```

## 再突入・ハンドオフの規則

- 同一フェーズの再突入 (やり直し) は **1 回まで** が固定値 (Phase 1b の AC 修正ループのみ、design 上の明示的な例外として 2 周まで)。1 回使い切って再度失敗した場合は機械再開せず、人間確認を要求する
- ハンドオフは常にファイルパス。要約して次フェーズへ渡すことは禁止する

## 併用推奨 skill

- `/review-design` — Phase 1a で起動 (不可逆決定を含むスライス)
- `/iterate-with-prototypes` — Phase 0 のスライス可逆性判定で可逆・小 blast radius と判定された場合、Phase 1a の代わりに起動
- `/define-acceptance-criteria` — Phase 1b で起動
- `/mece-plan-review` — Phase 1b で起動 (Orchestrated モード)
- `/finalize-plan` — Phase 1d で起動
- `/express-intent-in-code` — Phase 2 の実装 subagent プロンプトに生成時経路 (経路2) を組込み
- `/review-code-quality` — Phase 3 で起動 (Orchestrated モード)
- `/polish-before-commit` — Phase 3 で起動 (Orchestrated モード)
- `/qa-ui` — Phase 3 で起動 (Orchestrated モード)
- `/create-pr` — Phase 4 の出荷ゲート通過後に起動
