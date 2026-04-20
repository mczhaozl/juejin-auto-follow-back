# Redis Cluster 集群完全指南

## 一、Redis Cluster 概述

### 1.1 什么是 Redis Cluster

Redis 的分布式解决方案，提供数据分片和高可用。

### 1.2 核心特性

- 自动分片
- 主从复制
- 自动故障转移
- 无中心化

## 二、数据分片

### 2.1 哈希槽 (Hash Slot)

Redis Cluster 使用 16384 个哈希槽：

```
HASH_SLOT = CRC16(key) mod 16384
```

### 2.2 集群节点分配

```
节点 A: 0-5460
节点 B: 5461-10922
节点 C: 10923-16383
```

## 三、集群搭建

### 3.1 创建配置文件

```conf
# redis-7000.conf
port 7000
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 5000
appendonly yes
```

### 3.2 启动节点

```bash
# 启动 6 个节点
redis-server redis-7000.conf
redis-server redis-7001.conf
redis-server redis-7002.conf
redis-server redis-7003.conf
redis-server redis-7004.conf
redis-server redis-7005.conf
```

### 3.3 创建集群

```bash
redis-cli --cluster create \
    127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
    127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
    --cluster-replicas 1
```

## 四、集群管理

### 4.1 集群信息

```bash
redis-cli -c -p 7000 cluster info
redis-cli -c -p 7000 cluster nodes
```

### 4.2 集群槽管理

```bash
# 添加新节点
redis-cli --cluster add-node 127.0.0.1:7006 127.0.0.1:7000

# 删除节点
redis-cli --cluster del-node 127.0.0.1:7000 <node-id>

# 重新分片
redis-cli --cluster reshard 127.0.0.1:7000
```

## 五、高可用

### 5.1 主从复制

```
主节点 7000 -> 从节点 7003
主节点 7001 -> 从节点 7004
主节点 7002 -> 从节点 7005
```

### 5.2 故障转移

```bash
# 手动故障转移
redis-cli -c -p 7003 cluster failover
```

## 六、客户端连接

### 6.1 智能客户端

```javascript
const Redis = require('ioredis');

const cluster = new Redis.Cluster([
  { host: '127.0.0.1', port: 7000 },
  { host: '127.0.0.1', port: 7001 },
  { host: '127.0.0.1', port: 7002 }
]);

cluster.set('key1', 'value1');
cluster.get('key1');
```

### 6.2 Hash Tag

```javascript
// 使用 {user} 前缀确保相同槽位
cluster.set('{user}:123', 'data');
cluster.hgetall('{user}:123');
```

## 七、最佳实践

- 至少 3 主 3 从
- 合理规划哈希槽
- 监控集群状态
- 配置合适的超时时间
- 使用 hash tag 分组相关键
