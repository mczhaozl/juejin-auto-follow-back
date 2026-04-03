# Redis 高级应用完全指南

Redis 是最流行的内存数据库。本文将带你从基础到高级，全面掌握 Redis 的高级应用。

## 一、Redis 数据类型高级应用

### 1. String

```bash
# 基础操作
SET key "value"
GET key
SETNX key "value"  # 不存在才设置
SETEX key 60 "value"  # 设置过期时间

# 计数器
INCR counter
INCRBY counter 10
DECR counter
DECRBY counter 5

# 位操作
SETBIT key 0 1
GETBIT key 0
BITCOUNT key
BITOP AND dest key1 key2

# 实战：限流
SETEX user:1:limit 60 0
INCR user:1:limit
# 如果 > 100 则限流
```

### 2. Hash

```bash
# 基础操作
HSET user:1 name "John" age 30
HGET user:1 name
HGETALL user:1
HEXISTS user:1 name
HDEL user:1 age

# 批量操作
HMSET user:1 name "John" age 30 email "john@example.com"
HMGET user:1 name age email

# 计数器
HINCRBY user:1 age 1
HINCRBYFLOAT user:1 score 0.5

# 实战：购物车
HSET cart:user:1 product:1 2
HSET cart:user:1 product:2 1
HGETALL cart:user:1
```

### 3. List

```bash
# 基础操作
LPUSH list "a" "b" "c"
RPUSH list "x" "y" "z"
LPOP list
RPOP list
LLEN list
LRANGE list 0 -1

# 阻塞操作
BLPOP list1 list2 0
BRPOP list1 list2 0

# 实战：消息队列
LPUSH queue:tasks "task1"
RPOP queue:tasks

# 实战：最新列表
LPUSH latest:posts "post1" "post2" "post3"
LTRIM latest:posts 0 99  # 只保留最近 100 条
```

### 4. Set

```bash
# 基础操作
SADD set "a" "b" "c"
SREM set "a"
SISMEMBER set "b"
SMEMBERS set
SCARD set

# 集合操作
SINTER set1 set2  # 交集
SUNION set1 set2  # 并集
SDIFF set1 set2   # 差集

# 实战：标签
SADD post:1:tags "tech" "programming"
SADD post:2:tags "tech" "redis"
SINTER post:1:tags post:2:tags  # 共同标签

# 实战：点赞
SADD post:1:likes user:1 user:2
SISMEMBER post:1:likes user:1  # 是否已点赞
SCARD post:1:likes  # 点赞数
```

### 5. Sorted Set

```bash
# 基础操作
ZADD zset 1 "a" 2 "b" 3 "c"
ZRANGE zset 0 -1 WITHSCORES
ZREVRANGE zset 0 -1 WITHSCORES
ZSCORE zset "a"
ZRANK zset "a"
ZREVRANK zset "a"

# 范围操作
ZRANGEBYSCORE zset 1 3
ZCOUNT zset 1 3
ZREMRANGEBYSCORE zset 1 2

# 实战：排行榜
ZADD leaderboard 100 "user1" 200 "user2" 150 "user3"
ZREVRANGE leaderboard 0 9 WITHSCORES  # 前 10 名
ZINCRBY leaderboard 10 "user1"  # 增加分数
```

### 6. Stream

```bash
# 基础操作
XADD stream * name "John" age 30
XADD stream * name "Jane" age 25
XLEN stream
XRANGE stream - +
XREVRANGE stream + -

# 读取
XREAD COUNT 2 STREAMS stream 0-0

# 消费者组
XGROUP CREATE stream mygroup $ MKSTREAM
XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS stream >
XACK stream mygroup 1680000000000-0

# 实战：事件溯源
XADD events:user * type "created" user_id 1 name "John"
XADD events:user * type "updated" user_id 1 name "John Doe"
```

### 7. Bitmap

