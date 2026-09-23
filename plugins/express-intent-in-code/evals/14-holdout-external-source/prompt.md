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
cat > src/rate-limit.ts <<'EOF'
// レート制限のモジュール
// 決済代行 API 仕様書 (2025 年版) 4.2 節: 1 秒あたり 5 リクエストまで。超えると 429 を返し 60 秒遮断される
const L = 5;
// 時間窓 (ms)
const W = 1000;

// 送信時刻の一覧 ts と現在時刻 now を受け取り、今送ってよいかを返す
export function ok(ts: number[], now: number): boolean {
  // 直近の時間窓に入る送信を数える
  const n = ts.filter((t) => now - t < W).length;
  // 上限未満なら送ってよい
  return n < L;
}
EOF
cat > src/rate-limit.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { ok } from "./rate-limit.ts";

test("allows the 5th request within a second", () => {
  assert.equal(ok([0, 100, 200, 300], 500), true);
});
test("blocks the 6th request within a second", () => {
  assert.equal(ok([0, 100, 200, 300, 400], 500), false);
});
test("a send exactly one window ago no longer counts", () => {
  assert.equal(ok([0, 100, 200, 300, 400], 1000), true);
});
EOF
```

`node --test` が 3 件すべて成功することを確認してから、次の依頼に取りかかってください。

src/rate-limit.ts のコメントが多くて読みにくいので減らしてほしい。振る舞いは変えないで。
