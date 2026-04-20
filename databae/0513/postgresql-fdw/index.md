# PostgreSQL FDW 完全指南

## 一、Postgres FDW

```sql
-- 1. 安装扩展
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- 2. 创建外部服务器
CREATE SERVER foreign_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
  host 'other-postgres',
  port '5432',
  dbname 'other_db'
);

-- 3. 用户映射
CREATE USER MAPPING FOR current_user
SERVER foreign_server
OPTIONS (
  user 'foreign_user',
  password 'secret'
);

-- 4. 导入外部表
IMPORT FOREIGN SCHEMA public
FROM SERVER foreign_server
INTO local_schema;

-- 5. 查询外部表
SELECT * FROM local_schema.foreign_table;
```

## 二、File FDW

```sql
CREATE EXTENSION IF NOT EXISTS file_fdw;

CREATE SERVER file_server
FOREIGN DATA WRAPPER file_fdw;

CREATE FOREIGN TABLE csv_data (
  id int,
  name text,
  value numeric
)
SERVER file_server
OPTIONS (
  filename '/path/to/data.csv',
  format 'csv',
  header 'true',
  delimiter ',',
  encoding 'UTF8'
);

SELECT * FROM csv_data;
```

## 三、MongoDB FDW

```sql
CREATE EXTENSION IF NOT EXISTS mongo_fdw;

CREATE SERVER mongo_server
FOREIGN DATA WRAPPER mongo_fdw
OPTIONS (
  address 'localhost',
  port '27017'
);

CREATE USER MAPPING FOR current_user
SERVER mongo_server;

CREATE FOREIGN TABLE mongo_collection (
  id text,
  data jsonb
)
SERVER mongo_server
OPTIONS (
  database 'mydb',
  collection 'mycollection'
);

SELECT * FROM mongo_collection;
```

## 四、FDW 性能

```sql
-- 下推查询
EXPLAIN ANALYZE
SELECT * FROM foreign_table
WHERE id = 1;

-- 物化外部表
CREATE MATERIALIZED VIEW materialized_foreign AS
SELECT * FROM foreign_table;

REFRESH MATERIALIZED VIEW materialized_foreign;
```

## 最佳实践
- 使用 postgres_fdw 访问远程 Postgres
- file_fdw 处理 CSV/TSV 文件
- 注意权限控制
- 考虑查询下推优化
- 数据量大时使用物化视图
