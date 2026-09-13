---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/webhook
cat > package.json <<'EOF'
{
  "name": "webhook",
  "private": true,
  "scripts": { "test": "vitest run" },
  "devDependencies": { "vitest": "^2.0.0" }
}
EOF
cat > src/webhook/db.ts <<'EOF'
export type Delivery = { id: string; webhookId: string; status: "queued" | "done" | "failed" };
export type Subscription = { webhookId: string; url: string };

const deliveries: Delivery[] = [];
const subscriptions: Subscription[] = [{ webhookId: "w1", url: "https://example.test/hook" }];

export const db = {
  insertDelivery(d: Delivery): void {
    deliveries.push(d);
  },
  deliveries(): readonly Delivery[] {
    return deliveries;
  },
  subscriptions(): readonly Subscription[] {
    return subscriptions;
  },
  snapshotSubscriptions(): string {
    return JSON.stringify(subscriptions);
  },
  reset(): void {
    deliveries.length = 0;
  },
};
EOF
cat > src/webhook/transport.ts <<'EOF'
export const transport = {
  async post(url: string, body: unknown): Promise<number> {
    void url;
    void body;
    return 200;
  },
};
EOF
cat > src/webhook/deliver.ts <<'EOF'
import { db } from "./db";
import { transport } from "./transport";

let seq = 0;

// 現状: 4xx でも 3 回まで再試行し、同一 webhook の同時配信を制限していない。
export async function deliver(webhookId: string, payload: unknown): Promise<{ status: 201; deliveryId: string }> {
  const deliveryId = `d${++seq}`;
  db.insertDelivery({ id: deliveryId, webhookId, status: "queued" });
  const url = db.subscriptions().find((s) => s.webhookId === webhookId)?.url ?? "";
  for (let attempt = 0; attempt < 3; attempt++) {
    const code = await transport.post(url, payload);
    if (code < 400) break;
  }
  return { status: 201, deliveryId };
}
EOF
cat > src/webhook/deliver.test.ts <<'EOF'
import { describe, it, expect, beforeEach, vi } from "vitest";
import { deliver } from "./deliver";
import { db } from "./db";
import { transport } from "./transport";

describe("deliver", () => {
  beforeEach(() => db.reset());

  it("returns 201 and records a queued delivery", async () => {
    vi.spyOn(transport, "post").mockResolvedValue(200);
    const res = await deliver("w1", { a: 1 });
    expect(res.status).toBe(201);
    expect(db.deliveries().find((d) => d.id === res.deliveryId)?.status).toBe("queued");
  });
});
EOF
cat > plans/webhook.md <<'EOF'
# Webhook 配信 設計

## 1. 目的
配信要求を記録し、受信側のエラー種別に応じて再試行を制御する。

## 2. 仕様
- S-1: 配信要求は `201` と `deliveryId` を返し、`deliveries` に status `queued` の行を 1 行作る。
- S-2: 受信側が 4xx を返した配信は再試行しない。
- S-3: 同一 `webhookId` の配信は同時に最大 1 件だけ `transport.post` を実行する。
- S-4: 配信処理は `subscriptions` の内容を変更しない。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/webhook/deliver.ts | 4xx 非再試行、同時実行の制限 |
| src/webhook/deliver.test.ts | S-2 / S-3 / S-4 のテスト追加 |

## 4. 実装タスク
- T-1: `src/webhook/deliver.ts` で 4xx 応答時にループを抜ける。
- T-2: `src/webhook/deliver.ts` に `webhookId` ごとの実行中フラグを持たせ、実行中なら待機する。
- T-3: `src/webhook/deliver.test.ts` に S-2 / S-3 / S-4 のテストを追加する。

## 5. 検証メモ
- S-2〜S-4 は、配信を呼び出してから 5 秒待ち、追加の `transport.post` 呼び出しや `subscriptions` の変化が無いことを確認すればよい。

## Acceptance Criteria
- [ ] AC-001: `deliver("w1", payload)` は `{ status: 201, deliveryId }` を返し、`db.deliveries()` に `id === deliveryId` かつ `status === "queued"` の行が 1 行ある。
- [ ] AC-002: `transport.post` が `400` を返すとき、`deliver` の完了までに `transport.post` は 1 回だけ呼ばれる。
- [ ] AC-003: 同一 `webhookId` に対して `deliver` を 2 件同時に開始したとき、同時に実行中の `transport.post` は常に最大 1 件である。
- [ ] AC-004: `deliver` の開始前と完了後で `db.snapshotSubscriptions()` の値が同一である。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003, AC-004
- 対応: S-1→AC-001、S-2→AC-002、S-3→AC-003、S-4→AC-004。T-1→AC-002、T-2→AC-003、T-3→AC-002/AC-003/AC-004。
- 所見: なし。
- Gate: ready
EOF
```

plans/webhook.md 設計を /prepare-plan-for-implementation して、結果を設計書に反映して、設計を確定する。実装は指示まで禁止。
