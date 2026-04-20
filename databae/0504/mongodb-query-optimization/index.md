# MongoDB 查询优化完全指南

## 一、查询优化概述

### 1.1 为什么需要查询优化

MongoDB 作为文档型数据库，高效的查询是应用性能的关键。

### 1.2 优化策略

- 索引优化
- 查询重写
- 数据模型设计
- 执行计划分析

## 二、索引优化

### 2.1 单字段索引

```javascript
db.collection.createIndex({ field: 1 })  // 升序
db.collection.createIndex({ field: -1 }) // 降序
```

### 2.2 复合索引

```javascript
db.collection.createIndex({ field1: 1, field2: -1 })
```

复合索引遵循前缀原则：`{a:1, b:1, c:1}` 支持查询 `{a:1}`、`{a:1, b:1}`、`{a:1, b:1, c:1}`

### 2.3 多键索引

```javascript
db.collection.createIndex({ tags: 1 })  // 数组字段自动创建多键索引
```

### 2.4 文本索引

```javascript
db.collection.createIndex({ content: "text" })
db.collection.find({ $text: { $search: "mongodb" } })
```

### 2.5 地理位置索引

```javascript
db.collection.createIndex({ location: "2dsphere" })
db.collection.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [100, 0] },
      $maxDistance: 1000
    }
  }
})
```

## 三、查询性能分析

### 3.1 explain() 方法

```javascript
db.collection.find({ field: "value" }).explain("executionStats")
```

### 3.2 执行计划关键指标

```javascript
// 检查是否使用了索引
{
  "executionStats": {
    "executionSuccess": true,
    "nReturned": 100,
    "executionTimeMillis": 5,
    "totalKeysExamined": 100,
    "totalDocsExamined": 100,  // 理想情况：nReturned = totalDocsExamined
    "executionStages": {
      "stage": "FETCH",
      "inputStage": {
        "stage": "IXSCAN",  // 索引扫描
        "indexName": "field_1"
      }
    }
  }
}
```

### 3.3 常见问题

- **COLLSCAN**：集合扫描，未使用索引
- **IXSCAN**：索引扫描
- **SORT**：在内存中排序

## 四、查询重写技巧

### 4.1 避免范围查询后的索引失效

```javascript
// 不好的：范围查询后索引字段无法使用
db.collection.find({ a: 1, b: { $gt: 10 }, c: 1 })
db.collection.createIndex({ a: 1, b: 1, c: 1 })  // c 无法使用

// 好的：重新排序索引
db.collection.createIndex({ a: 1, c: 1, b: 1 })
```

### 4.2 选择性过滤条件

```javascript
// 将高选择性条件放前面
db.collection.find({ status: "active", date: { $gt: ISODate("2024-01-01") } })
```

### 4.3 避免 $where

```javascript
// 不好的：性能差
db.collection.find({ $where: "this.a + this.b > 10" })

// 好的：使用聚合或重新设计
db.collection.aggregate([
  { $addFields: { total: { $add: ["$a", "$b"] } } },
  { $match: { total: { $gt: 10 } } }
])
```

## 五、聚合优化

### 5.1 索引使用

```javascript
// match 阶段优先使用索引
db.collection.aggregate([
  { $match: { field: "value" } },  // 使用索引
  { $group: { _id: "$category", count: { $sum: 1 } } }
])
```

### 5.2 避免大内存排序

```javascript
// 不好的：大量数据排序
db.collection.aggregate([
  { $sort: { date: -1 } }
])

// 好的：使用索引排序
db.collection.createIndex({ date: -1 })
```

### 5.3 投影优化

```javascript
// 只查询需要的字段
db.collection.find({ field: "value" }, { field1: 1, field2: 1, _id: 0 })
```

## 六、覆盖查询

```javascript
// 索引包含所有需要的字段，不需要访问文档
db.collection.createIndex({ field1: 1, field2: 1 })
db.collection.find({ field1: "value" }, { field2: 1, _id: 0 })
```

## 七、实战优化案例

### 7.1 查询慢日志分析

```javascript
// 开启慢查询
db.setProfilingLevel(1, { slowms: 100 })

// 查看慢查询
db.system.profile.find().sort({ ts: -1 }).limit(10)
```

### 7.2 常见场景优化

#### 用户查询场景

```javascript
// 原来的慢查询
db.users.find({ status: "active", age: { $gt: 18 } }).sort({ created: -1 })

// 优化：创建复合索引
db.users.createIndex({ status: 1, age: 1, created: -1 })
```

#### 数据分析场景

```javascript
db.orders.aggregate([
  { $match: { date: { $gte: ISODate("2024-01-01") } } },
  { $group: { _id: "$productId", total: { $sum: "$amount" } } },
  { $sort: { total: -1 } },
  { $limit: 10 }
])
```

## 八、最佳实践

- 总是使用 explain() 分析查询
- 监控慢查询日志
- 合理设计复合索引
- 定期分析索引使用情况
- 避免在查询中使用正则表达式开头
- 合理使用投影减少数据传输

## 总结

MongoDB 查询优化是一个持续的过程，通过索引优化、查询重写和性能监控，可以显著提升应用性能。
