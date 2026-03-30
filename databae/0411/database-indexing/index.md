# 数据库索引完全指南：MySQL 索引设计与优化

> 深入讲解 MySQL 索引原理，包括 B+Tree、索引类型、SQL 优化，以及实际项目中的索引设计最佳实践。

## 一、索引基础

### 1.1 什么是索引

索引是数据结构，帮助快速定位数据：

```sql
-- 无索引 - 全表扫描
SELECT * FROM users WHERE name = '张三';

-- 有索引 - 快速查找
SELECT * FROM users WHERE id = 1;  -- 主键索引
```

### 1.2 索引优缺点

| 优点 | 缺点 |
|------|------|
| 加快查询速度 | 占用磁盘空间 |
| 减少 I/O 操作 | 增删改时需要维护 |
| 支持唯一性 | 过多索引影响性能 |

## 二、索引类型

### 2.1 主键索引

```sql
-- 主键自动创建索引
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);
```

### 2.2 唯一索引

```sql
-- 唯一索引
CREATE UNIQUE INDEX idx_email ON users(email);

-- 表创建时定义
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(100) UNIQUE
);
```

### 2.3 普通索引

```sql
-- 普通索引
CREATE INDEX idx_name ON users(name);

-- 复合索引
CREATE INDEX idx_name_age ON users(name, age);
```

### 2.4 全文索引

```sql
-- 全文索引
CREATE FULLTEXT INDEX idx_content ON articles(content);
```

## 三、B+Tree 原理

### 3.1 数据结构

```
        [50 | 100]
       /    |    \
  [10|20] [50|60] [100|120]
```

### 3.2 特点

- 所有数据在叶子节点
- 叶子节点链表连接
- 适合范围查询

## 四、索引设计

### 4.1 选择列

```sql
-- WHERE 条件
WHERE user_id = ?
WHERE status = ? AND date > ?

-- JOIN 条件
ON a.id = b.user_id

-- 排序
ORDER BY created_at
```

### 4.2 复合索引

```sql
-- 顺序很重要
CREATE INDEX idx_status_date ON orders(status, created_at);

-- 遵循最左前缀
WHERE status = ?           -- 使用索引
WHERE status = ? AND date > ?  -- 使用索引
WHERE date > ?             -- 不使用索引
```

### 4.3 注意事项

```sql
-- 不适合建索引
SELECT * FROM users WHERE LEFT(name, 1) = '张';

-- 不适合区分度低的列
-- 如性别、状态（值太少）

-- 避免过多索引
-- 每次 INSERT/UPDATE 需要维护
```

## 五、SQL 优化

### 5.1 慢查询分析

```sql
-- 开启慢查询日志
SHOW VARIABLES LIKE 'slow_query_log';

-- 查看慢查询
SHOW VARIABLES LIKE 'long_query_time';

-- 分析 EXPLAIN
EXPLAIN SELECT * FROM users WHERE name = '张三';
```

### 5.2 EXPLAIN 解读

```sql
EXPLAIN SELECT * FROM users WHERE id = 1;

-- type: const > eq_ref > ref > range > index > ALL
-- key: 使用的索引
-- rows: 扫描行数
```

### 5.3 优化技巧

```sql
-- 避免 SELECT *
SELECT id, name FROM users WHERE id = 1;

-- 避免函数操作
WHERE YEAR(created_at) = 2024  -- 不用索引
WHERE created_at >= '2024-01-01'  -- 用索引

-- 使用覆盖索引
SELECT id, name FROM users WHERE name = '张三';
```

## 六、实战案例

### 6.1 用户表

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    status TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);
```

### 6.2 订单表

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(32) NOT NULL,
    user_id INT NOT NULL,
    status TINYINT DEFAULT 0,
    amount DECIMAL(10,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_order_no (order_no),
    INDEX idx_user_status (user_id, status),
    INDEX idx_created (created_at)
);
```

### 6.3 分页优化

```sql
-- 慢
SELECT * FROM orders LIMIT 100000, 10;

-- 快 - 使用主键
SELECT * FROM orders 
WHERE id > 100000 
ORDER BY id 
LIMIT 10;

-- 快 - 记录上次的最大 ID
SELECT * FROM orders 
WHERE id > :last_max_id 
ORDER BY id 
LIMIT 10;
```

## 七、总结

数据库索引核心要点：

1. **索引类型**：主键、唯一、普通、全文
2. **B+Tree**：平衡树，适合范围查询
3. **复合索引**：最左前缀原则
4. **EXPLAIN**：分析查询计划
5. **优化技巧**：避免全表扫描
6. **分页**：使用主键优化

掌握这些，查询飞起来！

---

**推荐阅读**：
- [MySQL 索引原理](https://dev.mysql.com/doc/refman/8.0/en/mysql-indexes.html)
- [EXPLAIN 分析](https://dev.mysql.com/doc/refman/8.0/en/explain.html)

**如果对你有帮助，欢迎点赞收藏！**
