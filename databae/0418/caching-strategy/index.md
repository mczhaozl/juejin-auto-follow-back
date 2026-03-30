# 缓存策略完全指南：多级缓存与性能优化

> 深入讲解缓存策略，包括浏览器缓存、CDN 缓存、Redis 缓存、缓存穿透/击穿/雪崩，以及实际项目中的缓存设计和高可用方案。

## 一、缓存概述

### 1.1 多级缓存

```
┌─────────────────────────────────────────────────────────────┐
│                      多级缓存                               │
│                                                              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐  │
│  │ 浏览器  │──▶│  CDN   │──▶│  Redis  │──▶│ 数据库  │  │
│  │ 缓存    │   │  缓存   │   │  缓存    │   │         │  │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘  │
│                                                              │
│  延迟: ms       ms            μs          ms             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 缓存分类

| 层级 | 介质 | 容量 | 延迟 |
|------|------|------|------|
| L1 | CPU Cache | KB | ns |
| L2 | 内存 | GB | ns |
| L3 | Redis | GB | μs |
| L4 | SSD | TB | ms |

## 二、浏览器缓存

### 2.1 缓存头

```http
# 强缓存
Cache-Control: max-age=3600          # 3600秒内有效
Expires: Mon, 01 Jan 2025 00:00:00 GMT

# 协商缓存
ETag: "abc123"
Last-Modified: Mon, 01 Jan 2024 00:00:00 GMT
```

### 2.2 缓存策略

```javascript
// HTTP 响应头
app.get('/static/*', (req, res) => {
  // 静态资源长期缓存
  res.set({
    'Cache-Control': 'public, max-age=31536000',
    'ETag': generateHash(fileContent)
  })
  res.send(fileContent)
})

app.get('/api/*', (req, res) => {
  // API 不缓存
  res.set({
    'Cache-Control': 'no-cache, no-store, must-revalidate'
  })
  res.json(data)
})
```

## 三、Redis 缓存

### 3.1 基本操作

```javascript
const redis = require('redis')
const client = redis.createClient()

// 字符串
await client.set('user:1', JSON.stringify(user))
await client.get('user:1')

// Hash
await client.hset('user:1', 'name', '张三')
await client.hget('user:1', 'name')

// 设置过期
await client.setex('token:abc', 3600, token)
```

### 3.2 缓存模式

```javascript
// Cache-Aside（旁路缓存）
async function getUser(id) {
  // 1. 先查缓存
  const cached = await redis.get(`user:${id}`)
  if (cached) {
    return JSON.parse(cached)
  }
  
  // 2. 缓存未命中，查数据库
  const user = await db.users.findById(id)
  
  // 3. 写入缓存
  if (user) {
    await redis.setex(`user:${id}`, 3600, JSON.stringify(user))
  }
  
  return user
}

// Write-Through（写穿透）
async function updateUser(id, data) {
  await db.users.update(id, data)
  await redis.set(`user:${id}`, JSON.stringify(data))
}
```

## 四、缓存问题

### 4.1 缓存穿透

```
问题: 查询不存在的key，每次都打到数据库

方案: 
1. 布隆过滤器
2. 缓存空值
```

```javascript
// 布隆过滤器
const BloomFilter = require('bloomfilter')
const bloom = new BloomFilter.BloomFilter(1000000, 5)

// 添加
bloom.add('user:1000')

// 检查
if (bloom.test('user:1000')) {
  // 可能存在
}

// 缓存空值
const cached = await redis.get('user:9999')
if (cached === null) {
  // 缓存空值，防止穿透
  await redis.setex('user:9999', 60, 'NULL')
}
```

### 4.2 缓存击穿

```
问题: 热点key过期，瞬间大量请求打到数据库

方案:
1. 互斥锁
2. 永不过期
```

```javascript
// 互斥锁
async function getUser(id) {
  const key = `user:${id}`
  
  // 获取锁
  const lock = await redis.setnx(`lock:${key}`, '1')
  if (lock) {
    try {
      const user = await db.users.findById(id)
      await redis.setex(key, 3600, JSON.stringify(user))
      return user
    } finally {
      await redis.del(`lock:${key}`)
    }
  }
  
  // 等待其他请求写入缓存
  await sleep(100)
  return await redis.get(key)
}
```

### 4.3 缓存雪崩

```
问题: 大量key同时过期，请求打到数据库

方案:
1. 随机过期时间
2. 多级缓存
3. 限流
```

```javascript
// 随机过期时间
const baseExpire = 3600
const randomExpire = baseExpire + Math.random() * 300
await redis.setex(key, randomExpire, value)
```

## 五、缓存策略

### 5.1 更新策略

```javascript
// 1. Cache-Aside (常用)
async function updateUser(id, data) {
  await db.users.update(id, data)
  await redis.del(`user:${id}`)
}

// 2. Write-Through
async function updateUser(id, data) {
  await redis.set(`user:${id}`, JSON.stringify(data))
  await db.users.update(id, data)
}

// 3. Write-Behind
async function updateUser(id, data) {
  await redis.set(`user:${id}`, JSON.stringify(data))
  await queue.push('user:update', { id, data })
}
```

### 5.2 分级缓存

```javascript
// L1 (本地内存) + L2 (Redis)
class Cache {
  constructor() {
    this.l1 = new Map()
    this.l2 = redis
  }
  
  async get(key) {
    // L1 查找
    let value = this.l1.get(key)
    if (value) {
      return value
    }
    
    // L2 查找
    value = await this.l2.get(key)
    if (value) {
      this.l1.set(key, value)  // 回填 L1
    }
    
    return value
  }
  
  async set(key, value, l1Ttl = 60, l2Ttl = 3600) {
    this.l1.set(key, value)
    await this.l2.setex(key, l2Ttl, value)
  }
}
```

## 六、高可用

### 6.1 Redis 集群

```javascript
// Redis Cluster
const cluster = require('redis')

const client = cluster.createCluster({
  rootNodes: [
    { host: '127.0.0.1', port: 7000 },
    { host: '127.0.0.1', port: 7001 },
    { host: '127.0.0.1', port: 7002 }
  ]
})

await client.connect()
```

### 6.2 主从复制

```
┌─────────────────────────────────────────────────────────────┐
│                    Redis 主从                                │
│                                                              │
│     ┌─────────┐                                            │
│     │ Master  │                                            │
│     │ (写)   │                                            │
│     └────┬────┘                                            │
│          │ 同步                                             │
│    ┌─────┴─────┐                                          │
│    ▼           ▼                                           │
│ ┌──────┐   ┌──────┐                                        │
│ │ Slave│   │ Slave│                                        │
│ │ (读) │   │ (读) │                                        │
│ └──────┘   └──────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

## 七、总结

缓存策略核心要点：

1. **多级缓存**：浏览器/CDN/Redis
2. **Cache-Aside**：常用模式
3. **穿透/击穿/雪崩**：三大问题
4. **互斥锁**：防止击穿
5. **随机过期**：防止雪崩
6. **高可用**：Redis 集群

掌握这些，性能优化 so easy！

---

**推荐阅读**：
- [Redis 缓存设计](https://redis.io/documentation)

**如果对你有帮助，欢迎点赞收藏！**
