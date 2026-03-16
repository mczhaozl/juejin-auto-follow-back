# PostgreSQL 索引与查询优化深度指南

> 从原理到实战，全面掌握 PostgreSQL 索引设计与查询优化技巧

## 一、PostgreSQL 索引基础

### 1.1 什么是索引

索引是数据库系统中用于加速数据检索的特殊数据结构。它类似于书籍的目录，允许数据库引擎快速定位到所需的数据，而无需扫描整个表。在 PostgreSQL 中，索引本质上是一种数据结构（通常是 B-tree），它存储了索引列的值以及这些值在表中的物理位置信息。

索引的核心价值在于将全表扫描的 O(n) 时间复杂度降低到 O(log n) 或 O(1)。对于大型数据集，这种差异可能是几分钟与几毫秒的区别。然而，索引并非没有代价——每个索引都会占用额外的存储空间，并且在数据修改时需要维护索引的一致性，这会增加写入操作的开销。

理解索引的工作原理对于设计高效的数据库 schema 和编写优化的查询至关重要。PostgreSQL 提供了多种类型的索引，每种索引都针对特定的数据特征和查询模式进行了优化。选择正确的索引类型和正确的列是查询优化的关键。

### 1.2 索引的类型

PostgreSQL 支持多种索引类型，每种类型都有其特定的适用场景和性能特征。

B-tree 是 PostgreSQL 的默认索引类型，适用于可以比较排序的数据。B-tree 索引在处理等值查询和范围查询时表现优异，支持的操作符包括 =、<、>、<=、>= 以及 BETWEEN 和 IN。B-tree 索引对于排序操作也有优化，可以加速 ORDER BY 子句的执行。

Hash 索引只支持等值查询，不支持范围查询和排序。虽然在某些特定场景下 Hash 索引可能比 B-tree 更快，但由于其功能限制和较少的优化空间，在实际应用中很少使用。

GiST（Generalized Search Tree）索引适用于几何数据和全文搜索场景。它支持复杂的空间查询，如包含、相交、距离计算等。PostGIS 扩展广泛使用 GiST 索引来处理地理空间数据。

SP-GiST（Space-Partitioned GiST）索引适用于数据具有自然聚类特征的场景，如电话号码、IP 地址等。它在处理低维度数据时比 GiST 更高效。

BRIN（Block Range Index）索引适用于非常大的表，其中数据在物理上按索引列有序排列。BRIN 索引非常小，适合处理时间序列数据等按时间顺序插入的数据。

### 1.3 创建索引的基本语法

```sql
-- 创建 B-tree 索引（默认类型）
CREATE INDEX idx_user_email ON users(email);

-- 创建唯一索引
CREATE UNIQUE INDEX idx_user_username ON users(username);

-- 创建多列索引
CREATE INDEX idx_order_composite ON orders(customer_id, order_date DESC);

-- 创建表达式索引
CREATE INDEX idx_user_lower_email ON users(LOWER(email));

-- 创建部分索引
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- 创建并发索引（不阻塞写入）
CREATE INDEX CONCURRENTLY idx_user_phone ON users(phone);
```

## 二、索引设计原则

### 2.1 选择正确的列

并非所有列都需要索引，索引的设计需要权衡查询性能和写入开销。以下是选择索引列的一般原则。

查询条件中频繁使用的列是索引的首选候选。这包括 WHERE 子句中的列、JOIN 条件中的列以及 ORDER BY 子句中的列。主键和唯一约束自动创建索引，因此不需要额外考虑。

外键列应该建立索引，因为 PostgreSQL 在执行参照完整性检查时需要频繁查询这些列。没有索引的外键会导致级联操作（如 DELETE 或 UPDATE）性能严重下降。

低选择性的列不适合建立单列索引。选择性是指列中不同值的比例。如果一个列只有几个不同的值（如性别、状态），即使建立了索引，优化器也可能选择全表扫描而非索引扫描。

