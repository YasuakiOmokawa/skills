---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
git init -q --bare --template= ../remote.git
git remote add origin ../remote.git
mkdir -p src/__tests__
cat > src/order.ts <<'EOF'
export function placeOrder(id: string): string {
  return `order:${id}`;
}
EOF
git add -A
git commit -qm init
git push -q -u origin main
git switch -q -c feature/order-retry
cat > src/retry.ts <<'EOF'
export function retry<T>(attempts: number, run: () => T): T {
  let lastError: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      return run();
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}
EOF
git add -A
git commit -qm "feat: 注文の再試行を実装する"
cat > src/__tests__/retry.test.ts <<'EOF'
import { describe, expect, it } from "vitest";
import { retry } from "../retry";

describe("retry", () => {
  it("returns the first success", () => {
    let calls = 0;
    const result = retry(3, () => {
      calls += 1;
      if (calls < 2) throw new Error("fail");
      return "ok";
    });
    expect(result).toBe("ok");
  });

  it("throws the last error when every attempt fails", () => {
    expect(() =>
      retry(2, () => {
        throw new Error("always");
      }),
    ).toThrow("always");
  });
});
EOF
git add -A
git commit -qm "test: 再試行のテストを足す"
git push -q -u origin feature/order-retry
```

`repo/` の現在の branch は push 済みですが、実装とテストが別々の commit になっています。1 つの commit にまとめてください。履歴の書き換えも force push もして構いません。/create-commits
