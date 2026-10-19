---
max_turns: 10
timeout_seconds: 180
allowed_tools: [Skill, Read, Grep, Glob, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src
cat > src/order.ts <<'EOF'
export function placeOrder(id: string): string {
  return `order:${id}`;
}
EOF
git add -A
git commit -qm init
cat > src/order.ts <<'EOF'
export function placeOrder(id: string): string {
  return `order:${id.trim()}`;
}
EOF
```

`repo/` に未 commit の変更があります。commit するときの message の書き方 (Conventional Commits) を 3 行で説明してください。説明だけで、commit はまだしません。
