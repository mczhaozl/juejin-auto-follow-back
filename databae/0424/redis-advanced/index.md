# Redis 高级应用完全指南：从缓存到分布式系统

Redis 是一个高性能的内存数据库，除了作为缓存外，还有很多高级应用场景。本文将带你全面掌握 Redis 的高级功能。

## 一、Redis 基础回顾

### 1. 安装与连接

```bash
# 安装 Redis
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# macOS
brew install redis

# 使用 Docker
docker run -d -p 6379:6379 redis:latest
```

```javascript
// 使用 ioredis
const Redis = require('ioredis');
const redis = new Redis({
  host: 'localhost',
  port: 6379,
  password: 'your-password',
  db: 0,
});

// 测试连接
redis.ping().then(result => {
  console.log('Redis connected:', result);
});
```

### 2. 基本数据类型

```javascript
// String（字符串）
await redis.set('name', 'Alice');
const name = await redis.get('name');
console.log(name); // 输出: Alice

await redis.setex('token', 3600, 'abc123'); // 过期时间 1 小时
await redis.incr('counter');
await redis.incrby('counter', 10);

// Hash（哈希）
await redis.hset('user:1', {
  name: 'Alice',
  email: 'alice@example.com',
  age: '30'
});
const user = await redis.hgetall('user:1');
console.log(user); // 输出: { name: 'Alice', email: 'alice@example.com', age: '30' }

// List（列表）
await redis.lpush('messages', 'message 1');
await redis.rpush('messages', 'message 2');
const messages = await redis.lrange('messages', 0, -1);
console.log(messages); // 输出: ['message 1', 'message 2']

// Set（集合）
await redis.sadd('tags', 'javascript', 'redis', 'nodejs');
const tags = await redis.smembers('tags');
console.log(tags); // 输出: ['javascript', 'redis', 'nodejs']

// Sorted Set（有序集合）
await redis.zadd('leaderboard', 100, 'Alice', 200, 'Bob', 150, 'Charlie');
const leaderboard = await redis.zrange('leaderboard', 0, -1, 'WITHSCORES');
console.log(leaderboard);
```

## 二、缓存策略

### 1. 缓存穿透

```javascript
// 问题：查询不存在的数据
async function getUser(id) {
  const cacheKey = `user:${id}`;
  
  let user = await redis.get(cacheKey);
  if (user) {
    return JSON.parse(user);
  }
  
  user = await db.query('SELECT * FROM users WHERE id = ?', [id]);
  
  if (!user) {
    // 缓存空值，防止穿透
    await redis.setex(cacheKey, 300, 'null');
    return null;
  }
  
  await redis.setex(cacheKey, 3600, JSON.stringify(user));
  return user;
}

// 使用布隆过滤器
const BloomFilter = require('bloomfilter').BloomFilter;
const bloom = new BloomFilter(
  32 * 256, // number of bits to allocate
  3         // number of hash functions
);

// 添加现有用户 ID
const userIds = await db.query('SELECT id FROM users');
userIds.forEach(id => bloom.add(id.toString()));

async function getUserWithBloomFilter(id) {
  if (!bloom.test(id.toString())) {
    return null; // 肯定不存在
  }
  
  // 继续正常查询
  return await getUser(id);
}
```

### 2. 缓存击穿

```javascript
// 问题：热点 key 过期
const LOCK_KEY = 'user:1:lock';

async function getUserWithLock(id) {
  const cacheKey = `user:${id}`;
  
  let user = await redis.get(cacheKey);
  if (user) {
    return JSON.parse(user);
  }
  
  // 获取分布式锁
  const lockAcquired = await redis.set(LOCK_KEY, '1', 'NX', 'EX', 5);
  if (!lockAcquired) {
    // 锁被占用，等待并重试
    await new Promise(resolve => setTimeout(resolve, 100));
    return await getUserWithLock(id);
  }
  
  try {
    // 再次检查缓存（双重检查）
    user = await redis.get(cacheKey);
    if (user) {
      return JSON.parse(user);
    }
    
    // 查询数据库
    user = await db.query('SELECT * FROM users WHERE id = ?', [id]);
    if (user) {
      await redis.setex(cacheKey, 3600, JSON.stringify(user));
    }
    
    return user;
  } finally {
    // 释放锁
    await redis.del(LOCK_KEY);
  }
}
```

