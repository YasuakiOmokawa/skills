---
max_turns: 25
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/export
cat > src/export/csv.ts <<'EOF'
export function toCsv(rows: Record<string, string>[]): string {
  return rows.map((r) => Object.values(r).join(",")).join("\n");
}
EOF
cat > plans/export.md <<'EOF'
# CSV エクスポート 設計

## 1. 目的
顧客一覧を CSV でダウンロードできるようにする。

## 2. 仕様
- S-1: 1 行目はヘッダ行で、列は `id,email,signup_date` の順とする。
- S-2: 値にカンマまたは改行を含む場合はダブルクォートで囲み、内部のダブルクォートは 2 つ重ねる。
- S-3: 0 件のときはヘッダ行だけを返す。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/export/csv.ts | ヘッダ行とクォート処理 |

## 4. 実装タスク
- T-1: `toCsv` にヘッダ行を追加する。
- T-2: `toCsv` にクォート処理を追加する。
EOF
```

plans/export.md に受け入れ基準を定義して、設計書に書き込んで。
