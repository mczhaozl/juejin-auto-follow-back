# PostgreSQL JSONB 完全指南：高级查询与性能优化

> 一句话摘要：深入探索 PostgreSQL JSONB 数据类型的强大功能，涵盖存储、索引、查询、修改及性能优化技巧，让你在关系型数据库中高效处理半结构化数据。

## 一、引言

### 1.1 为什么使用 JSONB

现代应用产生大量半结构化数据，JSONB 提供了：

| 特性 | 说明 |
|------|------|
| 灵活性 | 无需预定义 schema，随时添加新字段 |
| 嵌套存储 | 支持复杂的层级结构 |
| 高效查询 | 原生支持 JSON 路径查询 |
| 索引支持 | 可对 JSON 字段建立 GIN 索引 |
| 完整性 | 二进制存储，解析更快 |

### 1.2 JSON vs JSONB

PostgreSQL 提供两种 JSON 数据类型：

```sql
-- JSON：存储为纯 JSON 文本，保留原始格式
CREATE TABLE json_table (
    data json
);

-- JSONB：存储为二进制，解析后存储，查询更快
CREATE TABLE jsonb_table (
    data jsonb
);
```

| 特性 | JSON | JSONB |
|------|------|-------|
| 存储格式 | 文本 | 二进制 |
| 查询性能 | 每次解析 | 直接访问 |
| 索引支持 | 有限 | GIN 索引 |
| 保留空白 | 是 | 否 |
| 保留顺序 | 是 | 否 |
| 重复键 | 保留所有 | 保留最后一个 |

### 1.3 本文目标

1. 掌握 JSONB 的存储和修改
2. 精通 JSONB 查询语法
3. 学会创建和使用 JSONB 索引
4. 了解性能优化技巧

## 二、基础操作

### 2.1 创建 JSONB 数据

```sql
-- 直接插入 JSONB
CREATE TABLE events (
    id serial primary key,
    event_data jsonb not null
);

INSERT INTO events (event_data) VALUES
    ('{"name": "Conference", "date": "2024-01-15", "location": "Beijing"}'),
    ('{"name": "Workshop", "tags": ["tech", "ai"], "capacity": 50}'),
    ('{"name": "Meetup", "attendees": ["Alice", "Bob", "Charlie"]}');
```

### 2.2 插入数组和嵌套对象

```sql
INSERT INTO events (event_data) VALUES
    ('{
        "title": "Tech Summit 2024",
        "sessions": [
            {"id": 1, "topic": "AI", "duration": 60},
            {"id": 2, "topic": "Cloud", "duration": 45}
        ],
        "speakers": [
            {"name": "Dr. Smith", "company": "AI Corp"},
            {"name": "Jane Doe", "company": "Cloud Inc"}
        ]
    }');
```

### 2.3 查询 JSONB 字段

```sql
-- 使用 -> 获取 JSON 对象（返回 JSON 类型）
SELECT event_data->'name' FROM events;

-- 使用 ->> 获取 JSON 对象（返回文本）
SELECT event_data->>'name' FROM events;

-- 使用 #> 获取嵌套路径
SELECT event_data#>'{sessions,0,topic}' FROM events;

-- 使用 #>> 获取嵌套路径（文本）
SELECT event_data#>>'{sessions,0,topic}' FROM events;
```

### 2.4 使用 WHERE 条件

```sql
-- 查询特定值
SELECT * FROM events
WHERE event_data->>'name' = 'Conference';

-- 查询数值比较
SELECT * FROM events
WHERE (event_data->'capacity')::int > 30;

-- 查询数组包含
SELECT * FROM events
WHERE event_data @> '{"tags": ["tech"]}';

-- 查询数组任意元素
SELECT * FROM events
WHERE event_data->'tags' ? 'ai';

-- 查询键存在
SELECT * FROM events
WHERE event_data ? 'capacity';

-- 查询键不存在
SELECT * FROM events
WHERE NOT event_data ? 'capacity';
```

## 三、JSONB 操作符

### 3.1 成员操作符

```sql
-- ? 键存在（顶层）
SELECT '{"a":1,"b":2}'::jsonb ? 'a';  -- true

-- ?| 任一键存在
SELECT '{"a":1,"b":2}'::jsonb ?| array['a','c'];  -- true

-- ?& 所有键存在
SELECT '{"a":1,"b":2}'::jsonb ?& array['a','b'];  -- true

-- 获取所有键
SELECT jsonb_object_keys(event_data) FROM events;

-- 获取嵌套键
SELECT jsonb_object_keys(event_data->'speakers') FROM events;
```

