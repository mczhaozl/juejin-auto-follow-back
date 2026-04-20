# MongoDB 索引与性能优化完全指南：从 B 树到执行计划

## 一、索引概述

索引是提升 MongoDB 查询性能的关键机制，通过高效数据结构加速查询。

### 1.1 为什么需要索引

- 避免全表扫描（COLLSCAN）
- 提升查询速度
- 支持排序
- 优化聚合管道

### 1.2 MongoDB 索引类型

| 类型 | 用途 | 场景 |
|-----|------|------|
| 单字段索引 | 单个字段查询 | 简单查询 |
| 复合索引 | 多字段查询 | 复杂业务场景 |
| 多键索引 | 数组字段 | 标签、数组查询 |
| 文本索引 | 全文搜索 | 内容搜索 |
| 地理空间索引 | 位置查询 | LBS、地图 |

---

## 二、索引基础

### 2.1 单字段索引

```javascript
// 创建升序索引
db.products.createIndex({ price: 1 })

// 创建降序索引
db.products.createIndex({ createdAt: -1 })

// 查询
db.products.find({ price: { $gt: 100 } })
```

### 2.2 复合索引

```javascript
// 复合索引，前缀很重要
db.orders.createIndex({ status: 1, createdAt: -1 })

// 有效查询（使用前缀）
db.orders.find({ status: "completed" })
db.orders.find({ status: "pending", createdAt: { $gt: ISODate() } })
db.orders.find({ status: "pending" }).sort({ createdAt: -1 })

// 无效查询（未使用前缀）
db.orders.find({ createdAt: { $gt: ISODate() } })
```

---

## 三、索引策略

### 3.1 ESR 原则

```
Equality（等值） → Sort（排序） → Range（范围）
```

```javascript
// 正确索引顺序
db.orders.createIndex({ status: 1, createdAt: -1, amount: 1 })

// 查询
db.orders.find({ 
  status: "completed", 
  amount: { $gt: 100 } 
}).sort({ createdAt: -1 })
```

### 3.2 覆盖查询

```javascript
// 创建索引，包含查询与返回字段
db.orders.createIndex({ status: 1, customerId: 1, amount: 1 })

// 覆盖查询，无需访问文档
db.orders.find(
  { status: "completed", customerId: ObjectId("...") },
  { status: 1, customerId: 1, amount: 1, _id: 0 }
)
```

---

## 四、执行计划与诊断

### 4.1 explain()

```javascript
// 查看执行计划
db.products.find({ price: 50 }).explain("executionStats")

/* 输出关键指标
- stage: "IXSCAN" (索引扫描) 或 "COLLSCAN" (全表扫描)
- executionTimeMillis: 执行时间
- totalKeysExamined: 索引扫描数
- totalDocsExamined: 文档扫描数
*/
```

### 4.2 慢查询日志

```javascript
// 启用慢查询日志（100ms）
db.setProfilingLevel(1, { slowms: 100 })

// 查看慢查询
db.system.profile.find().sort({ millis: -1 }).limit(10)
```

---

## 五、高级索引

### 5.1 多键索引

```javascript
db.products.createIndex({ tags: 1 })

// 查询数组字段
db.products.find({ tags: "electronics" })
db.products.find({ tags: { $all: ["electronics", "smartphones"] } })
```

### 5.2 文本索引

```javascript
// 创建文本索引
db.articles.createIndex({ content: "text", title: "text" })

// 全文搜索
db.articles.find(
  { $text: { $search: "mongodb indexing" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })
```

### 5.3 部分索引

```javascript
// 只索引符合条件的文档
db.orders.createIndex(
  { status: 1, createdAt: 1 },
  { partialFilterExpression: { status: { $ne: "draft" } } }
)
```

### 5.4 稀疏索引

```javascript
db.users.createIndex(
  { phone: 1 },
  { sparse: true }  // 只索引包含 phone 字段的文档
)
```

---

## 六、索引维护

### 6.1 查看索引

```javascript
// 查看集合索引
db.products.getIndexes()

// 查看索引大小
db.products.totalIndexSize()
```

### 6.2 删除索引

```javascript
// 删除单个索引
db.products.dropIndex("price_1")

// 删除所有索引
db.products.dropIndexes()
```

### 6.3 重建索引

```javascript
db.products.reIndex()
```

---

## 七、性能优化实战

### 7.1 场景一：电商产品查询

```javascript
// 分析查询
db.products.explain().find({
  category: "electronics",
  price: { $gt: 100, $lt: 500 }
}).sort({ rating: -1, createdAt: -1 })

// 创建优化的复合索引
db.products.createIndex({
  category: 1,
  price: 1,
  rating: -1,
  createdAt: -1
})
```

### 7.2 场景二：订单聚合

```javascript
// 聚合优化
db.orders.createIndex({
  status: 1,
  customerId: 1,
  orderDate: 1,
  totalAmount: 1
})

db.orders.aggregate([
  { $match: { status: "completed", orderDate: { $gte: startDate } } },
  { $group: { _id: "$customerId", total: { $sum: "$totalAmount" } } },
  { $sort: { total: -1 } }
])
```

---

## 八、最佳实践

1. **避免索引过多**：索引占用内存与存储
2. **优先使用复合索引**：复用率高
3. **遵循 ESR 原则**：等值→排序→范围
4. **定期分析执行计划**：及时发现慢查询
5. **监控索引使用情况**：删除未使用索引

---

## 九、总结

索引优化是 MongoDB 性能调优的核心，掌握索引原理与策略，能显著提升系统性能。
