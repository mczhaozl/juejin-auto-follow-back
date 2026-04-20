# MongoDB 性能调优完全指南

## 一、服务器配置优化

### 1.1 系统配置

```bash
# 最大文件描述符
* soft nofile 64000
* hard nofile 64000
```

### 1.2 内存配置

```yaml
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4  # 建议使用系统内存的 50%
```

## 二、WiredTiger 存储引擎

### 2.1 压缩配置

```yaml
storage:
  wiredTiger:
    collectionConfig:
      blockCompressor: snappy
    indexConfig:
      prefixCompression: true
```

### 2.2 Checkpoint 配置

```yaml
storage:
  wiredTiger:
    engineConfig:
      checkpointSizeMB: 2048
      checkpointDelaySecs: 60
```

## 三、连接池配置

```javascript
// Node.js 示例
const client = new MongoClient(uri, {
  maxPoolSize: 100,
  minPoolSize: 10,
  maxIdleTimeMS: 10000
});
```

## 四、索引优化

```javascript
// 1. 删除未使用的索引
db.aggregate([
  { $indexStats: {} },
  { $match: { accesses.ops: 0 } }
]);

// 2. 创建复合索引
db.collection.createIndex({ a: 1, b: -1 });
```

## 五、查询分析

```javascript
// 开启慢查询日志
db.setProfilingLevel(1, { slowms: 100 });

// 分析查询
db.collection.find(query).explain("executionStats");
```

## 六、监控工具

```bash
# MongoDB 自带监控
mongostat
mongotop

# 使用 Prometheus + Grafana
```

## 七、分片策略

```javascript
// 选择合适的分片键
db.collection.createIndex({ user_id: 1 });
sh.shardCollection("db.collection", { user_id: 1 });
```

## 八、最佳实践

- 合理设置 WiredTiger 缓存
- 定期整理索引
- 使用副本集实现读写分离
- 监控慢查询日志
- 合理使用 TTL 索引清理数据
