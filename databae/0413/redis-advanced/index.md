# Redis 高级应用：数据结构与缓存策略

> 深入讲解 Redis 高级特性，包括 Sorted Set、Bitmap、HyperLogLog、Pipeline，以及缓存策略和分布式锁实现。

## 一、Redis 数据结构

### 1.1 String

```javascript
// 基本操作
await client.set('key', 'value');
await client.get('key');

// 过期
await client.setex('key', 3600, 'value');

// 计数
await client.incr('counter');
await client.incrby('counter', 10);
```

### 1.2 List

```javascript
// 队列
await client.lpush('queue', 'item1');
await client.rpop('queue');

// 列表
await client.lrange('list', 0, -1);
```

### 1.3 Hash

```javascript
await client.hset('user:1', 'name', '张三');
await client.hget('user:1', 'name');
await client.hgetall('user:1');
```

### 1.4 Sorted Set

```javascript
// 排行榜
await client.zadd('leaderboard', { 'user1': 100, 'user2': 90 });

// 获取排名
await client.zrevrank('leaderboard', 'user1');
await client.zscore('leaderboard', 'user1');

// 范围查询
await client.zrevrange('leaderboard', 0, 9);
```

## 二、高级数据类型

### 2.1 Bitmap

```javascript
// 用户签到
await client.setbit('sign:2024:01', userId, 1);

// 统计
await client.bitcount('sign:2024:01');
```

### 2.2 HyperLogLog

```javascript
await client.pfadd('uv', 'user1', 'user2', 'user3');
await client.pfcount('uv');
```

## 三、Pipeline

### 3.1 批量操作

```javascript
const pipeline = client.pipeline();
pipeline.set('key1', 'value1');
pipeline.set('key2', 'value2');
pipeline.get('key1');
const results = await pipeline.exec();
```

## 四、缓存策略

### 4.1 缓存模式

```javascript
async function getData(key) {
  const cached = await client.get(key);
  if (cached) return JSON.parse(cached);
  
  const data = await db.query(key);
  await client.setex(key, 3600, JSON.stringify(data));
  return data;
}
```

### 4.2 分布式锁

```javascript
async function acquireLock(key, ttl = 10) {
  const result = await client.set(key, 'lock', 'EX', ttl, 'NX');
  return result === 'OK';
}

async function releaseLock(key) {
  await client.del(key);
}
```

## 五、总结

Redis 高级核心要点：

1. **String**：基础类型
2. **List**：队列
3. **Hash**：对象存储
4. **Sorted Set**：排行榜
5. **Bitmap**：位操作
6. **Pipeline**：批量操作

掌握这些，Redis 不再是简单的缓存！

---

**推荐阅读**：
- [Redis 官方文档](https://redis.io/docs/)

**如果对你有帮助，欢迎点赞收藏！**
