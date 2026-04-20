# Redis 持久化与备份完全指南

## 一、RDB 备份

```bash
# 备份 RDB
BGSAVE
cp /var/lib/redis/dump.rdb /backup/rdb-backup-$(date +%Y%m%d).rdb

# 自动备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M)
redis-cli BGSAVE
sleep 30
cp /var/lib/redis/dump.rdb /backup/rdb-$DATE.rdb
```

## 二、AOF 备份

```bash
# 备份 AOF
cp /var/lib/redis/appendonly.aof /backup/aof-backup.aof
```

## 三、从备份恢复

```bash
# 停止 Redis
systemctl stop redis

# 恢复备份
cp /backup/dump.rdb /var/lib/redis/dump.rdb

# 启动
systemctl start redis
```

## 四、AOF 修复

```bash
redis-check-aof --fix appendonly.aof
```

## 最佳实践
- 定期自动备份
- 测试恢复流程
- 使用独立文件系统
- 监控磁盘空间
- 异地备份
