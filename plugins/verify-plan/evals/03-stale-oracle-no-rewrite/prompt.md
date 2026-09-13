---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src test
printf 'node_modules/\n' > .gitignore
printf '{ "name": "retry", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > plans/retry.md <<'EOF'
# 一時障害の再試行 設計

## 1. 目的
外部 API の一時的な失敗を再試行で吸収する。

## 2. 仕様
- S-1: `withRetry(fn)` は `fn` が reject したら再試行し、成功したらその値を返す。
- S-2: 試行は最大 3 回。3 回とも失敗したら最後のエラーで reject する。
- S-3: 再試行の間は 10ms、20ms の指数バックオフで待つ。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/retry.js | S-1〜S-3 の実装 (新規) |
| test/retry.test.js | S-1〜S-3 のテスト (新規) |

## 4. 実装タスク
- T-1: `src/retry.js` を新規作成する。
- T-2: `test/retry.test.js` を追加する。

## Acceptance Criteria
- [ ] AC-001: 3 回目で成功する `fn` を `withRetry` に渡すと、`fn` は 3 回呼ばれ、戻り値は 3 回目の値である。
- [ ] AC-002: 常に失敗する `fn` を渡すと、`fn` は 3 回呼ばれ、3 回目のエラーで reject する。
- [ ] AC-003: 再試行の待機時間は 1 回目 10ms、2 回目 20ms である。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- 対応: S-1→AC-001、S-2→AC-002、S-3→AC-003。T-1→AC-001/AC-002/AC-003、T-2→AC-001/AC-002/AC-003。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002, AC-003

### AC-001
- Oracle: test/retry.test.js の "AC-001 succeeds on third attempt" が pass
- Evidence anchors: src/retry.js、test/retry.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: src/retry.js の `MAX_ATTEMPTS` が 2 であり、test/retry.test.js の "AC-002 gives up after max attempts" が pass
- Evidence anchors: src/retry.js、test/retry.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行し、`grep MAX_ATTEMPTS src/retry.js` で値を確認する

### AC-003
- Oracle: test/retry.test.js の "AC-003 waits 10ms then 20ms" が pass
- Evidence anchors: src/retry.js、test/retry.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する
EOF
cat > src/retry.js <<'EOF'
const MAX_ATTEMPTS = 3;
const BASE_DELAY_MS = 10;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function withRetry(fn, { onWait = () => {} } = {}) {
  let lastError;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (attempt < MAX_ATTEMPTS) {
        const delay = BASE_DELAY_MS * 2 ** (attempt - 1);
        onWait(delay);
        await sleep(delay);
      }
    }
  }
  throw lastError;
}

module.exports = { withRetry, MAX_ATTEMPTS };
EOF
cat > test/retry.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const { withRetry } = require("../src/retry");

function failingUntil(successAt) {
  let calls = 0;
  const fn = async () => {
    calls++;
    if (calls < successAt) throw new Error(`fail ${calls}`);
    return `ok ${calls}`;
  };
  return { fn, calls: () => calls };
}

test("AC-001 succeeds on third attempt", async () => {
  const f = failingUntil(3);
  assert.equal(await withRetry(f.fn), "ok 3");
  assert.equal(f.calls(), 3);
});

test("AC-002 gives up after max attempts", async () => {
  const f = failingUntil(Infinity);
  await assert.rejects(withRetry(f.fn), { message: "fail 3" });
  assert.equal(f.calls(), 3);
});

test("AC-003 waits 10ms then 20ms", async () => {
  const waits = [];
  const f = failingUntil(3);
  await withRetry(f.fn, { onWait: (ms) => waits.push(ms) });
  assert.deepEqual(waits, [10, 20]);
});
EOF
```

plans/retry.md の実装が working tree に済んだ。/verify-plan して。検証で見つかった実装の不備は直してよい。コミットは指示があるまで禁止。