### 3. 缓存雪崩

```javascript
// 问题：大量 key 同时过期
function randomExpire(baseTime, variance) {
  return baseTime + Math.floor(Math.random() * variance);
}

async function setCacheWithRandomExpire(key, value) {
  const expire = randomExpire(3600, 600); // 1 小时 ± 10 分钟
  await redis.setex(key, expire, JSON.stringify(value));
}

// 使用多级缓存
const L1_CACHE_TTL = 60; // 1 分钟
const L2_CACHE_TTL = 3600; // 1 小时

async function getUserMultiLevel(id) {
  const l1Key = `user:${id}:l1`;
  const l2Key = `user:${id}:l2`;
  
  let user = await redis.get(l1Key);
  if (user) {
    return JSON.parse(user);
  }
  
  user = await redis.get(l2Key);
  if (user) {
    // 回填 L1 缓存
    await redis.setex(l1Key, L1_CACHE_TTL, user);
    return JSON.parse(user);
  }
  
  user = await db.query('SELECT * FROM users WHERE id = ?', [id]);
  if (user) {
    await redis.setex(l1Key, L1_CACHE_TTL, JSON.stringify(user));
    await redis.setex(l2Key, L2_CACHE_TTL, JSON.stringify(user));
  }
  
  return user;
}
```

## 三、分布式锁

### 1. 简单分布式锁

```javascript
async function acquireLock(lockKey, expireTime = 10) {
  const result = await redis.set(
    lockKey,
    'locked',
    'NX',
    'EX',
    expireTime
  );
  return result === 'OK';
}

async function releaseLock(lockKey) {
  await redis.del(lockKey);
}

// 使用
async function doSomethingWithLock() {
  const lockKey = 'resource:lock';
  const acquired = await acquireLock(lockKey);
  
  if (!acquired) {
    throw new Error('Could not acquire lock');
  }
  
  try {
    console.log('Lock acquired, doing work...');
    await new Promise(resolve => setTimeout(resolve, 1000));
  } finally {
    await releaseLock(lockKey);
    console.log('Lock released');
  }
}
```

### 2. 带唯一标识的锁（更安全）

```javascript
const uuid = require('uuid');

async function acquireSafeLock(lockKey, expireTime = 10) {
  const identifier = uuid.v4();
  const result = await redis.set(
    lockKey,
    identifier,
    'NX',
    'EX',
    expireTime
  );
  return result === 'OK' ? identifier : null;
}

async function releaseSafeLock(lockKey, identifier) {
  const script = `
    if redis.call("get", KEYS[1]) == ARGV[1] then
      return redis.call("del", KEYS[1])
    else
      return 0
    end
  `;
  return await redis.eval(script, 1, lockKey, identifier);
}

// 使用
async function doSomethingWithSafeLock() {
  const lockKey = 'resource:lock';
  const identifier = await acquireSafeLock(lockKey);
  
  if (!identifier) {
    throw new Error('Could not acquire lock');
  }
  
  try {
    console.log('Lock acquired, doing work...');
    await new Promise(resolve => setTimeout(resolve, 1000));
  } finally {
    await releaseSafeLock(lockKey, identifier);
    console.log('Lock released');
  }
}
```

### 3. Redlock 算法（多实例）

