# Redis 入门完全指南：从安装到实战

Redis 是一个开源的内存数据结构存储系统，可用作数据库、缓存和消息中间件。本文将带你从零开始学习 Redis。

## 一、Redis 简介

### 1. 什么是 Redis

Redis（Remote Dictionary Server）是一个基于内存的高性能键值存储系统。

### 2. Redis 的特点

- **内存存储**：极快的读写速度
- **数据结构丰富**：String、List、Set、Hash、ZSet 等
- **持久化**：RDB 和 AOF 两种方式
- **主从复制**：支持数据复制
- **高可用**：Redis Sentinel 和 Redis Cluster
- **发布订阅**：支持消息队列

### 3. 适用场景

- **缓存**：减轻数据库压力
- **会话存储**：Session 管理
- **排行榜**：Sorted Set 实现
- **计数器**：原子操作
- **消息队列**：List 或 Stream
- **分布式锁**：SETNX 实现

## 二、安装 Redis

### 1. Linux 安装

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y redis-server

# CentOS/RHEL
sudo yum install -y redis

# 启动 Redis
sudo systemctl start redis
sudo systemctl enable redis

# 验证安装
redis-cli ping
```

### 2. macOS 安装

```bash
# 使用 Homebrew
brew install redis

# 启动 Redis
brew services start redis

# 验证安装
redis-cli ping
```

### 3. Windows 安装

下载 Redis for Windows：https://github.com/microsoftarchive/redis/releases

或使用 Docker：
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

### 4. 使用 Docker

```bash
# 拉取镜像
docker pull redis:7-alpine

# 运行容器
docker run -d \
  --name my-redis \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes

# 连接 Redis
docker exec -it my-redis redis-cli

# 或使用本地客户端
redis-cli -h 127.0.0.1 -p 6379
```

## 三、Redis 数据类型

### 1. String（字符串）

```bash
# 设置键值
SET key value
SET mykey "Hello Redis"

# 获取值
GET key
GET mykey

# 设置键值并设置过期时间
SETEX key 60 value
SETEX session:123 3600 "user data"

# 只在键不存在时设置
SETNX key value
SETNX lock:1 "locked"

# 批量设置
MSET key1 value1 key2 value2 key3 value3

# 批量获取
MGET key1 key2 key3

# 自增
INCR counter
INCRBY counter 10

# 自减
DECR counter
DECRBY counter 5

# 获取字符串长度
STRLEN key

# 追加内容
APPEND key " more content"
```

### 2. List（列表）

```bash
# 从左侧插入
LPUSH mylist "a"
LPUSH mylist "b"
LPUSH mylist "c"

# 从右侧插入
RPUSH mylist "x"
RPUSH mylist "y"
RPUSH mylist "z"

# 获取列表范围
LRANGE mylist 0 -1
LRANGE mylist 0 2

# 获取列表长度
LLEN mylist

# 从左侧弹出
LPOP mylist

# 从右侧弹出
RPOP mylist

# 移除并获取最后一个元素，添加到另一个列表
RPOPLPUSH list1 list2

# 根据索引获取元素
LINDEX mylist 0

# 根据索引设置元素
LSET mylist 0 "new value"

# 移除元素
LREM mylist 2 "value"  # 移除前2个值为value的元素

# 修剪列表
LTRIM mylist 0 9  # 只保留前10个元素
```

### 3. Hash（哈希）

```bash
# 设置单个字段
HSET user:1 name "张三"
HSET user:1 age 28
HSET user:1 email "zhangsan@example.com"

# 批量设置字段
HMSET user:2 name "李四" age 25 email "lisi@example.com"

# 获取单个字段
HGET user:1 name

# 获取多个字段
HMGET user:1 name age email

# 获取所有字段和值
HGETALL user:1

# 获取所有字段
HKEYS user:1

# 获取所有值
HVALS user:1

# 检查字段是否存在
HEXISTS user:1 name

# 删除字段
HDEL user:1 email

# 获取字段数量
HLEN user:1

# 字段自增
HINCRBY user:1 age 1
HINCRBYFLOAT user:1 score 0.5
```

### 4. Set（集合）

```bash
# 添加元素
SADD myset "a"
SADD myset "b"
SADD myset "c"
SADD myset "a"  # 重复元素不会添加

# 获取所有元素
SMEMBERS myset

# 检查元素是否存在
SISMEMBER myset "a"

# 获取集合大小
SCARD myset

# 移除元素
SREM myset "c"

# 随机弹出元素
SPOP myset

# 随机获取元素（不移除）
SRANDMEMBER myset
SRANDMEMBER myset 3  # 获取3个

