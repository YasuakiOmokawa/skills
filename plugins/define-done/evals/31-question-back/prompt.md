---
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo && cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
git config user.email dev@example.com
git config user.name dev
mkdir -p src test
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/password.js <<'EOF'
export function changePassword(user, newPassword) {
  user.password = newPassword;
  user.sessions.clear();
}
EOF
cat > test/password.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { changePassword } from '../src/password.js';

test('パスワードを変えると、その利用者のセッションをすべて無効にする', () => {
  const user = { password: 'old', sessions: new Set(['pc', 'phone']) };
  changePassword(user, 'new');
  assert.equal(user.sessions.size, 0);
});
EOF
git add -A && git commit -qm base
```

以下は、`repo/` のパスワード再設定について、ここまでの私とあなたの議論です。

> 私: ログインできない人が自分でパスワードを再設定できるようにしたい。登録済みのメールにだけ再設定のリンクを送って、未登録のメールでも同じ画面を見せたい。登録の有無がばれないように。
>
> 私: リンクは三十分有効にして、リンクは再送できるようにしたい。
>
> 私: 再設定しても、ほかの端末のログインは切らないでほしい。スマホで再設定したら PC がログアウトされた、という問い合わせが多いので。
>
> あなた: 理解した内容です。要求は、ログインできない利用者が自分でパスワードを再設定できること。登録済みのメールにだけリンクを送り、未登録でも同じ画面を見せて登録の有無を明かさないこと。リンクは三十分有効で、再送できること。再設定しても、ほかの端末のログインは維持すること。やってはいけないことは、登録の有無を画面で明かすことと、再設定でほかの端末をログアウトさせることです。背景は、スマホで再設定すると PC がログアウトされるという問い合わせが多いことです。
>
> 私: その理解で合っています。

/define-done これまで議論した要求/要件のうち、まだ曖昧なものを自分に問い返してください。
