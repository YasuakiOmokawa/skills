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
mkdir -p docs/runbook .github/workflows plans
cat > docs/runbook/staging.md <<'EOF'
# staging の運用

## deploy
main に merge すると、workflow `deploy-staging` の job `staging` が staging に配布する。

## 障害時
job `staging` の log を見て、失敗した step を直してから merge し直す。
EOF
cat > .github/workflows/deploy-staging.yml <<'EOF'
name: deploy-staging
on:
  push:
    branches: [main]
jobs:
  staging:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx tiny-deploy staging
EOF
cat > plans/secret-rotation.md <<'EOF'
# staging の secret を回す時の扱い 設計

## 目的
Secrets Store の `AUTH_SERVICE_KEY` を回した時に、運用者が迷わず新しい値を staging に効かせられるようにする。

## 決めたこと

| # | 決めること | 決定 |
|---|---|---|
| D1 | 反映のさせ方 | Secrets Store の値を回したら、workflow `deploy-staging` の job `staging` を re-run して新しい version を出す |
| D2 | 書く場所 | `docs/runbook/staging.md` に「secret を回す」節を足し、D1 の手順を書く |

## 変更対象
| ファイル | 変更 |
|---|---|
| docs/runbook/staging.md | 「secret を回す」節を足す |
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
```

依頼: secret を回した時の扱いを runbook に書いて。回したら新しい値が staging に反映されるようにしたい。

この依頼に対する `repo/plans/secret-rotation.md` の設計を /define-done。
