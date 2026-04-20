# PostgreSQL PL/pgSQL 存储过程完全指南

## 一、PL/pgSQL 概述

### 1.1 什么是 PL/pgSQL

PostgreSQL 的过程化编程语言，用于编写函数和存储过程。

### 1.2 优势

- 性能提升
- 业务逻辑封装
- 事务控制

---

## 二、函数基础

### 2.1 简单函数

```sql
CREATE OR REPLACE FUNCTION add(a INTEGER, b INTEGER)
RETURNS INTEGER AS $$
BEGIN
  RETURN a + b;
END;
$$ LANGUAGE plpgsql;

SELECT add(1, 2);
```

### 2.2 使用参数

```sql
CREATE OR REPLACE FUNCTION get_user(user_id INTEGER)
RETURNS users AS $$
DECLARE
  user_record users%ROWTYPE;
BEGIN
  SELECT * INTO user_record FROM users WHERE id = user_id;
  RETURN user_record;
END;
$$ LANGUAGE plpgsql;
```

---

## 三、控制结构

### 3.1 IF 条件

```sql
CREATE OR REPLACE FUNCTION check_age(age INTEGER)
RETURNS VARCHAR AS $$
BEGIN
  IF age < 18 THEN
    RETURN 'Minor';
  ELSIF age < 65 THEN
    RETURN 'Adult';
  ELSE
    RETURN 'Senior';
  END IF;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 循环

```sql
CREATE OR REPLACE FUNCTION loop_example(n INTEGER)
RETURNS INTEGER AS $$
DECLARE
  total INTEGER := 0;
  i INTEGER;
BEGIN
  FOR i IN 1..n LOOP
    total := total + i;
  END LOOP;
  RETURN total;
END;
$$ LANGUAGE plpgsql;
```

### 3.3 WHILE 循环

```sql
CREATE OR REPLACE FUNCTION while_example(n INTEGER)
RETURNS INTEGER AS $$
DECLARE
  i INTEGER := 1;
  total INTEGER := 0;
BEGIN
  WHILE i <= n LOOP
    total := total + i;
    i := i + 1;
  END LOOP;
  RETURN total;
END;
$$ LANGUAGE plpgsql;
```

---

## 四、存储过程（事务）

```sql
CREATE OR REPLACE PROCEDURE transfer_money(
  from_id INTEGER,
  to_id INTEGER,
  amount NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
  from_balance NUMERIC;
BEGIN
  SELECT balance INTO from_balance FROM accounts WHERE id = from_id;
  
  IF from_balance < amount THEN
    RAISE EXCEPTION '余额不足';
  END IF;
  
  UPDATE accounts SET balance = balance - amount WHERE id = from_id;
  UPDATE accounts SET balance = balance + amount WHERE id = to_id;
  
  COMMIT;
END;
$$;

CALL transfer_money(1, 2, 100.00);
```

---

## 五、异常处理

```sql
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
  IF b = 0 THEN
    RAISE EXCEPTION '除数不能为0';
  END IF;
  RETURN a / b;
EXCEPTION
  WHEN division_by_zero THEN
    RAISE EXCEPTION '捕获到除以0错误';
  WHEN OTHERS THEN
    RAISE EXCEPTION '未知错误: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

---

## 六、实战：审计日志

```sql
-- 创建审计表
CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  action VARCHAR(50),
  table_name VARCHAR(100),
  record_id INTEGER,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  old_data JSONB,
  new_data JSONB
);

-- 创建插入触发器函数
CREATE OR REPLACE FUNCTION audit_insert()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log (action, table_name, record_id, new_data)
  VALUES ('INSERT', TG_TABLE_NAME, NEW.id, row_to_json(NEW));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER users_audit_insert
AFTER INSERT ON users
FOR EACH ROW EXECUTE FUNCTION audit_insert();
```

---

## 七、最佳实践

- 保持函数简单
- 使用合适的参数类型
- 处理异常
- 添加注释
- 测试边界情况

---

## 总结

PL/pgSQL 让我们在数据库端实现复杂的业务逻辑，通过函数和存储过程提高性能和安全性。
