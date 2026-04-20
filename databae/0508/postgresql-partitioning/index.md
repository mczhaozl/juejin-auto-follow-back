# PostgreSQL 表分区完全指南

## 一、范围分区

```sql
-- 创建分区表
CREATE TABLE measurements (
  city_id int not null,
  logdate date not null,
  temp int
) PARTITION BY RANGE (logdate);

-- 创建子分区
CREATE TABLE measurements_2024 PARTITION OF measurements FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE measurements_2025 PARTITION OF measurements FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

## 二、列表分区

```sql
CREATE TABLE cities (
  id int,
  name text,
  region text
) PARTITION BY LIST (region);

CREATE TABLE cities_east PARTITION OF cities FOR VALUES IN ('Shanghai', 'Beijing');
CREATE TABLE cities_west PARTITION OF cities FOR VALUES IN ('Chengdu', 'Chongqing');
```

## 三、哈希分区

```sql
CREATE TABLE orders (
  id int,
  data text
) PARTITION BY HASH (id);

CREATE TABLE orders_p1 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE orders_p2 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE orders_p3 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE orders_p4 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

## 四、分区管理

```sql
-- 添加新分区
CREATE TABLE measurements_2026 PARTITION OF measurements FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- 删除旧分区
DROP TABLE measurements_2023;

-- 分离分区
ALTER TABLE measurements DETACH PARTITION measurements_2023;
```

## 五、分区优化

```sql
-- 分区剪枝查询（自动只扫描相关分区）
EXPLAIN SELECT * FROM measurements WHERE logdate = '2024-05-20';

-- 分区索引
CREATE INDEX ON measurements_2024 (city_id);
CREATE INDEX ON measurements_2025 (city_id);
```

## 六、最佳实践

- 选择合适的分区策略
- 合理设置分区大小
- 定期维护分区（创建、归档）
- 监控分区查询性能
- 利用分区剪枝优化查询
- 分区表与普通表性能对比
