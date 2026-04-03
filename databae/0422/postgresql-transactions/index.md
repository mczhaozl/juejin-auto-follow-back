# PostgreSQL 事务与并发控制完全指南：ACID、锁与隔离级别

事务是数据库的核心概念，PostgreSQL 提供了强大的事务和并发控制机制。本文将带你全面掌握这些内容。

## 一、事务基础

### 1. 什么是事务

事务是一组 SQL 语句，它们作为一个整体执行，要么全部成功，要么全部失败。

### 2. ACID 特性

```
A - Atomicity（原子性）：要么全做，要么全不做
C - Consistency（一致性）：数据库从一个一致状态到另一个一致状态
I - Isolation（隔离性）：并发事务互不干扰
D - Durability（持久性）：一旦提交，永久保存
```

### 3. 基本事务语法

```sql
BEGIN;
-- 或 START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;
-- 或 ROLLBACK;
```

## 二、事务控制

### 1. 提交和回滚

```sql
BEGIN;

INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- 检查一下
SELECT * FROM users WHERE name = 'Alice';

-- 决定提交
COMMIT;

-- 或者回滚
-- ROLLBACK;
```

### 2. 保存点 (Savepoint)

```sql
BEGIN;

INSERT INTO users (name) VALUES ('Alice');
SAVEPOINT sp1;

INSERT INTO users (name) VALUES ('Bob');
SAVEPOINT sp2;

-- 回滚到 sp2
ROLLBACK TO sp2;

-- 继续
INSERT INTO users (name) VALUES ('Charlie');

COMMIT;
```

### 3. 事务块

```sql
-- PostgreSQL 默认自动提交
INSERT INTO users (name) VALUES ('Alice'); -- 自动提交

-- 显式事务
BEGIN;
INSERT INTO users (name) VALUES ('Bob');
INSERT INTO users (name) VALUES ('Charlie');
COMMIT;
```

## 三、并发问题

### 1. 脏读 (Dirty Read)

```
事务 A 更新数据但未提交
事务 B 读取了未提交的数据
事务 A 回滚
事务 B 读到了脏数据
```

### 2. 不可重复读 (Non-repeatable Read)

```
事务 A 读取数据
事务 B 更新并提交
事务 A 再次读取，数据变了
```

### 3. 幻读 (Phantom Read)

```
事务 A 按条件查询
事务 B 插入符合条件的数据并提交
事务 A 再次查询，多了一行
```

### 4. 丢失更新 (Lost Update)

```
事务 A 读取值 = 100
事务 B 读取值 = 100
事务 A 更新为 100 + 1 = 101
事务 B 更新为 100 + 1 = 101
丢失了一次更新
```

## 四、隔离级别

### 1. 读未提交 (Read Uncommitted)

```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- 可以读取未提交的数据
-- 可能脏读、不可重复读、幻读
```

### 2. 读已提交 (Read Committed) - PostgreSQL 默认

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 只能读取已提交的数据
-- 避免脏读
-- 可能不可重复读、幻读
```

### 3. 可重复读 (Repeatable Read)

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 同一事务内读取结果一致
-- 避免脏读、不可重复读
-- 可能幻读（PostgreSQL 用 MVCC 避免）
```

### 4. 可串行化 (Serializable)

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 最高隔离级别
-- 避免所有并发问题
-- 性能开销大
```

## 五、锁机制

### 1. 行锁

```sql
BEGIN;

--  FOR UPDATE 锁
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;

-- FOR NO KEY UPDATE 锁（不锁外键）
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;

-- FOR SHARE 锁（共享锁）
SELECT * FROM accounts WHERE id = 1 FOR SHARE;

-- FOR KEY SHARE 锁
SELECT * FROM accounts WHERE id = 1 FOR KEY SHARE;

COMMIT;
```

### 2. 表锁

```sql
-- 锁表
LOCK TABLE accounts IN ACCESS EXCLUSIVE MODE;

-- 锁模式：
-- ACCESS SHARE
-- ROW SHARE
-- ROW EXCLUSIVE
-- SHARE UPDATE EXCLUSIVE
-- SHARE
-- SHARE ROW EXCLUSIVE
-- EXCLUSIVE
-- ACCESS EXCLUSIVE
```

### 3. 死锁

```sql
-- 事务 1
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- 此时事务 2 锁定了 id=2
UPDATE accounts SET balance = balance + 100 WHERE id = 2; -- 等待
COMMIT;

-- 事务 2
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 2;
-- 此时事务 1 锁定了 id=1
UPDATE accounts SET balance = balance + 100 WHERE id = 1; -- 死锁！
COMMIT;

-- PostgreSQL 会自动检测并终止一个事务
```

## 六、MVCC (多版本并发控制)

### 1. MVCC 原理

PostgreSQL 使用 MVCC 实现高并发：
- 每个事务看到的是数据的一个快照
- 写操作创建新版本，不覆盖旧版本
- 读操作不需要锁

### 2. 可见性规则

```sql
-- 查看系统列
SELECT xmin, xmax, * FROM accounts;

-- xmin: 创建该行的事务 ID
-- xmax: 删除/更新该行的事务 ID
```

## 七、实战：银行转账

```sql
BEGIN;

-- 检查余额
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;

-- 扣款
UPDATE accounts 
SET balance = balance - 100 
WHERE id = 1 AND balance >= 100;

IF NOT FOUND THEN
    RAISE EXCEPTION 'Insufficient balance';
END IF;

-- 收款
UPDATE accounts 
SET balance = balance + 100 
WHERE id = 2;

-- 记录交易
INSERT INTO transactions (from_id, to_id, amount)
VALUES (1, 2, 100);

COMMIT;
```

## 八、性能优化

### 1. 保持事务简短

```sql
-- ❌ 不好：事务中做耗时操作
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
SELECT pg_sleep(10); -- 耗时操作
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- ✅ 好：事务只做必要操作
-- 先准备数据
-- 再在短事务内更新
```

### 2. 选择合适的隔离级别

```sql
-- 大部分场景用默认的 READ COMMITTED
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 需要严格一致性时用 REPEATABLE READ
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

### 3. 监控锁

```sql
-- 查看锁
SELECT * FROM pg_locks;

-- 查看活跃事务
SELECT * FROM pg_stat_activity;

-- 查看等待
SELECT * FROM pg_stat_activity WHERE wait_event IS NOT NULL;
```

## 九、总结

PostgreSQL 事务与并发控制：
- 理解 ACID 特性
- 掌握事务控制语句
- 理解 4 种隔离级别
- 了解锁机制
- 使用 MVCC 提高并发
- 保持事务简短
- 监控和优化

掌握这些，让你的 PostgreSQL 应用更健壮！