```sql
-- 低选择性列示例
-- status 列只有几个值，索引效果有限
CREATE INDEX idx_orders_status ON orders(status);

-- 高选择性列示例
-- order_id 是主键，索引效果极佳
-- PostgreSQL 自动为主键创建索引
```

### 2.2 复合索引的设计

复合索引（多列索引）在多个列的查询中非常有用，但设计时需要考虑列的顺序和查询模式。

列的顺序至关重要。复合索引遵循最左前缀原则，即查询只能使用索引的前缀列。例如，索引 (a, b, c) 可以加速查询 WHERE a = ? AND b = ?，但无法加速 WHERE b = ? AND c = ?。

将选择性高的列放在前面可以提高索引的效率。同时，需要分析实际查询模式，将经常一起出现在 WHERE 子句中的列放在一起。

```sql
-- 复合索引设计示例
-- 常见查询模式
-- SELECT * FROM orders WHERE customer_id = ? AND order_date >= ?
-- SELECT * FROM orders WHERE customer_id = ?

-- 正确的索引设计
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date DESC);

-- 这个索引可以同时支持上述两个查询
-- 因为 customer_id 是最左列
```

### 2.3 部分索引与表达式索引

部分索引只对满足特定条件的行创建，可以显著减小索引大小并提高查询效率。表达式索引允许在索引中使用表达式或函数，这对于处理大小写不敏感查询或计算列非常有用。

```sql
-- 部分索引：只索引活跃用户
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- 这个索引只包含 status = 'active' 的行
-- 体积更小，查询更快

-- 表达式索引：大小写不敏感查询
CREATE INDEX idx_user_lower_email ON users(LOWER(email));

-- 支持 LOWER(email) = 'test@example.com' 的查询
-- 无需在查询中显式使用 LOWER()

-- 表达式索引：计算列
CREATE INDEX idx_orders_year ON orders(EXTRACT(YEAR FROM order_date));

-- 支持按年份分组的查询
```

## 三、查询执行计划分析

### 3.1 EXPLAIN 命令

EXPLAIN 命令是 PostgreSQL 提供的强大工具，用于查看查询的执行计划。理解执行计划是查询优化的基础，它揭示了数据库引擎如何执行你的查询。

```sql
-- 基本用法
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 显示实际执行时间
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- 显示缓冲区使用情况
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE email = 'test@example.com';

-- 显示格式化输出
EXPLAIN (FORMAT JSON) SELECT * FROM users WHERE email = 'test@example.com';
```

### 3.2 执行计划节点类型

PostgreSQL 的执行计划由多种节点组成，每个节点代表一个特定的操作。理解这些节点对于识别性能瓶颈至关重要。

Seq Scan（顺序扫描）是最基本的扫描方式，它读取表中的每一行。对于小表或没有合适索引的查询，顺序扫描可能是最优选择。但对于大表，顺序扫描的性能通常较差。

Index Scan（索引扫描）使用索引来定位表中的行。它首先在索引中查找匹配的行，然后根据索引中的指针读取实际的表数据。Index Scan 通常比顺序扫描快得多，特别是当只返回少量行时。

Index Only Scan（仅索引扫描）是 Index Scan 的优化版本。如果查询所需的全部数据都包含在索引中，PostgreSQL 可以只读取索引而不访问表数据。这种扫描方式非常高效。

Bitmap Index Scan（位图索引扫描）使用位图来组合多个索引的结果。当查询条件涉及多个索引列时，PostgreSQL 可能使用位图索引扫描来合并结果。

Nested Loop（嵌套循环）用于连接两个表。对于小表驱动大表的情况，嵌套循环非常高效。

Hash Join（哈希连接）使用哈希表来连接两个表。对于大表的等值连接，哈希连���通常比嵌套循环更高效。

Merge Join（归并连接）要求两个表都已排序。对于已经有序的数据或需要排序的查询，归并连接是高效的选择。

