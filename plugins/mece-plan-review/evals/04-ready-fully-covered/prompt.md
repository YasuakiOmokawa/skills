---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/notify
cat > plans/notify.md <<'EOF'
# 通知送信 設計

## 1. 目的
通知の送信結果を記録する。中断の判定は呼び出し時点だけで行う。

## 2. 仕様
- S-1: 送信に成功したら `sent` を返し、送信済みとして 1 回だけ記録する。
- S-2: 送信に失敗したら `failed` を返し、失敗として 1 回だけ記録する。
- S-3: 呼び出し時点で中断済みなら `aborted` を返し、送信も記録も行わない。
- S-4: 通知の唯一の入口 `handleNotify` は、送信結果をそのまま呼び出し元へ返す。
- S-5: 送信を試みる経路では `transport.deliver` を通知 ID だけを引数に 1 回呼ぶ。呼び出し時点で中断済みなら 0 回である。
- S-6: 呼び出し後に中断された場合、本設計は中断を検知しない。戻り値と記録は中断が無かった場合と同じである。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/notify/send.ts | 送信と記録 |
| src/notify/handler.ts | 入口 |

## 4. 実装タスク
- T-1: `src/notify/send.ts` に `sendNotification` を実装し、S-1 / S-2 / S-3 の 3 経路を返し分け、S-5 の `transport.deliver` 呼び出し回数と S-6 の中断非検知を満たす。
- T-2: `src/notify/handler.ts` に `handleNotify` を実装し、`sendNotification` の戻り値をそのまま返す。

## Acceptance Criteria
- [ ] AC-001: 送信が成功したとき `sendNotification` は `"sent"` を返し、その呼び出しの完了時点で `log.record` が `(id, "sent")` で 1 回だけ呼ばれる。観測は `log.reset()` 直後から数える。
- [ ] AC-002: `transport.deliver` が例外を投げたとき `sendNotification` は `"failed"` を返し、その呼び出しの完了時点で `log.record` が `(id, "failed")` で 1 回だけ呼ばれる。観測は `log.reset()` 直後から数える。
- [ ] AC-003: 中断済みの `AbortSignal` を渡したとき `sendNotification` は `"aborted"` を返し、その呼び出しの完了時点で `log.record` の呼び出し回数が 0 である。観測は `log.reset()` 直後から数える。
- [ ] AC-004: `sendNotification` を参照するのはリポジトリ内で `src/notify/handler.ts` の `handleNotify` だけであり、`handleNotify` は戻り値を加工せずそのまま返す。
- [ ] AC-005: 成功経路と失敗経路では `transport.deliver` が通知 ID だけを引数に 1 回呼ばれ、中断済み経路では 0 回である。
- [ ] AC-006: `await transport.deliver(id)` の最中に中断されても、`sendNotification` の戻り値と `log.record` の呼び出しは中断が無かった場合と同一である。

## MECE Review
- AC IDs: (なし)
EOF
cat > src/notify/send.ts <<'EOF'
import { transport } from "./transport";
import { log } from "./log";

export type SendResult = "sent" | "failed" | "aborted";

export async function sendNotification(
  id: string,
  signal: AbortSignal,
): Promise<SendResult> {
  if (signal.aborted) {
    return "aborted";
  }
  let delivered: boolean;
  try {
    await transport.deliver(id);
    delivered = true;
  } catch {
    delivered = false;
  }
  const status = delivered ? "sent" : "failed";
  log.record(id, status);
  return status;
}
EOF
cat > src/notify/handler.ts <<'EOF'
import { sendNotification, type SendResult } from "./send";

export async function handleNotify(
  id: string,
  signal: AbortSignal,
): Promise<SendResult> {
  return sendNotification(id, signal);
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

// 同期かつ全域。例外を送出する経路を持たない。
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
```

plans/notify.md 設計を /mece-plan-review して、レビュー結果を設計書に反映して、設計を確定する。