# 集合运算
SADD set1 "a" "b" "c"
SADD set2 "c" "d" "e"

# 交集
SINTER set1 set2

# 并集
SUNION set1 set2

# 差集
SDIFF set1 set2

# 交集存储到新集合
SINTERSTORE result set1 set2
```

### 5. Sorted Set（有序集合）

```bash
# 添加元素
ZADD myzset 1 "a"
ZADD myzset 2 "b"
ZADD myzset 3 "c"
ZADD myzset 2.5 "d"

# 获取元素（按分数排序）
ZRANGE myzset 0 -1
ZRANGE myzset 0 -1 WITHSCORES

# 反向获取
ZREVRANGE myzset 0 -1
ZREVRANGE myzset 0 -1 WITHSCORES

# 获取元素分数
ZSCORE myzset "a"

# 获取元素排名（从小到大）
ZRANK myzset "c"

# 获取元素排名（从大到小）
ZREVRANK myzset "a"

# 获取集合大小
ZCARD myzset

# 获取分数范围内的元素数量
ZCOUNT myzset 1 3

# 移除元素
ZREM myzset "d"

# 增加元素分数
ZINCRBY myzset 2 "a"

# 按分数范围获取元素
ZRANGEBYSCORE myzset 1 3
ZRANGEBYSCORE myzset -inf +inf

# 按排名范围移除
ZREMRANGEBYRANK myzset 0 1

# 按分数范围移除
ZREMRANGEBYSCORE myzset 1 2
```

### 6. Bitmap（位图）

```bash
# 设置位
SETBIT key 0 1
SETBIT key 1 0
SETBIT key 2 1

# 获取位
GETBIT key 0

# 统计1的数量
BITCOUNT key

# 位运算
BITOP AND result key1 key2
BITOP OR result key1 key2
BITOP XOR result key1 key2
BITOP NOT result key1
```

### 7. HyperLogLog

```bash
# 添加元素
PFADD hll "a"
PFADD hll "b"
PFADD hll "c"
PFADD hll "a"  # 重复元素不影响

# 估算基数
PFCOUNT hll

# 合并多个 HyperLogLog
PFMERGE result hll1 hll2 hll3
```

### 8. Stream（流）

```bash
# 添加消息
XADD mystream * name "张三" age 28
XADD mystream * name "李四" age 25

# 读取消息
XREAD COUNT 2 STREAMS mystream 0

# 按范围读取
XRANGE mystream - +
XRANGE mystream - + COUNT 2

# 创建消费者组
XGROUP CREATE mystream mygroup $

# 消费者读取
XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS mystream >

# 确认消息
XACK mystream mygroup message-id
```

## 四、键操作

```bash
# 查看所有键
KEYS *
KEYS user:*

# 检查键是否存在
EXISTS key

# 删除键
DEL key
DEL key1 key2 key3

# 设置过期时间（秒）
EXPIRE key 60

# 设置过期时间（毫秒）
PEXPIRE key 60000

# 设置过期时间点（时间戳）
EXPIREAT key 1735689600

# 查看剩余时间（秒）
TTL key

# 查看剩余时间（毫秒）
PTTL key

# 移除过期时间
PERSIST key

# 查看键类型
TYPE key

# 重命名键
RENAME oldkey newkey
RENAMENX oldkey newkey  # 仅当新键不存在时

# 随机获取一个键
RANDOMKEY

# 移动键到另一个数据库
MOVE key 1

# 序列化键
DUMP key

# 反序列化键
RESTORE key 0 serialized-value
```

## 五、数据库操作

```bash
# 选择数据库（0-15）
SELECT 0
SELECT 1

# 查看数据库大小
DBSIZE

# 清空当前数据库
FLUSHDB

# 清空所有数据库
FLUSHALL
```

## 六、发布订阅

```bash
# 订阅频道
SUBSCRIBE news

# 订阅多个频道
SUBSCRIBE news sports tech

# 按模式订阅
PSUBSCRIBE news.*

# 发布消息
PUBLISH news "Hello World!"

# 取消订阅
UNSUBSCRIBE news

# 取消模式订阅
PUNSUBSCRIBE news.*
```

## 七、事务

```bash
# 开始事务
MULTI

# 队列命令
SET key1 "value1"
SET key2 "value2"
INCR counter

# 执行事务
EXEC

# 放弃事务
DISCARD

# 监视键（乐观锁）
WATCH key
MULTI
SET key "new value"
EXEC

# 取消监视
UNWATCH
```

## 八、Lua 脚本

```bash
# 执行 Lua 脚本
EVAL "return 'Hello ' .. ARGV[1]" 0 "Redis"

# 带键的脚本
EVAL "return redis.call('GET', KEYS[1])" 1 mykey

