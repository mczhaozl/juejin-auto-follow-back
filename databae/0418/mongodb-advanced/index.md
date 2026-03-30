# MongoDB 高级完全指南：索引、聚合与集群

> 深入讲解 MongoDB 高级特性，包括索引优化、聚合管道、分片集群、事务处理，以及实际项目中的性能调优和最佳实践。

## 一、索引优化

### 1.1 索引类型

```javascript
// 单字段索引
db.users.createIndex({ age: 1 })

// 复合索引（注意顺序）
db.users.createIndex({ age: 1, name: -1 })

// 多键索引（数组）
db.products.createIndex({ tags: 1 })

// 文本索引
db.articles.createIndex({ content: "text" })

// 唯一索引
db.users.createIndex({ email: 1 }, { unique: true })

// 稀疏索引
db.sessions.createIndex({ token: 1 }, { sparse: true })
```

### 1.2 索引策略

```javascript
// 覆盖查询
db.users.createIndex({ name: 1, age: 1 })

// 查询使用覆盖索引
db.users.find({ name: "张三" }, { name: 1, age: 1, _id: 0 })

// 索引hint
db.users.find({ name: "张三", age: 25 }).hint({ name: 1, age: 1 })
```

### 1.3 分析查询

```javascript
// 查看查询计划
db.users.find({ age: { $gt: 25 } }).explain("executionStats")

// 结果分析
{
  "executionStats": {
    "totalDocsExamined": 1000,  // 扫描文档数
    "indexName": "age_1",       // 使用索引
    "indexBounds": "[(25, Infinity)]"
  }
}
```

## 二、聚合管道

### 2.1 管道阶段

```javascript
db.orders.aggregate([
  { $match: { status: "completed" } },      // 过滤
  { $sort: { createdAt: -1 } },            // 排序
  { $limit: 100 },                          // 限制
  { $skip: 50 },                            // 跳过
  { $group: {                              // 分组
    _id: "$userId",
    total: { $sum: "$amount" },
    count: { $sum: 1 }
  }},
  { $project: {                            // 投影
    _id: 0,
    userId: "$_id",
    total: 1
  }}
])
```

### 2.2 聚合操作符

```javascript
// $sum / $avg / $min / $max
{ $group: {
  _id: "$category",
  total: { $sum: "$price" },
  avg: { $avg: "$price" }
}}

// $push / $addToSet
{ $group: {
  _id: "$userId",
  orders: { $push: "$orderId" },
  uniqueProducts: { $addToSet: "$productId" }
}}

// $lookup（关联查询）
{ $lookup: {
  from: "users",
  localField: "userId",
  foreignField: "_id",
  as: "user"
}}

// $unwind
{ $unwind: "$tags" }

// $facet（多管道）
{ $facet: {
  byCategory: [{ $group: { _id: "$category", count: { $sum: 1 } } }],
  byStatus: [{ $group: { _id: "$status", count: { $sum: 1 } } }]
}}
```

## 三、分片集群

### 3.1 集群架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MongoDB 分片集群                          │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Router (mongos)                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│          ┌───────────────┼───────────────┐                  │
│          ▼               ▼               ▼                  │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐          │
│  │ Shard 1   │    │ Shard 2   │    │ Shard 3   │          │
│  │ (chunk)   │    │ (chunk)   │    │ (chunk)   │          │
│  └───────────┘    └───────────┘    └───────────┘          │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Config Server (副本集)                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 分片配置

```javascript
// 启用分片
sh.enableSharding("myapp")

// 分片集合
sh.shardCollection("myapp.orders", { orderId: "hashed" })

// 手动移动块
sh.moveChunk("myapp.orders", { orderId: NumberLong(1000) }, "shard2")
```

## 四、事务

### 4.1 多文档事务

```javascript
const session = db.getMongo().startSession()

session.startTransaction({
  readConcern: { level: "snapshot" },
  writeConcern: { w: "majority" }
})

try {
  const db1 = session.getDatabase("orders")
  const db2 = session.getDatabase("inventory")
  
  // 扣库存
  db2.products.updateOne(
    { productId: "123", stock: { $gte: 1 } },
    { $inc: { stock: -1 } }
  )
  
  // 创建订单
  db1.orders.insertOne({
    orderId: "ORDER001",
    productId: "123",
    status: "completed"
  })
  
  session.commitTransaction()
} catch (error) {
  session.abortTransaction()
} finally {
  session.endSession()
}
```

## 五、性能优化

### 5.1 内存问题

```javascript
// 查看内存使用
db.adminCommand({ top: 1 })

// WireTiger 缓存
db.adminCommand({ getParameter: 1, wiredTigerConcurrentReadTransactions: 1 })
```

### 5.2 查询优化

```javascript
// 避免全表扫描
// ❌ 慢
db.users.find({ name: /.*张三.*/ })

// ✅ 快（使用索引）
db.users.find({ name: "张三" })

// 投影优化
// ❌ 返回所有字段
db.users.find({})

// ✅ 只返回必要字段
db.users.find({}, { name: 1, email: 1 })
```

## 六、备份恢复

### 6.1 备份

```bash
# mongodump
mongodump --host localhost --port 27017 --db myapp --out /backup

# 副本集备份
mongodump --host rs0/localhost:27017,localhost:27018 --db myapp
```

### 6.2 恢复

```bash
mongorestore --host localhost --port 27017 --db myapp /backup/myapp
```

## 七、总结

MongoDB 高级核心要点：

1. **索引**：复合/文本/唯一
2. **聚合**：管道/操作符
3. **分片**：水平扩展
4. **事务**：多文档
5. **优化**：查询/内存
6. **备份**：mongodump

掌握这些，MongoDB 进阶 so easy！

---

**推荐阅读**：
- [MongoDB 高级](https://www.mongodb.com/docs/manual/administration/)

**如果对你有帮助，欢迎点赞收藏！**
