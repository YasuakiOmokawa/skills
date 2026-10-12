---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans
cat > plans/export.md <<'EOF'
# CSV 出力 設計

## 1. 目的
管理者がチームの一覧を CSV で取り出せるようにする。

## 2. 仕様
- S-1: 管理者が「CSV で出力」を押すと、`teams.csv` がダウンロードされる。
- S-2: `teams.csv` の 1 行目は `id,name` で、2 行目以降はチームを作った順に並ぶ。
- S-3: 管理者でないメンバーには「CSV で出力」を表示しない。
EOF
```

plans/export.md に /define-acceptance-criteria で受け入れ基準を作って。どの仕様をどの AC が受けるかの対応表も plan に残して。plan の更新は許可する。
