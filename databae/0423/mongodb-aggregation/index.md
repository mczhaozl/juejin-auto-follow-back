# MongoDB 聚合管道完全指南：从基础到复杂查询

MongoDB 聚合管道是处理数据的强大工具。本文将带你全面掌握聚合管道的各种技巧。

## 一、聚合基础

### 1. 什么是聚合管道

聚合管道由多个阶段组成，每个阶段对文档进行处理，然后将结果传递给下一个阶段。

```javascript
// 基本语法
db.collection.aggregate([
  { $match: { status: "active" } },
  { $group: { _id: "$category", total: { $sum: "$amount" } } },
  { $sort: { total: -1 } }
])
```

### 2. 数据准备

```javascript
// 示例数据：订单集合
db.orders.insertMany([
  { _id: 1, product: "A", category: "Electronics", price: 100, quantity: 2, status: "completed", date: ISODate("2024-01-05") },
  { _id: 2, product: "B", category: "Clothing", price: 50, quantity: 3, status: "completed", date: ISODate("2024-01-10") },
  { _id: 3, product: "C", category: "Electronics", price: 200, quantity: 1, status: "pending", date: ISODate("2024-01-15") },
  { _id: 4, product: "D", category: "Books", price: 30, quantity: 5, status: "completed", date: ISODate("2024-01-20") },
  { _id: 5, product: "E", category: "Electronics", price: 150, quantity: 2, status: "completed", date: ISODate("2024-02-01") },
  { _id: 6, product: "F", category: "Clothing", price: 80, quantity: 1, status: "cancelled", date: ISODate("2024-02-05") },
  { _id: 7, product: "G", category: "Books", price: 25, quantity: 4, status: "completed", date: ISODate("2024-02-10") },
  { _id: 8, product: "H", category: "Electronics", price: 300, quantity: 1, status: "completed", date: ISODate("2024-02-15") }
])
```

## 二、常用聚合阶段

### 1. $match - 过滤文档

```javascript
// 简单匹配
db.orders.aggregate([
  { $match: { status: "completed" } }
])

// 多条件匹配
db.orders.aggregate([
  {
    $match: {
      status: "completed",
      price: { $gt: 100 },
      category: { $in: ["Electronics", "Books"] }
    }
  }
])
```

### 2. $project - 投影字段

```javascript
// 选择字段
db.orders.aggregate([
  {
    $project: {
      product: 1,
      category: 1,
      total: { $multiply: ["$price", "$quantity"] },
      _id: 0
    }
  }
])

// 排除字段
db.orders.aggregate([
  { $project: { _id: 0, status: 0 } }
])
```

### 3. $group - 分组

```javascript
// 基本分组
db.orders.aggregate([
  {
    $group: {
      _id: "$category",
      count: { $sum: 1 },
      totalAmount: { $sum: { $multiply: ["$price", "$quantity"] } },
      avgPrice: { $avg: "$price" },
      maxPrice: { $max: "$price" },
      minPrice: { $min: "$price" }
    }
  }
])

// 多字段分组
db.orders.aggregate([
  {
    $group: {
      _id: {
        category: "$category",
        status: "$status"
      },
      count: { $sum: 1 }
    }
  }
])
```

### 4. $sort - 排序

```javascript
// 排序
db.orders.aggregate([
  { $sort: { price: -1, quantity: 1 } }
])

// 分组后排序
db.orders.aggregate([
  {
    $group: {
      _id: "$category",
      total: { $sum: { $multiply: ["$price", "$quantity"] } }
    }
  },
  { $sort: { total: -1 } }
])
```

### 5. $limit 和 $skip - 分页

```javascript
// 分页
db.orders.aggregate([
  { $sort: { date: -1 } },
  { $skip: 0 },
  { $limit: 5 }
])
```

### 6. $unwind - 展开数组

