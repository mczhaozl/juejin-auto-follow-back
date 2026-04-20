# MongoDB 时间序列集合完全指南

## 一、创建时间序列集合

```javascript
db.createCollection("sensors", {
  timeseries: {
    timeField: "timestamp",
    metaField: "metadata",
    granularity: "hours" // seconds, minutes, hours
  },
  expireAfterSeconds: 86400 * 30 // TTL
});
```

## 二、插入数据

```javascript
db.sensors.insertMany([
  {
    metadata: { sensorId: 1, location: "office" },
    timestamp: new Date(),
    temperature: 24.5,
    humidity: 50
  },
  {
    metadata: { sensorId: 2, location: "warehouse" },
    timestamp: new Date(),
    temperature: 22.0,
    humidity: 60
  }
]);
```

## 三、查询数据

```javascript
// 查询特定时间范围
db.sensors.find({
  timestamp: {
    $gte: new Date(Date.now() - 86400 * 1000),
    $lt: new Date()
  },
  "metadata.sensorId": 1
});

// 聚合
db.sensors.aggregate([
  { $match: { timestamp: { $gte: new Date(Date.now() - 3600 * 1000) } } },
  {
    $group: {
      _id: "$metadata.sensorId",
      avgTemp: { $avg: "$temperature" }
    }
  }
]);
```

## 四、索引优化

```javascript
db.sensors.createIndex({
  "metadata.sensorId": 1,
  timestamp: 1
});
```

## 五、最佳实践

- 合理选择 granularity（粒度）
- 使用 metaField 存储元数据
- 自动过期（TTL）历史数据
- 优化查询和聚合索引
- 监控存储使用