```javascript
const Redis = require('ioredis');

class Redlock {
  constructor(clients) {
    this.clients = clients;
    this.quorum = Math.floor(clients.length / 2) + 1;
  }

  async acquireLock(lockKey, expireTime = 10) {
    const identifier = uuid.v4();
    const start = Date.now();
    let successes = 0;

    for (const client of this.clients) {
      try {
        const result = await client.set(
          lockKey,
          identifier,
          'NX',
          'PX',
          expireTime * 1000
        );
        if (result === 'OK') {
          successes++;
        }
      } catch (e) {
        console.error('Error acquiring lock on instance:', e);
      }
    }

    const elapsed = Date.now() - start;
    const isValid = successes >= this.quorum && elapsed < expireTime * 1000;

    if (!isValid) {
      await this.releaseLock(lockKey, identifier);
      return null;
    }

    return identifier;
  }

  async releaseLock(lockKey, identifier) {
    for (const client of this.clients) {
      try {
        const script = `
          if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
          else
            return 0
          end
        `;
        await client.eval(script, 1, lockKey, identifier);
      } catch (e) {
        console.error('Error releasing lock on instance:', e);
      }
    }
  }
}

// 使用
const redlock = new Redlock([
  new Redis({ host: 'redis1.example.com' }),
  new Redis({ host: 'redis2.example.com' }),
  new Redis({ host: 'redis3.example.com' }),
]);

async function doSomethingWithRedlock() {
  const lockKey = 'resource:lock';
  const identifier = await redlock.acquireLock(lockKey, 10);

  if (!identifier) {
    throw new Error('Could not acquire lock');
  }

  try {
    console.log('Lock acquired, doing work...');
    await new Promise(resolve => setTimeout(resolve, 1000));
  } finally {
    await redlock.releaseLock(lockKey, identifier);
    console.log('Lock released');
  }
}
```

## 四、消息队列

### 1. List 实现简单队列

```javascript
// 生产者
async function produceMessage(queueName, message) {
  await redis.rpush(queueName, JSON.stringify(message));
}

// 消费者
async function consumeMessage(queueName) {
  const result = await redis.blpop(queueName, 0); // 0 表示无限等待
  if (result) {
    const [key, message] = result;
    return JSON.parse(message);
  }
  return null;
}

// 使用
async function exampleQueue() {
  // 生产消息
  await produceMessage('queue:tasks', { id: 1, task: 'do something' });
  await produceMessage('queue:tasks', { id: 2, task: 'do another thing' });
  
  // 消费消息
  const message1 = await consumeMessage('queue:tasks');
  console.log('Consumed:', message1);
  
  const message2 = await consumeMessage('queue:tasks');
  console.log('Consumed:', message2);
}
```

### 2. 发布/订阅

```javascript
// 发布者
async function publishMessage(channel, message) {
  await redis.publish(channel, JSON.stringify(message));
}

// 订阅者
async function subscribeToChannel(channel, callback) {
  const subscriber = new Redis();
  
  await subscriber.subscribe(channel);
  
  subscriber.on('message', (chan, message) => {
    if (chan === channel) {
      callback(JSON.parse(message));
    }
  });
  
  return subscriber;
}

// 使用
async function examplePubSub() {
  // 启动订阅者
  const subscriber = await subscribeToChannel('notifications', (message) => {
    console.log('Received notification:', message);
  });
  
  // 发布消息
  await publishMessage('notifications', { type: 'email', to: 'user@example.com' });
  await publishMessage('notifications', { type: 'sms', to: '+1234567890' });
  
  // 清理
  await new Promise(resolve => setTimeout(resolve, 1000));
  subscriber.quit();
}
```

### 3. Stream（Redis 5.0+）

```javascript
// 生产者
async function produceToStream(streamName, message) {
  const id = await redis.xadd(streamName, '*', ...Object.entries(message).flat());
  return id;
}

// 消费者组
async function createConsumerGroup(streamName, groupName) {
  try {
    await redis.xgroup('CREATE', streamName, groupName, '0', 'MKSTREAM');
  } catch (e) {
    if (!e.message.includes('already exists')) {
      throw e;
    }
  }
}

// 消费者
async function consumeFromStream(streamName, groupName, consumerName, callback) {
  while (true) {
    const results = await redis.xreadgroup(
      'GROUP',
      groupName,
      consumerName,
      'COUNT',
      1,
      'BLOCK',
      5000,
      'STREAMS',
      streamName,
      '>'
    );
    
    if (results) {
      const [key, messages] = results[0];
      for (const [id, message] of messages) {
        const parsedMessage = {};
        for (let i = 0; i < message.length; i += 2) {
          parsedMessage[message[i]] = message[i + 1];
        }
        
        try {
          await callback(parsedMessage);
          await redis.xack(streamName, groupName, id);
        } catch (e) {
          console.error('Error processing message:', e);
        }
      }
    }
  }
}

// 使用
async function exampleStream() {
  const streamName = 'orders';
  const groupName = 'order-processors';
  
  // 创建消费者组
  await createConsumerGroup(streamName, groupName);
  
  // 生产消息
  await produceToStream(streamName, { orderId: '1', product: 'Widget' });
  await produceToStream(streamName, { orderId: '2', product: 'Gadget' });
  
  // 启动消费者
  consumeFromStream(streamName, groupName, 'consumer-1', (message) => {
    console.log('Processing order:', message);
  });
}
```

