# MongoDB 基础入门：NoSQL 数据库实战指南

> 全面介绍 MongoDB 核心概念、CRUD 操作、聚合管道，以及 Node.js 中的实际应用案例。

## 一、MongoDB 简介

### 1.1 什么是 MongoDB

MongoDB 是最流行的 NoSQL 文档数据库：

- 文档存储（类似 JSON）
- 灵活的 Schema
- 高性能、高可用
- 水平扩展

### 1.2 基本概念

| SQL 术语 | MongoDB 术语 |
|---------|-------------|
| Database | Database |
| Table | Collection |
| Row | Document |
| Column | Field |
| Index | Index |

## 二、基础操作

### 2.1 连接数据库

```javascript
const { MongoClient } = require('mongodb');

const url = 'mongodb://localhost:27017';
const client = new MongoClient(url);

async function main() {
  await client.connect();
  const db = client.db('test');
  console.log('连接成功');
  
  await client.close();
}

main();
```

### 2.2 Collection 操作

```javascript
// 创建 Collection
await db.createCollection('users');

// 获取 Collection
const users = db.collection('users');
```

## 三、CRUD 操作

### 3.1 插入文档

```javascript
// 单条插入
await users.insertOne({
  name: '张三',
  age: 25,
  email: 'zhangsan@example.com'
});

// 多条插入
await users.insertMany([
  { name: '李四', age: 30 },
  { name: '王五', age: 28 }
]);
```

### 3.2 查询文档

```javascript
// 查询所有
const allUsers = await users.find().toArray();

// 条件查询
const result = await users.find({ age: { $gt: 20 } }).toArray();

// 查询单条
const user = await users.findOne({ name: '张三' });

// 投影（只返回指定字段）
const names = await users.find({}, { projection: { name: 1 } }).toArray();
```

### 3.3 更新文档

```javascript
// 更新单条
await users.updateOne(
  { name: '张三' },
  { $set: { age: 26 } }
);

// 更新多条
await users.updateMany(
  { age: { $lt: 18 } },
  { $set: { status: 'minor' } }
);

// 替换文档
await users.replaceOne(
  { name: '张三' },
  { name: '张三', age: 27, city: '北京' }
);
```

### 3.4 删除文档

```javascript
// 删除单条
await users.deleteOne({ name: '张三' });

// 删除多条
await users.deleteMany({ status: 'inactive' });
```

## 四、查询运算符

### 4.1 比较运算符

```javascript
// $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin
await users.find({ age: { $gte: 18, $lte: 30 } });
await users.find({ name: { $in: ['张三', '李四'] } });
```

### 4.2 逻辑运算符

```javascript
// $and, $or, $not, $nor
await users.find({
  $and: [
    { age: { $gte: 18 } },
    { status: 'active' }
  ]
});
```

### 4.3 数组运算符

```javascript
// $push, $pop, $pull, $addToSet
await users.updateOne(
  { name: '张三' },
  { $push: { tags: 'developer' } }
);
```

## 五、聚合管道

### 5.1 基础聚合

```javascript
const pipeline = [
  { $match: { age: { $gte: 20 } } },
  { $group: { _id: '$city', count: { $sum: 1 } } },
  { $sort: { count: -1 } }
];

const result = await users.aggregate(pipeline).toArray();
```

### 5.2 常用阶段

| 阶段 | 说明 |
|------|------|
| $match | 过滤文档 |
| $group | 分组统计 |
| $project | 投影 |
| $sort | 排序 |
| $limit | 限制数量 |
| $skip | 跳过数量 |

## 六、索引

### 6.1 创建索引

```javascript
// 单字段索引
await users.createIndex({ name: 1 });

// 复合索引
await users.createIndex({ age: 1, city: -1 });

// 唯一索引
await users.createIndex({ email: 1 }, { unique: true });

// 文本索引
await users.createIndex({ name: 'text', bio: 'text' });
```

### 7.2 查询计划

```javascript
const explain = await users.find({ name: '张三' }).explain();
console.log(explain.queryPlanner);
```

## 七、实战案例

### 7.1 分页查询

```javascript
async function getUsers(page = 1, limit = 10) {
  const skip = (page - 1) * limit;
  const [users, total] = await Promise.all([
    usersCollection.find().skip(skip).limit(limit).toArray(),
    usersCollection.countDocuments()
  ]);
  
  return {
    data: users,
    pagination: { page, limit, total, totalPages: Math.ceil(total / limit) }
  };
}
```

### 7.2 关联查询

```javascript
const pipeline = [
  {
    $lookup: {
      from: 'orders',
      localField: '_id',
      foreignField: 'userId',
      as: 'orders'
    }
  }
];

const result = await users.aggregate(pipeline).toArray();
```

## 八、总结

MongoDB 核心要点：

1. **文档数据库**：灵活的 JSON 文档
2. **CRUD 操作**：增删改查
3. **查询运算符**：强大的查询能力
4. **聚合管道**：数据处理和分析
5. **索引**：提升查询性能
6. **分片**：水平扩展

掌握这些，MongoDB 使用不再难！

---

**推荐阅读**：
- [MongoDB 官方文档](https://docs.mongodb.com/)
- [MongoDB University](https://university.mongodb.com/)

**如果对你有帮助，欢迎点赞收藏！**
