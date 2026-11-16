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
mkdir -p src/__tests__ src/config/__tests__ plans
cat > src/config/env.ts <<'EOF'
export const isProduction = process.env.APP_ENV === "production";
EOF
cat > src/config/log-level.ts <<'EOF'
export const logLevel = process.env.APP_ENV === "production" ? "warn" : "debug";
EOF
cat > src/__tests__/env.test.ts <<'EOF'
test("APP_ENV を production にしても起動する", () => {
  process.env.APP_ENV = "production";
  expect(() => require("../config/env")).not.toThrow();
});
EOF
cat > src/config/__tests__/log-level.test.ts <<'EOF'
test("APP_ENV が無くても logLevel が決まる", () => {
  delete process.env.APP_ENV;
  expect(require("../log-level").logLevel).toBeDefined();
});
EOF
cat > plans/no-app-env.md <<'EOF'
# 製品コードから APP_ENV を外す 設計

## 1. 目的
製品コードが実行環境の名前で振る舞いを変えないようにする。

## 2. 仕様
- S-1: 変更後、`src/` の製品コード (試験を除く) に `APP_ENV` が残らない。
- S-2: `isProduction` と `logLevel` は、起動時に渡す設定 `config.production` から決まる。
- S-3: 既存の試験 (`src/__tests__/env.test.ts`、`src/config/__tests__/log-level.test.ts`) は、`APP_ENV` を設定しても起動が壊れないことを確かめ続けるので、`APP_ENV` の記述を残す。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/config/env.ts | `config.production` から決める |
| src/config/log-level.ts | `config.production` から決める |
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
```

`repo/plans/no-app-env.md` の設計を /define-done。
