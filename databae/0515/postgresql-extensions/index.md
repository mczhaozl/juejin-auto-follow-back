# PostgreSQL 扩展完全指南

## 一、安装扩展

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

## 二、PostGIS

```sql
-- 创建表
CREATE TABLE places (
  id SERIAL PRIMARY KEY,
  name TEXT,
  location GEOGRAPHY(Point, 4326)
);

-- 查询附近
SELECT name, ST_Distance(
  location,
  ST_SetSRID(ST_MakePoint(-73.9857, 40.7484), 4326)::GEOGRAPHY
) AS dist
FROM places
WHERE ST_DWithin(
  location,
  ST_SetSRID(ST_MakePoint(-73.9857, 40.7484), 4326)::GEOGRAPHY,
  1000
)
ORDER BY dist;
```

## 三、TimescaleDB

```sql
-- 创建超表
CREATE TABLE conditions (
  time TIMESTAMPTZ NOT NULL,
  device TEXT,
  temperature NUMERIC
);

SELECT create_hypertable('conditions', 'time');

-- 查询
SELECT time_bucket('1 hour', time) AS hour, 
  AVG(temperature) AS temp
FROM conditions
WHERE time > now() - INTERVAL '1 day'
GROUP BY hour
ORDER BY hour;
```

## 四、pg_stat_statements

```sql
CREATE EXTENSION pg_stat_statements;

-- 查询执行时间
SELECT query, total_time, calls, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

## 最佳实践
- 使用权威扩展
- 阅读扩展文档
- 定期更新扩展
- 监控扩展性能
- 注意扩展兼容性