```sql
-- 查看执行计划示例
EXPLAIN ANALYZE
SELECT u.username, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.username;

-- 输出示例
-- GroupAggregate  (cost=125.43..125.48 rows=1 width=45) (actual time=2.156..2.157 rows=1 loops=1)
--   ->  Nested Loop Left Join  (cost=0.29..125.41 rows=10 width=45) (actual time=0.045..2.100 rows=100 loops=1)
--         ->  Index Scan using idx_users_created_at on users u  (cost=0.29..8.31 rows=10 width=45) (actual time=0.025..0.050 rows=10 loops=1)
--               Index Cond: (created_at > '2024-01-01'::timestamp)
--         ->  Index Scan using idx_orders_user_id on orders o  (cost=0.29..11.71 rows=10 width=8) (actual time=0.015..0.200 rows=10 loops=10)
--               Index Cond: (user_id = u.id)
-- Planning Time: 0.234 ms
-- Execution Time: 2.312 ms
```

### 3.3 成本估算

PostgreSQL 使用成本模型来选择最优的执行计划。成本是一个相对值，表示查询执行的估计开销。理解成本计算有助于理解优化器的选择。

成本由多个因素决定，包括磁盘 I/O 成本、CPU 成本、内存使用等。seq_page_cost 表示顺序读取一个磁盘页的成本，random_page_cost 表示随机读取一个磁盘页的成本。cpu_tuple_cost 表示处理每一行的 CPU 成本。

```sql
-- 查看当前成本参数
SHOW seq_page_cost;
SHOW random_page_cost;
SHOW cpu_tuple_cost;
SHOW cpu_index_tuple_cost;

-- 临时调整成本参数（用于测试）
SET seq_page_cost = 1.0;
SET random_page_cost = 1.0;

-- 重新执行查询，查看执行计划变化
EXPLAIN (ANALYZE) SELECT * FROM users WHERE id = 1;
```

## 四、查询优化技巧

### 4.1 WHERE 子句优化

WHERE 子句中的条件顺序会影响查询性能。PostgreSQL 会根据统计信息自动优化条件的执行顺序，但了解其原理有助于编写更高效的查询。

将选择性高的条件放在前面可以减少后续处理的数据量。使用函数或表达式在索引列上会阻止索引的使用，应该尽量避免或在索引中使用表达式。

```sql
-- 低效：函数阻止索引使用
SELECT * FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2024;

-- 高效：使用表达式索引
CREATE INDEX idx_orders_year ON orders(EXTRACT(YEAR FROM order_date));
SELECT * FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2024;

-- 低效：OR 条件可能阻止索引使用
SELECT * FROM users WHERE status = 'active' OR status = 'pending';

-- 高效：使用 IN 替代 OR
SELECT * FROM users WHERE status IN ('active', 'pending');

-- 低效：LIKE 模式以通配符开头
SELECT * FROM products WHERE name LIKE '%laptop%';

-- 高效：避免前导通配符或使用全文搜索
SELECT * FROM products WHERE name ILIKE '%laptop%';  -- 仍然无法使用索引
-- 考虑使用 PostgreSQL 的全文搜索功能
```

### 4.2 JOIN 优化

JOIN 是查询性能问题的常见来源。优化 JOIN 需要考虑索引、连接顺序和连接类型的选择。

确保连接列上有索引。外键列应该始终有索引，这不仅加速 JOIN 操作，还加速参照完整性检查。

```sql
-- 确保连接列有索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- 优化 JOIN 查询
EXPLAIN ANALYZE
SELECT u.username, p.name as product_name, oi.quantity
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.created_at > '2024-01-01';
```

### 4.3 子查询优化

子查询可以转换为 JOIN 以获得更好的性能。PostgreSQL 的优化器会自动进行一些转换，但手动优化可能带来更好的效果。

