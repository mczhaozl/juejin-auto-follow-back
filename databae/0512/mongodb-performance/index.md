# MongoDB 性能优化完全指南

## 一、索引优化

```javascript
// 创建复合索引
db.collection.createIndex({ field1: 1, field2: -1 })

// 部分索引
db.collection.createIndex(
  { field: 1 },
  { partialFilterExpression: { status: { $eq: 'active' } } }
)

// 稀疏索引
db.collection.createIndex({ field: 1 }, { sparse: true })

// 查看执行计划
db.collection.find({ field: 'value' }).explain('executionStats')
```

## 二、查询优化

```javascript
// 1. 避免 SELECT *
db.collection.find({}, { field1: 1, field2: 1 })

// 2. 使用 hint 强制索引
db.collection.find({ field: 'value' }).hint({ field: 1 })

// 3. 分页优化
db.collection.find()
  .sort({ _id: -1 })
  .skip(1000)
  .limit(100)

// 4. 避免 n+1 查询
db.collection.aggregate([
  { $lookup: { from: 'other', localField: 'id', foreignField: 'id', as: 'joined' } }
])
```

## 三、写入优化

```javascript
// 批量插入
db.collection.insertMany([
  { /* doc1 */ },
  { /* doc2 */ },
  { /* doc3 */ }
], { ordered: false })

// 写入关注
db.collection.insertOne(doc, {
  writeConcern: { w: 1, j: true, wtimeout: 5000 }
})

// 批量更新
db.collection.updateMany(
  { status: 'old' },
  { $set: { status: 'new' } }
)
```

## 四、内存与存储优化

```javascript
// 1. 查看存储统计
db.collection.stats()

// 2. 压缩集合
db.collection.compact()

// 3. 启用压缩
// 在 MongoDB 配置中启用 snappy/zstd 压缩
```

## 五、监控与诊断

```javascript
// 1. 查看慢查询
db.setProfilingLevel(1, { slowms: 100 })
db.system.profile.find().sort({ ts: -1 }).limit(10)

// 2. 服务器状态
db.serverStatus()

// 3. 数据库状态
db.stats()
```

## 最佳实践
- 合理规划索引，避免过多索引
- 使用复合索引优化多字段查询
- 定期分析慢查询日志
- 注意文档大小不要超过 16MB
- 选择合适的分片策略