## 五、限速器

### 1. 固定窗口

```javascript
async function fixedWindowRateLimit(key, limit, windowSeconds) {
  const current = await redis.incr(key);
  
  if (current === 1) {
    await redis.expire(key, windowSeconds);
  }
  
  return current <= limit;
}

// 使用
async function exampleFixedWindow() {
  const key = 'rate-limit:user:123';
  const limit = 10;
  const window = 60; // 1 分钟
  
  for (let i = 1; i <= 15; i++) {
    const allowed = await fixedWindowRateLimit(key, limit, window);
    console.log(`Request ${i}: ${allowed ? 'Allowed' : 'Blocked'}`);
  }
}
```

### 2. 滑动窗口

```javascript
async function slidingWindowRateLimit(key, limit, windowMs) {
  const now = Date.now();
  const windowStart = now - windowMs;
  
  const pipeline = redis.pipeline();
  pipeline.zremrangebyscore(key, 0, windowStart);
  pipeline.zadd(key, now, `${now}-${Math.random()}`);
  pipeline.zcard(key);
  pipeline.expire(key, Math.ceil(windowMs / 1000) + 1);
  
  const results = await pipeline.exec();
  const count = results[2][1];
  
  return count <= limit;
}

// 使用
async function exampleSlidingWindow() {
  const key = 'rate-limit:user:456';
  const limit = 5;
  const window = 60000; // 1 分钟
  
  for (let i = 1; i <= 10; i++) {
    const allowed = await slidingWindowRateLimit(key, limit, window);
    console.log(`Request ${i}: ${allowed ? 'Allowed' : 'Blocked'}`);
    await new Promise(resolve => setTimeout(resolve, 500));
  }
}
```

### 3. 令牌桶

```javascript
async function tokenBucketRateLimit(key, maxTokens, refillRate, capacity) {
  const script = `
    local key = KEYS[1]
    local maxTokens = tonumber(ARGV[1])
    local refillRate = tonumber(ARGV[2])
    local capacity = tonumber(ARGV[3])
    local now = tonumber(ARGV[4])
    
    local data = redis.call("HMGET", key, "tokens", "lastRefill")
    local tokens = tonumber(data[1]) or maxTokens
    local lastRefill = tonumber(data[2]) or now
    
    local elapsed = now - lastRefill
    local newTokens = math.min(tokens + elapsed * refillRate, capacity)
    
    if newTokens >= 1 then
      newTokens = newTokens - 1
      redis.call("HMSET", key, "tokens", newTokens, "lastRefill", now)
      return 1
    else
      redis.call("HMSET", key, "tokens", newTokens, "lastRefill", now)
      return 0
    end
  `;
  
  const result = await redis.eval(
    script,
    1,
    key,
    maxTokens,
    refillRate,
    capacity,
    Date.now()
  );
  
  return result === 1;
}

// 使用
async function exampleTokenBucket() {
  const key = 'rate-limit:user:789';
  const maxTokens = 10;
  const refillRate = 0.1; // 每秒 0.1 个令牌
  const capacity = 10;
  
  for (let i = 1; i <= 20; i++) {
    const allowed = await tokenBucketRateLimit(key, maxTokens, refillRate, capacity);
    console.log(`Request ${i}: ${allowed ? 'Allowed' : 'Blocked'}`);
    await new Promise(resolve => setTimeout(resolve, 500));
  }
}
```

