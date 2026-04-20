# Redis Cluster 完全指南

## 一、集群搭建

```bash
# 创建配置文件
# redis-cluster.conf
port 7001
cluster-enabled yes
cluster-config-file nodes-7001.conf
cluster-node-timeout 5000
appendonly yes

# 启动节点
redis-server redis-cluster.conf
# 同样启动 7002, 7003, 7004, 7005, 7006

# 创建集群
redis-cli --cluster create 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 127.0.0.1:7006 --cluster-replicas 1
```

## 二、集群管理

```bash
# 检查集群状态
redis-cli -c -p 7001 cluster info

# 查看节点
redis-cli -c -p 7001 cluster nodes

# 添加节点
redis-cli --cluster add-node 127.0.0.1:7007 127.0.0.1:7001

# 重新分片
redis-cli --cluster reshard 127.0.0.1:7001
```

## 三、使用集群

```bash
# 使用 -c 参数开启集群模式
redis-cli -c -p 7001

# 设置和获取键 (自动路由)
SET key1 value1
GET key1

# 查看键所在节点
redis-cli -c -p 7001 CLUSTER KEYSLOT key1
```

## 四、Jedis (Java) 客户端

```java
import redis.clients.jedis.JedisCluster;
import redis.clients.jedis.HostAndPort;

Set<HostAndPort> jedisClusterNodes = new HashSet<>();
jedisClusterNodes.add(new HostAndPort("127.0.0.1", 7001));
JedisCluster jedisCluster = new JedisCluster(jedisClusterNodes);

jedisCluster.set("key", "value");
String value = jedisCluster.get("key");
```

## 最佳实践
- 每个主节点至少一个从节点
- slot 迁移需要注意
- 避免跨 slot 操作
- 监控节点内存和延迟
- 合理选择集群大小
