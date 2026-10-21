---
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p docs plans .cache
printf '# 旧ガイド\n' > docs/old-guide.md
printf 'see docs/old-guide.md\n' > README.md
printf '.cache/\n' > .gitignore
printf 'blob docs/old-guide.md history\n' > .cache/history.bin
cat > plans/rename.md <<'EOF'
# ガイドの改名 設計

## 1. 目的
`docs/old-guide.md` を `docs/guide.md` に改名する。

## 2. 仕様
- S-1: 変更後、`docs/old-guide.md` は無く、`docs/guide.md` がある。
- S-2: 変更後、repository の中に `docs/old-guide.md` を指す記述が残らない。
- S-3: `.cache/` は開発ツールが git の履歴から作る cache で、`.gitignore` が無視する。
EOF
```

`repo/plans/rename.md` の設計を /define-done して、設計を確定する。plan の更新は許可する。
