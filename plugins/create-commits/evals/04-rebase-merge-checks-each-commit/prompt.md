---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src test plans
cat > CONTRIBUTING.md <<'EOF'
# 開発の約束

- PR は rebase merge で取り込む。取り込まれた各 commit が単独で `sh check.sh` を通ること。
EOF
cat > check.sh <<'EOF'
set -e
n=0
for f in src/*.sh test/*_test.sh; do
  . "./$f"
  n=$((n + 1))
done
sum=$(cat src/*.sh test/*_test.sh | cksum | cut -d' ' -f1)
echo "checks passed ($n files, $sum)"
EOF
cat > plans/invoice-rounding.md <<'EOF'
# 請求額の端数処理

## 作業項目

1. 請求額の計算で端数を `round_yen` で丸める
   - 対象: `src/invoice.sh`、`test/invoice_test.sh`
2. 金額の丸め関数 `round_yen` を追加する
   - 対象: `src/money.sh`、`test/money_test.sh`
EOF
cat > src/invoice.sh <<'EOF'
total() {
  echo $(( $1 * 110 / 100 ))
}
EOF
cat > test/invoice_test.sh <<'EOF'
got=$(total 1000)
[ "$got" = "1100" ] || { echo "total 1000 gave '$got'"; exit 1; }
EOF
git add -A
git commit -qm init
git switch -q -c feature/invoice-rounding
cat > src/money.sh <<'EOF'
round_yen() {
  echo $(( ($1 + 50) / 100 ))
}
EOF
cat > test/money_test.sh <<'EOF'
got=$(round_yen 110550)
[ "$got" = "1106" ] || { echo "round_yen 110550 gave '$got'"; exit 1; }
EOF
cat > src/invoice.sh <<'EOF'
total() {
  round_yen $(( $1 * 110 ))
}
EOF
cat > test/invoice_test.sh <<'EOF'
got=$(total 1000)
[ "$got" = "1100" ] || { echo "total 1000 gave '$got'"; exit 1; }
got=$(total 1005)
[ "$got" = "1106" ] || { echo "total 1005 gave '$got'"; exit 1; }
EOF
```

`repo/plans/invoice-rounding.md` の計画どおりの実装が `repo/` の作業ツリーで終わりました。/create-commits
