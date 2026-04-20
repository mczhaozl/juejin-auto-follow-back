# PostgreSQL Stored Procedures & Functions 完全指南

## 一、创建函数

```sql
-- 简单函数
CREATE OR REPLACE FUNCTION add_numbers(a INTEGER, b INTEGER)
RETURNS INTEGER AS $$
BEGIN
    RETURN a + b;
END;
$$ LANGUAGE plpgsql;

-- 使用
SELECT add_numbers(1, 2);
```

## 二、返回表

```sql
CREATE OR REPLACE FUNCTION get_users_by_country(country TEXT)
RETURNS TABLE (id INTEGER, name TEXT, email TEXT) AS $$
BEGIN
    RETURN QUERY SELECT id, name, email FROM users WHERE users.country = country;
END;
$$ LANGUAGE plpgsql;

-- 使用
SELECT * FROM get_users_by_country('China');
```

## 三、存储过程

```sql
CREATE OR REPLACE PROCEDURE transfer_money(from_acc INTEGER, to_acc INTEGER, amount NUMERIC)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE accounts SET balance = balance - amount WHERE id = from_acc;
    UPDATE accounts SET balance = balance + amount WHERE id = to_acc;
END;
$$;

-- 调用
CALL transfer_money(1, 2, 100.00);
```

## 四、触发器

```sql
-- 触发器函数
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER users_update_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

## 五、最佳实践

- 函数用于查询和计算
- 过程用于修改数据
- 使用事务确保一致性
- 适当使用触发器
- 性能考虑：避免复杂逻辑
- 版本管理和文档
- 考虑安全性和权限
