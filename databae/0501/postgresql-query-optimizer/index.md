# PostgreSQL 查询优化器深度解析：从 EXPLAIN 到执行计划调优

## 一、查询优化器概述

### 1.1 优化器的作用

PostgreSQL 查询优化器负责将 SQL 查询转换为最有效的执行计划。

### 1.2 优化器类型

- **基于规则的优化器（RBO）**：基于预定义规则
- **基于成本的优化器（CBO）**：基于成本估算（PostgreSQL 使用）

---

## 二、EXPLAIN 基础

### 2.1 基本用法

```sql
EXPLAIN SELECT * FROM users WHERE id = 1;
```

### 2.2 EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;
```

### 2.3 EXPLAIN 选项

```sql
EXPLAIN (
  ANALYZE,
  VERBOSE,
  COSTS,
  BUFFERS,
  TIMING,
  SUMMARY,
  FORMAT JSON
) SELECT * FROM users WHERE id = 1;
```

### 2.4 阅读执行计划

```
Seq Scan on users  (cost=0.00..100.00 rows=1000 width=100)
  Filter: (id = 1)
```

- **Seq Scan**：执行的操作
- **cost**：0.00（启动成本）..100.00（总成本）
- **rows**：预计返回行数
- **width**：平均行宽（字节）

---

## 三、常见扫描操作

### 3.1 顺序扫描（Seq Scan）

```sql
-- 没有索引或选择率高时
EXPLAIN SELECT * FROM users WHERE status = 'active';
```

### 3.2 索引扫描（Index Scan）

```sql
-- 使用索引查找行
EXPLAIN SELECT * FROM users WHERE id = 1;
```

### 3.3 仅索引扫描（Index Only Scan）

```sql
-- 查询列都在索引中
EXPLAIN SELECT id FROM users WHERE id = 1;
```

### 3.4 位图扫描（Bitmap Scan）

```sql
-- 多个条件组合
EXPLAIN SELECT * FROM users WHERE status = 'active' AND age > 18;
```

---

## 四、连接操作

### 4.1 嵌套循环连接（Nested Loop）

```sql
-- 小表驱动大表
EXPLAIN
SELECT *
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.id = 1;
```

### 4.2 哈希连接（Hash Join）

```sql
-- 大表连接
EXPLAIN
SELECT *
FROM orders o
JOIN users u ON o.user_id = u.id;
```

### 4.3 归并连接（Merge Join）

```sql
-- 数据已排序
EXPLAIN
SELECT *
FROM orders o
JOIN users u ON o.user_id = u.id
ORDER BY o.user_id;
```

---

## 五、排序操作

### 5.1 内存排序

```sql
-- work_mem 足够大
EXPLAIN ANALYZE SELECT * FROM users ORDER BY created_at;
```

### 5.2 磁盘排序

```sql
-- work_mem 不足，使用临时文件
SET work_mem = '64kB';
EXPLAIN ANALYZE SELECT * FROM users ORDER BY created_at;
```

### 5.3 索引排序

```sql
-- 使用索引避免排序
CREATE INDEX idx_users_created_at ON users(created_at);
EXPLAIN ANALYZE SELECT * FROM users ORDER BY created_at;
```

---

## 六、查询优化技巧

### 6.1 索引优化

```sql
-- 创建复合索引
CREATE INDEX idx_users_status_age ON users(status, age);

-- 部分索引
CREATE INDEX idx_active_users ON users(id) WHERE status = 'active';

-- 表达式索引
CREATE INDEX idx_users_lower_email ON users(lower(email));
```

### 6.2 重写查询

```sql
-- 避免 SELECT *
SELECT id, name FROM users WHERE id = 1;

-- 使用 JOIN 代替子查询
SELECT u.* FROM users u JOIN orders o ON u.id = o.user_id WHERE o.amount > 100;

-- 使用 UNION ALL 代替 OR
SELECT * FROM users WHERE status = 'active'
UNION ALL
SELECT * FROM users WHERE status = 'pending';
```

### 6.3 统计信息

```sql
-- 更新统计信息
ANALYZE users;

-- 查看统计信息
SELECT * FROM pg_stats WHERE tablename = 'users';

-- 调整统计信息收集
ALTER TABLE users ALTER COLUMN status SET STATISTICS 1000;
```

---

## 七、配置参数调优

### 7.1 内存配置

```sql
-- 工作内存（排序、哈希）
SET work_mem = '64MB';

-- 维护内存（CREATE INDEX、VACUUM）
SET maintenance_work_mem = '1GB';

-- 共享缓冲区
SET shared_buffers = '8GB';
```

### 7.2 优化器开关

```sql
-- 禁用某些操作
SET enable_seqscan = off;
SET enable_nestloop = off;
SET enable_hashjoin = off;
SET enable_mergejoin = off;

-- 成本参数
SET random_page_cost = 1.1;
SET effective_cache_size = '24GB';
```

---

## 八、实际案例分析

### 8.1 慢查询诊断

```sql
-- 查看活跃查询
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- 查看慢查询
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 分析表
SELECT
  schemaname,
  tablename,
  seq_scan,
  seq_tup_read,
  idx_scan,
  idx_tup_fetch
FROM pg_stat_user_tables
WHERE tablename = 'users';
```

### 8.2 性能优化实例

```sql
-- 优化前：顺序扫描
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- 创建索引
CREATE INDEX idx_users_email ON users(email);

-- 优化后：索引扫描
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

---

## 总结

理解 PostgreSQL 查询优化器和执行计划是性能调优的关键。通过合理使用索引、重写查询和调整配置，可以显著提升查询性能。
