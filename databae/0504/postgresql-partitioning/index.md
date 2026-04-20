# PostgreSQL 分区表完全指南

## 一、分区表概述

### 1.1 什么是分区表

将大表逻辑上分成多个小的物理表，提升查询性能和管理效率。

### 1.2 分区的优势

- 提高查询性能
- 简化数据维护
- 优化存储
- 更快的数据加载和删除

## 二、分区类型

### 2.1 范围分区 (Range Partitioning)

```sql
-- 创建父表
CREATE TABLE orders (
    id BIGSERIAL,
    order_date DATE NOT NULL,
    customer_id INT,
    amount NUMERIC(10,2)
) PARTITION BY RANGE (order_date);

-- 创建子分区
CREATE TABLE orders_2024_01 PARTITION OF orders
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 2.2 列表分区 (List Partitioning)

```sql
CREATE TABLE users (
    id SERIAL,
    region VARCHAR(50),
    name VARCHAR(100)
) PARTITION BY LIST (region);

CREATE TABLE users_us PARTITION OF users
FOR VALUES IN ('US', 'USA', 'United States');

CREATE TABLE users_eu PARTITION OF users
FOR VALUES IN ('UK', 'Germany', 'France', 'Spain');
```

### 2.3 哈希分区 (Hash Partitioning)

```sql
CREATE TABLE events (
    id UUID,
    event_type VARCHAR(50),
    data JSONB
) PARTITION BY HASH (id);

CREATE TABLE events_p0 PARTITION OF events
FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE events_p1 PARTITION OF events
FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE events_p2 PARTITION OF events
FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE events_p3 PARTITION OF events
FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### 2.4 复合分区

```sql
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE,
    region VARCHAR(50),
    amount NUMERIC(10,2)
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_2024 PARTITION OF sales
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
PARTITION BY LIST (region);

CREATE TABLE sales_2024_us PARTITION OF sales_2024
FOR VALUES IN ('US');
```

## 三、分区管理

### 3.1 添加新分区

```sql
-- 添加新月份分区
CREATE TABLE orders_2024_03 PARTITION OF orders
FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- 使用默认分区
CREATE TABLE orders_default PARTITION OF orders
DEFAULT;
```

### 3.2 删除旧分区

```sql
-- 直接删除
DROP TABLE orders_2024_01;

-- 分离分区
ALTER TABLE orders DETACH PARTITION orders_2024_01;
```

### 3.3 拆分分区

```sql
-- 拆分范围分区
ALTER TABLE orders DETACH PARTITION orders_2024_q1;

CREATE TABLE orders_2024_01 PARTITION OF orders
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

## 四、索引与分区

### 4.1 创建分区索引

```sql
-- 在父表上创建索引（自动传播到子表）
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- 在单个分区上创建索引
CREATE INDEX idx_orders_2024_01_amount ON orders_2024_01(amount);
```

### 4.2 约束

```sql
ALTER TABLE orders_2024_01
ADD CONSTRAINT chk_order_date CHECK (order_date >= '2024-01-01' AND order_date < '2024-02-01');
```

## 五、查询优化

### 5.1 分区裁剪

```sql
-- 只扫描相关分区
SELECT * FROM orders 
WHERE order_date BETWEEN '2024-01-15' AND '2024-01-20';

-- 查看执行计划
EXPLAIN ANALYZE SELECT * FROM orders 
WHERE order_date = '2024-01-15';
```

### 5.2 并行查询

```sql
SET max_parallel_workers_per_gather = 4;

EXPLAIN ANALYZE SELECT count(*) FROM orders;
```

## 六、实战场景

### 6.1 日志表分区

```sql
CREATE TABLE application_logs (
    id BIGSERIAL,
    log_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    level VARCHAR(10),
    message TEXT,
    metadata JSONB
) PARTITION BY RANGE (log_timestamp);

-- 按月份创建分区
CREATE TABLE application_logs_2024_01 PARTITION OF application_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE application_logs_2024_02 PARTITION OF application_logs
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 自动创建分区的函数
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS TRIGGER AS $$
DECLARE
    partition_date TEXT;
    partition_name TEXT;
    start_date TEXT;
    end_date TEXT;
BEGIN
    partition_date := to_char(NEW.log_timestamp, 'YYYY_MM');
    partition_name := 'application_logs_' || partition_date;
    start_date := date_trunc('month', NEW.log_timestamp);
    end_date := start_date + interval '1 month';
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = partition_name) THEN
        EXECUTE format('CREATE TABLE %I PARTITION OF application_logs 
                       FOR VALUES FROM (%L) TO (%L)',
                       partition_name, start_date, end_date);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 6.2 数据归档

```sql
-- 分离旧分区
ALTER TABLE orders DETACH PARTITION orders_2023;

-- 移动到归档表空间
ALTER TABLE orders_2023 SET TABLESPACE archive_ts;

-- 或直接导出
COPY orders_2023 TO '/backup/orders_2023.csv';
DROP TABLE orders_2023;
```

## 七、维护与监控

### 7.1 查看分区信息

```sql
-- 查看所有分区
SELECT
    nmsp_parent.nspname AS parent_schema,
    parent.relname AS parent_table,
    nmsp_child.nspname AS child_schema,
    child.relname AS child_table
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
JOIN pg_namespace nmsp_parent ON nmsp_parent.oid = parent.relnamespace
JOIN pg_namespace nmsp_child ON nmsp_child.oid = child.relnamespace
WHERE parent.relname = 'orders';

-- 查看分区大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'orders_%';
```

## 八、最佳实践

- 选择合适的分区键（时间、区域常见）
- 合理设置分区大小（百万-千万数据级）
- 定期维护分区（添加、删除）
- 监控分区裁剪效果
- 使用默认分区处理异常数据
- 注意分区对索引维护的影响

## 总结

PostgreSQL 分区表是管理大数据量的有力工具，通过合理的分区策略，可以显著提升查询性能和数据管理效率。
