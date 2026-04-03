# PostgreSQL JSONB 完全指南：高级查询与性能优化

PostgreSQL 的 JSONB 类型提供了强大的半结构化数据存储能力。本文将深入探讨 JSONB 的高级用法和性能优化。

## 一、JSONB 基础

### 1. 创建表

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    details JSONB
);
```

### 2. 插入数据

```sql
INSERT INTO products (name, details) VALUES
('iPhone 15', '{
    "brand": "Apple",
    "price": 7999,
    "specs": {
        "screen": "6.1 inch",
        "chip": "A17"
    },
    "tags": ["smartphone", "apple", "5g"]
}'::jsonb),
('MacBook Pro', '{
    "brand": "Apple",
    "price": 14999,
    "specs": {
        "screen": "14 inch",
        "chip": "M3 Pro"
    },
    "tags": ["laptop", "apple", "professional"]
}'::jsonb);
```

## 二、基础查询

### 1. 访问 JSON 字段

```sql
SELECT 
    name,
    details->'brand' as brand,
    details->>'price' as price,
    details->'specs'->>'screen' as screen
FROM products;
```

### 2. 条件查询

```sql
SELECT * FROM products
WHERE details->>'brand' = 'Apple';

SELECT * FROM products
WHERE (details->'price')::numeric > 10000;
```

## 三、高级查询

### 1. 包含查询

```sql
SELECT * FROM products
WHERE details @> '{"brand": "Apple"}'::jsonb;

SELECT * FROM products
WHERE details ? 'tags';

SELECT * FROM products
WHERE details ?| array['tags', 'specs'];
```

### 2. 数组查询

```sql
SELECT * FROM products
WHERE details->'tags' @> '["apple"]'::jsonb;

SELECT 
    name,
    jsonb_array_elements_text(details->'tags') as tag
FROM products;
```

### 3. 路径查询

```sql
SELECT 
    name,
    jsonb_extract_path_text(details, 'specs', 'chip') as chip
FROM products;

SELECT * FROM products
WHERE jsonb_extract_path(details, 'specs', 'chip') = '"M3 Pro"'::jsonb;
```

## 四、索引优化

### 1. GIN 索引

```sql
CREATE INDEX idx_products_details_gin ON products USING GIN (details);

CREATE INDEX idx_products_tags_gin ON products USING GIN ((details->'tags'));
```

### 2. BTREE 索引

```sql
CREATE INDEX idx_products_brand ON products ((details->>'brand'));
CREATE INDEX idx_products_price ON products (((details->'price')::numeric));
```

### 3. 表达式索引

```sql
CREATE INDEX idx_products_chip ON products ((details->'specs'->>'chip'));
```

## 五、更新操作

### 1. 替换字段

```sql
UPDATE products
SET details = jsonb_set(
    details,
    '{price}',
    '8999'::jsonb
)
WHERE name = 'iPhone 15';
```

### 2. 添加字段

```sql
UPDATE products
SET details = details || '{"color": "black"}'::jsonb
WHERE name = 'iPhone 15';
```

### 3. 删除字段

```sql
UPDATE products
SET details = details - 'color'
WHERE name = 'iPhone 15';
```

### 4. 数组操作

```sql
UPDATE products
SET details = jsonb_set(
    details,
    '{tags}',
    (details->'tags') || '["new"]'::jsonb
)
WHERE name = 'iPhone 15';
```

## 六、聚合与统计

```sql
SELECT 
    details->>'brand' as brand,
    COUNT(*) as count,
    AVG((details->'price')::numeric) as avg_price
FROM products
GROUP BY details->>'brand';

SELECT 
    jsonb_object_agg(name, details->'price') as price_map
FROM products;
```

## 七、性能优化建议

1. 使用 GIN 索引进行包含查询
2. 使用 BTREE 索引进行范围查询
3. 避免在大 JSONB 上使用 `->` 链式调用
4. 合理设计 JSON 结构
5. 定期分析查询计划

## 八、实战案例：电商商品系统

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT,
    items JSONB,
    total NUMERIC,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO orders (user_id, items, total) VALUES
(1, '[
    {"product_id": 1, "quantity": 2, "price": 7999},
    {"product_id": 2, "quantity": 1, "price": 14999}
]'::jsonb, 30997);

CREATE INDEX idx_orders_items_gin ON orders USING GIN (items);

SELECT 
    o.id,
    i->>'product_id' as product_id,
    (i->>'quantity')::int as quantity,
    (i->>'price')::numeric as price
FROM orders o,
     jsonb_array_elements(o.items) i
WHERE o.id = 1;
```

## 九、总结

PostgreSQL JSONB 是处理半结构化数据的强大工具：
- 使用 GIN 索引优化包含查询
- 使用 BTREE 索引优化范围查询
- 合理设计 JSON 结构
- 注意更新性能

掌握 JSONB，让你的 PostgreSQL 更加强大！
