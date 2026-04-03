# MongoDB 高级特性完全指南

MongoDB 是最流行的 NoSQL 数据库。本文将带你从基础到高级，全面掌握 MongoDB 的高级特性。

## 一、MongoDB 基础

### 1. 连接和 CRUD

```javascript
// 连接
const { MongoClient } = require('mongodb');

const uri = 'mongodb://localhost:27017';
const client = new MongoClient(uri);

async function main() {
  await client.connect();
  const db = client.db('mydb');
  const collection = db.collection('users');
  
  // 插入
  await collection.insertOne({ name: 'John', age: 30 });
  await collection.insertMany([
    { name: 'Jane', age: 25 },
    { name: 'Bob', age: 35 },
  ]);
  
  // 查询
  const user = await collection.findOne({ name: 'John' });
  const users = await collection.find({ age: { $gt: 25 } }).toArray();
  
  // 更新
  await collection.updateOne(
    { name: 'John' },
    { $set: { age: 31 } }
  );
  
  // 删除
  await collection.deleteOne({ name: 'John' });
  
  await client.close();
}

main();
```

### 2. 查询操作符

```javascript
// 比较操作符
db.users.find({ age: { $gt: 25 } });        // 大于
db.users.find({ age: { $gte: 25 } });       // 大于等于
db.users.find({ age: { $lt: 30 } });        // 小于
db.users.find({ age: { $lte: 30 } });       // 小于等于
db.users.find({ age: { $ne: 30 } });        // 不等于
db.users.find({ age: { $in: [25, 30, 35] } });  // 在...中
db.users.find({ age: { $nin: [25, 30, 35] } }); // 不在...中

// 逻辑操作符
db.users.find({
  $and: [{ age: { $gt: 25 } }, { age: { $lt: 35 } }]
});
db.users.find({
  $or: [{ age: { $lt: 25 } }, { age: { $gt: 35 } }]
});
db.users.find({
  $not: { age: { $gt: 30 } }
});
db.users.find({
  $nor: [{ age: 25 }, { age: 30 }]
});

// 元素操作符
db.users.find({ name: { $exists: true } });
db.users.find({ age: { $type: 'int' } });

// 数组操作符
db.users.find({ tags: { $all: ['a', 'b'] } });
db.users.find({ tags: { $elemMatch: { $gt: 5 } } });
db.users.find({ tags: { $size: 3 } });

// 评估操作符
db.users.find({ $expr: { $gt: ['$age', 30] } });
db.users.find({ $jsonSchema: { /* schema */ } });
db.users.find({ $text: { $search: 'John' } });
db.users.find({ $where: 'this.age > 30' });
```

### 3. 更新操作符

```javascript
// 字段更新
db.users.updateOne(
  { name: 'John' },
  { $set: { age: 31, email: 'john@example.com' } }
);

db.users.updateOne(
  { name: 'John' },
  { $unset: { email: '' } }
);

db.users.updateOne(
  { name: 'John' },
  { $inc: { age: 1 } }
);

db.users.updateOne(
  { name: 'John' },
  { $mul: { score: 1.1 } }
);

db.users.updateOne(
  { name: 'John' },
  { $min: { score: 100 } }
);

db.users.updateOne(
  { name: 'John' },
  { $max: { score: 0 } }
);

db.users.updateOne(
  { name: 'John' },
  { $rename: { oldField: 'newField' } }
);

// 数组更新
db.users.updateOne(
  { name: 'John' },
  { $push: { tags: 'new' } }
);

db.users.updateOne(
  { name: 'John' },
  { $push: { tags: { $each: ['a', 'b'] } } }
);

db.users.updateOne(
  { name: 'John' },
  { $addToSet: { tags: 'unique' } }
);

db.users.updateOne(
  { name: 'John' },
  { $pull: { tags: 'old' } }
);

db.users.updateOne(
  { name: 'John' },
  { $pop: { tags: 1 } }  // 1: 末尾, -1: 开头
);
```

## 二、索引

### 1. 基础索引