## 六、排行榜与计数

### 1. 游戏排行榜

```javascript
async function updateScore(game, player, score) {
  await redis.zadd(`leaderboard:${game}`, score, player);
}

async function getLeaderboard(game, topN = 10) {
  return await redis.zrevrange(`leaderboard:${game}`, 0, topN - 1, 'WITHSCORES');
}

async function getPlayerRank(game, player) {
  const rank = await redis.zrevrank(`leaderboard:${game}`, player);
  const score = await redis.zscore(`leaderboard:${game}`, player);
  return { rank: rank !== null ? rank + 1 : null, score };
}

// 使用
async function exampleLeaderboard() {
  await updateScore('game1', 'Alice', 1000);
  await updateScore('game1', 'Bob', 1500);
  await updateScore('game1', 'Charlie', 750);
  await updateScore('game1', 'Alice', 1200);
  
  const leaderboard = await getLeaderboard('game1');
  console.log('Leaderboard:', leaderboard);
  
  const aliceRank = await getPlayerRank('game1', 'Alice');
  console.log('Alice rank:', aliceRank);
}
```

### 2. 日/周/月统计

```javascript
async function incrementDailyCount(key, date = new Date()) {
  const dateStr = date.toISOString().slice(0, 10);
  await redis.incr(`${key}:daily:${dateStr}`);
}

async function getDailyCount(key, date = new Date()) {
  const dateStr = date.toISOString().slice(0, 10);
  return parseInt(await redis.get(`${key}:daily:${dateStr}`) || '0');
}

async function incrementWeeklyCount(key, date = new Date()) {
  const weekStart = new Date(date);
  weekStart.setDate(date.getDate() - date.getDay());
  const weekStr = weekStart.toISOString().slice(0, 10);
  await redis.incr(`${key}:weekly:${weekStr}`);
}

async function incrementMonthlyCount(key, date = new Date()) {
  const monthStr = date.toISOString().slice(0, 7);
  await redis.incr(`${key}:monthly:${monthStr}`);
}

// 使用
async function exampleAnalytics() {
  const today = new Date();
  
  await incrementDailyCount('pageviews', today);
  await incrementDailyCount('pageviews', today);
  await incrementWeeklyCount('pageviews', today);
  await incrementMonthlyCount('pageviews', today);
  
  const dailyViews = await getDailyCount('pageviews', today);
  console.log('Daily pageviews:', dailyViews);
}
```

## 七、Redis Cluster

### 1. 集群基本概念

```
Redis Cluster:
- 16384 个哈希槽
- 每个节点负责一部分槽
- 主从复制
- 自动故障转移
```

### 2. 使用 Cluster

```javascript
const Redis = require('ioredis');

const cluster = new Redis.Cluster([
  { host: '127.0.0.1', port: 7000 },
  { host: '127.0.0.1', port: 7001 },
  { host: '127.0.0.1', port: 7002 },
]);

// 正常使用
async function exampleCluster() {
  await cluster.set('key1', 'value1');
  const value = await cluster.get('key1');
  console.log(value);
  
  await cluster.hset('user:1', 'name', 'Alice');
  const user = await cluster.hgetall('user:1');
  console.log(user);
}
```

## 八、最佳实践

1. 合理设计 Key 前缀
2. 选择合适的数据类型
3. 设置合理的过期时间
4. 处理缓存三大问题（穿透、击穿、雪崩）
5. 使用 Pipeline 优化性能
6. 合理使用持久化（RDB/AOF）
7. 监控内存使用
8. 实现合适的分布式锁
9. 使用连接池
10. 做好备份和恢复

## 九、总结

Redis 高级应用：
- 掌握缓存策略和问题处理
- 实现分布式锁
- 构建消息队列
- 实现限速器
- 构建排行榜和统计
- 了解 Redis Cluster
- 遵循最佳实践

开始用 Redis 构建高性能应用吧！