### 3.2 连接操作符

```sql
-- || JSONB 合并（左侧值优先）
SELECT '{"a":1,"b":2}'::jsonb || '{"b":3,"c":4}'::jsonb;
-- 结果: {"a":1,"b":2,"c":4}

-- - 删除键
SELECT '{"a":1,"b":2}'::jsonb - 'b';
-- 结果: {"a":1}

-- #- 删除嵌套键
SELECT '{"a":{"b":1}}'::jsonb #- '{a,b}';
-- 结果: {"a":{}}
```

### 3.3 包含操作符

```sql
-- @> 包含（左侧包含右侧）
SELECT '{"a":1,"b":2}'::jsonb @> '{"a":1}';
-- true

-- <@ 被包含
SELECT '{"a":1}'::jsonb <@ '{"a":1,"b":2}';
-- true
```

### 3.4 路径操作符

```sql
-- 使用 jsonb_path_query 递归查询
SELECT jsonb_path_query(
    '{"items":[{"id":1},{"id":2}]}'::jsonb,
    '$.items[*].id'
);
-- 返回: 1, 2

-- 使用 jsonb_path_query_array
SELECT jsonb_path_query_array(
    '{"items":[{"id":1},{"id":2}]}'::jsonb,
    '$.items[*].id'
);
-- 返回: [1, 2]

-- 路径匹配
SELECT jsonb_path_exists(
    '{"a":[1,2,3]}'::jsonb,
    '$.a[*] ? (@ > 2)'
);
-- true
```

## 四、函数

### 4.1 聚合函数

```sql
-- jsonb_object_agg：键值对聚合
SELECT user_id,
    jsonb_object_agg(key, value) as properties
FROM user_properties
GROUP BY user_id;

-- jsonb_agg：聚合为 JSONB 数组
SELECT department,
    jsonb_agg(employee) as employees
FROM employees
GROUP BY department;

-- jsonb_set_array：设置数组元素
SELECT jsonb_set_array(
    '[{"a":"b"},{"a":"c"}]'::jsonb,
    '{0,a}',
    '"x"'
);
-- 结果: [{"a":"x"},{"a":"c"}]
```

### 4.2 转换函数

```sql
-- jsonb_populate_record：将 JSONB 展开为行
CREATE TABLE person (
    name text,
    age int,
    email text
);

SELECT p.*
FROM jsonb_populate_record(
    null::person,
    '{"name":"张三","age":25,"email":"zhang@example.com"}'::jsonb
) p;

-- jsonb_populate_recordset：JSONB 数组展开为多行
SELECT p.*
FROM jsonb_populate_recordset(
    null::person,
    '[{"name":"张三"},{"name":"李四"}]'::jsonb
) p;

-- jsonb_to_record：类似但更灵活
SELECT p.*
FROM jsonb_to_record(
    '{"name":"张三","age":25}'::jsonb
) AS p(name text, age int);
```

### 4.3 生成函数

```sql
-- jsonb_build_object：构建 JSONB 对象
SELECT jsonb_build_object(
    'name', '张三',
    'age', 25,
    'skills', ARRAY['Python', 'JavaScript']
);

-- jsonb_build_array：构建 JSONB 数组
SELECT jsonb_build_array(1, 2, 3, 'a', 'b');

-- jsonb_build_array 多参数
SELECT jsonb_build_array(
    jsonb_build_object('name', 'Alice'),
    jsonb_build_object('name', 'Bob')
);
```

### 4.4 修改函数

```sql
-- jsonb_insert：插入值
SELECT jsonb_insert(
    '{"a":[1,2,3]}'::jsonb,
    '{a,1}',
    '"new"',
    true  -- true: 在指定位置插入，false: 替换
);
-- 结果: {"a":[1,"new",2,3]}

-- jsonb_set：设置值
SELECT jsonb_set(
    '{"a":{"b":1}}'::jsonb,
    '{a,c}',
    '2'
);
-- 结果: {"a":{"b":1,"c":2}}

-- jsonb_concat：合并
SELECT jsonb_concat(
    '{"a":1}'::jsonb,
    '{"b":2}'::jsonb
);
-- 结果: {"a":1,"b":2}

-- jsonb_delete：删除键
SELECT jsonb_delete(
    '{"a":1,"b":2}'::jsonb,
    'b'
);
-- 结果: {"a":1}
```

## 五、索引

### 5.1 GIN 索引

GIN（Generalized Inverted Index）是 JSONB 最常用的索引类型：

