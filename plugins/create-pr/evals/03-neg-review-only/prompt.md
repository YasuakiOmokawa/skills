---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p gitdir
git init -q -b main --separate-git-dir=gitdir/repo repo
cd repo
git config user.name dev
git config user.email dev@example.com
printf '.claude/\n' > .gitignore
mkdir -p src/billing docs
cat > src/billing/invoice.ts <<'EOF'
export type Invoice = { id: string; amount: number };

export async function sendInvoice(invoice: Invoice): Promise<void> {
  await fetch(`https://billing.example.test/invoices/${invoice.id}`, {
    method: "POST",
    body: JSON.stringify(invoice),
  });
}
EOF
cat > docs/developer-guide.md <<'EOF'
# 開発者ガイド

## 請求書

請求書は `sendInvoice` で送る。
EOF
git add .gitignore src docs
git commit -qm scaffold
git checkout -q -b feature/billing-reliability
cat > src/billing/retry.ts <<'EOF'
export async function withRetry<T>(
  run: () => Promise<T>,
  attempts: number,
  intervalMs: number,
): Promise<T> {
  let lastError: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      return await run();
    } catch (error) {
      lastError = error;
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }
  }
  throw lastError;
}
EOF
cat > src/billing/retry.test.ts <<'EOF'
import { withRetry } from "./retry";

test("withRetry retries a failing call at a fixed interval", async () => {
  let calls = 0;
  const result = await withRetry(
    async () => {
      calls += 1;
      if (calls < 3) throw new Error("temporary");
      return "ok";
    },
    3,
    1,
  );
  expect(result).toBe("ok");
  expect(calls).toBe(3);
});
EOF
cat > src/billing/invoice.ts <<'EOF'
import { withRetry } from "./retry";

export type Invoice = { id: string; amount: number };

export async function sendInvoice(invoice: Invoice): Promise<void> {
  await withRetry(
    () =>
      fetch(`https://billing.example.test/invoices/${invoice.id}`, {
        method: "POST",
        body: JSON.stringify(invoice),
      }),
    3,
    1000,
  );
}
EOF
git add src/billing
git commit -qm "feat: 請求書の送信失敗を固定間隔で再試行する"
cat >> docs/developer-guide.md <<'EOF'

請求書の送信は失敗すると 1 秒間隔で最大 3 回まで再試行する。
EOF
git add docs
git commit -qm "docs: 開発者ガイドに請求書の再試行を追記する"
```

repo の feature/billing-reliability の PR をレビューして、気になる点を教えてください。
