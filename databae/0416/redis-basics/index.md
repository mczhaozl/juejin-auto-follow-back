# Redis 完全指南：内存数据库实战

> 深入讲解 Redis，包括数据结构（String、Hash、List、Set、ZSet）、持久化、事务、集群，以及 Node.js 集成和缓存实战。

## 一、Redis 基础

### 1.1 什么是 Redis

内存数据结构存储：

```
┌─────────────────────────────────┐
│            Redis               │
├─────────────────────────────────┤
│  String  │  Hash  │  List     │
│  Set     │  ZSet  │  Bitmap   │
│  HyperLogLog │  Streams    │
└─────────────────────────────────┘
```

### 1.2 安装与连接

```bash
# Docker 启动
docker run -d -p 6379:6379 redis

# 命令行连接
redis-cli
```

## 二、数据结构

### 2.1 String

```bash
# 设置
SET name "张三"
SETEX token 3600 "abc123"  # 过期时间

# 获取
GET name
MGET name age  # 批量获取

# 数字
INCR counter
INCRBY counter 10
DECR counter
```

JavaScript:

```javascript
await client.set('name', '张三');
await client.get('name');
await client.incr('counter');
```

### 2.2 Hash

```bash
# 设置
HSET user:1 name "张三"
HSET user:1 age 25
HMSET user:1 name "张三" age 25  # 批量

# 获取
HGET user:1 name
HMGET user:1 name age
HGETALL user:1

# 操作
HINCRBY user:1 age 1
HEXISTS user:1 name
HDEL user:1 age
```

### 2.3 List

```bash
# 插入
LPUSH tasks "task1"    # 头部插入
RPUSH tasks "task2"    # 尾部插入

# 获取
LRANGE tasks 0 -1      # 获取所有
LINDEX tasks 0        # 按索引获取

# 操作
LPOP tasks            # 头部弹出
RPOP tasks            # 尾部弹出
LLEN tasks            # 长度
```

### 2.4 Set

```bash
# 添加
SADD tags "react" "vue" "react"

# 获取
SMEMBERS tags         # 所有成员
SISMEMBER tags "vue"   # 是否存在

# 操作
SCARD tags            # 数量
SREM tags "vue"       # 删除
SUNION tags1 tags2    # 并集
SINTER tags1 tags2    # 交集
SDIFF tags1 tags2    # 差集
```

### 2.5 ZSet（有序集合）

```bash
# 添加
ZADD leaderboard 100 "user1"
ZADD leaderboard 90 "user2"
ZADD leaderboard 80 "user3"

# 获取
ZRANGE leaderboard 0 -1         # 按分数升序
ZREVRANGE leaderboard 0 -1     # 按分数降序
ZSCORE leaderboard "user1"     # 获取分数

# 操作
ZRANK leaderboard "user1"      # 排名（升序）
ZREVRANK leaderboard "user1"   # 排名（降序）
ZINCRBY leaderboard 10 "user1" # 增加分数
```

## 三、持久化

### 3.1 RDB

定时快照：

```bash
# 配置
save 900 1      # 1个 key 变化，900秒后保存
save 300 10     # 10个 key 变化，300秒后保存
save 60 10000   # 10000个 key 变化，60秒后保存
```

### 3.2 AOF

命令日志：

```bash
# 配置
appendonly yes
appendfsync everysec  # 每秒同步
```

### 3.3 混合模式

```
┌────────────────────────────────────┐
│            Redis                   │
│  ┌──────────┐    ┌──────────────┐ │
│  │   RDB    │ +  │     AOF      │ │
│  └──────────┘    └──────────────┘ │
└────────────────────────────────────┘
```

## 四、事务

### 4.1 基本事务

```bash
MULTI
SET key1 "value1"
SET key2 "value2"
EXEC
```

### 4.2 乐观锁

```bash
WATCH key
MULTI
SET key "newvalue"
EXEC  # 如果 key 被其他客户端修改，事务失败
```

## 五、发布/订阅

### 5.1 发布

```bash
PUBLISH channel "message"
```

### 5.2 订阅

```bash
SUBSCRIBE channel
PSUBSCRIBE pattern*  # 模式匹配
```

## 六、集群

### 6.1 主从复制

```
┌─────────┐     复制      ┌─────────┐
│ Master  │ ───────────► │ Slave   │
│ (写)    │              │ (读)    │
└─────────┘              └─────────┘
```

配置：

```bash
# slaveof
slaveof 127.0.0.1 6379
```

### 6.2 Redis Cluster

```
┌─────────────────────────────────────┐
│           Redis Cluster             │
│  ┌─────┐ ┌─────┐ ┌─────┐          │
│  │slot │ │slot │ │slot │  ...     │
│  │0-5460│ │5461-10922│ │10923-16383│
│  └─────┘ └─────┘ └─────┘          │
└─────────────────────────────────────┘
```

## 七、缓存实战

### 7.1 缓存模式

```javascript
async function getUser(id) {
  // 1. 先查缓存
  const cached = await client.get(`user:${id}`);
  if (cached) return JSON.parse(cached);
  
  // 2. 缓存没有，查数据库
  const user = await db.users.findById(id);
  
  // 3. 存入缓存
  await client.setex(`user:${id}`, 3600, JSON.stringify(user));
  
  return user;
}
```

### 7.2 分布式锁

```javascript
async function acquireLock(key, ttl = 10) {
  const result = await client.set(key, 'lock', 'EX', ttl, 'NX');
  return result === 'OK';
}

async function releaseLock(key) {
  await client.del(key);
}
```

## 八、总结

Redis 核心要点：

1. **String**：字符串
2. **Hash**：对象
3. **List**：列表
4. **Set**：集合
5. **ZSet**：有序集合
6. **持久化**：RDB + AOF
7. **集群**：主从 + Cluster

掌握这些，Redis 使用 so easy！

---

**推荐阅读**：
- [Redis 官方文档](https://redis.io/documentation)

**如果对你有帮助，欢迎点赞收藏！**