```sql
-- 创建 GIN 索引
CREATE INDEX idx_events_data ON events USING GIN (event_data);

-- 创建表达式索引（针对特定路径）
CREATE INDEX idx_events_name ON events ((event_data->>'name'));

-- 复合 GIN 索引
CREATE INDEX idx_events_capacity ON events
USING GIN ((event_data->'tags'));

-- 使用索引优化查询
EXPLAIN SELECT * FROM events
WHERE event_data @> '{"tags":["tech"]}';
-- 现在会使用 idx_events_capacity
```

### 5.2 B-Tree 索引

```sql
-- 对提取的值创建 B-Tree 索引
CREATE INDEX idx_events_date ON events ((event_data->>'date'));

-- 对数值创建索引
CREATE INDEX idx_events_capacity ON events
WHERE event_data ? 'capacity';

-- 部分索引
CREATE INDEX idx_events_with_capacity ON events
WHERE event_data->'capacity' IS NOT NULL;
```

### 5.3 表达式索引

```sql
-- 创建复杂的表达式索引
CREATE INDEX idx_events_session_count ON events (
    jsonb_array_length(event_data->'sessions')
);

-- 多列表达式索引
CREATE INDEX idx_events_complex ON events (
    (event_data->>'name'),
    (event_data->'capacity')::int
);

-- 索引使用示例
SELECT * FROM events
WHERE jsonb_array_length(event_data->'sessions') > 3;
```

### 5.4 索引类型选择

| 索引类型 | 适用场景 |
|---------|---------|
| GIN | 包含查询、键存在、数组包含 |
| B-Tree | 值的比较、排序、范围查询 |
| Hash | 简单的等值查询（不推荐） |
| GiST | 几何类型、全文搜索 |

## 六、实战案例

### 6.1 用户行为追踪

```sql
CREATE TABLE user_events (
    id bigserial primary key,
    user_id bigint not null,
    event_type text not null,
    properties jsonb not null default '{}',
    created_at timestamp with time zone default now()
);

-- 创建索引
CREATE INDEX idx_user_events_user_id ON user_events (user_id);
CREATE INDEX idx_user_events_type ON user_events (event_type);
CREATE INDEX idx_user_events_props ON user_events USING GIN (properties);
CREATE INDEX idx_user_events_created ON user_events (created_at DESC);

-- 查询特定用户最近7天的行为
SELECT
    event_type,
    properties->>'action' as action,
    properties->>'page' as page,
    created_at
FROM user_events
WHERE user_id = 12345
    AND created_at > now() - interval '7 days'
ORDER BY created_at DESC;

-- 统计用户行为分布
SELECT
    event_type,
    properties->>'action' as action,
    COUNT(*) as count
FROM user_events
WHERE created_at > now() - interval '30 days'
GROUP BY event_type, properties->>'action'
ORDER BY count DESC
LIMIT 20;

-- 查询特定页面访问
SELECT DISTINCT user_id
FROM user_events
WHERE properties->>'page' = '/checkout'
    AND event_type = 'page_view';
```

### 6.2 配置管理

```sql
CREATE TABLE app_configs (
    id serial primary key,
    app_name text not null,
    config jsonb not null
);

-- 存储应用配置
INSERT INTO app_configs (app_name, config) VALUES
    ('web', '{
        "theme": "dark",
        "language": "zh-CN",
        "notifications": {
            "email": true,
            "push": false
        },
        "features": {
            "beta": true,
            "experimental": false
        }
    }'),
    ('mobile', '{
        "theme": "light",
        "language": "zh-CN",
        "notifications": {
            "email": false,
            "push": true
        }
    }');

-- 查询特定配置
SELECT app_name,
    config->>'theme' as theme,
    config->'notifications'->>'push' as push_enabled
FROM app_configs;

-- 更新嵌套配置
UPDATE app_configs
SET config = jsonb_set(
    config,
    '{notifications,email}',
    'true'::jsonb
)
WHERE app_name = 'web';

-- 合并新配置
UPDATE app_configs
SET config = config || '{
    "version": "2.0",
    "updated_at": "2024-01-01"
}'::jsonb
WHERE app_name = 'web';
```

### 6.3 日志存储

