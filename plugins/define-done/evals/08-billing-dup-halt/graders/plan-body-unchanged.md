---
type: regex
target: {source: file, path: plans/billing.md}
match: contains
flags: s
---
- T-1: `src/billing/create\.ts` に請求作成 API を実装する。\n- T-2: `src/billing/create\.ts` に請求レコードの生成処理を実装する。