# 脚本示例：原子操作
EVAL "
  local current = redis.call('GET', KEYS[1])
  if not current then
    current = 0
  end
  current = current + ARGV[1]
  redis.call('SET', KEYS[1], current)
  return current
" 1 counter 10

# 加载脚本
SCRIPT LOAD "return 'Hello'"

# 执行已加载的脚本
EVALSHA <sha1> 0
```

## 九、持久化

### 1. RDB（Redis Database）

```conf
# redis.conf
save 900 1      # 900秒内至少1个键改变
save 300 10     # 300秒内至少10个键改变
save 60 10000   # 60秒内至少10000个键改变

dbfilename dump.rdb
dir /var/lib/redis
```

```bash
# 手动保存 RDB
SAVE

# 后台保存 RDB
BGSAVE
```

### 2. AOF（Append Only File）

```conf
# redis.conf
appendonly yes
appendfilename "appendonly.aof"

# 同步策略
appendfsync always   # 每次写都同步
appendfsync everysec # 每秒同步一次（推荐）
appendfsync no       # 不同步

# AOF 重写
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

```bash
# 手动重写 AOF
BGREWRITEAOF
```

## 十、主从复制

```conf
# 从节点配置（redis.conf）
replicaof master-host 6379

# 认证（如果主节点有密码）
masterauth password

# 只读
replica-read-only yes
```

```bash
# 运行时设置主节点
REPLICAOF master-host 6379

# 取消复制
REPLICAOF NO ONE

# 查看复制信息
INFO replication
```

## 十一、安全配置

```conf
# redis.conf
# 设置密码
requirepass yourpassword

# 绑定地址
bind 127.0.0.1

# 禁用危险命令
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

## 十二、客户端连接

### 1. Node.js（ioredis）

```javascript
const Redis = require('ioredis');

const redis = new Redis({
  host: 'localhost',
  port: 6379,
  password: 'yourpassword'
});

async function example() {
  // String
  await redis.set('key', 'value');
  const value = await redis.get('key');
  console.log(value);

  // Hash
  await redis.hset('user:1', 'name', '张三', 'age', 28);
  const user = await redis.hgetall('user:1');
  console.log(user);

  // List
  await redis.lpush('mylist', 'a', 'b', 'c');
  const list = await redis.lrange('mylist', 0, -1);
  console.log(list);

  await redis.quit();
}

example();
```

### 2. Python（redis-py）

```python
import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    password='yourpassword',
    decode_responses=True
)

# String
r.set('key', 'value')
print(r.get('key'))

# Hash
r.hset('user:1', mapping={'name': '张三', 'age': 28})
print(r.hgetall('user:1'))

# List
r.lpush('mylist', 'a', 'b', 'c')
print(r.lrange('mylist', 0, -1))
```

## 十三、实战案例

### 1. 缓存实现

```javascript
async function getProduct(id) {
  const cacheKey = `product:${id}`;
  
  let product = await redis.get(cacheKey);
  if (product) {
    return JSON.parse(product);
  }
  
  product = await db.getProduct(id);
  await redis.setex(cacheKey, 3600, JSON.stringify(product));
  
  return product;
}
```

### 2. 分布式锁

```javascript
async function acquireLock(lockKey, timeout = 10000) {
  const result = await redis.set(lockKey, 'locked', 'PX', timeout, 'NX');
  return result === 'OK';
}

async function releaseLock(lockKey) {
  await redis.del(lockKey);
}

async function doSomething() {
  const lockKey = 'lock:resource';
  
  if (await acquireLock(lockKey)) {
    try {
      // 执行操作
    } finally {
      await releaseLock(lockKey);
    }
  }
}
```

### 3. 排行榜

```javascript
async function addScore(userId, score) {
  await redis.zadd('leaderboard', score, userId);
}

async function getTopN(n) {
  return await redis.zrevrange('leaderboard', 0, n - 1, 'WITHSCORES');
}

async function getUserRank(userId) {
  return await redis.zrevrank('leaderboard', userId);
}
```

## 十四、总结

Redis 是一个功能强大的内存数据存储系统。通过本文的学习，你应该已经掌握了：

1. Redis 的安装和基本配置
2. 所有数据类型的使用
3. 常用命令和操作
4. 持久化和复制
5. 客户端库的使用
6. 实战应用案例

继续深入学习 Redis，充分发挥它的威力！

## 参考资料

- [Redis 官方文档](https://redis.io/docs/)
- [Redis 命令参考](https://redis.io/commands/)
- [ioredis](https://github.com/luin/ioredis)
- [redis-py](https://github.com/redis/redis-py)
