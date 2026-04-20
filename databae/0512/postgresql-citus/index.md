# PostgreSQL Citus 完全指南

## 一、Citus 安装与配置

```sql
-- 扩展安装
CREATE EXTENSION citus;

-- 添加节点
SELECT * from citus_add_node('worker1', 5432);
SELECT * from citus_add_node('worker2', 5432);

-- 查看节点状态
SELECT * FROM citus_get_active_worker_nodes();
```

## 二、创建分布式表

```sql
-- 1. 普通分布式表 (Hash 分片)
CREATE TABLE events (
  id bigint,
  data text,
  created_at timestamptz
);

SELECT create_distributed_table('events', 'id');

-- 2. 参考表 (复制到所有节点)
CREATE TABLE countries (
  id int,
  name text
);

SELECT create_reference_table('countries');

-- 3. 本地表
CREATE TABLE local_data (id int);
```

## 三、分布式查询

```sql
-- 基本查询 (Citus 自动路由)
SELECT * FROM events WHERE id = 1;
SELECT count(*) FROM events;

-- JOIN 查询
SELECT e.*, c.name
FROM events e
JOIN countries c ON e.country_id = c.id
WHERE e.id = 1;

-- 聚合查询
SELECT date_trunc('day', created_at) as day, count(*)
FROM events
GROUP BY day;
```

## 四、分片与扩容

```sql
-- 查看分片信息
SELECT * FROM citus_shards;

-- 重新平衡分片
SELECT rebalance_table_shards('events');

-- 添加新节点后平衡
SELECT * from citus_add_node('worker3', 5432);
SELECT rebalance_table_shards();
```

## 五、最佳实践
- 选择合适的分布键（均匀分布、查询频繁）
- 参考表适合维度数据
- 合理设置分片数量
- 监控分片大小和负载
- 参考表与分布式表关联性能最佳
