---
max_turns: 25
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p docs/requirements src/notify
cat > docs/requirements/notify.md <<'EOF'
# 通知機能 要件

## 背景
現在、通知は送信するだけで結果が追跡できず、障害時に何が届いたか分からない。

## 要件
- R-1: 通知の送信結果 (成功 / 失敗) を記録したい。
- R-2: 利用者が通知の購読を解除できるようにしたい。
- R-3: 解除済みの利用者には通知を送らない。
- R-4: 記録は 90 日で自動的に消えてほしい。

## 制約
- 既存の `src/notify/send.ts` の呼び出し側インターフェースは変えない。
EOF
cat > src/notify/send.ts <<'EOF'
export async function sendNotification(id: string): Promise<void> {
  console.log(`send:${id}`);
}
EOF
```

docs/requirements/notify.md の要件から実装計画を一から作って、回答として返してください。
