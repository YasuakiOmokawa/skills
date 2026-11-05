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
mkdir -p node_modules/tiny-deploy scripts dist docs plans
printf 'node_modules/\n.deploy-state.json\n' > .gitignore
printf '{ "name": "web", "private": true, "scripts": { "deploy": "node scripts/deploy.js" }, "dependencies": { "tiny-deploy": "1.4.0" } }\n' > package.json
printf '{ "name": "tiny-deploy", "version": "1.4.0", "main": "index.js" }\n' > node_modules/tiny-deploy/package.json
cat > node_modules/tiny-deploy/index.js <<'EOF'
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const STATE = path.join(process.cwd(), ".deploy-state.json");

function hashDir(dir) {
  const hash = crypto.createHash("sha256");
  for (const name of fs.readdirSync(dir).sort()) {
    hash.update(name);
    hash.update(fs.readFileSync(path.join(dir, name)));
  }
  return hash.digest("hex");
}

async function deploy({ bundleDir, upload }) {
  const hash = hashDir(bundleDir);
  const last = fs.existsSync(STATE) ? JSON.parse(fs.readFileSync(STATE, "utf8")).hash : null;
  if (hash === last) {
    return { skipped: true, reason: "bundle unchanged" };
  }
  await upload(bundleDir, { secrets: { AUTH_SERVICE_KEY: process.env.AUTH_SERVICE_KEY } });
  fs.writeFileSync(STATE, JSON.stringify({ hash }));
  return { skipped: false };
}

module.exports = { deploy };
EOF
cat > scripts/deploy.js <<'EOF'
const { deploy } = require("tiny-deploy");

deploy({
  bundleDir: "dist",
  upload: async (dir, { secrets }) => {
    console.log(`upload ${dir} with ${Object.keys(secrets).join(",")}`);
  },
}).then((result) => console.log(JSON.stringify(result)));
EOF
printf 'console.log("app");\n' > dist/app.js
cat > docs/operations.md <<'EOF'
# 運用

- 配布は `npm run deploy` で行う。
EOF
cat > plans/rotate-secret.md <<'EOF'
# secret を回した後の反映 設計

## 目的
`AUTH_SERVICE_KEY` を回した後、新しい値が本番に効くようにし、その手順を `docs/operations.md` に書く。

## 決めたこと

| # | 決めること | 決定 |
|---|---|---|
| D1 | 反映のさせ方 | `AUTH_SERVICE_KEY` を変えたら、同じ commit のまま `npm run deploy` を再実行する。同じ入力でも再実行すれば新しい secret が反映される |
| D2 | 書く場所 | `docs/operations.md` に「secret を回す」節を足し、D1 の手順を書く |

## 変更対象
| ファイル | 変更 |
|---|---|
| docs/operations.md | 「secret を回す」節を足す |
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
```

`repo/plans/rotate-secret.md` の設計を /define-done。
