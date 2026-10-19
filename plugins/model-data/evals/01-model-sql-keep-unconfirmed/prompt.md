---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p docs db
cat > docs/requirements.md <<'EOF'
# 受注管理の要求

## 確定している要求

- 顧客は複数の受注を持つ。受注を一件も持たない顧客もいる。
- 受注は必ず一人の顧客に属する。
- 受注は一件以上の明細を持つ。明細は必ず一つの受注に属する。
- 各テーブルの `id` は主キーとする。`customer_id` と `order_id` は必須の外部キーとする。
- 受注が確定したあとに、請求書を作る。請求書は請求額 (`amount`) と支払期限 (`due_date`) を持つ。

## 前提

- 請求書のテーブルは請求システムの DB にあり、この repository の `db/` には含まれない。請求システムの DB は本番環境にしか無く、開発者は接続できない。
- 既存の `orders.ref_no` には、確定前は見積番号 (`Q-` で始まる)、確定後は受注番号 (`O-` で始まる) が入る。
- 既存の `orders.item_ids` には、その受注の明細の id をカンマ区切りで入れている。
EOF
cat > db/schema.sql <<'EOF'
CREATE TABLE customers (
  id BIGINT PRIMARY KEY,
  name VARCHAR(200) NOT NULL
);

CREATE TABLE orders (
  id BIGINT PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customers (id),
  ref_no VARCHAR(20) NOT NULL,
  item_ids TEXT NOT NULL,
  ordered_at TIMESTAMP NOT NULL
);

CREATE TABLE order_items (
  id BIGINT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  sku VARCHAR(40) NOT NULL,
  quantity INTEGER NOT NULL
);
EOF
cat > db/queries.sql <<'EOF'
SELECT o.id, o.ref_no
FROM orders o
WHERE ',' || o.item_ids || ',' LIKE '%,1002,%';

SELECT id, ordered_at FROM orders WHERE ref_no LIKE 'Q-%';

SELECT id, ordered_at FROM orders WHERE ref_no LIKE 'O-%';

SELECT c.id, c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name;

SELECT order_id, COUNT(*) AS item_count
FROM order_items
GROUP BY order_id;
EOF
```

docs/requirements.md を参考に /model-data して、docs/order-model.dbml と docs/order-model-review.md に出力してください。受注まわりについて、要求と既存スキーマ (db/ 配下の SQL) の関係をデータモデルレベルで理解したいためです。docs/order-model.dbml にはモデルを DBML で、docs/order-model-review.md にはモデルの説明と、既存 SQL の問題点や確認が必要な点を書いてください。書き込んでよいのはこの 2 ファイルだけで、ほかのファイルは読み取りのみです。
