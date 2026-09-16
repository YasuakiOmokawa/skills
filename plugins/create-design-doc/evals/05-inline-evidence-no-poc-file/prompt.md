---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。
```bash
mkdir -p docs app/billing
cat > app/billing/charge.py <<'EOF'
class ChargeClient:
    def __init__(self, gateway):
        self._gateway = gateway

    def charge(self, invoice_id, amount, idempotency_key):
        return self._gateway.post("/charges", {"invoice": invoice_id, "amount": amount, "key": idempotency_key})
EOF
```

PoC のファイルは作っていないので、根拠はここに書く。これで `docs/design.md` に Design Doc を作って。

承認済み計画 (2026-09-10 課金チーム リード 佐藤が承認):
- 決済ゲートウェイの一時失敗時に最大 3 回再試行する。間隔は 1 分 / 5 分 / 30 分
- 二重請求を防ぐ

検証結果 (ローカルで手元確認、PR は作っていない):
- 冪等キーを invoice_id 固定にして再試行した 1000 件で二重請求 0 件
- 取引照会 API で状態確認する案は照会自体が timeout するので不採用
- `app/billing/charge.py` の `ChargeClient.charge` は冪等キーを受け取る契約なので、呼び出し側に再試行ループを置けば既存契約を変えずに済む
- 失敗確定時の通知時刻は未決