```sql
CREATE TABLE application_logs (
    id bigserial primary key,
    level text not null,
    message text not null,
    metadata jsonb default '{}',
    service text not null,
    created_at timestamp with time zone default now()
);

-- 创建索引
CREATE INDEX idx_logs_level ON application_logs (level);
CREATE INDEX idx_logs_service ON application_logs (service);
CREATE INDEX idx_logs_created ON application_logs (created_at DESC);
CREATE INDEX idx_logs_meta ON application_logs USING GIN (metadata);

-- 查询错误日志
SELECT
    message,
    metadata->>'request_id' as request_id,
    created_at
FROM application_logs
WHERE level = 'error'
    AND service = 'api'
    AND created_at > now() - interval '1 hour';

-- 查询包含特定上下文的日志
SELECT *
FROM application_logs
WHERE metadata @> '{"user_id": 12345}'
    AND metadata ?| array['error_code', 'stack_trace'];
```

### 6.4 多租户数据隔离

```sql
CREATE TABLE tenant_data (
    id bigserial primary key,
    tenant_id uuid not null,
    entity_type text not null,
    data jsonb not null,
    created_at timestamp with time zone default now()
);

-- 创建租户索引
CREATE INDEX idx_tenant ON tenant_data (tenant_id);
CREATE INDEX idx_tenant_entity ON tenant_data (tenant_id, entity_type);
CREATE INDEX idx_tenant_gin ON tenant_data USING GIN (data);

-- 查询特定租户的数据
SELECT
    entity_type,
    data->>'name' as name,
    data->>'status' as status
FROM tenant_data
WHERE tenant_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
    AND entity_type = 'order';

-- 租户级别的数据聚合
SELECT
    tenant_id,
    entity_type,
    COUNT(*) as count,
    jsonb_agg(id) as ids
FROM tenant_data
WHERE created_at > now() - interval '24 hours'
GROUP BY tenant_id, entity_type;
```

## 七、性能优化

### 7.1 查询优化

```sql
-- 避免全表扫描：使用具体的路径
-- ❌ 低效
SELECT * FROM events WHERE event_data @> '{"name":"Conference"}';

-- ✅ 高效（如果有表达式索引）
CREATE INDEX idx_events_name ON events ((event_data->>'name'));
SELECT * FROM events WHERE event_data->>'name' = 'Conference';

-- 使用 B-Tree 替代 GIN（如果查询模式已知）
-- 对于精确值查询，B-Tree 通常更快
CREATE INDEX idx_events_capacity_btree ON events
WHERE event_data->'capacity' IS NOT NULL;

-- 使用 jsonb_path_query 的优化版本
-- jsonb_path_query_first 只返回第一个匹配
SELECT jsonb_path_query_first(
    event_data,
    '$.sessions[*] ? (@.topic == "AI")'
) FROM events;
```

### 7.2 存储优化

```sql
-- 避免过度嵌套：扁平化设计
-- ❌ 过度嵌套
{
    "user": {
        "profile": {
            "name": "张三",
            "settings": {...}
        }
    }
}

-- ✅ 适度嵌套
{
    "user_id": 123,
    "user_name": "张三",
    "profile_settings": {...}
}

-- 使用 jsonb_strip_nulls 移除 null 值
SELECT jsonb_strip_nulls('{
    "a":1,
    "b":null,
    "c":{"d":null}
}'::jsonb);
-- 结果: {"a":1,"c":{}}
```

### 7.3 批量操作

```sql
-- 批量插入
INSERT INTO events (event_data)
SELECT jsonb_build_object(
    'name', name,
    'date', date,
    'tags', tags
)
FROM (VALUES
    ('Event1', '2024-01-01', ARRAY['tech']),
    ('Event2', '2024-01-02', ARRAY['ai','ml'])
) AS source(name, date, tags);

-- 批量更新
UPDATE events
SET event_data = event_data || jsonb_build_object(
    'updated_at', now()::text,
    'version', (event_data->>'version'::int + 1)::text
)
WHERE event_data @> '{"type":"active"}';

-- 使用 UPSERT
INSERT INTO events (event_data)
VALUES ('{"id":1,"name":"Event"}')
ON CONFLICT (id) DO UPDATE
SET event_data = events.event_data || EXCLUDED.event_data;
```

### 7.4 VACUUM 与维护

```sql
-- 定期 VACUUM（JSONB 更新会产生 dead tuples）
VACUUM ANALYZE events;

-- 查看表膨胀
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_dead_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- 查看索引使用情况
SELECT
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

## 八、高级技巧

### 8.1 递归查询

```sql
-- 查询 JSONB 树结构
WITH RECURSIVE tree AS (
    SELECT
        id,
        event_data,
        event_data->'name' as name,
        0 as depth
    FROM events
    WHERE event_data->'parent_id' IS NULL

    UNION ALL

    SELECT
        e.id,
        e.event_data,
        e.event_data->'name',
        t.depth + 1
    FROM events e
    JOIN tree t ON e.event_data->>'parent_id' = t.id::text
)
SELECT id, name, depth FROM tree;

