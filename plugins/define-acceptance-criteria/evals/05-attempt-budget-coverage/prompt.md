---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans
cat > plans/attempt-budget.md <<'EOF'
# ログイン試行上限 設計

## 1. 背景
パスワード総当たりを防ぐため、失敗回数に上限を設ける。

## 2. 仕様
- S-1: 同一ユーザーのパスワード認証失敗が連続五回に達した時点で、そのユーザーをロックする。四回目の失敗の直後は正しいパスワードでログインできる。五回目の失敗の直後は正しいパスワードでもログインできず、「一時的にロックされています」を表示する。
- S-2: ロックは最後の失敗から十五分間続く。十四分五十九秒後は正しいパスワードでもロック中、十五分一秒後はログインできる。
- S-3: ロック前にログインに成功すると、失敗回数は零に戻る。

## 3. 監査
| 事象 | 記録 | 記録に失敗したとき |
|---|---|---|
| ロック発生 | audit_log に `account_locked` を 1 行 | ロック自体は成立し、ログイン応答は記録成功時と同じ |
| ロック解除 | 記録しない | - |

## 4. 変更対象
- src/auth/attempt-budget.ts (新規)
- src/auth/login.ts

## Ground Review
- R1: 失敗回数は Redis ではなく users テーブルの `failed_attempts` 列に持つ。実装後、`src/auth/` 配下に `redis` への参照が増えていないことを確認対象にすること。
- R2: ユーザー A のロックはユーザー B のログイン可否に影響しない。非影響を明示すること。
EOF
```

current plan は plans/attempt-budget.md。設計を /define-acceptance-criteria して、設計を確定する。
