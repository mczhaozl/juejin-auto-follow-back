# MongoDB Sharding 分片集群完全指南

## 一、分片概述

### 1.1 什么是分片

将数据水平拆分到多台机器上的过程。

### 1.2 核心组件

- **Shard**：存储数据的节点
- **mongos**：查询路由器
- **Config Server**：存储集群元数据

---

## 二、分片键选择

### 2.1 好的分片键

```javascript
// 高基数、读写分布均匀
{ userId: 1 }
{ createdAt: 1 }
{ _id: "hashed" }
```

### 2.2 复合分片键

```javascript
{ userId: 1, createdAt: -1 }
```

---

## 三、部署分片集群

### 3.1 配置 Config Server

```bash
mongod --configsvr --replSet configReplica --dbpath /data/config
```

```javascript
rs.initiate({
  _id: "configReplica",
  configsvr: true,
  members: [
    { _id: 0, host: "config1:27019" },
    { _id: 1, host: "config2:27019" },
    { _id: 2, host: "config3:27019" }
  ]
})
```

### 3.2 添加 Shard

```bash
mongod --shardsvr --replSet shard1 --dbpath /data/shard1
```

```javascript
sh.addShard("shard1/host1:27018")
sh.addShard("shard2/host2:27018")
```

### 3.3 启动 mongos

```bash
mongos --configdb configReplica/config1:27019,config2:27019,config3:27019
```

---

## 四、启用分片

### 4.1 对数据库启用分片

```javascript
sh.enableSharding("mydb")
```

### 4.2 对集合分片

```javascript
sh.shardCollection("mydb.users", { userId: 1 })

// Hashed 分片
sh.shardCollection("mydb.logs", { _id: "hashed" })

// Zone 分片
sh.shardCollection("mydb.data", { region: 1, _id: 1 })
```

---

## 五、分片管理

### 5.1 查看分片状态

```javascript
sh.status()
sh.addShardTag("shard1", "us-east")
sh.addShardTag("shard2", "us-west")
```

### 5.2 管理 Chunk

```javascript
sh.splitFind("mydb.users", { userId: 5000 })
sh.moveChunk("mydb.users", { userId: 1 }, "shard1")
```

### 5.3 Chunk 大小

```javascript
use config
db.settings.save({ _id: "chunksize", value: 128 })
```

---

## 六、Zone 分片

```javascript
// 添加 Zone
sh.addShardTag("shard1", "EU")
sh.addShardTag("shard2", "US")

// 定义范围
sh.addTagRange("mydb.users", { region: "EU" }, { region: "EU" }, "EU")
sh.addTagRange("mydb.users", { region: "US" }, { region: "US" }, "US")
```

---

## 七、最佳实践

- 选择好的分片键
- 预分片
- 监控 chunk 分布
- 避免热点
- 定期平衡

---

## 总结

分片是 MongoDB 水平扩展的核心，合理规划分片键和架构可以支撑大规模数据和高并发。
