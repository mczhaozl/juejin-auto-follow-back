# PostgreSQL 索引与查询优化实战：打造高性能数据库

> 深入讲解 PostgreSQL 索引类型、查询优化技巧和执行计划分析，帮你解决数据库性能瓶颈。

## 一、为什么需要索引

索引就像书籍的目录，没有索引意味着要全表扫描：

```sql
-- 没有索引：全表扫描
SELECT * FROM users WHERE name = '张三';

-- 有索引：快速定位
CREATE INDEX idx_users_name ON users(name);
```

## 二、索引类型详解

### 2.1 B-Tree 索引（默认）

适用于：=、>、<、>=、<=、BETWEEN、IN

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
```

### 2.2 Hash 索引

适用于：= 精确匹配

```sql
CREATE INDEX idx_users_phone ON users USING HASH(phone);
```

### 2.3 GIN 索引

适用于：数组、全文检索、JSONB

```sql
-- 数组索引
CREATE INDEX idx_tags ON posts USING GIN(tags);

-- JSONB 索引
CREATE INDEX idx_data ON logs USING GIN(data);
```

### 2.4 GiST 索引

适用于：地理位置、范围类型

```sql
-- 地理位置索引
CREATE INDEX idx_location ON places USING GIST(location);
```

### 2.5 复合索引

```sql
-- 多列索引
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);

-- 索引顺序重要！
-- 适用于: WHERE user_id = ? AND created_at > ?
-- 不适用于: WHERE created_at > ?
```

## 三、EXPLAIN 分析执行计划

### 3.1 基本用法

```sql
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 查看更详细信息
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT * FROM users WHERE email = 'test@example.com';
```

### 3.2 关键指标

| 操作 | 说明 |
|------|------|
| Seq Scan | 全表扫描（慢） |
| Index Scan | 索引扫描（快） |
| Index Only Scan | 索引覆盖扫描（最快） |
| Bitmap Scan | 位图扫描 |
| Nested Loop | 嵌套循环 |
| Hash Join | 哈希连接 |
| Merge Join | 归并连接 |

### 3.3 案例分析

```sql
EXPLAIN ANALYZE 
SELECT u.name, o.total 
FROM users u 
JOIN orders o ON u.id = o.user_id 
WHERE u.status = 'active';

-- 输出示例:
-- Nested Loop  (cost=0.85..1234.56 rows=100 width=64) (actual time=0.1..5.2 rows=100 loops=1)
--   ->  Index Scan using idx_users_status on users u  (cost=0.42..4.50 rows=10 width=32) (actual time=0.05..0.1 rows=10 loops=1)
--   ->  Index Scan using idx_orders_user on orders o  (cost=0.43..123.00 rows=10 width=32) (actual time=0.1..0.5 rows=10 loops=10)
```

## 四、查询优化技巧

### 4.1 避免 SELECT *

```sql
-- 慢
SELECT * FROM users WHERE id = 1;

-- 快：只查询需要的列
SELECT id, name, email FROM users WHERE id = 1;
```

### 4.2 使用覆盖索引

```sql
-- 索引包含所有查询的列
CREATE INDEX idx_users_email_name ON users(email, name);

-- 查询可直接从索引返回
SELECT name FROM users WHERE email = 'test@example.com';
```

### 4.3 避免函数操作

```sql
-- 慢：函数导致索引失效
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- 快：使用索引
SELECT * FROM users WHERE email = 'TEST@EXAMPLE.COM';

-- 如果必须使用函数
CREATE INDEX idx_users_email_lower ON users((LOWER(email)));
```

### 4.4 使用 LIMIT

```sql
-- 分页优化
SELECT * FROM orders 
WHERE user_id = 123 
ORDER BY created_at DESC 
LIMIT 10 OFFSET 1000;

-- 优化：使用游标
SELECT * FROM orders 
WHERE user_id = 123 
AND created_at < '2024-01-01'
ORDER BY created_at DESC 
LIMIT 10;
```

### 4.5 批量插入

```sql
-- 慢：逐条插入
INSERT INTO logs (message) VALUES ('msg1');
INSERT INTO logs (message) VALUES ('msg2');

-- 快：批量插入
INSERT INTO logs (message) VALUES ('msg1'), ('msg2'), ('msg3');

-- 更快：COPY
COPY logs(message) FROM STDIN;
```

## 五、索引设计原则

### 5.1 选择性高的列

```sql
-- 高选择性：适合建索引
CREATE INDEX idx_users_id ON users(id);

-- 低选择性：不适合建索引
CREATE INDEX idx_users_gender ON users(gender); -- 只有 male/female
```

### 5.2 覆盖查询

```sql
-- 查询 age 和 name
CREATE INDEX idx_users_age_name ON users(age, name);

-- 包含额外列（PostgreSQL 12+）
CREATE INDEX idx_users_age ON users(age) INCLUDE (name);
```

### 5.3 避免冗余索引

```sql
-- 冗余
CREATE INDEX idx1 ON users(age);
CREATE INDEX idx2 ON users(age, name);

-- 保留
CREATE INDEX idx ON users(age, name);
```

## 六、性能监控

### 6.1 查看索引使用

```sql
SELECT 
  schemaname,
  relname,
  indexrelname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### 6.2 查找未使用的索引

```sql
SELECT 
  indexrelname,
  idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexrelname NOT LIKE '%pkey%';
```

### 6.3 表大小和索引大小

```sql
SELECT 
  pg_size_pretty(pg_total_relation_size('users')),
  pg_size_pretty(pg_indexes_size('users')),
  pg_size_pretty(pg_relation_size('users'));
```

## 七、常见场景优化

### 7.1 分页查询

```sql
-- 传统 OFFSET/LIMIT（慢）
SELECT * FROM orders ORDER BY id LIMIT 10 OFFSET 10000;

-- 优化：游标分页
SELECT * FROM orders 
WHERE id > 10000 
ORDER BY id 
LIMIT 10;

-- 优化：时间分页
SELECT * FROM orders 
WHERE created_at < '2024-01-01'
ORDER BY created_at DESC 
LIMIT 10;
```

### 7.2 范围查询

```sql
-- 日期范围
CREATE INDEX idx_orders_date ON orders(created_at);

-- 多条件范围
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- 查询
SELECT * FROM orders 
WHERE user_id = 123 
AND created_at BETWEEN '2024-01-01' AND '2024-01-31';
```

### 7.3 全文检索

```sql
-- 创建全文检索索引
CREATE INDEX idx_posts_title ON posts USING GIN(to_tsvector('english', title));

-- 查询
SELECT * FROM posts 
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'postgres & optimization');
```

### 7.4 JSON 查询

```sql
-- JSONB 索引
CREATE INDEX idx_data ON logs USING GIN(data);

-- 查询
SELECT * FROM logs 
WHERE data->>'status' = 'error';

-- 包含索引
CREATE INDEX idx_data_path ON logs USING GIN((data->'user'->>'id'));
```

## 八、总结

PostgreSQL 优化核心要点：

1. **选择合适索引**：B-Tree、GIN、GiST 等
2. **分析执行计划**：EXPLAIN 是优化的关键
3. **避免全表扫描**：确保查询走索引
4. **合理设计索引**：考虑查询模式
5. **监控索引使用**：定期清理无用索引

记住：**测量后再优化**，不要猜测！

---

**推荐阅读**：
- [PostgreSQL 官方文档 - 索引](https://www.postgresql.org/docs/current/indexes.html)
- [EXPLAIN 分析指南](https://www.postgresql.org/docs/current/using-explain.html)

**如果对你有帮助，欢迎点赞收藏！**
