# PostgreSQL 扩展完全指南

## 一、常用扩展

```sql
-- UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SELECT uuid_generate_v4();

-- 模糊搜索
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 表分区管理
CREATE EXTENSION IF NOT EXISTS pg_partman;

-- 统计信息
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

## 二、PostGIS

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE places (
  id serial PRIMARY KEY,
  name text,
  location geography(Point, 4326)
);

CREATE INDEX ON places USING GIST(location);

SELECT * FROM places WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(0,0),4326)::geography, 1000);
```

## 三、timescaledb

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE metrics (
  ts timestamptz NOT NULL,
  value float NOT NULL
);

SELECT create_hypertable('metrics', 'ts');
```

## 四、最佳实践

- 使用 UUID 生成唯一 ID
- PostGIS 处理空间数据
- TimescaleDB 处理时间序列
- pg_stat_statements 优化慢查询
- 合理使用索引
