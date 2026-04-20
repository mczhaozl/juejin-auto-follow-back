# PostgreSQL GIN 和 GiST 索引完全指南

## 一、GIN 索引（倒排索引）

```sql
-- 数组索引
CREATE INDEX idx_items ON orders USING GIN (items);

-- 查询
SELECT * FROM orders WHERE items @> ARRAY['apple', 'banana'];
SELECT * FROM orders WHERE items && ARRAY['apple', 'banana'];

-- JSONB 索引
CREATE INDEX idx_data ON docs USING GIN (data);

-- 查询
SELECT * FROM docs WHERE data @> '{"key": "value"}';
SELECT * FROM docs WHERE data ? 'key';
```

## 二、GiST 索引（通用搜索树）

```sql
-- 全文搜索 GIN
CREATE INDEX idx_content ON docs USING GIN (to_tsvector('english', content));

-- 查询
SELECT * FROM docs WHERE to_tsvector('english', content) @@ to_tsquery('english', 'hello');

-- 几何类型 GiST
CREATE INDEX idx_location ON places USING GIST (location);

-- 查询
SELECT * FROM places WHERE location @> point(0,0);
```

## 三、全文搜索

```sql
-- 创建搜索向量列
ALTER TABLE docs ADD COLUMN ts tsvector GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || content)) STORED;
CREATE INDEX idx_ts ON docs USING GIN (ts);

-- 查询
SELECT * FROM docs WHERE ts @@ to_tsquery('english', 'hello & world');
```

## 四、最佳实践

- GIN 适合查询性能要求高、更新频率低的场景
- GiST 适合空间和多维度数据
- tsvector 用于全文搜索
- 使用 GIN 索引优化 LIKE '%term%'
- 合理配置维护成本
