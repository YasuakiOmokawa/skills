# Phase 0: preflight 収集 + PRD 分解 + スライス可逆性判定 + 版数確認 + status 初期化

## preflight 契約

ベースの preflight 契約 (項目表・セキュリティ規則・フォーマット) は `/finalize-plan` の `references/preflight.md` を SSOT とし、本 skill は変更を加えない。仕様判断の扱いは preflight の選択式項目にしない — Phase 1c (仕様判断バッチ) は常に停止して人間確認する仕様に一本化する (仕様判断は削減対象ではなく設計された人間の工程、利用者決定 2026-07-06)。

## 収集手順

1. `$ARGUMENTS` で渡された仕様文書パスからプランファイルの置き場を決め、`<plan>.preflight.md` の存在を確認する。既存なら不足項目のみ収集し、無ければ新規作成する
2. 1 回の `AskUserQuestion` で、この時点で答えられる項目 (ベース URL / ログイン手段 / 起点ブランチ / サーバ・DB 起動コマンド) をまとめて確認する
3. **権限アカウント一覧・テストデータ準備手順は、AC がまだ存在しないため Phase 0 では確定できない。** この 2 項目は `未定` のまま残し、Phase 1c (仕様判断バッチ) に確定を委ねる。Phase 0 はこの 2 項目を空欄放置ではなく明示的に `未定` と記載する

## Phase 0 の完了条件 (機械判定)

素朴に「全欄が `未定` 以外」を判定すると、AC 未確定の 2 項目 (権限アカウント一覧・テストデータ準備手順) のせいで Phase 0 が恒久的に完了しない。これらは Phase 1c で確定する設計 (設計文書の「preflight の未定項目もここに合流させる」節) のため、Phase 0 の完了ゲートは次の 2 段構えにする:

- ベース URL / ログイン手段 / 起点ブランチ / サーバ・DB 起動コマンド の 4 項目 → `未定` を許容しない (Phase 0 中に確定必須)
- 権限アカウント一覧 / テストデータ準備手順 → `未定` のままで Phase 0 は完了してよい (Phase 1c で確定)

判定 Bash (`未定` の完全一致セルのみを見る。`未定 (Phase1c 待ち)` のような注記付きセルは Phase 1c 確定待ちの意図表示であり、機械判定の対象外とする):

```bash
PREFLIGHT="<plan>.preflight.md"
REQUIRED_ROWS="ベース URL|ログイン手段|起点ブランチ|サーバ・DB 起動コマンド"

UNRESOLVED=$(awk -F'|' -v rows="$REQUIRED_ROWS" '
  BEGIN { n = split(rows, arr, "|"); for (i = 1; i <= n; i++) want[arr[i]] = 1 }
  /^\|/ {
    label = $2; gsub(/^[ \t]+|[ \t]+$/, "", label)
    val = $3; gsub(/^[ \t]+|[ \t]+$/, "", val)
    if (want[label] && val == "未定") print label
  }
' "$PREFLIGHT")

if [ -n "$UNRESOLVED" ]; then
  echo "Phase 0 未完了、以下が未定のまま:"
  echo "$UNRESOLVED"
  exit 1
else
  echo "Phase 0 完了条件 pass (環境系 4 項目確定済み。権限アカウント一覧/テストデータ準備手順は Phase 1c で確定予定)"
  exit 0
fi
```

## PRD 分解と進捗台帳の起票

Phase 0 のうちに、仕様文書 (`$ARGUMENTS`) を `Read` して要求単位 (節/項) へ分解し、`<PRD>.progress-ledger.md` の全行を起票する。台帳の行フォーマット・状態語彙・「最新行が勝つ」規約は [references/progress-ledger.md](progress-ledger.md) を参照 (既存の qa-ledger / orchestration-status.md と同じ規約を流用し、新しい記法は作らない)。

今回の deliver-from-spec 実行が PRD 全体のうち一部のスライスのみを対象にする場合、対象スライスの要求行だけを進めればよい。対象外の要求行は `未着手` のまま残す (今回どこを実装するかを台帳上で明示するため)。

## スライスの可逆性判定

対象スライスについて、Phase 1a (design-first) と `/iterate-with-prototypes` (プロトタイプ先行) のどちらの経路を通すかを判定する。判定基準は `/iterate-with-prototypes` の適用条件をそのまま転記して流用する (新しい基準を作らない):

> 危険な未知が**戻しにくい決定** (DB スキーマ / migration / 公開 API 契約 / チーム間境界) を含むなら code-first は不可。
> (出典: `plugins/iterate-with-prototypes/skills/iterate-with-prototypes/SKILL.md` ガードレール節)

- **不可逆決定を含むスライス** → 現行どおり Phase 1a (design-first、`/review-design`) を起動する
- **可逆・小 blast radius のスライス** → Phase 1a を起動せず `/iterate-with-prototypes` を起動する。iwp の step 5 (post-code の AC/MECE カバレッジ検証 = `/define-acceptance-criteria` → `/mece-plan-review`) まで**必ず完走させ**、分析ファイルに `## 受け入れ条件` / `## MECE分析結果` が揃った状態で Phase 1c (仕様判断バッチ) → Phase 1d (`/finalize-plan` の通常起動) へ合流させる

**合流の受け渡し (依存関係)**: finalize-plan Step 1.5 の即中断ゲート (AC/MECE 欠落時) はそのまま機能する — 迂回せず、iwp 側の step 5 完走で入力を要件に合わせる方式 (SKILL.md 冒頭の依存関係の注記の 3 点目)。step 4-5 を省略した genuine ledger 駆動の状態では finalize-plan を起動できないため、本 skill 経由のスライスでは step 5 完走を必須とする。未更新の環境では、finalize-plan 起動前に分析ファイルの両セクションが揃っていることを人間が確認する (graceful degradation)。

## 版数確認 (警告どまり)

開始時に、起動された各 skill の frontmatter `version` と、ローカルリポジトリが存在する場合の `plugins/<name>/.claude-plugin/plugin.json` の `version` を突き合わせる。ドリフトがあれば警告し、`<plan>.orchestration-status.md` の Phase 0 行の成果物パス欄に注記して継続する (ブロックしない)。リポジトリが無い利用者環境 (npx install のみ) ではこの確認自体をスキップする。

## status 初期化

`<plan>.orchestration-status.md` が無ければヘッダ行を書き出す (詳細は [references/orchestration-status.md](orchestration-status.md))。