IN 子查询在 PostgreSQL 中通常会被优化为 JOIN，但 EXISTS 子查询在某些情况下可能更高效，特别是当只需要检查存在性时。

```sql
-- 子查询示例
SELECT * FROM products p
WHERE EXISTS (
  SELECT 1 FROM order_items oi
  JOIN orders o ON oi.order_id = o.id
  WHERE oi.product_id = p.id
  AND o.created_at > '2024-01-01'
);

-- 转换为 JOIN
SELECT DISTINCT p.*
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
WHERE o.created_at > '2024-01-01';
```

### 4.4 分页查询优化

分页查询是 Web 应用中常见的模式。传统的 OFFSET/LIMIT 在大偏移量时性能很差，因为数据库需要扫描并丢弃大量行。

```sql
-- 低效的分页查询
SELECT * FROM orders ORDER BY created_at DESC LIMIT 50 OFFSET 10000;
-- 当 OFFSET 很大时，性能急剧下降

-- 高效的分页查询：使用游标
SELECT * FROM orders
WHERE created_at < '2024-01-15 00:00:00'
ORDER BY created_at DESC
LIMIT 50;

-- 使用 keyset 游标
SELECT * FROM orders
WHERE (created_at, id) < (last_seen_created_at, last_seen_id)
ORDER BY created_at DESC, id DESC
LIMIT 50;

-- 在应用层保存上一页的最后一条记录的信息
-- 上一页最后一条：created_at = '2024-01-10 12:00:00', id = 12345
-- 下一页查询：
SELECT * FROM orders
WHERE (created_at, id) < ('2024-01-10 12:00:00', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

## 五、索引维护与监控

### 5.1 索引膨胀

随着数据的增删改，索引可能会产生膨胀（bloat），即索引中包含大量已删除或过时的条目。这会导致索引变大、查询变慢。

```sql
-- 检查索引膨胀
-- 使用 pgstattuple 扩展
CREATE EXTENSION IF NOT EXISTS pgstattuple;

SELECT indexname, index_size, tuple_count, tuple_len, dead_tuple_count, dead_tuple_len
FROM pgstatindex('idx_user_email');

-- 估算索引膨胀
SELECT
  n.nspname,
  c.relname AS index_name,
  pg_size_pretty(pg_relation_size(n.nspname || '.' || c.relname::text)) AS index_size,
  pg_size_pretty(pg_total_relation_size(n.nspname || '.' || c.relname::text)) AS total_size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'i'
ORDER BY pg_relation_size(n.nspname || '.' || c.relname::text) DESC;
```

### 5.2 重建索引

当索引膨胀严重时，需要重建索引以恢复性能。PostgreSQL 提供了多种重建索引的方法。

```sql
-- 传统方法：REINDEX（会阻塞写入）
REINDEX INDEX idx_user_email;

-- PostgreSQL 12+：CONCURRENTLY（不阻塞写入）
REINDEX INDEX CONCURRENTLY idx_user_email;

-- 重建表的所有索引
REINDEX TABLE CONCURRENTLY users;

-- 使用 CREATE INDEX CONCURRENTLY ... DROP INDEX 旧索引
-- 这种方法在 PostgreSQL 12+ 可以用 REINDEX CONCURRENTLY 替代
```

### 5.3 统计信息

PostgreSQL 使用统计信息来优化查询计划。定期更新统计信息可以确保优化器做出正确的选择。

```sql
-- 更新表的统计信息
ANALYZE users;

-- 更新特定列的统计信息
ANALYZE users(email);

-- 自动收集统计信息
-- PostgreSQL 的 autovacuum 会自动执行 ANALYZE

-- 查看统计信息
SELECT * FROM pg_stats WHERE tablename = 'users';
```

### 5.4 监控查询性能

```sql
-- 查看当前运行的查询
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC
LIMIT 10;

-- 查看查询统计
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 启用 pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

## 六、高级索引技术

### 6.1 覆盖索引