```bash
# 基础操作
SETBIT bitmap 0 1
SETBIT bitmap 1 0
GETBIT bitmap 0
BITCOUNT bitmap
BITPOS bitmap 1

# 实战：用户签到
SETBIT user:1:sign 20240401 1
SETBIT user:1:sign 20240402 1
BITCOUNT user:1:sign  # 签到天数

# 实战：在线用户
SETBIT online:users user_id 1
BITCOUNT online:users  # 在线人数
```

### 8. HyperLogLog

```bash
# 基础操作
PFADD hll "a" "b" "c"
PFCOUNT hll
PFMERGE hll3 hll1 hll2

# 实战：UV 统计
PFADD uv:20240401 user:1 user:2 user:3
PFCOUNT uv:20240401  # 独立访客数
```

## 二、Redis 高级功能

### 1. 事务

```bash
# 基础事务
MULTI
SET key1 "value1"
SET key2 "value2"
EXEC

# 乐观锁
WATCH key
GET key
MULTI
SET key "new value"
EXEC

# 实战：秒杀
WATCH stock:product:1
GET stock:product:1
MULTI
DECR stock:product:1
EXEC
```

### 2. 发布订阅

```bash
# 发布者
PUBLISH channel "message"

# 订阅者
SUBSCRIBE channel
PSUBSCRIBE pattern:*

# 实战：实时通知
PUBLISH notifications:user:1 "You have a new message"
```

### 3. Lua 脚本

```lua
-- 原子操作
local current = redis.call('GET', KEYS[1])
if current == ARGV[1] then
    redis.call('SET', KEYS[1], ARGV[2])
    return 1
else
    return 0
end
```

```bash
# 执行脚本
EVAL "redis.call('SET', KEYS[1], ARGV[1])" 1 key value

# 脚本缓存
SCRIPT LOAD "return redis.call('GET', KEYS[1])"
EVALSHA <sha1> 1 key
```

### 4. 管道（Pipeline）

```bash
# 批量操作
SET key1 value1
SET key2 value2
SET key3 value3

# Redis CLI 管道
cat commands.txt | redis-cli --pipe
```

### 5. 键空间通知

```bash
# 启用通知
CONFIG SET notify-keyspace-events KEA

# 订阅键事件
PSUBSCRIBE __keyspace@0__:*
PSUBSCRIBE __keyevent@0__:expired
```

## 三、Redis 高级应用场景

### 1. 缓存

```python
import redis

r = redis.Redis()

def get_user(user_id):
    cache_key = f"user:{user_id}"
    
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    user = db.get_user(user_id)
    r.setex(cache_key, 3600, json.dumps(user))
    
    return user

# 缓存击穿
def get_product(product_id):
    cache_key = f"product:{product_id}"
    
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    lock_key = f"lock:product:{product_id}"
    if r.set(lock_key, "1", nx=True, ex=5):
        try:
            product = db.get_product(product_id)
            r.setex(cache_key, 3600, json.dumps(product))
            return product
        finally:
            r.delete(lock_key)
    else:
        time.sleep(0.1)
        return get_product(product_id)
```

### 2. 分布式锁

```python
import redis
import uuid
import time

class DistributedLock:
    def __init__(self, redis_client, lock_key, expire=30):
        self.redis = redis_client
        self.lock_key = lock_key
        self.expire = expire
        self.lock_value = str(uuid.uuid4())
    
    def acquire(self, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            if self.redis.set(
                self.lock_key,
                self.lock_value,
                nx=True,
                ex=self.expire
            ):
                return True
            time.sleep(0.1)
        return False
    
    def release(self):
        script = """
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("DEL", KEYS[1])
            else
                return 0
            end
        """
        self.redis.eval(script, 1, self.lock_key, self.lock_value)

# 使用
r = redis.Redis()
lock = DistributedLock(r, "resource:1")

if lock.acquire():
    try:
        print("Do something")
    finally:
        lock.release()
```

### 3. 限流

```python
import redis

class RateLimiter:
    def __init__(self, redis_client, limit=100, window=60):
        self.redis = redis_client
        self.limit = limit
        self.window = window
    
    def is_allowed(self, user_id):
        key = f"rate_limit:{user_id}"
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, self.window)
        return current <= self.limit

# 使用
r = redis.Redis()
limiter = RateLimiter(r, limit=100, window=60)

if limiter.is_allowed("user:1"):
    print("Allowed")
else:
    print("Blocked")
```

