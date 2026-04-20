# Redis AOF 与 RDB 持久化完全指南

## 一、RDB 持久化

```conf
# redis.conf
save 900 1      # 900 秒内至少 1 个键修改
save 300 10     # 300 秒内至少 10 个键修改
save 60 10000   # 60 秒内至少 10000 个键修改

dbfilename dump.rdb
dir ./
```

```bash
# 手动生成 RDB
redis-cli BGSAVE

# 查看持久化状态
redis-cli INFO persistence
```

## 二、AOF 持久化

```conf
# 开启 AOF
appendonly yes
appendfilename "appendonly.aof"

# 同步策略
# appendfsync always  # 每次写入都同步
appendfsync everysec # 每秒同步
# appendfsync no      # 操作系统自己决定

# AOF 重写
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

```bash
# 手动 AOF 重写
redis-cli BGREWRITEAOF
```

## 三、混合持久化

```conf
# 4.0+ 混合 RDB+AOF
aof-use-rdb-preamble yes
```

## 四、备份恢复

```bash
# 1. 备份 RDB
cp dump.rdb dump.rdb.backup

# 2. 备份 AOF
cp appendonly.aof appendonly.aof.backup

# 3. 恢复
# 只需将 RDB/AOF 放到 dir 目录重启 Redis
```

## 最佳实践
- 生产环境同时开启 RDB + AOF
- AOF 推荐 everysec
- 监控持久化频率和延迟
- 定期测试备份恢复流程
- 使用混合持久化获得最佳性能
