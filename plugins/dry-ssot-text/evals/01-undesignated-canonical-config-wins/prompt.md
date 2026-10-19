---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src/db docs/design .github/workflows
cat > package.json <<'EOF'
{
  "name": "orders-api",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc -p .",
    "lint": "eslint ."
  },
  "dependencies": {
    "pg": "^8.13.0"
  },
  "devDependencies": {
    "@types/pg": "^8.11.0",
    "eslint": "^9.0.0",
    "typescript": "^5.6.0",
    "typescript-eslint": "^8.0.0"
  }
}
EOF
cat > tsconfig.json <<'EOF'
{
  "compilerOptions": { "strict": true, "target": "ES2022", "module": "NodeNext", "outDir": "dist" },
  "include": ["src/**/*.ts"],
  "exclude": ["src/**/__tests__/**"]
}
EOF
cat > eslint.config.js <<'EOF'
import tseslint from "typescript-eslint";

const message = "pg は src/db/client.ts からだけ import する";

export default [
  { ignores: ["dist/**"] },
  {
    files: ["**/*.{ts,tsx,mts,cts}"],
    ignores: ["src/db/client.ts"],
    languageOptions: { parser: tseslint.parser },
    rules: {
      "no-restricted-imports": [
        "error",
        {
          paths: [{ name: "pg", message }],
          patterns: [{ group: ["pg/**"], message }],
        },
      ],
    },
  },
];
EOF
cat > .github/workflows/ci.yml <<'EOF'
name: ci
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm install
      - run: npm run lint
      - run: npm run build
EOF
cat > src/db/client.ts <<'EOF'
import pg from "pg";

const pool = new pg.Pool();

export function query(text: string, params: unknown[] = []) {
  return pool.query(text, params);
}
EOF
cat > README.md <<'EOF'
# orders-api

注文を管理する API サーバー。

## 開発

- ビルド対象は `src/**/*.ts` で、`src/**/__tests__/**` は含めない。
- ローカルの DB は `docker compose up db` で起動する。
EOF
cat > CLAUDE.md <<'EOF'
# orders-api

## 規則

- TypeScript のコードでは、`pg` (`pg/...` のサブパスを含む) を `src/db/client.ts` 以外から `import` 文で読み込まない。
- デバッグ用の `console.log` を commit しない。
- migration を追加したら、他のブランチの migration と番号が衝突していないかを確認する。
EOF
cat > docs/design/order-flow.md <<'EOF'
# 設計書: 注文フロー

## DB アクセス

- DB には `src/db/client.ts` の `query` だけを通して触る。`pg` を直接 import するのはそのファイルだけにする。

## 注文の流れ

1. 注文を受け付ける。
2. 在庫を確保する。
3. 決済して確定する。
EOF
```

コードコメントと設計書以外のmdファイルに /dry-ssot-text を実行する。
