---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src/db scripts
cat > tsconfig.json <<'EOF'
{
  "compilerOptions": { "strict": true, "target": "ES2022", "module": "NodeNext", "outDir": "dist" },
  "include": ["src/**/*.ts"],
  "exclude": ["src/**/__tests__/**"]
}
EOF
cat > eslint.config.js <<'EOF'
export default [
  {
    files: ["src/**/*.ts"],
    ignores: ["src/db/client.ts"],
    rules: {
      "no-restricted-imports": [
        "error",
        { paths: [{ name: "pg", message: "pg は src/db/client.ts からだけ import する" }] },
      ],
    },
  },
];
EOF
cat > src/db/client.ts <<'EOF'
import pg from "pg";

const pool = new pg.Pool();

export function query(text: string, params: unknown[] = []) {
  return pool.query(text, params);
}
EOF
cat > scripts/seed.ts <<'EOF'
import { query } from "../src/db/client.js";

await query("insert into orders (id) values ($1)", ["seed-1"]);
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

- `scripts/` を含む全ての TypeScript で、`pg` を `src/db/client.ts` 以外から import しない。
- migration を追加したら、他のブランチの migration と番号が衝突していないかを確認する。
EOF
```

コードコメントと設計書以外のmdファイルに /dry-ssot-text を実行する。