```javascript
// 准备数组数据
db.products.insertOne({
  _id: 1,
  name: "Laptop",
  tags: ["electronics", "computer", "tech"],
  variants: [
    { size: "13 inch", price: 999 },
    { size: "15 inch", price: 1299 },
    { size: "17 inch", price: 1599 }
  ]
})

// 展开数组
db.products.aggregate([
  { $unwind: "$tags" }
])

// 展开嵌套数组
db.products.aggregate([
  { $unwind: "$variants" },
  {
    $project: {
      name: 1,
      size: "$variants.size",
      price: "$variants.price"
    }
  }
])
```

### 7. $lookup - 关联查询

```javascript
// 准备关联数据
db.customers.insertMany([
  { _id: 1, name: "Alice", email: "alice@example.com" },
  { _id: 2, name: "Bob", email: "bob@example.com" }
])

db.orders.updateMany({}, { $set: { customerId: 1 } })
db.orders.updateOne({ _id: 2 }, { $set: { customerId: 2 } })
db.orders.updateOne({ _id: 5 }, { $set: { customerId: 2 } })

// 左连接
db.orders.aggregate([
  {
    $lookup: {
      from: "customers",
      localField: "customerId",
      foreignField: "_id",
      as: "customer"
    }
  },
  { $unwind: "$customer" },
  {
    $project: {
      product: 1,
      customerName: "$customer.name",
      customerEmail: "$customer.email"
    }
  }
])
```

## 三、常用聚合表达式

### 1. 算术表达式

```javascript
db.orders.aggregate([
  {
    $project: {
      product: 1,
      price: 1,
      quantity: 1,
      total: { $multiply: ["$price", "$quantity"] },
      discounted: { $subtract: [{ $multiply: ["$price", "$quantity"] }, 10] },
      halfPrice: { $divide: ["$price", 2] },
      priceSquared: { $pow: ["$price", 2] },
      modulo: { $mod: ["$price", 3] }
    }
  }
])
```

### 2. 字符串表达式

```javascript
db.orders.aggregate([
  {
    $project: {
      product: 1,
      productUpper: { $toUpper: "$product" },
      productLower: { $toLower: "$product" },
      categoryLen: { $strLenCP: "$category" },
      combined: { $concat: ["$product", " - ", "$category"] },
      substring: { $substrCP: ["$product", 0, 2] }
    }
  }
])
```

### 3. 日期表达式

```javascript
db.orders.aggregate([
  {
    $project: {
      product: 1,
      date: 1,
      year: { $year: "$date" },
      month: { $month: "$date" },
      day: { $dayOfMonth: "$date" },
      week: { $week: "$date" },
      hour: { $hour: "$date" },
      dayOfWeek: { $dayOfWeek: "$date" },
      dateToString: { $dateToString: { format: "%Y-%m-%d", date: "$date" } }
    }
  }
])

// 按月份分组
db.orders.aggregate([
  {
    $group: {
      _id: {
        year: { $year: "$date" },
        month: { $month: "$date" }
      },
      total: { $sum: { $multiply: ["$price", "$quantity"] } },
      count: { $sum: 1 }
    }
  },
  { $sort: { "_id.year": 1, "_id.month": 1 } }
])
```

### 4. 条件表达式

```javascript
db.orders.aggregate([
  {
    $project: {
      product: 1,
      price: 1,
      priceRange: {
        $cond: {
          if: { $lt: ["$price", 50] },
          then: "Low",
          else: {
            $cond: {
              if: { $lt: ["$price", 150] },
              then: "Medium",
              else: "High"
            }
          }
        }
      },
      isElectronics: {
        $eq: ["$category", "Electronics"]
      }
    }
  }
])

// $switch
db.orders.aggregate([
  {
    $project: {
      product: 1,
      category: 1,
      categoryLabel: {
        $switch: {
          branches: [
            { case: { $eq: ["$category", "Electronics"] }, then: "电子产品" },
            { case: { $eq: ["$category", "Clothing"] }, then: "服装" },
            { case: { $eq: ["$category", "Books"] }, then: "图书" }
          ],
          default: "其他"
        }
      }
    }
  }
])
```

## 四、实战案例

### 1. 销售报表

