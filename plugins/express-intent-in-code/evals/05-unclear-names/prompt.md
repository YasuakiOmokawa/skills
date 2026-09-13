---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src
cat > package.json <<'EOF'
{ "name": "fixture", "private": true, "type": "module", "scripts": { "test": "node --test" } }
EOF
cat > src/backoff.ts <<'EOF'
// n: 何回目の試行か (0 始まり)
// base: 初回待ち時間 ms
// cap: 上限 ms
export function calc(n: number, base: number, cap: number): number {
  // 2 の n 乗を掛ける (指数バックオフ)
  const v = base * 2 ** n;
  // cap を超えないようにする
  const c = Math.min(v, cap);
  // jitter は入れない。呼び出し側の queue worker が付与するため、二重に付けると p99 が SLO を超えた (2025-11 障害)
  return c;
}

// ms を秒に
export function s(ms: number): number {
  // 切り上げ
  return Math.ceil(ms / 1000);
}
EOF
cat > src/backoff.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { calc, s } from "./backoff.ts";

test("first attempt waits base", () => {
  assert.equal(calc(0, 100, 1000), 100);
});
test("grows exponentially", () => {
  assert.equal(calc(3, 100, 1000), 800);
});
test("capped", () => {
  assert.equal(calc(4, 100, 1000), 1000);
});
test("ms to seconds rounds up", () => {
  assert.equal(s(1500), 2);
  assert.equal(s(1000), 1);
});
EOF
```

`node --test` が 3 件以上すべて成功することを確認してから、次の依頼に取りかかってください。

src/backoff.ts の意図がコードから分かるようにして。コメントは減らす方向で。
