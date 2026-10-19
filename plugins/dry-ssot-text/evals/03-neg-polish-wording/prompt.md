---
max_turns: 15
timeout_seconds: 300
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src/db
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
    files: ["**/*.ts"],
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
cat > README.md <<'EOF'
# orders-api

本プロジェクトは、注文の情報を管理するところの API サーバーであるということができる。

## 開発

- ビルドの対象となるものは `src/**/*.ts` であり、`src/**/__tests__/**` はビルドの対象に含まれないこととなっている。
- ローカルの DB は `docker compose up db` を実行することによって起動することが可能である。
EOF
cat > CLAUDE.md <<'EOF'
# orders-api

## 規則

- TypeScript のコードでは、`pg` を `src/db/client.ts` 以外から import しない。
- デバッグ用の `console.log` を commit しない。
- migration を追加したら、他のブランチの migration と番号が衝突していないかを確認する。
EOF
```

README.md の言い回しを読みやすく推敲して。