```javascript
db.orders.aggregate([
  { $match: { status: "completed" } },
  {
    $group: {
      _id: {
        year: { $year: "$date" },
        month: { $month: "$date" },
        category: "$category"
      },
      totalSales: { $sum: { $multiply: ["$price", "$quantity"] } },
      totalQuantity: { $sum: "$quantity" },
      orderCount: { $sum: 1 },
      avgOrderValue: { $avg: { $multiply: ["$price", "$quantity"] } }
    }
  },
  {
    $sort: {
      "_id.year": 1,
      "_id.month": 1,
      totalSales: -1
    }
  }
])
```

### 2. 商品分析

```javascript
db.orders.aggregate([
  { $match: { status: "completed" } },
  {
    $group: {
      _id: "$product",
      category: { $first: "$category" },
      totalSold: { $sum: "$quantity" },
      totalRevenue: { $sum: { $multiply: ["$price", "$quantity"] } },
      timesOrdered: { $sum: 1 },
      avgPrice: { $avg: "$price" }
    }
  },
  { $sort: { totalRevenue: -1 } },
  { $limit: 5 }
])
```

### 3. 客户购买分析

```javascript
db.orders.aggregate([
  { $match: { status: "completed" } },
  {
    $lookup: {
      from: "customers",
      localField: "customerId",
      foreignField: "_id",
      as: "customer"
    }
  },
  { $unwind: "$customer" },
  {
    $group: {
      _id: "$customerId",
      customerName: { $first: "$customer.name" },
      customerEmail: { $first: "$customer.email" },
      totalOrders: { $sum: 1 },
      totalSpent: { $sum: { $multiply: ["$price", "$quantity"] } },
      categories: { $addToSet: "$category" },
      firstOrder: { $min: "$date" },
      lastOrder: { $max: "$date" }
    }
  },
  { $sort: { totalSpent: -1 } }
])
```

### 4. 时间序列分析

```javascript
db.orders.aggregate([
  { $match: { status: "completed" } },
  {
    $group: {
      _id: {
        $dateTrunc: {
          date: "$date",
          unit: "day"
        }
      },
      dailySales: { $sum: { $multiply: ["$price", "$quantity"] } },
      dailyOrders: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { _id: 1 },
      output: {
        movingAverage: {
          $avg: "$dailySales",
          window: {
            range: [-6, "current"],
            unit: "day"
          }
        }
      }
    }
  }
])
```

## 五、聚合性能优化

### 1. $match 尽早执行

```javascript
// ✅ 好：先过滤再分组
db.orders.aggregate([
  { $match: { status: "completed", date: { $gte: ISODate("2024-01-01") } } },
  { $group: { _id: "$category", total: { $sum: 1 } } }
])

// ❌ 不好：先分组再过滤
db.orders.aggregate([
  { $group: { _id: { category: "$category", status: "$status" }, total: { $sum: 1 } } },
  { $match: { "_id.status": "completed" } }
])
```

### 2. 使用索引

```javascript
// 创建索引
db.orders.createIndex({ status: 1, date: -1 })
db.orders.createIndex({ category: 1, status: 1 })
```

### 3. 限制数据量

```javascript
// 使用 limit 和 skip
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { date: -1 } },
  { $limit: 100 }
])
```

### 4. 允许磁盘使用

```javascript
// 大数据量聚合
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: { _id: "$category", total: { $sum: 1 } } }
], { allowDiskUse: true })
```

## 六、最佳实践

1. 尽早使用 $match 过滤
2. 合理使用索引
3. 减少 $project 中的字段
4. 注意 $unwind 的使用
5. 监控聚合性能
6. 使用 explain 分析
7. 考虑数据量大小

## 七、总结

MongoDB 聚合管道：
- 掌握常用阶段（$match, $group, $sort, $project）
- 理解聚合表达式
- 实战复杂查询
- 关联查询使用 $lookup
- 优化聚合性能
- 遵循最佳实践

掌握聚合管道，让你的 MongoDB 查询更强大！