��盖索引包含查询所需的所有列，PostgreSQL 可以通过 Index Only Scan 直接从索引中获取数据，而无需访问表。

```sql
-- 创建覆盖索引
CREATE INDEX idx_orders_covering ON orders(user_id, order_date, status)
INCLUDE (total_amount);

-- 这个索引可以支持以下查询的 Index Only Scan
SELECT order_date, status, total_amount
FROM orders
WHERE user_id = 123
AND order_date > '2024-01-01';

-- 检查是否使用了覆盖索引
EXPLAIN (ANALYZE)
SELECT order_date, status, total_amount
FROM orders
WHERE user_id = 123
AND order_date > '2024-01-01';
```

### 6.2 条件索引

条件索引（部分索引）只对满足特定条件的行创建索引，可以显著减小索引大小并提高查询效率。

```sql
-- 只索引最近一年的订单
CREATE INDEX idx_orders_recent ON orders(order_date DESC)
WHERE order_date > CURRENT_DATE - INTERVAL '1 year';

-- 只索引已完成的订单
CREATE INDEX idx_orders_completed ON orders(user_id, order_date DESC)
WHERE status = 'completed';

-- 只索引大额订单
CREATE INDEX idx_orders_large ON orders(total_amount)
WHERE total_amount > 10000;
```

### 6.3 排序优化

对于 ORDER BY 和 LIMIT 结合的查询，合适的索引可以避免显式的排序操作。

```sql
-- 创建支持排序的索引
CREATE INDEX idx_orders_date_status ON orders(order_date DESC, status);

-- 这个索引可以加速以下查询
SELECT * FROM orders
WHERE status = 'completed'
ORDER BY order_date DESC
LIMIT 10;

-- PostgreSQL 可以使用索引扫描，避免额外的排序操作
```

### 6.4 全文搜索索引

PostgreSQL 内置的全文搜索功能使用特殊的索引类型。

```sql
-- 创建全文搜索索引
ALTER TABLE products ADD COLUMN search_vector tsvector;

-- 更新搜索向量
UPDATE products
SET search_vector = to_tsvector('english', name || ' ' || description);

-- 创建 GIN 索引
CREATE INDEX idx_products_search ON products USING GIN(search_vector);

-- 使用全文搜索
SELECT * FROM products
WHERE search_vector @@ to_tsquery('english', 'laptop & gaming')
ORDER BY ts_rank(search_vector, to_tsquery('english', 'laptop & gaming')) DESC;
```

## 七、常见性能问题与解决方案

### 7.1 缺失索引

最常见的性能问题是查询缺少必要的索引。

```sql
-- 识别缺失的索引
-- 查找经常被顺序扫描的大表
SELECT relname, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_scan DESC;

-- 查找没有索引的外键
SELECT conname, conrelid::regclass AS table_name
FROM pg_constraint
WHERE contype = 'f'
AND NOT EXISTS (
  SELECT 1 FROM pg_index
  WHERE pg_index.indrelid = conrelid
  AND pg_index.indkey[0] = conattnum[0]
);
```

### 7.2 索引未被使用

有时创建了索引但查询并未使用，这可能是由于统计信息过时或查询模式不匹配。

```sql
-- 查找未被使用的索引
SELECT indexrelid::regclass AS index_name, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname = 'public';

-- 可能的原因：
-- 1. 统计信息过时 - 运行 ANALYZE
-- 2. 查询模式不匹配 - 检查查询是否使用了索引列
-- 3. 索引列选择性太低 - 考虑使用部分索引
```

### 7.3 锁等待问题

长时间运行的查询和索引创建可能导致锁等待。

```sql
-- 查看当前锁等待
SELECT wait_event_type, wait_event, state, query
FROM pg_stat_activity
WHERE wait_event IS NOT NULL;

-- 查看锁持有情况
SELECT l.locktype, l.mode, l.granted, a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.database = (SELECT oid FROM pg_database WHERE datname = current_database());
```

