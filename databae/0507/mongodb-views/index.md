# MongoDB Views 完全指南

## 一、创建视图

```javascript
db.createView("user_summaries", "users", [
  {
    $project: {
      name: 1,
      email: 1,
      createdAt: 1,
      postCount: { $size: "$posts" }
    }
  }
]);
```

## 二、视图查询

```javascript
db.user_summaries.find();
db.user_summaries.aggregate([...]);
```

## 三、物化视图

```javascript
db.createCollection("user_summaries_mv", {
  viewOn: "users",
  pipeline: [
    { $group: { _id: "$status", count: { $sum: 1 } } }
  ]
});

// 刷新
db.user_summaries_mv.aggregate([...]);
```

## 四、视图最佳实践

- 只读视图简化查询
- 对敏感信息进行投影
- 合理设置权限控制
- 监控查询性能
- 考虑物化视图
- 使用视图进行数据聚合
