# MongoDB 聚合管道完全指南

## 一、基本管道

```javascript
db.sales.aggregate([
  { $match: { date: { $gte: ISODate('2024-01-01') } } },
  { $group: { _id: '$product', total: { $sum: '$amount' } } },
  { $sort: { total: -1 } }
]);
```

## 二、$lookup

```javascript
db.orders.aggregate([
  {
    $lookup: {
      from: 'products',
      localField: 'productId',
      foreignField: '_id',
      as: 'product'
    }
  }
]);
```

## 三、$unwind

```javascript
db.sales.aggregate([
  { $unwind: '$items' },
  { $group: { _id: '$items.sku', count: { $sum: 1 } } }
]);
```

## 四、$project

```javascript
db.collection.aggregate([
  {
    $project: {
      name: 1,
      _id: 0,
      total: { $multiply: ['$price', '$quantity'] }
    }
  }
]);
```

## 最佳实践
- $match 尽量靠前
- 索引优化 $match 和 $sort
- 管道阶段顺序重要
- 避免 $unwind 大数据集
- explain() 分析性能
