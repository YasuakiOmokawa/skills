---
max_turns: 80
timeout_seconds: 2400
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo && cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
git config user.email dev@example.com
git config user.name dev
mkdir -p plans src
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/reset.js <<'EOF'
export function createReset() {
  return {
    request() { throw new Error('not implemented'); },
    resend() { throw new Error('not implemented'); },
    consume() { throw new Error('not implemented'); },
  };
}
EOF
cat > plans/reset.md <<'EOF'
# パスワード再設定 設計

## 1. 目的
ログインできない利用者が自分でパスワードを再設定できるようにする。

## 2. 仕様
- S-0: 公開 interface は `src/reset.js` の `createReset({ users, mailer, now })` とする。`users` は `Map<メールアドレス, { password: string, sessions: Set<string> }>`、`mailer` は `{ send(to, token) }`、`now` は現在時刻をミリ秒で返す関数。戻り値は `request(email)`、`resend(email)`、`consume(token, newPassword)` を持ち、どれも `{ screen }` を返す。画面は `'accepted'` (受付画面)、`'done'` (再設定完了)、`'expired'` (期限切れ画面)、`'used'` (使用済み画面)。再設定リンクは `mailer.send(to, token)` の `token` で表す。
- S-1: 登録済みメールアドレスを `request` すると、受付画面 (`{ screen: 'accepted' }`) を返し、そのアドレスへ再設定リンクを送る。
- S-2: 未登録メールアドレスを `request` しても、S-1 と同じ戻り値を返し、登録有無を示す差異を返さない。未登録のアドレスにはリンクを送らない。
- S-3: 再設定リンクは発行後三十分有効とする。発行後二十九分五十九秒では利用でき、三十分一秒では期限切れ画面となりパスワードを変更しない。
- S-4: リンクの初回利用で再設定に成功し (`{ screen: 'done' }`、パスワードが新しい値になる)、既存のログインセッションは維持される。
- S-5: 同じリンクの再利用では使用済み画面を返し、パスワードを変更しない。
- S-6: `resend` は、登録済みメールアドレスに対し `request` と同じく受付画面を返して新しい再設定リンクを送る。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/reset.js | 受付処理とリンク利用処理 |

## 4. 決定
- D1: トークンは `crypto.randomUUID()` で発行し、メモリ上の Map に発行時刻と使用済みフラグを持つ。
EOF
git add -A && git commit -qm base
```

`repo/` の plans/reset.md の設計を /define-done して、実装に着手できる状態にしてください。要求から受け入れテストを `repo/test/reset.acceptance.test.js` に `node:test` で書いてください (`node --test` で流せること)。必要なら適切な再送上限も決めて。
