# Redis 缓存实战：全面掌握 Redis 数据结构与缓存策略

> 深入讲解 Redis 核心数据结构、缓存策略、持久化机制，以及 Redis 在实际项目中的最佳应用实践。

## 一、Redis 基础

### 1.1 为什么用 Redis

Redis 是内存数据库，性能极高：

- 读：110000 次/秒
- 写：81000 次/秒

### 1.2 数据结构

| 类型 | 用途 |
|------|------|
| String | 缓存、计数器 |
| Hash | 对象存储 |
| List | 队列、列表 |
| Set | 去重、标签 |
| ZSet | 排行榜、排序 |

## 二、核心数据结构

### 2.1 String

```bash
SET key value
GET key

# 设置过期时间
SETEX key 60 value

# 计数器
INCR counter
DECR counter

# 批量操作
MSET key1 value1 key2 value2
MGET key1 key2
```

### 2.2 Hash

```bash
HSET user:1 name zhangsan age 25
HGET user:1 name
HGETALL user:1

# 批量
HMSET user:1 name lisi city beijing
```

### 2.3 List

```bash
LPUSH mylist a
RPUSH mylist b
LRANGE mylist 0 -1

# 队列
LPOP mylist
RPOP mylist
```

### 2.4 Set

```bash
SADD tags 1 2 3
SMEMBERS tags
SISMEMBER tags 1

# 交集、并集
SINTER set1 set2
SUNION set1 set2
```

### 2.5 ZSet

```bash
ZADD leaderboard 100 user1
ZADD leaderboard 90 user2

# 排名
ZRANGE leaderboard 0 -1 WITHSCORES
ZREVRANGE leaderboard 0 9 WITHSCORES
```

## 三、缓存策略

### 3.1 Cache-Aside

```javascript
async function getUser(id) {
  // 1. 先查缓存
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);
  
  // 2. 缓存未命中，查数据库
  const user = await db.query('SELECT * FROM users WHERE id = ?', [id]);
  
  // 3. 存入缓存
  await redis.setex(`user:${id}`, 3600, JSON.stringify(user));
  
  return user;
}
```

### 3.2 Read-Through

```javascript
async function getData(key) {
  return await cache.get(key, async () => {
    return await db.query(key);
  });
}
```

### 3.3 Write-Through

```javascript
async function updateUser(id, data) {
  await db.update(id, data);
  await redis.set(`user:${id}`, JSON.stringify(data));
}
```

### 3.4 缓存过期策略

```bash
# 设置过期时间
EXPIRE key 3600

# 查看剩余时间
TTL key

# 惰性删除：使用时检查过期
# 定期删除：随机检查部分 key
```

## 四、Redis 持久化

### 4.1 RDB 快照

```bash
# 自动触发
save 900 1
save 300 10
save 60 10000

# 手动触发
BGSAVE
```

### 4.2 AOF 日志

```bash
# 开启
appendonly yes

# 同步策略
appendfsync always
appendfsync everysec
appendfsync no
```

## 五、Redis 集群

### 5.1 主从复制

```bash
# 从节点配置
replicaof 127.0.0.1 6379
```

### 5.2 Sentinel

```bash
# 监控
sentinel monitor mymaster 127.0.0.1 6379 2
```

### 5.3 Cluster

```bash
# 创建集群
redis-cli --cluster create 127.0.0.1:7001 127.0.0.1:7002
```

## 六、实战案例

### 6.1 分布式锁

```javascript
async function acquireLock(key, ttl = 10) {
  const result = await redis.set(`lock:${key}`, '1', 'EX', ttl, 'NX');
  return result === 'OK';
}

async function releaseLock(key) {
  await redis.del(`lock:${key}`);
}
```

### 6.2 限流

```javascript
async function rateLimit(key, limit, window) {
  const now = Date.now();
  await redis.zremrangebyscore(key, 0, now - window * 1000);
  
  const count = await redis.zcard(key);
  if (count >= limit) return false;
  
  await redis.zadd(key, now, `${now}-${Math.random()}`);
  await redis.expire(key, window);
  
  return true;
}
```

### 6.3 延迟队列

```javascript
// 生产者
async function addDelayJob(jobId, delay) {
  const score = Date.now() + delay;
  await redis.zadd('delay:queue', score, jobId);
}

// 消费者
async function consume() {
  while (true) {
    const jobs = await redis.zrangebyscore('delay:queue', 0, Date.now());
    if (jobs.length === 0) {
      await sleep(1000);
      continue;
    }
    
    const jobId = jobs[0];
    await redis.zrem('delay:queue', jobId);
    await processJob(jobId);
  }
}
```

## 七、总结

Redis 核心要点：

1. **数据结构**：String、Hash、List、Set、ZSet
2. **缓存策略**：Cache-Aside、Read-Through
3. **持久化**：RDB、AOF
4. **集群**：主从、Sentinel、Cluster
5. **应用**：分布式锁、限流、延迟队列

掌握这些，你就能玩转 Redis 缓存！

---

**推荐阅读**：
- [Redis 官方文档](https://redis.io/documentation)
- [Redis 命令参考](https://redis.io/commands)

**如果对你有帮助，欢迎点赞收藏！**
