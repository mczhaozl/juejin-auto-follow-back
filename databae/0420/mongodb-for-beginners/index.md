# MongoDB 入门完全指南：从安装到实战

MongoDB 是一个开源的 NoSQL 文档数据库，使用灵活的文档模型存储数据。本文将带你从零开始学习 MongoDB。

## 一、MongoDB 简介

### 1. 什么是 MongoDB

MongoDB 是一个基于分布式文件存储的 NoSQL 数据库，使用 BSON（Binary JSON）存储数据。

### 2. MongoDB 的特点

- **文档模型**：灵活的 JSON 类似文档
- **动态模式**：无需预定义表结构
- **高可用**：副本集（Replica Set
- **可扩展**：分片（Sharding）
- **索引支持**：多种索引类型
- **聚合管道**：强大的数据处理能力

### 3. 核心概念

| SQL | MongoDB | 说明 |
|-----|---------|------|
| 数据库（Database） | 数据库（Database） | 数据库 |
| 表（Table） | 集合（Collection） | 数据集合 |
| 行（Row） | 文档（Document） | 单条数据 |
| 列（Column） | 字段（Field） | 数据字段 |
| 主键（Primary Key） | _id | 主键 |

## 二、安装 MongoDB

### 1. Linux 安装

```bash
# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# 启动 MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# 验证安装
mongosh
```

### 2. macOS 安装

```bash
# 使用 Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0

# 启动 MongoDB
brew services start mongodb-community

# 验证安装
mongosh
```

### 3. Windows 安装

下载 MongoDB Community Server：https://www.mongodb.com/try/download/community

### 4. 使用 Docker

```bash
# 拉取镜像
docker pull mongo:7

# 运行容器
docker run -d \
  --name my-mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -v mongo-data:/data/db \
  mongo:7

# 连接 MongoDB
docker exec -it my-mongodb mongosh -u admin -p secret

# 或使用本地客户端
mongosh mongodb://admin:secret@localhost:27017
```

## 三、MongoDB Shell 基础操作

### 1. 数据库操作

```javascript
// 显示所有数据库
show dbs

// 切换/创建数据库
use mydb

// 查看当前数据库
db

// 删除数据库
db.dropDatabase()
```

### 2. 集合操作

```javascript
// 显示所有集合
show collections

// 创建集合
db.createCollection('users')

// 删除集合
db.users.drop()
```

### 3. 文档操作 - CRUD

#### 插入文档

```javascript
// 插入单个文档
db.users.insertOne({
  name: '张三',
  age: 28,
  email: 'zhangsan@example.com',
  createdAt: new Date()
})

// 插入多个文档
db.users.insertMany([
  { name: '李四',
    age: 25,
    email: 'lisi@example.com',
    createdAt: new Date()
  },
  {
    name: '王五',
    age: 32,
    email: 'wangwu@example.com',
    createdAt: new Date()
  }
])
```

#### 查询文档

```javascript
// 查询所有文档
db.users.find()
db.users.find().pretty()

// 查询单个文档
db.users.findOne({ name: '张三' })

// 条件查询
db.users.find({ age: { $gt: 25 } })
db.users.find({ age: { $gte: 25, $lte: 30 } })
db.users.find({ name: { $in: ['张三', '李四'] } })

// 逻辑运算
db.users.find({ $and: [{ age: { $gt: 20 }, { age: { $lt: 30 } }] })
db.users.find({ $or: [{ name: '张三' }, { age: 25 }])

// 正则匹配
db.users.find({ name: /^张/ })
db.users.find({ name: { $regex: '^张', $options: 'i' })

// 字段存在
db.users.find({ email: { $exists: true } })

// 投影（只返回指定字段）
db.users.find({}, { name: 1, age: 1, _id: 0 })

// 排序
db.users.find().sort({ age: 1 })   // 升序
db.users.find().sort({ age: -1 })  // 降序

// 分页
db.users.find().skip(10).limit(10)

// 计数
db.users.countDocuments()
db.users.countDocuments({ age: { $gt: 25 })

// 去重
db.users.distinct('age')
```

#### 更新文档

```javascript
// 更新单个文档
db.users.updateOne(
  { name: '张三' },
  { $set: { age: 29, email: 'zhangsan_new@example.com' } }
)

// 更新多个文档
db.users.updateMany(
  { age: { $lt: 30 } },
  { $set: { category: 'young' } }
)

// 替换文档
db.users.replaceOne(
  { name: '张三' },
  {
    name: '张三',
    age: 29,
    email: 'zhangsan_new@example.com'
  }
)

// 更新操作符
db.users.updateOne(
  { name: '张三' },
  {
    $inc: { age: 1 },           // 自增
    $push: { hobbies: '读书' },     // 数组添加
    $addToSet: { hobbies: '运动' }, // 数组添加（去重）
    $pull: { hobbies: '看电视' },  // 数组移除
    $rename: { oldField: 'newField' } // 重命名字段
  }
)

// 数组更新
db.users.updateOne(
  { name: '张三' },
  { $push: { scores: { $each: [80, 90, 85], $sort: -1 } } }
)
```