-- 使用 jsonb_tree CTE
WITH RECURSIVE jsonb_tree AS (
    SELECT
        key,
        value,
        path,
        0 as depth
    FROM jsonb_each_text('{"a":{"b":{"c":1}}}'::jsonb) AS t(key, value)

    UNION ALL

    SELECT
        t.key,
        t.value,
        jsonb_tree.path || t.key,
        jsonb_tree.depth + 1
    FROM jsonb_each_text(jsonb_tree.value) AS t(key, value)
    WHERE jsonb_tree.depth < 10
)
SELECT * FROM jsonb_tree;
```

### 8.2 全文搜索

```sql
-- JSONB 全文搜索
CREATE INDEX idx_events_search ON events
USING GIN (to_tsvector('simple', event_data->>'name'));

-- 搜索包含特定关键词的事件
SELECT *
FROM events
WHERE to_tsvector('simple', event_data->>'name') @@ to_tsquery('simple', 'Conference & Tech');

-- 高级搜索
SELECT *,
    ts_rank(
        to_tsvector('simple', event_data->>'name'),
        to_tsquery('simple', 'tech | ai')
    ) as rank
FROM events
WHERE to_tsvector('simple', event_data->>'name') @@ to_tsquery('simple', 'tech | ai')
ORDER BY rank DESC;
```

### 8.3 分页查询

```sql
-- 使用 Keyset 分页（比 OFFSET 更高效）
SELECT *
FROM events
WHERE (created_at, id) < (last_timestamp, last_id)
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- JSONB 数组分页
SELECT
    id,
    event_data,
    jsonb_array_elements(event_data->'items') as item
FROM events
LIMIT 100;

-- 数组切片
SELECT event_data->'items'->0 as first_item,
    event_data->'items'->-1 as last_item
FROM events;
```

## 九、限制与注意事项

### 9.1 JSONB 限制

```sql
-- JSONB 值不能超过 255 字节（键名）
-- 实际限制：整个 JSONB 文档建议不超过几 MB

-- 检查 JSONB 大小
SELECT
    pg_column_size(event_data) as bytes,
    pg_size_pretty(pg_column_size(event_data)) as pretty
FROM events;

-- 大文档警告
SELECT id, pg_column_size(event_data) as size
FROM events
WHERE pg_column_size(event_data) > 1024 * 1024;  -- > 1MB
```

### 9.2 类型安全

```sql
-- 始终进行类型转换
-- ❌ 可能出错
SELECT event_data->'count' + 1 FROM events;

-- ✅ 安全
SELECT (event_data->>'count')::int + 1 FROM events;

-- 处理 null 和类型错误
SELECT
    COALESCE((event_data->>'count')::int, 0) + 1 as count
FROM events;
```

### 9.3 最佳实践

```sql
-- 1. 使用约束保证数据完整性
ALTER TABLE events
ADD CONSTRAINT valid_capacity
CHECK (
    event_data->'capacity' IS NULL OR
    jsonb_typeof(event_data->'capacity') = 'number'
);

-- 2. 使用默认值
ALTER TABLE events
ALTER COLUMN event_data
SET DEFAULT '{}'::jsonb;

-- 3. 设置 NOT NULL 约束
ALTER TABLE events
ALTER COLUMN event_data SET NOT NULL;

-- 4. 定期维护
VACUUM ANALYZE events;
REINDEX INDEX idx_events_props;
```

## 十、总结

### 10.1 核心要点

1. **JSONB 是二进制 JSON，查询性能优于 JSON**
2. **丰富的操作符支持灵活的查询**
3. **GIN 索引是 JSONB 查询的关键**
4. **表达式索引针对特定路径优化**
5. **注意数据类型安全和性能维护**

### 10.2 选型建议

- ✅ 需要灵活 schema 时使用 JSONB
- ✅ 半结构化数据存储
- ✅ 配置、设置、日志存储
- ❌ 需要强一致性时用普通列
- ❌ 频繁更新的字段不适合 JSONB
- ❌ 已有明确 schema 的数据用普通表

### 10.3 资源链接

- [PostgreSQL JSONB 文档](https://www.postgresql.org/docs/current/datatype-json.html)
- [JSONB 函数参考](https://www.postgresql.org/docs/current/functions-json.html)
- [GIN 索引文档](https://www.postgresql.org/docs/current/gin.html)

> 如果对你有帮助，欢迎点赞、收藏！有任何问题欢迎在评论区讨论。
