# PostgreSQL 高级特性完全实战指南

PostgreSQL 是最强大的开源关系型数据库。本文将带你全面掌握 PostgreSQL 的高级特性。

## 一、JSONB 数据类型

### 1. JSON vs JSONB

```sql
-- JSON: 存储为文本，保留格式
CREATE TABLE data_json (
    id SERIAL PRIMARY KEY,
    data JSON
);

-- JSONB: 存储为二进制，支持索引
CREATE TABLE data_jsonb (
    id SERIAL PRIMARY KEY,
    data JSONB
);

-- 插入数据
INSERT INTO data_json (data) VALUES
('{"name": "John", "age": 30, "tags": ["a", "b"]}');

INSERT INTO data_jsonb (data) VALUES
('{"name": "John", "age": 30, "tags": ["a", "b"]}');
```

### 2. JSONB 查询

```sql
-- 访问属性
SELECT data->'name' FROM data_jsonb;
SELECT data->>'name' FROM data_jsonb;  -- 返回文本

-- 访问嵌套属性
SELECT data->'address'->>'city' FROM data_jsonb;

-- 查询条件
SELECT * FROM data_jsonb 
WHERE data @> '{"name": "John"}';

SELECT * FROM data_jsonb 
WHERE data ? 'tags';

SELECT * FROM data_jsonb 
WHERE data ?| array['tags', 'name'];

-- 数组查询
SELECT * FROM data_jsonb 
WHERE data->'tags' @> '["a"]';

-- 更新
UPDATE data_jsonb 
SET data = data || '{"age": 31}' 
WHERE id = 1;

UPDATE data_jsonb 
SET data = jsonb_set(data, '{age}', '31') 
WHERE id = 1;

-- 删除属性
UPDATE data_jsonb 
SET data = data - 'tags' 
WHERE id = 1;
```

### 3. JSONB 索引

```sql
-- GIN 索引
CREATE INDEX idx_data_jsonb ON data_jsonb USING GIN (data);

-- 特定路径的索引
CREATE INDEX idx_data_name ON data_jsonb USING GIN ((data->'name'));

-- B-tree 索引（用于 >, <, =）
CREATE INDEX idx_data_age ON data_jsonb ((data->>'age'));

-- 表达式索引
CREATE INDEX idx_data_lower_name 
ON data_jsonb (lower((data->>'name')::text));
```

## 二、窗口函数

### 1. 基础窗口函数

```sql
-- 准备数据
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product VARCHAR(50),
    amount NUMERIC(10, 2),
    sale_date DATE
);

INSERT INTO sales (product, amount, sale_date) VALUES
('A', 100.00, '2024-01-01'),
('A', 150.00, '2024-01-02'),
('A', 200.00, '2024-01-03'),
('B', 50.00, '2024-01-01'),
('B', 75.00, '2024-01-02'),
('B', 100.00, '2024-01-03');

-- ROW_NUMBER
SELECT 
    product,
    amount,
    sale_date,
    ROW_NUMBER() OVER (PARTITION BY product ORDER BY amount DESC) as rn
FROM sales;

-- RANK
SELECT 
    product,
    amount,
    RANK() OVER (PARTITION BY product ORDER BY amount DESC) as rnk
FROM sales;

-- DENSE_RANK
SELECT 
    product,
    amount,
    DENSE_RANK() OVER (PARTITION BY product ORDER BY amount DESC) as drnk
FROM sales;
```

### 2. 聚合窗口函数

```sql
-- SUM 窗口函数
SELECT 
    product,
    amount,
    sale_date,
    SUM(amount) OVER (PARTITION BY product) as total,
    SUM(amount) OVER (PARTITION BY product ORDER BY sale_date) as running_total
FROM sales;

-- AVG, MIN, MAX
SELECT 
    product,
    amount,
    AVG(amount) OVER (PARTITION BY product) as avg_amount,
    MIN(amount) OVER (PARTITION BY product) as min_amount,
    MAX(amount) OVER (PARTITION BY product) as max_amount
FROM sales;
```

### 3. 偏移窗口函数

```sql
-- LAG 和 LEAD
SELECT 
    product,
    amount,
    sale_date,
    LAG(amount, 1) OVER (PARTITION BY product ORDER BY sale_date) as prev_day,
    LEAD(amount, 1) OVER (PARTITION BY product ORDER BY sale_date) as next_day
FROM sales;

-- FIRST_VALUE 和 LAST_VALUE
SELECT 
    product,
    amount,
    FIRST_VALUE(amount) OVER (PARTITION BY product ORDER BY sale_date) as first,
    LAST_VALUE(amount) OVER (
        PARTITION BY product 
        ORDER BY sale_date
        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last
FROM sales;
```

## 三、CTE 和递归 CTE

### 1. 普通 CTE

```sql
WITH product_sales AS (
    SELECT 
        product,
        SUM(amount) as total
    FROM sales
    GROUP BY product
),
top_products AS (
    SELECT * 
    FROM product_sales
    WHERE total > 200
)
SELECT * FROM top_products;
```

### 2. 递归 CTE

```sql
-- 层级数据
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    parent_id INTEGER REFERENCES categories(id)
);

INSERT INTO categories (name, parent_id) VALUES
('电子产品', NULL),
('手机', 1),
('电脑', 1),
('iPhone', 2),
('MacBook', 3);

-- 递归查询
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 1 as level
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree;
```

## 四、全文搜索

### 1. 基础全文搜索

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO articles (title, content) VALUES
('PostgreSQL 教程', '这是一篇关于 PostgreSQL 的教程文章'),
('数据库优化', '数据库优化技巧包括索引和查询优化'),
('全文搜索', 'PostgreSQL 支持强大的全文搜索功能');

