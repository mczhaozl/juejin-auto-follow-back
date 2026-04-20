# PostgreSQL 主从复制与高可用完全指南

## 一、复制概述

### 1.1 复制类型

- **流复制（Streaming Replication）**：实时传输 WAL
- **逻辑复制（Logical Replication）**：复制数据变更
- **归档复制**：基于 WAL 归档

### 1.2 复制模式

- **异步复制**：性能高，可能丢失数据
- **同步复制**：数据安全，性能较低

---

## 二、流复制配置

### 2.1 主节点配置

```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1GB
hot_standby = on
listen_addresses = '*'
```

```ini
# pg_hba.conf
host  replication  repuser  192.168.1.0/24  scram-sha-256
```

```sql
-- 创建复制用户
CREATE USER repuser REPLICATION LOGIN PASSWORD 'password';

-- 基础备份
SELECT pg_backup_start('replica');
-- 复制数据目录
SELECT pg_backup_stop();
```

### 2.2 从节点配置

```ini
# postgresql.conf
hot_standby = on
primary_conninfo = 'host=192.168.1.10 port=5432 user=repuser password=password'
primary_slot_name = 'replica1'
```

```conf
# recovery.signal
standby_mode = 'on'
```

### 2.3 使用 pg_basebackup

```bash
# 从节点
pg_basebackup -h 192.168.1.10 -D /var/lib/postgresql/15/main -U repuser -P -R
```

---

## 三、监控复制

### 3.1 主节点监控

```sql
-- 查看复制状态
SELECT * FROM pg_stat_replication;

-- 查看发送延迟
SELECT
  pid,
  usename,
  application_name,
  state,
  sent_lsn,
  write_lsn,
  flush_lsn,
  replay_lsn,
  pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) AS delay
FROM pg_stat_replication;
```

### 3.2 从节点监控

```sql
-- 查看恢复状态
SELECT * FROM pg_stat_wal_receiver;

-- 查看复制延迟
SELECT
  pg_is_in_recovery(),
  pg_last_wal_receive_lsn(),
  pg_last_wal_replay_lsn(),
  pg_last_xact_replay_timestamp(),
  now() - pg_last_xact_replay_timestamp() AS replication_lag;
```

---

## 四、同步复制

### 4.1 配置同步复制

```ini
# 主节点 postgresql.conf
synchronous_commit = on
synchronous_standby_names = 'replica1'
```

### 4.2 多同步副本

```ini
synchronous_standby_names = 'ANY 2 (replica1, replica2, replica3)'
```

---

## 五、故障转移

### 5.1 手动故障转移

```bash
# 在从节点上
pg_ctl promote -D /var/lib/postgresql/15/main
```

### 5.2 使用触发器文件

```bash
# 创建触发文件
touch /var/lib/postgresql/15/main/trigger

# postgresql.conf
promote_trigger_file = '/var/lib/postgresql/15/main/trigger'
```

---

## 六、逻辑复制

### 6.1 发布者配置

```sql
-- 创建发布
CREATE PUBLICATION my_publication FOR TABLE users, orders;

-- 添加表
ALTER PUBLICATION my_publication ADD TABLE products;
```

### 6.2 订阅者配置

```sql
-- 创建订阅
CREATE SUBSCRIPTION my_subscription
CONNECTION 'host=192.168.1.10 port=5432 dbname=mydb user=repuser password=password'
PUBLICATION my_publication;
```

### 6.3 监控逻辑复制

```sql
-- 发布者
SELECT * FROM pg_publication;
SELECT * FROM pg_stat_replication;

-- 订阅者
SELECT * FROM pg_subscription;
SELECT * FROM pg_stat_subscription;
```

---

## 七、高可用方案

### 7.1 Patroni

```yaml
# patroni.yml
scope: postgres
namespace: /service/
name: postgresql-0

restapi:
  listen: 0.0.0.0:8008
  connect_address: 192.168.1.10:8008

etcd:
  host: 192.168.1.10:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      use_slots: true

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 192.168.1.10:5432
  data_dir: /var/lib/postgresql/15/main
  pgpass: /tmp/pgpass
  authentication:
    replication:
      username: replicator
      password: rep-pass
    superuser:
      username: postgres
      password: postgres
  parameters:
    wal_level: replica
    hot_standby: "on"
    wal_keep_size: 1GB
    max_wal_senders: 5
    max_replication_slots: 5
    checkpoint_timeout: 300
```

### 7.2 启动 Patroni

```bash
patroni patroni.yml
```

### 7.3 查看集群状态

```bash
patronictl -c patroni.yml list
```

---

## 八、备份与恢复

### 8.1 pg_basebackup 备份

```bash
# 完整备份
pg_basebackup -h master -U repuser -D /backup/$(date +%Y%m%d) -P -X stream
```

### 8.2 WAL 归档

```ini
# postgresql.conf
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
```

### 8.3 时间点恢复

```bash
# 恢复基础备份
tar -xzf /backup/20240101.tar.gz -C /var/lib/postgresql/15/main

# 创建 recovery.signal
echo "restore_command = 'cp /backup/wal/%f %p'" > /var/lib/postgresql/15/main/recovery.signal
echo "recovery_target_time = '2024-01-01 12:00:00'" >> /var/lib/postgresql/15/main/recovery.signal

# 启动
pg_ctl start
```

---

## 九、最佳实践

### 9.1 监控指标

- 复制延迟
- WAL 生成速度
- 从节点状态
- 同步复制状态

### 9.2 维护建议

- 定期测试故障转移
- 监控磁盘空间
- 定期备份
- 升级规划

---

## 总结

PostgreSQL 提供了强大的复制功能，通过流复制和逻辑复制可以构建高可用架构。结合 Patroni 等工具，可以实现自动化的故障转移。
