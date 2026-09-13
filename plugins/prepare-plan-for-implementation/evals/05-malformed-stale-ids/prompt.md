---
max_turns: 25
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/billing
cat > src/billing/date.ts <<'EOF'
export function nextBillingDate(billingDay: number, from: Date): Date {
  return new Date(Date.UTC(from.getUTCFullYear(), from.getUTCMonth(), billingDay));
}
EOF
cat > plans/billing-date.md <<'EOF'
# 請求日計算 設計

## 1. 目的
新規顧客の請求日を登録日の日付で固定し、その日が存在しない月は末日に丸める。既存顧客の請求日は変えない。

## 2. 仕様
- S-1: 登録日が 1〜28 日なら、毎月同じ日を請求日とする。
- S-2: 登録日が 29〜31 日なら、その日が存在しない月は末日を請求日とする。
- S-3: 既存顧客の請求日は変更しない。
- S-4: 請求日は `customers.billing_day` 列に永続化する。

## 3. 実装タスク
- T-1: `src/billing/date.ts` の `nextBillingDate` で S-1 / S-2 を実装する。
- T-2: `customers.billing_day` 列を追加し、登録時に保存する。

## Acceptance Criteria
- [ ] AC-001: `nextBillingDate(15, new Date("2026-02-01"))` は `2026-02-15` を返す。
- [ ] AC-002: `nextBillingDate(31, new Date("2026-02-01"))` は `2026-02-28` を返す。
- [ ] AC-003: `registerCustomer` を登録日 `2026-01-30` で呼ぶと `customers.billing_day` が `30` になる。
- [ ] AC-004: `billing_day` が設定済みの既存顧客について、本変更の前後で請求の日付が同一である。
- AC-005 請求日の変更は監査ログに残る

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- 対応: S-1→AC-001、S-2→AC-002、S-3→AC-004、S-4→AC-003。
- 所見: なし。
- Gate: ready
- Gate: unverified
EOF
```

plans/billing-date.md 設計を /prepare-plan-for-implementation して、結果を設計書に反映して、設計を確定する。実装は指示まで禁止。
