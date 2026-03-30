# NoSQL 数据库完全指南：MongoDB、Redis 与 Cassandra

> 深入讲解 NoSQL 数据库，包括文档数据库 MongoDB、键值数据库 Redis、列式数据库 Cassandra，以及实际项目中的选型和实践。

## 一、NoSQL 概述

### 1.1 什么是 NoSQL

非关系型数据库：

```
┌─────────────────────────────────────────────────────────────┐
│                    数据库类型                                │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  关系型     │  │   NoSQL     │  │  NewSQL    │       │
│  │  MySQL      │  │  MongoDB    │  │  TiDB      │       │
│  │  PostgreSQL │  │  Redis      │  │  CockroachDB│       │
│  └─────────────┘  │  Cassandra  │  └─────────────┘       │
│                   │  Elasticsearch│                        │
│                   └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 NoSQL 分类

| 类型 | 代表 | 特点 |
|------|------|------|
| 文档 | MongoDB | JSON 存储 |
| 键值 | Redis | 内存存储 |
| 列式 | Cassandra | 分布式 |
| 图 | Neo4j | 图关系 |

## 二、MongoDB

### 2.1 安装

```bash
# Docker 安装
docker run -d --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo

# 连接
mongosh -u admin -p password
```

### 2.2 CRUD 操作

```javascript
// 插入
db.users.insertOne({ name: "张三", age: 25 })
db.users.insertMany([
  { name: "李四", age: 30 },
  { name: "王五", age: 35 }
])

// 查询
db.users.find({ age: { $gt: 20 } })
db.users.findOne({ name: "张三" })
db.users.find().sort({ age: -1 }).limit(10)

// 更新
db.users.updateOne(
  { name: "张三" },
  { $set: { age: 26 } }
)

// 删除
db.users.deleteOne({ name: "张三" })
```

### 2.3 聚合

```javascript
// 聚合管道
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: { _id: "$product", total: { $sum: "$amount" } } },
  { $sort: { total: -1 } }
])
```

## 三、Redis

### 3.1 数据结构

```bash
# String
SET user:1 "张三"
GET user:1

# Hash
HSET user:1 name "张三" age 25
HGET user:1 name

# List
LPUSH list1 "a"
RPUSH list1 "b"

# Set
SADD tags "javascript" "nodejs"
SMEMBERS tags

# Sorted Set
ZADD leaderboard 100 "张三"
ZRANGE leaderboard 0 -1 WITHSCORES
```

### 3.2 高级功能

```bash
# 过期时间
SET token "abc123" EX 3600

# 事务
MULTI
SET key1 "value1"
SET key2 "value2"
EXEC

# 管道
redis-cli --pipe < data.txt
```

## 四、Cassandra

### 4.1 CQL

```sql
-- 创建表
CREATE KEYSPACE myapp WITH REPLICATION = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

CREATE TABLE myapp.users (
  id UUID PRIMARY KEY,
  name TEXT,
  email TEXT,
  created_at TIMESTAMP
);

-- 插入
INSERT INTO myapp.users (id, name, email, created_at)
VALUES (uuid(), '张三', 'zhangsan@example.com', now());

-- 查询
SELECT * FROM myapp.users WHERE id = ?
```

## 五、选型指南

### 5.1 场景对比

| 场景 | 推荐 |
|------|------|
| 缓存 | Redis |
| 会话 | Redis |
| 文档存储 | MongoDB |
| 实时分析 | Cassandra |
| 全文搜索 | Elasticsearch |
| 图关系 | Neo4j |

### 5.2 选型因素

- 数据模型
- 一致性要求
- 性能需求
- 扩展性
- 运维成本

## 六、实战案例

### 6.1 MongoDB + Node.js

```javascript
const { MongoClient } = require('mongodb')

async function main() {
  const client = new MongoClient('mongodb://localhost:27017')
  
  await client.connect()
  const db = client.db('myapp')
  
  // 查询
  const users = await db.collection('users')
    .find({ age: { $gte: 18 } })
    .sort({ createdAt: -1 })
    .toArray()
  
  console.log(users)
  
  await client.close()
}

main()
```

### 6.2 Redis 缓存

```javascript
const redis = require('redis')

async function getUser(id) {
  const client = redis.createClient()
  
  // 先查缓存
  const cached = await client.get(`user:${id}`)
  if (cached) {
    return JSON.parse(cached)
  }
  
  // 查数据库
  const user = await db.users.findById(id)
  
  // 写入缓存
  await client.set(`user:${id}`, JSON.stringify(user), 'EX', 3600)
  
  return user
}
```

## 七、总结

NoSQL 核心要点：

1. **MongoDB**：文档数据库
2. **Redis**：内存数据库
3. **Cassandra**：列式数据库
4. **选型**：根据场景
5. **聚合**：MongoDB 管道
6. **缓存**：Redis

掌握这些，NoSQL so easy！

---

**推荐阅读**：
- [MongoDB 官方文档](https://docs.mongodb.com/)
- [Redis 官方文档](https://redis.io/documentation)

**如果对你有帮助，欢迎点赞收藏！**