-- to_tsvector 和 to_tsquery
SELECT 
    title,
    content,
    to_tsvector('english', content) as vector,
    to_tsquery('english', 'PostgreSQL & 教程') as query
FROM articles;

-- 搜索
SELECT * FROM articles
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'PostgreSQL');

-- 中文搜索
SELECT * FROM articles
WHERE to_tsvector('simple', content) @@ to_tsquery('simple', '教程');
```

### 2. GIN 索引

```sql
-- 创建索引
CREATE INDEX idx_articles_content 
ON articles USING GIN (to_tsvector('english', content));

-- 或者使用 generated column
ALTER TABLE articles 
ADD COLUMN content_tsv tsvector 
GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

CREATE INDEX idx_articles_tsv 
ON articles USING GIN (content_tsv);

-- 查询
SELECT * FROM articles 
WHERE content_tsv @@ to_tsquery('english', 'PostgreSQL');
```

### 3. 排名

```sql
SELECT 
    title,
    content,
    ts_rank(content_tsv, to_tsquery('english', 'PostgreSQL')) as rank
FROM articles
WHERE content_tsv @@ to_tsquery('english', 'PostgreSQL')
ORDER BY rank DESC;

-- ts_rank_cd
SELECT 
    title,
    ts_rank_cd(content_tsv, to_tsquery('english', 'PostgreSQL')) as rank
FROM articles
WHERE content_tsv @@ to_tsquery('english', 'PostgreSQL')
ORDER BY rank DESC;
```

## 五、物化视图

### 1. 创建物化视图

```sql
CREATE MATERIALIZED VIEW product_summary AS
SELECT 
    product,
    COUNT(*) as total_sales,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM sales
GROUP BY product;

-- 查询物化视图
SELECT * FROM product_summary;
```

### 2. 刷新物化视图

```sql
-- 刷新（会阻塞）
REFRESH MATERIALIZED VIEW product_summary;

-- 并发刷新（需要唯一索引）
CREATE UNIQUE INDEX idx_product_summary_product 
ON product_summary(product);

REFRESH MATERIALIZED VIEW CONCURRENTLY product_summary;

-- 自动刷新（使用触发器）
CREATE OR REPLACE FUNCTION refresh_product_summary()
RETURNS trigger AS $$
BEGIN
    REFRESH MATERIALIZED VIEW product_summary;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_refresh_summary
AFTER INSERT OR UPDATE OR DELETE ON sales
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_product_summary();
```

## 六、分区表

### 1. 范围分区

```sql
-- 创建分区表
CREATE TABLE measurements (
    id INTEGER,
    logdate DATE NOT NULL,
    peaktemp INTEGER,
    unitsales INTEGER
) PARTITION BY RANGE (logdate);

-- 创建分区
CREATE TABLE measurements_2024_01 
PARTITION OF measurements
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE measurements_2024_02 
PARTITION OF measurements
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 插入数据（自动路由到分区）
INSERT INTO measurements VALUES
(1, '2024-01-15', 30, 100),
(2, '2024-02-15', 25, 200);

-- 查询
SELECT * FROM measurements WHERE logdate = '2024-01-15';
```

### 2. 列表分区

```sql
CREATE TABLE products (
    id INTEGER,
    category TEXT NOT NULL,
    price NUMERIC
) PARTITION BY LIST (category);

CREATE TABLE products_electronics
PARTITION OF products
FOR VALUES IN ('手机', '电脑', '平板');

CREATE TABLE products_clothing
PARTITION OF products
FOR VALUES IN ('上衣', '裤子', '鞋子');
```

### 3. 哈希分区

```sql
CREATE TABLE customers (
    id INTEGER,
    name TEXT,
    email TEXT
) PARTITION BY HASH (id);

CREATE TABLE customers_p1
PARTITION OF customers
FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE customers_p2
PARTITION OF customers
FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE customers_p3
PARTITION OF customers
FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE customers_p4
PARTITION OF customers
FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

## 七、事务和锁

### 1. 事务隔离级别

```sql
-- 读未提交
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- 读已提交（默认）
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 可重复读
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 可串行化
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

BEGIN;
-- 事务操作
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- 或 ROLLBACK;
```

### 2. 锁

```sql
-- 行锁
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- 其他事务无法更新此行
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- 共享锁
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR SHARE;
-- 其他事务可以读，但不能写
COMMIT;

-- 表锁
LOCK TABLE accounts IN ACCESS EXCLUSIVE MODE;
```

### 3. 乐观锁

```sql
-- 使用版本号
ALTER TABLE accounts ADD COLUMN version INTEGER DEFAULT 1;

UPDATE accounts 
SET balance = balance - 100, version = version + 1
WHERE id = 1 AND version = 1;
-- 检查影响行数，如果为 0 说明版本不匹配
```

## 八、最佳实践

1. 使用 JSONB 存储半结构化数据
2. 合理使用窗口函数进行分析
3. 全文搜索使用 GIN 索引
4. 物化视图用于复杂查询缓存
5. 分区表处理大数据量
6. 选择合适的事务隔离级别
7. 乐观锁处理并发
8. 定期维护（VACUUM、ANALYZE）
9. 监控慢查询
10. 合理使用索引

## 九、总结

PostgreSQL 高级特性核心要点：
- JSONB 类型和索引
- 窗口函数（ROW_NUMBER、RANK、LAG、LEAD）
- CTE 和递归 CTE
- 全文搜索（tsvector、tsquery、GIN 索引）
- 物化视图
- 分区表（范围、列表、哈希）
- 事务和锁
- 最佳实践

掌握这些高级特性，让你成为 PostgreSQL 专家！
