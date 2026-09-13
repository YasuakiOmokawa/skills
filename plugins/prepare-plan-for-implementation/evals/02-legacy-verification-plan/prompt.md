---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/notify
cat > package.json <<'EOF'
{
  "name": "notify",
  "private": true,
  "scripts": { "test": "vitest run" },
  "devDependencies": { "vitest": "^2.0.0" }
}
EOF
cat > src/notify/transport.ts <<'EOF'
export const transport = {
  async deliver(id: string): Promise<void> {
    if (id === "") throw new Error("empty id");
  },
};
EOF
cat > src/notify/log.ts <<'EOF'
const lines: string[] = [];

export const log = {
  record(id: string, status: "sent" | "failed"): void {
    lines.push(`${id}:${status}`);
  },
  read(): readonly string[] {
    return lines;
  },
  reset(): void {
    lines.length = 0;
  },
};
EOF
cat > src/notify/send.ts <<'EOF'
import { transport } from "./transport";
import { log } from "./log";

export type SendResult = "sent" | "failed" | "aborted";

// 現状: 中断済み signal を見ていない。
export async function sendNotification(id: string, signal: AbortSignal): Promise<SendResult> {
  void signal;
  try {
    await transport.deliver(id);
    log.record(id, "sent");
    return "sent";
  } catch {
    log.record(id, "failed");
    return "failed";
  }
}
EOF
cat > src/notify/send.test.ts <<'EOF'
import { describe, it, expect, beforeEach } from "vitest";
import { sendNotification } from "./send";
import { log } from "./log";

describe("sendNotification", () => {
  beforeEach(() => log.reset());

  it("records sent once on success", async () => {
    expect(await sendNotification("n1", new AbortController().signal)).toBe("sent");
    expect(log.read()).toEqual(["n1:sent"]);
  });
});
EOF
cat > plans/notify.md <<'EOF'
# 通知送信 設計

## 1. 目的
通知の送信結果を記録する。中断の判定は呼び出し時点だけで行う。

## 2. 仕様
- S-1: 送信に成功したら `sent` を返し、送信済みとして 1 回だけ記録する。
- S-2: 送信に失敗したら `failed` を返し、失敗として 1 回だけ記録する。
- S-3: 呼び出し時点で中断済みなら `aborted` を返し、送信も記録も行わない。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/notify/send.ts | 中断済み判定の追加 |
| src/notify/send.test.ts | 失敗・中断のテスト追加 |

## 4. 実装タスク
- T-1: `src/notify/send.ts` の `sendNotification` 冒頭で `signal.aborted` を判定し `aborted` を返す。
- T-2: `src/notify/send.test.ts` に S-2 / S-3 のテストを追加する。

## Acceptance Criteria
- [ ] AC-001: 送信が成功したとき `sendNotification` は `"sent"` を返し、`log.reset()` 直後から数えて `log.record` が `(id, "sent")` で 1 回だけ呼ばれる。
- [ ] AC-002: `transport.deliver` が例外を投げたとき `sendNotification` は `"failed"` を返し、`log.reset()` 直後から数えて `log.record` が `(id, "failed")` で 1 回だけ呼ばれる。
- [ ] AC-003: 中断済みの `AbortSignal` を渡したとき `sendNotification` は `"aborted"` を返し、`log.reset()` 直後から数えて `log.record` の呼び出し回数が 0 である。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- 対応: S-1→AC-001、S-2→AC-002、S-3→AC-003。T-1→AC-003、T-2→AC-002/AC-003。
- 所見: なし。
- Gate: ready

## Verification Plan
検証担当は送信結果を手動で確認し、気になる点があれば実装者に口頭で伝える。

- AC IDs: AC-001, AC-002, AC-003

### AC-001
- Oracle: sent が返る
- 手順: 送信して確認する

### AC-002
- Oracle: failed が返る

### AC-009
- Oracle: 旧仕様の購読解除が動く
- Evidence anchors: なし
- Prerequisites: なし
- Required effects: なし
EOF
```

plans/notify.md は受け入れ基準も MECE レビューも済んでいる。実装に着手できるように、作業の順序と各受け入れ基準の検証の対応を plans/notify.md に書き込んで。実装はまだしない。