### 7.4 连接池配置

对于高并发应用，连接池配置对性能影响显著。

```sql
-- 查看当前连接数
SELECT count(*) FROM pg_stat_activity;

-- 查看最大连接数
SHOW max_connections;

-- 推荐使用连接池工具如 PgBouncer 或 PgPool-II
-- 配置示例（pgbouncer.ini）
-- [databases]
-- mydb = host=localhost port=5432 dbname=mydb

-- [pgbouncer]
-- pool_mode = transaction
-- max_client_conn = 100
-- default_pool_size = 20
```

## 八、性能调优最佳实践

### 8.1 定期维护任务

```sql
-- 创建定期维护函数
CREATE OR REPLACE FUNCTION maintenance_routine()
RETURNS void AS $$
BEGIN
  -- 更新统计信息
  ANALYZE;
  
  -- 清理死元组
  VACUUM ANALYZE;
  
  -- 重建膨胀严重的索引
  -- 需要根据实际情况调整
END;
$$ LANGUAGE plpgsql;

-- 使用 cron 或 pg_cron 调度
-- SELECT cron.schedule('daily-maintenance', '0 2 * * *', 'SELECT maintenance_routine()');
```

### 8.2 查询优化检查清单

在进行查询优化时，应该系统地检查以下方面。

首先，确认查询是否使用了索引。查看执行计划中的扫描类型，确认是否使用了 Index Scan 或 Index Only Scan。

其次，检查连接顺序。对于多表连接，确认驱动表的选择是否合理。驱动表应该是返回行数最少的表。

第三，验证选择性估计。查看执行计划中的行数估计是否与实际接近。如果估计与实际差异很大，可能需要更新统计信息或调整成本参数。

第四，考虑覆盖索引。对于频繁执行的查询，检查是否可以创建覆盖索引以避免表访问。

第五，评估查询重写。有时重写查询可以带来更好的性能，如将子查询转换为 JOIN。

### 8.3 监控与告警

```sql
-- 创建性能监控视图
CREATE VIEW performance_overview AS
SELECT
  (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') AS active_connections,
  (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') AS idle_connections,
  (SELECT count(*) FROM pg_stat_activity WHERE wait_event IS NOT NULL) AS waiting_queries,
  (SELECT pg_database_size(current_database()) / 1024 / 1024) AS db_size_mb,
  (SELECT SUM(idx_scan) FROM pg_stat_user_tables) AS total_index_scans,
  (SELECT SUM(seq_scan) FROM pg_stat_user_tables) AS total_seq_scans;

-- 创建慢查询告警
CREATE OR REPLACE FUNCTION check_slow_queries()
RETURNS trigger AS $$
BEGIN
  IF NEW.mean_time > 1000 THEN
    PERFORM pg_notify('slow_query', NEW.query);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER slow_query_alert
AFTER INSERT ON pg_stat_statements
FOR EACH ROW EXECUTE FUNCTION check_slow_queries();
```

## 九、总结

PostgreSQL 的索引和查询优化是一个复杂但非常重要的主题。掌握索引类型的选择、索引设计原则、查询计划分析技巧以及性能监控方法，是构建高性能数据库应用的关键。

索引的设计需要根据实际的查询模式来进行。没有放之四海而皆准的最佳实践，关键是理解业务需求，分析查询模式，然后选择合适的索引策略。

查询优化是一个持续的过程。随着数据量和业务逻辑的变化，需要不断监控性能，调整索引策略，优化查询语句。PostgreSQL 提供了丰富的工具来帮助我们完成这项工作，包括 EXPLAIN ANALYZE、pg_stat_statements、pgstattuple 等。

最后，记住性能优化应该基于数据而非猜测。使用 EXPLAIN ANALYZE 查看实际的执行计划，使用 pg_stat_statements 识别真正的性能瓶颈，然后有针对性地进行优化。这样才能确保优化工作产生实际的效果。