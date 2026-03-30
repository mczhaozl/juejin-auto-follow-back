# MongoDB 完全指南：文档数据库实战

> 深入讲解 MongoDB，包括文档模型、CRUD 操作、聚合管道、索引优化，以及 Node.js 集成和实际项目中的数据建模。

## 一、MongoDB 基础

### 1.1 什么是 MongoDB

NoSQL 文档数据库：

```json
{
  "_id": ObjectId("..."),
  "name": "张三",
  "age": 25,
  "email": "zhangsan@example.com",
  "address": {
    "city": "北京",
    "country": "中国"
  },
  "tags": ["前端", "JavaScript"]
}
```

### 1.2 基本概念

| SQL | MongoDB |
|-----|---------|
| Database | Database |
| Table | Collection |
| Row | Document |
| Column | Field |
| Index | Index |

## 二、CRUD 操作

### 2.1 插入

```javascript
// 单个文档
db.users.insertOne({
  name: "张三",
  age: 25
});

// 多个文档
db.users.insertMany([
  { name: "李四", age: 30 },
  { name: "王五", age: 28 }
]);
```

### 2.2 查询

```javascript
// 查询所有
db.users.find();

// 条件查询
db.users.find({ age: { $gt: 20 } });

// 投影（只返回指定字段）
db.users.find({}, { name: 1, _id: 0 });

// 排序
db.users.find().sort({ age: -1 });

// 分页
db.users.find().skip(10).limit(10);
```

### 2.3 更新

```javascript
// 更新单个
db.users.updateOne(
  { name: "张三" },
  { $set: { age: 26 } }
);

// 更新多个
db.users.updateMany(
  { age: { $lt: 25 } },
  { $inc: { age: 1 } }
);

// 替换
db.users.replaceOne(
  { name: "张三" },
  { name: "张三", age: 27, city: "上海" }
);
```

### 2.4 删除

```javascript
// 删除单个
db.users.deleteOne({ name: "张三" });

// 删除多个
db.users.deleteMany({ age: { $lt: 18 } });
```

## 三、聚合管道

### 3.1 基础聚合

```javascript
// 统计数量
db.orders.aggregate([
  { $count: "total" }
]);

// 分组统计
db.orders.aggregate([
  { $group: {
    _id: "$product",
    totalAmount: { $sum: "$amount" }
  }}
]);
```

### 3.2 常用阶段

```javascript
db.orders.aggregate([
  // 筛选
  { $match: { status: "completed" } },
  
  // 投影
  { $project: {
    product: 1,
    amount: 1,
    _id: 0
  }},
  
  // 分组
  { $group: {
    _id: "$product",
    total: { $sum: "$amount" }
  }},
  
  // 排序
  { $sort: { total: -1 } },
  
  // 限制
  { $limit: 5 }
]);
```

### 3.3 运算符

```javascript
// 条件
{ $cond: { if: "$completed", then: "$amount", else: 0 } }

// 日期
{ $year: "$createdAt" }

// 字符串
{ $toUpper: "$product" }
```

## 四、索引

### 4.1 创建索引

```javascript
// 单字段索引
db.users.createIndex({ name: 1 });

// 复合索引
db.users.createIndex({ age: 1, name: -1 });

// 唯一索引
db.users.createIndex({ email: 1 }, { unique: true });

// 文本索引
db.products.createIndex({ description: "text" });
```

### 4.2 索引类型

| 类型 | 说明 |
|------|------|
| 单字段 | 单个字段索引 |
| 复合 | 多个字段索引 |
| 多键 | 数组字段索引 |
| 文本 | 全文搜索 |
| 地理空间 | 位置索引 |

### 4.3 性能分析

```javascript
// 查看查询计划
db.users.find({ name: "张三" }).explain();

// 查看索引
db.users.getIndexes();
```

## 五、Node.js 集成

### 5.1 连接 MongoDB

```javascript
const { MongoClient } = require('mongodb');

async function main() {
  const client = new MongoClient('mongodb://localhost:27017');
  await client.connect();
  
  const db = client.db('myapp');
  const users = db.collection('users');
  
  // CRUD 操作
  await users.insertOne({ name: "张三", age: 25 });
  
  const result = await users.find({ age: { $gt: 20 } }).toArray();
  
  await client.close();
}
```

### 5.2 Mongoose

```javascript
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  age: { type: Number, min: 0 },
  email: { type: String, unique: true }
});

const User = mongoose.model('User', userSchema);

// 使用
const user = await User.create({ name: "张三", age: 25 });
const users = await User.find({ age: { $gt: 20 } });
```

## 六、数据建模

### 6.1 关系建模

```javascript
// 嵌入（1:1 或 1:多）
{
  name: "张三",
  address: {
    city: "北京",
    street: "xxx"
  }
}

// 引用（多:多）
{
  _id: ObjectId("..."),
  title: "文章",
  author_ids: [ObjectId("1"), ObjectId("2")]
}
```

## 七、总结

MongoDB 核心要点：

1. **文档模型**：灵活的 JSON 结构
2. **CRUD**：增删改查操作
3. **聚合管道**：复杂数据处理
4. **索引**：查询优化
5. **Mongoose**：Node.js ODM

掌握这些，MongoDB 使用 so easy！

---

**推荐阅读**：
- [MongoDB 官方文档](https://docs.mongodb.com/)

**如果对你有帮助，欢迎点赞收藏！**
