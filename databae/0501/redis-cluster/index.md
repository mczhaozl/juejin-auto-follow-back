# Redis Cluster 集群完全指南：从原理到实战部署

## 一、Redis Cluster 概述

### 1.1 集群特性

- **数据分片**：16384 个槽位（hash slots）
- **高可用**：主从复制，自动故障转移
- **去中心化**：无中心节点，gossip 协议
- **在线扩缩容**：不影响服务的情况下增加/删除节点

### 1.2 架构原理

```
节点1 (主)  ──  节点2 (从)
   |
节点3 (主)  ──  节点4 (从)
   |
节点5 (主)  ──  节点6 (从)
```

---

## 二、集群部署

### 2.1 节点配置

```redis
# 7000.conf
port 7000
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 5000
appendonly yes
```

### 2.2 启动节点

```bash
# 启动多个节点
redis-server 7000.conf
redis-server 7001.conf
redis-server 7002.conf
redis-server 7003.conf
redis-server 7004.conf
redis-server 7005.conf
```

### 2.3 创建集群

```bash
# Redis 5.0+ 使用 redis-cli
redis-cli --cluster create \
  127.0.0.1:7000 \
  127.0.0.1:7001 \
  127.0.0.1:7002 \
  127.0.0.1:7003 \
  127.0.0.1:7004 \
  127.0.0.1:7005 \
  --cluster-replicas 1
```

---

## 三、Hash Tag 与数据分布

### 3.1 哈希槽计算

```javascript
// CRC16 算法计算槽位
function hashSlot(key) {
  const hash = crc16(key);
  return hash % 16384;
}

console.log(hashSlot('user:1'));  // 某个槽位
```

### 3.2 Hash Tag 使用

```bash
# 使用 {} 指定相同槽位
SET {user:1}:name "Alice"
SET {user:1}:email "alice@example.com"
SET {user:1}:age 30
```

---

## 四、集群管理

### 4.1 集群信息

```bash
CLUSTER INFO
CLUSTER NODES
CLUSTER SLOTS
```

### 4.2 节点信息

```bash
CLUSTER MYID
CLUSTER KEYSLOT "key"
CLUSTER COUNTKEYSINSLOT 0
CLUSTER GETKEYSINSLOT 0 10
```

---

## 五、扩容与缩容

### 5.1 添加主节点

```bash
# 启动新节点
redis-server 7006.conf

# 加入集群
redis-cli --cluster add-node 127.0.0.1:7006 127.0.0.1:7000

# 迁移槽位
redis-cli --cluster reshard 127.0.0.1:7000
```

### 5.2 添加从节点

```bash
# 启动新节点
redis-server 7007.conf

# 加入集群作为从节点
redis-cli --cluster add-node \
  --cluster-slave \
  --cluster-master-id <master-id> \
  127.0.0.1:7007 127.0.0.1:7000
```

### 5.3 删除节点

```bash
# 先迁移槽位
redis-cli --cluster reshard 127.0.0.1:7000

# 删除节点
redis-cli --cluster del-node 127.0.0.1:7000 <node-id>
```

---

## 六、故障转移

### 6.1 手动故障转移

```bash
# 在从节点上执行
CLUSTER FAILOVER
```

### 6.2 强制故障转移

```bash
CLUSTER FAILOVER FORCE
```

---

## 七、客户端连接

### 7.1 Jedis 集群连接

```java
Set<HostAndPort> jedisClusterNodes = new HashSet<>();
jedisClusterNodes.add(new HostAndPort("127.0.0.1", 7000));
jedisClusterNodes.add(new HostAndPort("127.0.0.1", 7001));

JedisCluster jedisCluster = new JedisCluster(jedisClusterNodes);

jedisCluster.set("key", "value");
String value = jedisCluster.get("key");
```

### 7.2 ioredis 集群连接

```javascript
const Redis = require('ioredis');

const cluster = new Redis.Cluster([
  { host: '127.0.0.1', port: 7000 },
  { host: '127.0.0.1', port: 7001 }
]);

cluster.set('key', 'value');
cluster.get('key');
```

### 7.3 Python redis-py-cluster

```python
from rediscluster import RedisCluster

startup_nodes = [
    {"host": "127.0.0.1", "port": "7000"},
    {"host": "127.0.0.1", "port": "7001"}
]

rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

rc.set("key", "value")
print(rc.get("key"))
```

---

## 八、监控与运维

### 8.1 集群健康检查

```bash
redis-cli --cluster check 127.0.0.1:7000
```

### 8.2 性能监控

```bash
# 集群信息
CLUSTER INFO

# 慢查询
SLOWLOG GET 10
```

### 8.3 备份与恢复

```bash
# 备份：在每个主节点执行 BGSAVE
# 恢复：重启节点
```

---

## 九、最佳实践

### 9.1 集群规划

- 至少 3 个主节点
- 每个主节点至少 1 个从节点
- 节点分布在不同物理机

### 9.2 Key 设计

- 使用 Hash Tag 处理事务
- 避免 bigkey
- 合理设置过期时间

### 9.3 运维注意

- 监控节点状态
- 定期备份
- 小心扩容操作

---

## 总结

Redis Cluster 提供了强大的数据分片和高可用能力。通过合理的集群规划和运维，可以构建稳定、可扩展的 Redis 服务。
