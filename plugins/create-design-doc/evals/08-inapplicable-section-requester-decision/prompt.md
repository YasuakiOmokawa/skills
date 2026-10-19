---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。
```bash
mkdir -p webhook/retry app/webhook templates
cat > app/webhook/deliver.py <<'EOF'
class WebhookClient:
    def __init__(self, http):
        self._http = http

    def deliver(self, endpoint, payload, delivery_id):
        return self._http.post(endpoint, payload, headers={"X-Delivery-Id": delivery_id})
EOF
cat > webhook/retry/plan.md <<'EOF'
# Webhook 配信再試行計画 (承認済み: 2026-10-02 ユーザー)

- 対象: 顧客のエンドポイントへの Webhook 配信が失敗 (HTTP 5xx / timeout) したときの再試行
- 再試行は最大 3 回。間隔は 1 分、5 分、30 分
- 受信側で同じイベントが二重に処理されないこと
- 3 回失敗したら配信失敗として確定し、配信ログに記録して担当者へ通知する
EOF
cat > webhook/retry/poc.md <<'EOF'
# Webhook 再試行 PoC

## 問い
顧客エンドポイントの一時失敗 (HTTP 5xx / timeout) に対し、最大 3 回の再試行で、受信側に二重処理を起こさず到達率を回復できるか。

## 星取表
| 案 | 二重処理 | 到達率 | 実装量 | 判定 |
|---|---|---|---|---|
| A: 配信 ID を `X-Delivery-Id` に固定して再送し、受信側が ID で重複を捨てる | 防止できた (1000 件で重複 0) | 91% → 99.5% | 小 | 基準を満たす |
| B: 再送のたびに受信側の確認用エンドポイントで処理済みかを照会する | 防止できた (1000 件で重複 0) | 91% → 99.6% | 中 (受信側に照会口が要る) | 基準を満たす |
| C: 再送せず日次バッチで再配信 | 該当なし | 回復せず | 小 | 基準を満たさない |

## 結論
案 A と案 B はどちらも成功基準 (到達率 99% 以上、二重処理 0) を満たす。どちらを採るかは未決。配信 ID はイベントごとに固定し、試行回ごとに変えない。再試行間隔 1 分 / 5 分 / 30 分で 3 回。失敗確定の通知時刻 (即時か、翌朝の日次まとめか) は PoC の範囲外で未決。

## PR
- PoC: https://github.com/example/webhook/pull/51 (draft)

## 申し送り
- 配信ログの項目は event_id, delivery_id, attempt, status, http_status で確定

## Prototype
- 適合性: `app/webhook/deliver.py` の `WebhookClient.deliver` に `delivery_id` を渡す既存契約に合致 (案 A で検証)。呼び出し側 `app/webhook/dispatcher.py` に再試行ループを置く配置で責務分離を保てた
- 検証: 既存テストスイート pass、再試行 3 回で二重処理 0 件を再確認
- draft PR: https://github.com/example/webhook/pull/52
EOF
cat > templates/dd_template.md <<'EOF'
# サンプルプロジェクト

# **背景**

*\# 前提やこの施策を行う動機*

*

# **目的**

*\# プロジェクトの目的を端的に1-2行で*

*

# **やること**

*\# スコープ内で技術的にやることを箇条書きで列挙*

*

# **やらないこと**

*\# やることの対比で、スコープ外でやらないことを箇条書きで列挙*

*

# **概要**

*\# 概要設計・やることをどう実現するか*

*

# **詳細**

*\# 詳細設計（データフロー・スキーマ・失敗時の扱いなど）*

*

# **品質管理のプラン・リスクなど**

*\# この案件用にQAが作成したテスト計画があればリンクを貼る*

*

# **モニタリング**

*\# 計測するメトリクスや監視項目を設定する。既存メトリクスがあればリンクを貼る*

*

# **会計基盤連携**

*\# 会計基盤（LEDGER）へ仕訳データを連携する場合は、連携する勘定科目・連携タイミング・突合方法を記載し、経理システム部のレビューを受けてください。*

| 勘定科目 | 連携タイミング | 突合方法 |
| :---- | :---- | :---- |
|  |  |  |

- [ ] 経理システム部のレビュー済み

# **営業支援システム連携**

*\# 営業支援システム（SFA）への連携が必要そうな場合には、まず営業企画部に相談してください。*
*\# 例：新プランの追加、契約項目の追加、問い合わせ窓口の追加・変更など*

*

# **スケジュール**

*\# だいたいのスケジュールを載せる*

*

# **資料**

*\# 設計の元になった資料へのリンクを貼る*

*
EOF
```

承認済みの計画 `webhook/retry/plan.md` と、プロトタイプ追記済みの `webhook/retry/poc.md` を根拠に /create-design-doc をすすめましょう。方式は案 A を採用、失敗確定の通知は即時で進めてください。テンプレートは `templates/dd_template.md`、保存先は `webhook/retry/design-doc.md` です。
