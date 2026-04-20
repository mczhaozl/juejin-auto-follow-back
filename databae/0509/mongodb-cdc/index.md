# MongoDB Change Data Capture 完全指南

## 一、开启 Change Streams

```javascript
// 监听集合变化
const changeStream = db.collection.watch();

changeStream.on("change", (changeEvent) => {
  console.log("变更事件:", changeEvent);
  // {
  //   _id: { _data: "..." },
  //   operationType: "insert", // update, delete, replace
  //   ns: { db: "test", coll: "mycollection" },
  //   documentKey: { _id: ObjectId("...") },
  //   fullDocument: { ... }
  // }
});

// 使用聚合管道过滤事件
const changeStream = db.collection.watch([
  { $match: { operationType: "insert" } }
]);
```

## 二、恢复与故障转移

```javascript
// 记录 resume token 用于断点续传
const resumeToken = changeStream.resumeToken;

// 从上次中断的地方继续
const newStream = db.collection.watch([], { resumeAfter: resumeToken });
```

## 三、完整 CDC 管道

```javascript
// 更新数据到 Elasticsearch
changeStream.on("change", async (event) => {
  if (event.operationType === "insert" || event.operationType === "update") {
    const doc = event.fullDocument || event.documentKey;
    await esClient.index({
      index: "my-index",
      id: doc._id.toString(),
      body: doc
    });
  } else if (event.operationType === "delete") {
    await esClient.delete({
      index: "my-index",
      id: event.documentKey._id.toString()
    });
  }
});
```

## 四、完整文档监听

```javascript
// 更新时获取完整文档
const changeStream = db.collection.watch([], { fullDocument: "updateLookup" });
```

## 五、最佳实践

- 保存 resume token 用于断点续传
- 处理重连逻辑
- 合理过滤事件减少处理负担
- 使用 fullDocument: "updateLookup" 简化处理
- 监控延迟并告警
- 考虑并行处理能力
- 设计好的幂等性处理逻辑
