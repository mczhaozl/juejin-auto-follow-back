# Redis 内存优化完全指南

## 一、内存使用分析

```bash
# 查看内存信息
INFO memory

# 查看键内存占用
DEBUG OBJECT key

# 使用 redis-rdb-tools 分析
rdb dump.rdb -c memory
```

## 二、数据结构优化

### 2.1 合理选择数据类型

```javascript
// 使用 Hash 代替多个 String
// 不推荐
user:100:name "Alice"
user:100:age "25"

// 推荐
HSET user:100 name Alice age 25
```

### 2.2 使用整数编码

```javascript
// 整数会被优化存储
SET counter:1 100
```

### 2.3 List 压缩列表

```bash
# 配置
list-max-ziplist-entries 512
list-max-ziplist-value 64
```

## 三、内存过期策略

### 3.1 设置过期时间

```javascript
SET key value EX 3600

// LRU 策略
EXPIRE cache:user:1 86400
```

### 3.2 淘汰策略配置

```conf
maxmemory 10gb
maxmemory-policy allkeys-lru
```

## 四、持久化优化

```conf
# RDB 持久化
save 900 1
save 300 10
save 60 10000

# AOF 持久化
appendfsync everysec
no-appendfsync-on-rewrite yes
```

## 五、集群分片

```javascript
// 使用 Redis Cluster 水平扩展
// 合理分配 hash slot
```

## 六、监控与告警

```bash
INFO stats

// 监控指标
used_memory_rss
evicted_keys
keyspace_hits/misses
```

## 七、最佳实践

- 合理设计键名和数据结构
- 为缓存设置过期时间
- 使用合适的淘汰策略
- 监控内存使用情况
- 定期清理过期数据
- 使用压缩列表优化小对象
