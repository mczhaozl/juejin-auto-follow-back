# MySQL 查询优化完全指南：执行计划与性能调优

> 深入讲解 MySQL 查询优化，包括执行计划分析、索引优化、SQL 调优技巧，以及慢查询分析和性能监控。

## 一、执行计划

### 1.1 EXPLAIN

```sql
EXPLAIN SELECT * FROM users WHERE id = 1;
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE name = '张三';
```

### 1.2 关键字段

| 字段 | 说明 |
|------|------|
| type | 连接类型 |
| key | 使用的索引 |
| rows | 扫描行数 |
| Extra | 额外信息 |

### 1.3 type 类型

```
const > eq_ref > ref > range > index > ALL
```

## 二、索引优化

### 2.1 避免全表扫描

```sql
-- 不好
SELECT * FROM users WHERE YEAR(created_at) = 2024;

-- 好
SELECT * FROM users WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';
```

### 2.2 覆盖索引

```sql
-- 索引覆盖查询
CREATE INDEX idx_name ON users(name);
SELECT name FROM users WHERE name = '张三';
```

### 2.3 最左前缀

```sql
-- 复合索引
CREATE INDEX idx_a_b ON users(a, b, c);

-- 使用索引
WHERE a = 1
WHERE a = 1 AND b = 2
WHERE a = 1 AND b = 2 AND c = 3

-- 不使用索引
WHERE b = 2
WHERE c = 3
```

## 三、SQL 优化

### 3.1 SELECT 优化

```sql
-- 避免 SELECT *
SELECT id, name, email FROM users;

-- 使用 LIMIT
SELECT * FROM users LIMIT 10;
```

### 3.2 JOIN 优化

```sql
-- 小表驱动大表
SELECT * FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE u.status = 1;

-- 添加索引
CREATE INDEX idx_user_id ON orders(user_id);
```

### 3.3 分页优化

```sql
-- 慢
SELECT * FROM orders LIMIT 100000, 10;

-- 快 - 游标分页
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 10;
```

## 四、慢查询

### 4.1 开启慢查询

```sql
SHOW VARIABLES LIKE 'slow_query_log%';

SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

### 4.2 分析工具

```bash
# mysqldumpslow
mysqldumpslow -s t /var/log/mysql/slow.log | head -10
```

## 五、总结

MySQL 优化核心要点：

1. **EXPLAIN**：分析执行计划
2. **索引**：合理创建使用
3. **SQL**：避免全表扫描
4. **分页**：游标分页
5. **慢查询**：监控分析

掌握这些，MySQL 性能飞起来！

---

**推荐阅读**：
- [MySQL 优化官方指南](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)

**如果对你有帮助，欢迎点赞收藏！**
