# MongoDB Change Streams 实时数据流完全指南

## 一、Change Streams 概述

### 1.1 什么是 Change Streams

Change Streams 允许实时监听数据库的变更，类似数据库触发器。

### 1.2 支持的操作

- insert
- update
- replace
- delete
- drop
- rename
- dropDatabase

---

## 二、基本用法

### 2.1 开启 Change Stream

```javascript
const MongoClient = require('mongodb').MongoClient;

async function watchChanges() {
  const client = await MongoClient.connect('mongodb://localhost:27017');
  const db = client.db('mydb');
  const collection = db.collection('users');
  
  const changeStream = collection.watch();
  
  changeStream.on('change', next => {
    console.log('Change:', next);
  });
  
  changeStream.on('error', err => {
    console.error('Error:', err);
  });
}

watchChanges();
```

### 2.2 事件结构

```javascript
{
  _id: { _data: '...' },
  operationType: 'insert',
  clusterTime: Timestamp(...),
  ns: { db: 'mydb', coll: 'users' },
  documentKey: { _id: ObjectId('...') },
  fullDocument: { _id: ObjectId('...'), name: 'John' }
}
```

---

## 三、高级配置

### 3.1 过滤变更

```javascript
// 只监听 insert 操作
const changeStream = collection.watch([
  { $match: { operationType: 'insert' } }
]);

// 过滤特定字段
const changeStream = collection.watch([
  {
    $match: {
      $or: [
        { operationType: 'insert' },
        { operationType: 'update' }
      ]
    }
  }
]);
```

### 3.2 获取更新前文档

```javascript
const changeStream = collection.watch([], {
  fullDocument: 'updateLookup'
});

changeStream.on('change', next => {
  console.log('Full document:', next.fullDocument);
});
```

### 3.3 获取更新前文档（v6.0+）

```javascript
const changeStream = collection.watch([], {
  fullDocumentBeforeChange: 'whenAvailable'
});

changeStream.on('change', next => {
  console.log('Before:', next.fullDocumentBeforeChange);
  console.log('After:', next.fullDocument);
});
```

---

## 四、管道操作

### 4.1 字段投影

```javascript
const changeStream = collection.watch([
  {
    $project: {
      'fullDocument.name': 1,
      'fullDocument.email': 1,
      operationType: 1
    }
  }
]);
```

### 4.2 过滤条件

```javascript
const changeStream = collection.watch([
  {
    $match: {
      $or: [
        { 'fullDocument.age': { $gt: 18 } },
        { operationType: 'delete' }
      ]
    }
  }
]);
```

### 4.3 字段重命名

```javascript
const changeStream = collection.watch([
  {
    $addFields: {
      user: '$fullDocument',
      timestamp: '$clusterTime'
    }
  },
  {
    $project: {
      fullDocument: 0
    }
  }
]);
```

---

## 五、恢复与重连

### 5.1 从断点恢复

```javascript
let resumeToken = null;

async function watchWithResume() {
  const client = await MongoClient.connect('mongodb://localhost:27017');
  const db = client.db('mydb');
  const collection = db.collection('users');
  
  const options = resumeToken ? { resumeAfter: resumeToken } : {};
  const changeStream = collection.watch([], options);
  
  changeStream.on('change', next => {
    resumeToken = next._id;
    console.log('Change:', next);
    // 处理变更...
  });
}

// 保存 resumeToken 到数据库或文件
```

### 5.2 重连机制

```javascript
async function watchWithRetry() {
  let resumeToken = null;
  
  while (true) {
    try {
      const client = await MongoClient.connect('mongodb://localhost:27017');
      const db = client.db('mydb');
      const collection = db.collection('users');
      
      const options = resumeToken ? { resumeAfter: resumeToken } : {};
      const changeStream = collection.watch([], options);
      
      for await (const change of changeStream) {
        resumeToken = change._id;
        console.log('Change:', change);
      }
    } catch (err) {
      console.error('Error:', err);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}
```

---

## 六、实战场景

### 6.1 实时通知系统

```javascript
async function notificationService() {
  const client = await MongoClient.connect('mongodb://localhost:27017');
  const db = client.db('mydb');
  const ordersCollection = db.collection('orders');
  
  const changeStream = ordersCollection.watch([
    {
      $match: {
        operationType: 'insert'
      }
    }
  ]);
  
  changeStream.on('change', next => {
    const order = next.fullDocument;
    sendNotification(order.userId, `订单 ${order._id} 已创建`);
  });
}

function sendNotification(userId, message) {
  console.log(`发送通知给用户 ${userId}: ${message}`);
  // 调用推送服务...
}
```

### 6.2 数据同步

```javascript
async function dataSync() {
  const client = await MongoClient.connect('mongodb://localhost:27017');
  const sourceDb = client.db('source');
  const targetDb = client.db('target');
  const sourceCollection = sourceDb.collection('users');
  const targetCollection = targetDb.collection('users');
  
  const changeStream = sourceCollection.watch();
  
  changeStream.on('change', async next => {
    switch (next.operationType) {
      case 'insert':
        await targetCollection.insertOne(next.fullDocument);
        break;
      case 'update':
        await targetCollection.updateOne(
          { _id: next.documentKey._id },
          next.updateDescription.updatedFields
        );
        break;
      case 'delete':
        await targetCollection.deleteOne({ _id: next.documentKey._id });
        break;
    }
  });
}
```

### 6.3 全文索引更新

```javascript
async function searchIndexService() {
  const client = await MongoClient.connect('mongodb://localhost:27017');
  const db = client.db('mydb');
  const articles = db.collection('articles');
  
  const changeStream = articles.watch([], {
    fullDocument: 'updateLookup'
  });
  
  changeStream.on('change', async next => {
    if (next.operationType === 'insert' || next.operationType === 'update') {
      const article = next.fullDocument;
      await updateSearchIndex(article);
    } else if (next.operationType === 'delete') {
      await removeFromSearchIndex(next.documentKey._id);
    }
  });
}

async function updateSearchIndex(article) {
  console.log('更新搜索索引:', article._id);
  // 调用 Elasticsearch 或其他搜索服务...
}

async function removeFromSearchIndex(id) {
  console.log('从搜索索引删除:', id);
}
```

---

## 七、Watch 整个数据库

```javascript
async function watchDatabase() {
  const client = await MongoClient.connect('mongodb://localhost:27017');
  const db = client.db('mydb');
  
  const changeStream = db.watch();
  
  changeStream.on('change', next => {
    console.log('DB Change:', next);
  });
}
```

---

## 八、Watch 整个集群

```javascript
async function watchCluster() {
  const client = await MongoClient.connect('mongodb://localhost:27017');
  
  const changeStream = client.watch();
  
  changeStream.on('change', next => {
    console.log('Cluster Change:', next);
  });
}
```

---

## 九、性能与限制

### 9.1 注意事项

- Change Stream 需要 replica set 或 sharded cluster
- 变更事件有过期时间（默认 oplog 大小）
- 大量变更时注意性能

### 9.2 最佳实践

- 保存 resumeToken 以便恢复
- 批量处理变更
- 合理设置批大小

---

## 总结

Change Streams 是 MongoDB 强大的实时数据变更监听功能，适用于实时通知、数据同步、搜索索引更新等场景。
