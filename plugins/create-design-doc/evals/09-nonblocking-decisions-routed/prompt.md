---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。
```bash
mkdir -p billing/retry app/billing
cat > app/billing/charge.py <<'EOF'
class ChargeClient:
    def __init__(self, gateway):
        self._gateway = gateway

    def charge(self, invoice_id, amount, idempotency_key):
        return self._gateway.post("/charges", {"invoice": invoice_id, "amount": amount, "key": idempotency_key})
EOF
cat > billing/retry/plan.md <<'EOF'
# 請求再試行計画 (承認済み: 2026-09-10 課金チーム リード 佐藤)

- 段階 1 (この計画の対象): 月次請求の決済ゲートウェイ呼び出し失敗時の再試行
  - 再試行は最大 3 回。間隔は 1 分、5 分、30 分
  - 二重請求を防ぐこと
  - 失敗確定時に通知する
- 段階 2: 返金処理にも再試行を広げる。段階 1 の後に別の設計で扱う
EOF
cat > billing/retry/poc.md <<'EOF'
# 請求再試行 PoC

## 問い
ゲートウェイの一時失敗 (HTTP 5xx / timeout) に対し、最大 3 回の再試行で二重請求を起こさずに成功率を回復できるか。

## 星取表
| 案 | 二重請求 | 成功率回復 | 実装量 | 判定 |
|---|---|---|---|---|
| A: 冪等キー (invoice_id) を付けて再試行 | 防止できた (1000 件で重複 0) | 92% → 99.6% | 小 | 採用 |
| B: 再試行前に取引照会 API で状態確認 | 防止できたが照会自体が timeout する | 92% → 98.1% | 中 | 不採用 |

## 結論
案 A を採用。冪等キーは `invoice_id` を固定値として使い、試行回ごとに変えない。

## PR
- PoC: https://github.com/example/billing/pull/41 (draft)

## 申し送り
- 再試行間隔 (1 分 / 5 分 / 30 分) を定数にするか設定値にするかは未決。どちらでも段階 1 の実装は進められる
- 失敗確定の通知の宛先を担当者個人にするか課金チームのチャンネルにするかは未決。どちらでも段階 1 の実装は進められる
- 段階 2 の返金の再試行で、冪等キーに何を使うか (refund_id か invoice_id + 連番か) は未決

## Prototype
- 適合性: `app/billing/charge.py` の `ChargeClient.charge` に冪等キーを渡す既存契約に合致。呼び出し側 `app/billing/service.py` に再試行ループを置く配置で責務分離を保てた
- 再試行間隔は定数で実装した。通知は担当者個人に送る形で実装した
- 検証: 既存テストスイート pass、再試行 3 回で二重請求 0 件を再確認
- draft PR: https://github.com/example/billing/pull/42
EOF
```

`billing/retry/poc.md` を Design Doc にまとめて。
