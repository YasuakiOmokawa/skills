# Phase 0: preflight 収集 + 版数確認 + status 初期化

## preflight 契約の拡張

ベースの preflight 契約 (項目表・セキュリティ規則・フォーマット) は `/finalize-plan` の `references/preflight.md` を SSOT とし、ここでは変更しない。本 skill は起動時にその契約へ次の 1 行を追加する:

| 項目 | 内容 | 記載範囲 |
|---|---|---|
| 仕様判断の扱い | `停止して確認` (既定) / `推奨案で続行し escalation 記帳` | Phase 1c (仕様判断バッチ) が参照。`推奨案で続行し escalation 記帳` を選んだ案件のみ、実装フェーズ中に生じる仕様判断を停止せず escalation ledger へ記帳して続行する (full-auto 運用) |

## 収集手順

1. `$ARGUMENTS` で渡された仕様文書パスからプランファイルの置き場を決め、`<plan>.preflight.md` の存在を確認する。既存なら不足項目のみ収集し、無ければ新規作成する
2. 1 回の `AskUserQuestion` で、この時点で答えられる項目 (ベース URL / ログイン手段 / 起点ブランチ / サーバ・DB 起動コマンド / 仕様判断の扱い) をまとめて確認する
3. **権限アカウント一覧・テストデータ準備手順は、AC がまだ存在しないため Phase 0 では確定できない。** この 2 項目は `未定` のまま残し、Phase 1c (仕様判断バッチ) に確定を委ねる。Phase 0 はこの 2 項目を空欄放置ではなく明示的に `未定` と記載する

## Phase 0 の完了条件 (機械判定)

素朴に「全欄が `未定` 以外」を判定すると、AC 未確定の 2 項目 (権限アカウント一覧・テストデータ準備手順) のせいで Phase 0 が恒久的に完了しない。これらは Phase 1c で確定する設計 (設計文書の「preflight の未定項目もここに合流させる」節) のため、Phase 0 の完了ゲートは次の 2 段構えにする:

- ベース URL / ログイン手段 / 起点ブランチ / サーバ・DB 起動コマンド / 仕様判断の扱い の 5 項目 → `未定` を許容しない (Phase 0 中に確定必須)
- 権限アカウント一覧 / テストデータ準備手順 → `未定` のままで Phase 0 は完了してよい (Phase 1c で確定)

判定 Bash (`未定` の完全一致セルのみを見る。`未定 (Phase1c 待ち)` のような注記付きセルは Phase 1c 確定待ちの意図表示であり、機械判定の対象外とする):

```bash
PREFLIGHT="<plan>.preflight.md"
REQUIRED_ROWS="ベース URL|ログイン手段|起点ブランチ|サーバ・DB 起動コマンド|仕様判断の扱い"

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
  echo "Phase 0 完了条件 pass (環境系 5 項目確定済み。権限アカウント一覧/テストデータ準備手順は Phase 1c で確定予定)"
  exit 0
fi
```

## 版数確認 (警告どまり)

開始時に、起動された各 skill の frontmatter `version` と、ローカルリポジトリが存在する場合の `plugins/<name>/.claude-plugin/plugin.json` の `version` を突き合わせる。ドリフトがあれば警告し、`<plan>.orchestration-status.md` の Phase 0 行の成果物パス欄に注記して継続する (ブロックしない)。リポジトリが無い利用者環境 (npx install のみ) ではこの確認自体をスキップする。

## status 初期化

`<plan>.orchestration-status.md` が無ければヘッダ行を書き出す (詳細は [references/orchestration-status.md](orchestration-status.md))。
