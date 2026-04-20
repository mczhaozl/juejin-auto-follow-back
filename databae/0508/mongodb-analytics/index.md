# MongoDB 数据分析完全指南

## 一、MongoDB 聚合管道进阶

```javascript
// 数据仓库查询模式
db.orders.aggregate([
  // 时间范围筛选
  { $match: { orderDate: { $gte: new Date("2025-01-01"), $lt: new Date("2026-01-01") } } },
  // 多字段分组
  { $group: { _id: { month: { $month: "$orderDate" }, category: "$category" }, totalAmount: { $sum: "$amount" }, count: { $sum: 1 } } },
  // 排序
  { $sort: { "_id.month": 1, totalAmount: -1 } }
])

// 窗口函数
db.sales.aggregate([
  { $sort: { date: 1 } },
  { $setWindowFields: {
      partitionBy: "$product",
      sortBy: { date: 1 },
      output: {
          cumulativeSales: { $sum: "$amount", window: { documents: ["unbounded", "current"] } },
          movingAvg: { $avg: "$amount", window: { documents: [-2, "current"] } }
      }
    }
  }
])
```

## 二、MongoDB 数据仓库架构

```javascript
// 物化视图模式
db.createCollection("sales_summary", {
  viewOn: "orders",
  pipeline: [
    { $group: { _id: { day: { $dayOfMonth: "$orderDate" }, product: "$product" }, amount: { $sum: "$total" } } },
    { $project: { date: "$_id.day", product: "$_id.product", amount: 1, _id: 0 } }
  ]
})

// 增量更新
db.orders.watch().on("change", (change) => {
  // 更新摘要数据
})
```

## 三、MongoDB 与 BI 工具集成

```javascript
// MongoDB Connector for BI
// 支持 SQL 查询和 Tableau/Power BI 集成
```

## 四、实战：电商销售分析

```javascript
// 用户购买分析
db.users.aggregate([
  { $lookup: { from: "orders", localField: "_id", foreignField: "userId", as: "orders" } },
  { $project: { name: 1, orderCount: { $size: "$orders" }, totalSpent: { $sum: "$orders.total" } } },
  { $sort: { totalSpent: -1 } },
  { $limit: 100 }
])

// 产品销量排行榜
db.orders.aggregate([
  { $unwind: "$items" },
  { $group: { _id: "$items.product", totalQuantity: { $sum: "$items.quantity" }, totalRevenue: { $sum: "$items.price" } } },
  { $sort: { totalRevenue: -1 } },
  { $limit: 10 }
])
```

## 五、最佳实践

- 合理设计聚合管道阶段
- 利用索引加速匹配阶段
- 分区集合优化大数据查询
- 物化视图预计算摘要数据
- 监控聚合查询性能
- 定期归档历史数据
