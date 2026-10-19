---
max_turns: 15
timeout_seconds: 300
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p db
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
CREATE INDEX orders_customer_id_idx ON orders (customer_id);

CREATE TABLE order_items (
  id BIGINT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  sku VARCHAR(40) NOT NULL,
  quantity INTEGER NOT NULL
);
EOF
cat > db/explain.txt <<'EOF'
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.id, o.ref_no, COUNT(i.id) AS item_count
FROM orders o
JOIN order_items i ON i.order_id = o.id
WHERE o.customer_id = 1042
GROUP BY o.id, o.ref_no;

                                                                   QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------
 HashAggregate  (cost=52411.20..52429.80 rows=1860 width=29) (actual time=905.114..905.512 rows=1860 loops=1)
   Group Key: o.id
   Buffers: shared hit=1410 read=15843
   ->  Hash Join  (cost=1105.42..52320.10 rows=18200 width=25) (actual time=4.931..899.203 rows=18340 loops=1)
         Hash Cond: (i.order_id = o.id)
         Buffers: shared hit=1410 read=15843
         ->  Seq Scan on order_items i  (cost=0.00..43120.00 rows=2400000 width=16) (actual time=0.021..612.874 rows=2400000 loops=1)
               Buffers: shared hit=402 read=15843
         ->  Hash  (cost=1082.17..1082.17 rows=1860 width=25) (actual time=4.874..4.875 rows=1860 loops=1)
               Buckets: 2048  Batches: 1  Memory Usage: 118kB
               Buffers: shared hit=1008
               ->  Index Scan using orders_customer_id_idx on orders o  (cost=0.43..1082.17 rows=1860 width=25) (actual time=0.038..4.211 rows=1860 loops=1)
                     Index Cond: (customer_id = 1042)
                     Buffers: shared hit=1008
 Planning Time: 0.388 ms
 Execution Time: 906.044 ms
EOF
```

db/explain.txt の実行計画を読んで、このクエリが遅い理由を説明してください。
