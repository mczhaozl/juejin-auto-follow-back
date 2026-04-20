# PostgreSQL PgBouncer 完全指南

## 一、基本配置

```ini
# pgbouncer.ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

## 二、用户列表

```text
# userlist.txt
"user1" "scram-sha-256:..."
"user2" "scram-sha-256:..."
```

## 三、连接方式

```bash
# psql 连接
psql -h localhost -p 6432 -U user1 mydb
```

```javascript
// Node.js
const client = new Client({
  host: 'localhost',
  port: 6432,
  user: 'user1',
  database: 'mydb'
});
```

## 四、管理

```sql
-- 连接到 pgbouncer 数据库
psql -p 6432 pgbouncer

-- 查看状态
SHOW STATS;
SHOW POOLS;
SHOW CLIENTS;

-- 管理
RELOAD;
PAUSE;
RESUME;
```

## 最佳实践
- 使用 transaction 模式
- 合理设置连接池大小
- 监控连接使用
- 注意 prepared statements
- 定期查看 pgbouncer 日志