#### 删除文档

```javascript
// 删除单个文档
db.users.deleteOne({ name: '张三' })

// 删除多个文档
db.users.deleteMany({ age: { $gt: 30 } })

// 删除所有文档
db.users.deleteMany({})
```

## 四、索引

```javascript
// 创建单字段索引
db.users.createIndex({ name: 1 })

// 创建复合索引
db.users.createIndex({ name: 1, age: -1 })

// 创建唯一索引
db.users.createIndex({ email: 1 }, { unique: true })

// 创建稀疏索引
db.users.createIndex({ optionalField: 1 }, { sparse: true })

// 创建 TTL 索引（自动过期）
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })

// 查看索引
db.users.getIndexes()

// 删除索引
db.users.dropIndex('name_1')
db.users.dropIndexes()

// 查看查询计划
db.users.find({ name: '张三' }).explain('executionStats')
```

## 五、聚合管道

```javascript
// $match：过滤
db.users.aggregate([
  { $match: { age: { $gt: 25 } } }
])

// $group：分组
db.users.aggregate([
  {
    $group: {
      _id: null,
      avgAge: { $avg: '$age' },
      maxAge: { $max: '$age' },
      minAge: { $min: '$age' },
      count: { $sum: 1 }
    }
  }
])

// 按字段分组
db.users.aggregate([
  {
    $group: {
      _id: '$category',
      count: { $sum: 1 },
      users: { $push: '$name' }
    }
  }
])

// $sort：排序
db.users.aggregate([
  { $sort: { age: -1 } }
])

// $skip 和 $limit：分页
db.users.aggregate([
  { $skip: 10 },
  { $limit: 10 }
])

// $project：投影
db.users.aggregate([
  {
    $project: {
      name: 1,
      age: 1,
      isAdult: { $gte: ['$age', 18] },
      _id: 0
    }
  }
])

// $lookup：关联查询
db.orders.aggregate([
  {
    $lookup: {
      from: 'users',
      localField: 'userId',
      foreignField: '_id',
      as: 'user'
    }
  }
])

// $unwind：展开数组
db.users.aggregate([
  { $unwind: '$hobbies' }
])

// 完整示例
db.sales.aggregate([
  { $match: { date: { $gte: new Date('2024-01-01') } },
  {
    $group: {
      _id: { month: { $month: '$date' }, product: '$product' },
      totalAmount: { $sum: '$amount' },
      count: { $sum: 1 }
    }
  },
  { $sort: { totalAmount: -1 } },
  { $limit: 10 }
])
```

## 六、副本集（Replica Set）

```javascript
// 初始化副本集
rs.initiate({
  _id: 'myReplicaSet',
  members: [
    { _id: 0, host: 'mongodb1:27017' },
    { _id: 1, host: 'mongodb2:27017' },
    { _id: 2, host: 'mongodb3:27017', arbiterOnly: true }
  ]
})

// 查看副本集状态
rs.status()

// 添加节点
rs.add('mongodb4:27017')

// 移除节点
rs.remove('mongodb4:27017')
```

## 七、安全配置

```javascript
// 创建管理员用户
use admin
db.createUser({
  user: 'admin',
  pwd: 'password',
  roles: [{ role: 'root', db: 'admin' }]
})

// 创建普通用户
use mydb
db.createUser({
  user: 'myuser',
  pwd: 'password',
  roles: [{ role: 'readWrite', db: 'mydb' }]
})

// 启用认证
// mongod.conf
security:
  authorization: enabled
```

## 八、Node.js 客户端

```javascript
const { MongoClient } = require('mongodb');

const uri = 'mongodb://localhost:27017';
const client = new MongoClient(uri);

async function main() {
  try {
    await client.connect();
    const db = client.db('mydb');
    const collection = db.collection('users');

    // 插入
    const result = await collection.insertOne({
      name: '张三',
      age: 28,
      email: 'zhangsan@example.com'
    });
    console.log('Inserted:', result.insertedId);

    // 查询
    const users = await collection.find({ age: { $gt: 25 } }).toArray();
    console.log('Users:', users);

    // 更新
    const updateResult = await collection.updateOne(
      { name: '张三' },
      { $set: { age: 29 } }
    );
    console.log('Updated:', updateResult.modifiedCount);

    // 删除
    const deleteResult = await collection.deleteOne({ name: '张三' });
    console.log('Deleted:', deleteResult.deletedCount);

    // 聚合
    const pipeline = [
      { $match: { age: { $gt: 20 } } },
      { $group: { _id: null, avgAge: { $avg: '$age' } }
    ];
    const aggResult = await collection.aggregate(pipeline).toArray();
    console.log('Aggregation:', aggResult);

  } finally {
    await client.close();
  }
}

main().catch(console.error);
```

