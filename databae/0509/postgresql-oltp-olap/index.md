# PostgreSQL OLTP 和 OLAP 优化完全指南

## 一、OLTP 优化

```sql
-- 索引优化（B-tree索引适合点查和范围查询）
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_date ON orders(order_date);

-- 事务优化
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- 连接池配置（PgBouncer）
-- server_tls_sslmode = prefer
-- pool_mode = transaction
```

## 二、OLAP 优化

```sql
-- 并行查询
SET max_parallel_workers_per_gather = 8;

-- 分析型查询（聚合、窗口函数）
EXPLAIN ANALYZE
SELECT
  date_trunc('month', order_date) AS month,
  category,
  SUM(total_amount),
  AVG(total_amount),
  COUNT(*)
FROM orders
JOIN order_items ON orders.id = order_items.order_id
JOIN products ON order_items.product_id = products.id
GROUP BY 1, 2;

-- 物化视图
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT
  date_trunc('month', order_date) AS month,
  category,
  SUM(total_amount) AS total
FROM orders
GROUP BY 1, 2;

-- 刷新物化视图
REFRESH MATERIALIZED VIEW monthly_sales;
```

## 三、混合负载策略

```sql
-- 读写分离：主库写，从库读
-- 配置连接池
-- 索引平衡
```

## 四、配置参数优化

```sql
-- postgresql.conf 调优
-- shared_buffers = 1/4 系统内存
-- work_mem = 32MB
-- maintenance_work_mem = 2GB
-- effective_cache_size = 3/4 系统内存
```

## 五、最佳实践

- OLTP：小事务、索引优化、连接池
- OLAP：并行查询、物化视图、列式存储
- 使用 EXPLAIN ANALYZE 分析慢查询
- 监控等待事件和性能指标
- 定期维护（VACUUM、ANALYZE）
- 考虑使用 TimescaleDB 等扩展