```javascript
// 单字段索引
db.users.createIndex({ name: 1 });  // 1: 升序, -1: 降序

// 复合索引
db.users.createIndex({ name: 1, age: -1 });

// 唯一索引
db.users.createIndex({ email: 1 }, { unique: true });

// 稀疏索引
db.users.createIndex({ email: 1 }, { sparse: true });

// 部分索引
db.users.createIndex(
  { email: 1 },
  { partialFilterExpression: { email: { $exists: true } } }
);

// TTL 索引
db.logs.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 });

// 查看索引
db.users.getIndexes();

// 删除索引
db.users.dropIndex('name_1');
```

### 2. 文本索引

```javascript
// 创建文本索引
db.articles.createIndex({ title: 'text', content: 'text' });

// 文本搜索
db.articles.find({ $text: { $search: 'MongoDB' } });

// 短语搜索
db.articles.find({ $text: { $search: '"MongoDB tutorial"' } });

// 排除词
db.articles.find({ $text: { $search: 'MongoDB -SQL' } });

// 得分排序
db.articles.find(
  { $text: { $search: 'MongoDB' } },
  { score: { $meta: 'textScore' } }
).sort({ score: { $meta: 'textScore' } });
```

### 3. 地理空间索引

```javascript
// 2dsphere 索引
db.places.createIndex({ location: '2dsphere' });

// 插入地理位置数据
db.places.insertOne({
  name: 'Place',
  location: {
    type: 'Point',
    coordinates: [-73.9667, 40.78]
  }
});

// 附近查询
db.places.find({
  location: {
    $near: {
      $geometry: {
        type: 'Point',
        coordinates: [-73.9667, 40.78]
      },
      $maxDistance: 1000
    }
  }
});

// 范围内查询
db.places.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: 'Polygon',
        coordinates: [[
          [-74, 40.7],
          [-74, 40.8],
          [-73.9, 40.8],
          [-73.9, 40.7],
          [-74, 40.7]
        ]]
      }
    }
  }
});
```

### 4. 索引分析

```javascript
// explain()
db.users.find({ name: 'John' }).explain('executionStats');

// hint() - 强制使用索引
db.users.find({ name: 'John' }).hint({ name: 1 });

// 索引使用统计
db.users.aggregate([{ $indexStats: {} }]);
```

## 三、聚合管道

### 1. 基础聚合

```javascript
// $match - 过滤
db.users.aggregate([
  { $match: { age: { $gt: 25 } } }
]);

// $group - 分组
db.users.aggregate([
  {
    $group: {
      _id: '$country',
      count: { $sum: 1 },
      avgAge: { $avg: '$age' }
    }
  }
]);

// $project - 投影
db.users.aggregate([
  {
    $project: {
      name: 1,
      age: 1,
      _id: 0
    }
  }
]);

// $sort - 排序
db.users.aggregate([
  { $sort: { age: -1 } }
]);

// $skip 和 $limit - 分页
db.users.aggregate([
  { $skip: 10 },
  { $limit: 10 }
]);
```

### 2. 常用聚合操作符

```javascript
// 算术表达式
db.sales.aggregate([
  {
    $project: {
      total: { $multiply: ['$price', '$quantity'] },
      tax: { $multiply: ['$total', 0.1] }
    }
  }
]);

// 数组表达式
db.users.aggregate([
  {
    $project: {
      tags: { $filter: {
        input: '$tags',
        as: 'tag',
        cond: { $ne: ['$$tag', 'old'] }
      }},
      tagCount: { $size: '$tags' }
    }
  }
]);

// 日期表达式
db.logs.aggregate([
  {
    $project: {
      year: { $year: '$createdAt' },
      month: { $month: '$createdAt' },
      day: { $dayOfMonth: '$createdAt' }
    }
  }
]);

// 条件表达式
db.users.aggregate([
  {
    $project: {
      name: 1,
      age: 1,
      status: {
        $cond: {
          if: { $gte: ['$age', 18] },
          then: 'adult',
          else: 'minor'
        }
      }
    }
  }
]);
```

### 3. 实战聚合