### 4. 排行榜

```python
import redis

class Leaderboard:
    def __init__(self, redis_client, key="leaderboard"):
        self.redis = redis_client
        self.key = key
    
    def add_score(self, user_id, score):
        self.redis.zadd(self.key, {user_id: score})
    
    def get_rank(self, user_id):
        rank = self.redis.zrevrank(self.key, user_id)
        return rank + 1 if rank is not None else None
    
    def get_top(self, n=10):
        return self.redis.zrevrange(self.key, 0, n-1, withscores=True)

# 使用
r = redis.Redis()
leaderboard = Leaderboard(r)

leaderboard.add_score("user:1", 100)
leaderboard.add_score("user:2", 200)
print(leaderboard.get_top(10))
```

### 5. 消息队列

```python
import redis
import time

class MessageQueue:
    def __init__(self, redis_client, queue_name="queue"):
        self.redis = redis_client
        self.queue_name = queue_name
    
    def produce(self, message):
        self.redis.lpush(self.queue_name, message)
    
    def consume(self, timeout=0):
        return self.redis.brpop(self.queue_name, timeout=timeout)

# 使用
r = redis.Redis()
queue = MessageQueue(r)

# 生产者
queue.produce("task1")
queue.produce("task2")

# 消费者
while True:
    _, message = queue.consume()
    print(f"Processing: {message}")
```

### 6. 会话存储

```python
import redis
import uuid

class SessionStore:
    def __init__(self, redis_client, expire=3600):
        self.redis = redis_client
        self.expire = expire
    
    def create_session(self, user_id):
        session_id = str(uuid.uuid4())
        key = f"session:{session_id}"
        self.redis.setex(key, self.expire, user_id)
        return session_id
    
    def get_user_id(self, session_id):
        key = f"session:{session_id}"
        return self.redis.get(key)
    
    def destroy_session(self, session_id):
        key = f"session:{session_id}"
        self.redis.delete(key)

# 使用
r = redis.Redis()
store = SessionStore(r)

session_id = store.create_session("user:1")
user_id = store.get_user_id(session_id)
```

## 四、Redis 集群

### 1. 主从复制

```bash
# 从节点配置
replicaof master_host master_port

# 查看复制信息
INFO replication
```

### 2. 哨兵（Sentinel）

```bash
# sentinel.conf
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 10000
sentinel parallel-syncs mymaster 1

# 启动哨兵
redis-sentinel sentinel.conf
```

### 3. 集群（Cluster）

```bash
# 创建集群
redis-cli --cluster create 127.0.0.1:7000 127.0.0.1:7001 \
  127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1

# 集群操作
CLUSTER INFO
CLUSTER NODES
CLUSTER KEYSLOT key
```

## 五、Redis 持久化

### 1. RDB

```bash
# 配置
save 900 1
save 300 10
save 60 10000
rdbcompression yes
dbfilename dump.rdb
dir /var/lib/redis

# 手动保存
SAVE
BGSAVE
```

### 2. AOF

```bash
# 配置
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# AOF 重写
BGREWRITEAOF
```

## 六、最佳实践

1. 合理选择数据类型
2. 使用批量操作减少网络开销
3. 合理设置过期时间
4. 使用 Lua 脚本保证原子性
5. 使用管道提高性能
6. 合理使用持久化
7. 使用连接池
8. 监控 Redis 性能
9. 合理设计 Key
10. 做好备份和恢复

## 七、总结

Redis 高级应用核心要点：
- 数据类型（String、Hash、List、Set、Sorted Set、Stream、Bitmap、HyperLogLog）
- 高级功能（事务、发布订阅、Lua 脚本、管道）
- 应用场景（缓存、分布式锁、限流、排行榜、消息队列、会话）
- 集群（主从复制、哨兵、Cluster）
- 持久化（RDB、AOF）
- 最佳实践

开始用 Redis 构建高性能应用吧！
