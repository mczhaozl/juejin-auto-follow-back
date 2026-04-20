# MongoDB 多区域部署完全指南

## 一、Replica Set 配置

```javascript
// 配置成员
var config = {
  "_id": "myReplicaSet",
  "version": 1,
  "members": [
    { "_id": 0, "host": "us-east.example.com:27017", priority: 2 },
    { "_id": 1, "host": "us-west.example.com:27017", priority: 1 },
    { "_id": 2, "host": "eu-west.example.com:27017", priority: 0 }
  ]
};

rs.initiate(config);
```

## 二、写入关注

```javascript
// 1. 等待主要
db.collection.insertOne(
  { x: 1 }, 
  { writeConcern: { w: "majority" } }
);

// 2. 等待特定标签
db.collection.insertOne(
  { x: 1 }, 
  { writeConcern: { w: 2, wtimeout: 5000 } }
);
```

## 三、读取偏好

```javascript
const MongoClient = require('mongodb').MongoClient;
const uri = "mongodb://.../?readPreference=secondaryPreferred";

MongoClient.connect(uri, (err, client) => {
  // ...
});

// 或者
const collection = db.collection('mycollection');
collection.find({})
  .readPreference('secondaryPreferred')
  .toArray();
```

## 四、分片集群

```javascript
// Shard 标签
sh.addShard("shard0/us-east:27017");
sh.addShard("shard1/us-west:27017");

sh.addShardTag("shard0", "US");
sh.addShardTag("shard1", "EU");

// Tag-aware sharding
sh.addTagRange("myDB.myCollection", 
  { region: "US" }, { region: "US" }, "US");
sh.addTagRange("myDB.myCollection", 
  { region: "EU" }, { region: "EU" }, "EU");
```

## 最佳实践
- 至少 3 个成员
- 优先级设置合理
- writeConcern: majority 保证安全
- 选择合适的 readPreference
- 监控延迟和副本状态
