# PostgreSQL TimescaleDB 时序数据库完全指南

## 一、扩展安装

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

## 二、创建超表

```sql
-- 普通表
CREATE TABLE conditions (
  time TIMESTAMPTZ NOT NULL,
  location TEXT NOT NULL,
  temperature NUMERIC,
  humidity NUMERIC
);

-- 创建超表
SELECT create_hypertable('conditions', 'time');
```

## 三、数据分区

```sql
-- 按时间分区（7天）
SELECT set_chunk_time_interval('conditions', INTERVAL '7 days');
```

## 四、数据查询

```sql
-- 查询过去 24 小时数据
SELECT * FROM conditions
WHERE time > NOW() - INTERVAL '24 hours';

-- 聚合查询
SELECT time_bucket('1 hour', time) as hour,
  avg(temperature) as avg_temp
FROM conditions
GROUP BY hour
ORDER BY hour;
```

## 五、连续聚合

```sql
-- 创建连续聚合视图
CREATE MATERIALIZED VIEW conditions_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) as hour,
  location,
  avg(temperature) as avg_temp,
  max(temperature) as max_temp
FROM conditions
GROUP BY hour, location;

-- 刷新聚合
CALL refresh_continuous_aggregate('conditions_hourly', NULL, NULL);
```

## 六、数据保留策略

```sql
-- 保留 90 天数据
SELECT add_retention_policy('conditions', INTERVAL '90 days');
```

## 七、压缩

```sql
-- 启用压缩
ALTER TABLE conditions SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'location',
  timescaledb.compress_orderby = 'time DESC'
);

-- 压缩策略
SELECT add_compression_policy('conditions', INTERVAL '7 days');
```

## 八、最佳实践

- 合理设置分区大小
- 使用连续聚合优化常用查询
- 配置数据保留策略
- 启用压缩节省空间
- 利用并行查询提升性能
- 适当创建索引