## 九、Python 客户端

```python
from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['mydb']
collection = db['users']

# 插入
result = collection.insert_one({
    'name': '张三',
    'age': 28,
    'email': 'zhangsan@example.com',
    'createdAt': datetime.now()
})
print('Inserted:', result.inserted_id)

# 查询
users = list(collection.find({'age': {'$gt': 25}}))
print('Users:', users)

# 更新
update_result = collection.update_one(
    {'name': '张三'},
    {'$set': {'age': 29}}
)
print('Updated:', update_result.modified_count)

# 删除
delete_result = collection.delete_one({'name': '张三'})
print('Deleted:', delete_result.deleted_count)

# 聚合
pipeline = [
    {'$match': {'age': {'$gt': 20}}},
    {'$group': {'_id': None, 'avgAge': {'$avg': '$age'}}}
]
agg_result = list(collection.aggregate(pipeline))
print('Aggregation:', agg_result)
```

## 十、实战案例

### 1. 用户管理系统

```javascript
// 用户 Schema（MongoDB 灵活文档
{
  "_id": ObjectId("..."),
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "hashed_password",
  "profile": {
    "name": "张三",
    "age": 28,
    "avatar": "https://..."
  },
  "hobbies": ["读书", "运动"],
  "settings": {
    "notifications": true,
    "theme": "dark"
  },
  "createdAt": ISODate("2024-01-01T00:00:00Z"),
  "updatedAt": ISODate("2024-01-01T00:00:00Z")
}
```

```javascript
// 查询活跃用户
db.users.find({
  'settings.notifications': true,
  createdAt: { $gte: new Date('2024-01-01') }
})

// 统计各年龄段用户数
db.users.aggregate([
  {
    $bucket: {
      groupBy: '$profile.age',
      boundaries: [0, 18, 25, 35, 50, 100],
      default: 'other',
      output: { count: { $sum: 1 } }
    }
  }
])
```

### 2. 电商订单系统

```javascript
// 订单文档
{
  "_id": ObjectId("..."),
  "orderNo": "ORD-2024-00001",
  "userId": ObjectId("..."),
  "items": [
    {
      "productId": ObjectId("..."),
      "name": "商品1",
      "price": 99.99,
      "quantity": 2
    }
  ],
  "totalAmount": 199.98,
  "status": "paid",
  "address": {
    "name": "张三",
    "phone": "13800138000",
    "city": "北京"
  },
  "createdAt": ISODate("2024-01-01T00:00:00Z")
}
```

```javascript
// 查询用户订单
db.orders.aggregate([
  { $match: { userId: ObjectId("...") } },
  { $sort: { createdAt: -1 } },
  {
    $lookup: {
      from: 'users',
      localField: 'userId',
      foreignField: '_id',
      as: 'user'
    }
  },
  { $unwind: '$user' }
])

// 统计销售额
db.orders.aggregate([
  { $match: { status: 'paid', createdAt: { $gte: new Date('2024-01-01') } } },
  {
    $group: {
      _id: { $dateToString: { format: '%Y-%m', date: '$createdAt' } },
      totalSales: { $sum: '$totalAmount' },
      orderCount: { $sum: 1 }
    }
  },
  { $sort: { '_id': 1 } }
])
```

## 十一、最佳实践

### 1. 文档设计

- 嵌入优先，关联次之
- 合理使用数组
- 避免过大的文档

### 2. 索引策略

- 为常用查询创建索引
- 避免过多索引
- 定期分析查询性能

### 3. 性能优化

- 使用投影减少数据传输
- 合理使用分页
- 批量操作代替单次操作

## 十二、总结

MongoDB 是一个灵活强大的 NoSQL 数据库。通过本文的学习，你应该已经掌握了：

1. MongoDB 的安装和基本配置
2. CRUD 操作
3. 索引和聚合管道
4. 客户端库的使用
5. 实战应用案例

继续深入学习 MongoDB，构建灵活的数据存储方案！

## 参考资料

- [MongoDB 官方文档](https://www.mongodb.com/docs/)
- [MongoDB Node.js Driver](https://mongodb.github.io/node-mongodb-native/)
- [PyMongo 文档](https://pymongo.readthedocs.io/)
- [MongoDB University](https://university.mongodb.com/)
