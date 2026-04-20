# Redis Sentinel 高可用完全指南

## 一、Sentinel 概述

### 1.1 什么是 Sentinel

Redis 的高可用解决方案，监控主从、自动故障转移。

### 1.2 核心功能

- **监控**：检查主从节点状态
- **通知**：故障时通知管理员
- **故障转移**：自动提升从节点为主节点
- **配置提供者**：为客户端提供发现服务

---

## 二、部署架构

### 2.1 推荐架构

```
Sentinel 1     Sentinel 2     Sentinel 3
     \             |             /
      ---------------------------
                  |
         Master (Node 1)
          /            \
  Slave (Node 2)   Slave (Node 3)
```

### 2.2 Sentinel 数量

- 至少 3 个 Sentinel
- 奇数个节点（防止脑裂）

---

## 三、配置 Sentinel

### 3.1 Sentinel 配置

```conf
# sentinel.conf
port 26379
daemonize yes
logfile "/var/log/redis/sentinel.log"
dir "/var/redis"

sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 60000
```

### 3.2 参数说明

- `monitor`：监控的主节点
- `quorum`：判断主观下线的最少 Sentinel 数
- `down-after-milliseconds`：主观下线判断时间
- `failover-timeout`：故障转移超时时间

---

## 四、启动流程

### 4.1 启动 Redis 节点

```bash
# 主节点
redis-server redis.conf --port 6379

# 从节点
redis-server redis.conf --port 6380 --slaveof 127.0.0.1 6379
redis-server redis.conf --port 6381 --slaveof 127.0.0.1 6379
```

### 4.2 启动 Sentinel

```bash
redis-sentinel sentinel.conf
redis-sentinel sentinel-2.conf
redis-sentinel sentinel-3.conf
```

---

## 五、Sentinel 命令

```bash
# 查看监控的主节点
redis-cli -p 26379 SENTINEL masters

# 查看从节点
redis-cli -p 26379 SENTINEL slaves mymaster

# 查看 Sentinel 信息
redis-cli -p 26379 SENTINEL ckquorum mymaster

# 手动触发故障转移
redis-cli -p 26379 SENTINEL failover mymaster
```

---

## 六、客户端连接

### 6.1 使用 Sentinel 发现

```javascript
const Redis = require('ioredis');

const redis = new Redis({
  sentinels: [
    { host: 'sentinel1', port: 26379 },
    { host: 'sentinel2', port: 26379 },
    { host: 'sentinel3', port: 26379 }
  ],
  name: 'mymaster'
});
```

### 6.2 读写分离

```javascript
const master = new Redis({ sentinels, name: 'mymaster', role: 'master' });
const slave = new Redis({ sentinels, name: 'mymaster', role: 'slave' });
```

---

## 七、故障转移过程

1. 检测主节点下线
2. Sentinel 投票选举领头
3. 选择从节点
4. 升级从节点
5. 通知其他从节点跟随新主
6. 更新配置

---

## 八、监控与运维

```bash
# 检查状态
redis-cli -p 26379 INFO Sentinel

# 查看日志
tail -f /var/log/redis/sentinel.log

# 测试故障转移
redis-cli -p 6379 DEBUG sleep 30
```

---

## 九、最佳实践

- Sentinel 部署在不同机器
- 使用至少 3 个 Sentinel
- 合理配置时间参数
- 监控日志
- 定期测试故障转移

---

## 总结

Redis Sentinel 提供了可靠的高可用保障，通过自动故障转移确保服务连续性。
