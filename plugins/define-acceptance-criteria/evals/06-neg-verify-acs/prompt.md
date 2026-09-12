---
max_turns: 15
timeout_seconds: 600
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans
cat > plans/reset.md <<'EOF'
# パスワード再設定 設計

## 1. 目的
ログインできない利用者が自分でパスワードを再設定できるようにする。

## 2. 仕様
- S-1: 登録済みメールアドレスを送信すると、「受付が完了しました」と表示する受付画面へ遷移する。
- S-2: 未登録メールアドレスを送信しても、S-1 と同じ受付画面へ遷移し、登録有無を示す差異を表示しない。
- S-3: 登録済みメールには発行後三十分有効な再設定リンクを送る。発行後二十九分五十九秒では利用でき、三十分一秒では期限切れ画面となりパスワードを変更しない。
- S-4: リンクの初回利用で再設定に成功し、既存のログインセッションは維持される。
- S-5: 同じリンクの再利用では「このリンクは使用済みです」と表示し、パスワードを変更しない。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/reset/request.ts | 受付処理 |
| src/reset/consume.ts | リンク利用処理 |

## Acceptance Criteria
- [ ] AC-001: 発行後二十九分五十九秒のリンクを開くと、パスワード再設定フォームが表示される
- [ ] AC-002: 発行後三十分一秒のリンクを開くと、期限切れ画面が表示され、パスワードは変更されない
- [ ] AC-003: 同じリンクを二回目に開くと、「このリンクは使用済みです」が表示され、パスワードは変更されない
EOF
mkdir -p src/reset
cat > src/reset/consume.ts <<'EOF'
export const LINK_TTL_MS = 30 * 60 * 1000;

export type Token = { issuedAt: number; usedAt: number | null };

export function consume(token: Token, now: number) {
  if (token.usedAt !== null) return { view: "used" as const, changed: false };
  if (now - token.issuedAt > LINK_TTL_MS) return { view: "expired" as const, changed: false };
  token.usedAt = now;
  return { view: "reset-form" as const, changed: true };
}
EOF
```

current plan は plans/reset.md。全 AC が src/reset/consume.ts の実装で満たされているか検証して、AC ごとの結果を報告して。AC の追加・変更はしないこと。
