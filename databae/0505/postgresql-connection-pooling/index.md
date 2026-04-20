# PostgreSQL 连接池完全指南

## 一、连接池简介

### 1.1 为什么需要连接池

- 避免频繁创建/销毁连接的开销
- 控制数据库连接数
- 提高应用性能

## 二、PgBouncer 配置

### 2.1 安装 PgBouncer

```bash
sudo apt-get install pgbouncer
```

### 2.2 配置文件

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

### 2.3 用户认证

```bash
# /etc/pgbouncer/userlist.txt
"myuser" "md5xxxxxxxxxx"
```

## 三、连接池模式

- **Session 模式**: 每个客户端会话独占连接
- **Transaction 模式**: 每个事务复用连接
- **Statement 模式**: 每条语句复用连接

## 四、应用侧连接池

### 4.1 Node.js (pg-pool)

```javascript
const { Pool } = require('pg');
const pool = new Pool({
  host: 'localhost',
  port: 6432,  // 使用 PgBouncer 端口
  max: 20,
  idleTimeoutMillis: 30000
});
```

### 4.2 Go (sql.DB)

```go
db, err := sql.Open("postgres", "host=localhost port=6432 ...")
db.SetMaxOpenConns(20)
db.SetMaxIdleConns(10)
```

## 五、监控

```sql
-- 查询活动连接
SELECT count(*) FROM pg_stat_activity;

-- PgBouncer 管理命令
SHOW STATS;
SHOW POOLS;
```

## 六、最佳实践

- 使用 PgBouncer 作为外部连接池
- 应用侧也配置连接池
- 选择合适的 pool_mode（通常用 transaction）
- 合理设置连接池大小
- 监控连接池状态
- 定期维护和优化配置