```javascript
// 销售统计
db.sales.aggregate([
  {
    $match: {
      date: { $gte: new Date('2024-01-01') }
    }
  },
  {
    $group: {
      _id: {
        year: { $year: '$date' },
        month: { $month: '$date' },
        product: '$product'
      },
      totalSales: { $sum: { $multiply: ['$price', '$quantity'] } },
      avgPrice: { $avg: '$price' },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { '_id.year': 1, '_id.month': 1, totalSales: -1 }
  }
]);

// 用户行为分析
db.events.aggregate([
  {
    $match: {
      type: 'page_view'
    }
  },
  {
    $group: {
      _id: '$page',
      views: { $sum: 1 },
      uniqueUsers: { $addToSet: '$userId' }
    }
  },
  {
    $project: {
      page: '$_id',
      views: 1,
      uniqueUsers: { $size: '$uniqueUsers' },
      _id: 0
    }
  },
  {
    $sort: { views: -1 }
  }
]);
```

## 四、数据建模

### 1. 嵌入 vs 引用

```javascript
// 嵌入（一对少）
{
  _id: 1,
  name: 'John',
  addresses: [
    { street: '123 Main St', city: 'NY' },
    { street: '456 Oak Ave', city: 'LA' }
  ]
}

// 引用（一对多）
// users 集合
{
  _id: 1,
  name: 'John'
}

// posts 集合
{
  _id: 1,
  title: 'Hello',
  authorId: 1,
  comments: [1, 2, 3]
}
```

### 2. 数据验证

```javascript
// Schema Validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'email'],
      properties: {
        name: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 50
        },
        email: {
          bsonType: 'string',
          pattern: '^.+@.+$'
        },
        age: {
          bsonType: 'int',
          minimum: 0,
          maximum: 120
        }
      }
    }
  },
  validationLevel: 'strict',
  validationAction: 'error'
});
```

### 3. 变更流

```javascript
// 监听变更
const changeStream = db.users.watch();

changeStream.on('change', (change) => {
  console.log(change);
});

// 特定操作
const changeStream = db.users.watch([
  { $match: { operationType: 'insert' } }
]);

// 完整文档
const changeStream = db.users.watch([], { fullDocument: 'updateLookup' });
```

## 五、性能优化

### 1. 查询优化

```javascript
// 使用索引
db.users.find({ name: 'John' }).explain('executionStats');

// 覆盖查询
db.users.find(
  { name: 'John' },
  { name: 1, email: 1, _id: 0 }
);

// 避免使用 $where
// ❌ 不好
db.users.find({ $where: 'this.age > 30' });

// ✅ 好
db.users.find({ age: { $gt: 30 } });
```

### 2. 批量操作

```javascript
// 批量插入
db.users.insertMany([
  { name: 'User 1' },
  { name: 'User 2' },
  { name: 'User 3' }
]);

// 批量更新
db.users.bulkWrite([
  { updateOne: { filter: { name: 'User 1' }, update: { $set: { age: 25 } } } },
  { updateOne: { filter: { name: 'User 2' }, update: { $set: { age: 30 } } } }
]);
```

## 六、事务

```javascript
// 会话和事务
const session = client.startSession();

try {
  session.startTransaction();
  
  await db.accounts.updateOne(
    { _id: 'from' },
    { $inc: { balance: -100 } },
    { session }
  );
  
  await db.accounts.updateOne(
    { _id: 'to' },
    { $inc: { balance: 100 } },
    { session }
  );
  
  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

## 七、最佳实践

1. 合理设计数据模型
2. 创建适当的索引
3. 使用聚合管道
4. 避免大文档
5. 使用批量操作
6. 配置数据验证
7. 监控性能
8. 使用事务
9. 合理分片
10. 定期备份

## 八、总结

MongoDB 高级特性核心要点：
- 查询和更新操作符
- 索引（单字段、复合、文本、地理空间）
- 聚合管道
- 数据建模（嵌入 vs 引用）
- 数据验证
- 变更流
- 性能优化
- 事务
- 最佳实践

开始用 MongoDB 构建你的应用吧！
