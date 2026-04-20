# MongoDB 事务与并发控制完全指南：从单文档到分布式事务

## 一、MongoDB 事务概述

### 1.1 事务的发展历程

MongoDB 的事务支持经历了从无到有、从简单到复杂的演进过程。

- **3.x 及之前**：仅支持单文档原子操作
- **4.0**：引入多文档事务（副本集）
- **4.2**：支持分布式事务（分片集群）
- **5.0+**：事务性能优化，快照读

### 1.2 ACID 特性

MongoDB 事务支持完整的 ACID 特性：

| 特性 | 说明 |
|------|------|
| **原子性（Atomicity）** | 事务内所有操作要么全部成功，要么全部回滚 |
| **一致性（Consistency）** | 事务将数据库从一个一致状态转换到另一个一致状态 |
| **隔离性（Isolation）** | 并发事务互不干扰 |
| **持久性（Durability）** | 事务提交后，变更永久保存 |

---

## 二、单文档原子操作

### 2.1 原子操作基础

MongoDB 对单文档的所有写操作都是原子的。

```javascript
db.collection.updateOne(
  { _id: 1 },
  {
    $inc: { count: 1 },
    $set: { status: "updated" }
  }
);
```

### 2.2 findAndModify 原子操作

```javascript
const result = db.collection.findAndModify({
  query: { _id: 1, status: "pending" },
  update: { $set: { status: "processing" } },
  new: true,
  upsert: false
});
```

### 2.3 原子更新操作符

```javascript
// $inc 原子递增
db.products.updateOne(
  { _id: 1 },
  { $inc: { stock: -1, sold: 1 } }
);

// $addToSet 原子添加到集合
db.users.updateOne(
  { _id: 1 },
  { $addToSet: { roles: "admin" } }
);

// $push + $each 原子批量添加
db.orders.updateOne(
  { _id: 1 },
  { $push: { items: { $each: ["a", "b", "c"] } } }
);

// 乐观锁模式
function updateWithOptimisticLock(id, data, version) {
  const result = db.collection.updateOne(
    { _id: id, version: version },
    {
      $set: data,
      $inc: { version: 1 }
    }
  );
  
  if (result.modifiedCount === 0) {
    throw new Error("Concurrent modification detected");
  }
  
  return result;
}
```

---

## 三、副本集多文档事务

### 3.1 启动会话与事务

```javascript
const session = db.getMongo().startSession();
session.startTransaction();

try {
  const collection = session.getDatabase("test").getCollection("orders");
  
  collection.updateOne(
    { _id: 1 },
    { $set: { status: "paid" } }
  );
  
  collection.updateOne(
    { _id: 2 },
    { $inc: { balance: -100 } }
  );
  
  session.commitTransaction();
} catch (error) {
  session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

### 3.2 事务选项配置

```javascript
session.startTransaction({
  readConcern: { level: "snapshot" },
  writeConcern: { w: "majority", j: true },
  readPreference: "primary",
  maxCommitTimeMS: 5000
});
```

### 3.3 事务与隔离级别

```javascript
// snapshot 隔离级别（默认）
session.startTransaction({
  readConcern: { level: "snapshot" }
});

// local 隔离级别
session.startTransaction({
  readConcern: { level: "local" }
});

// majority 隔离级别
session.startTransaction({
  readConcern: { level: "majority" }
});
```

### 3.4 转账事务实战

```javascript
async function transfer(fromAccount, toAccount, amount) {
  const session = db.getMongo().startSession();
  
  try {
    session.startTransaction({
      readConcern: { level: "snapshot" },
      writeConcern: { w: "majority" }
    });
    
    const accounts = session.getDatabase("bank").getCollection("accounts");
    
    const fromResult = accounts.updateOne(
      { _id: fromAccount, balance: { $gte: amount } },
      { $inc: { balance: -amount } }
    );
    
    if (fromResult.modifiedCount === 0) {
      throw new Error("Insufficient balance or account not found");
    }
    
    accounts.updateOne(
      { _id: toAccount },
      { $inc: { balance: amount } }
    );
    
    accounts.insertOne({
      type: "transfer",
      from: fromAccount,
      to: toAccount,
      amount: amount,
      timestamp: new Date()
    });
    
    session.commitTransaction();
    console.log("Transfer completed successfully");
  } catch (error) {
    session.abortTransaction();
    console.error("Transaction aborted:", error);
    throw error;
  } finally {
    session.endSession();
  }
}

transfer("alice", "bob", 100);
```

### 3.5 购物车结账事务

```javascript
async function checkout(userId, cartItems) {
  const session = db.getMongo().startSession();
  
  try {
    session.startTransaction({
      readConcern: { level: "snapshot" },
      writeConcern: { w: "majority" }
    });
    
    const db = session.getDatabase("ecommerce");
    const products = db.getCollection("products");
    const orders = db.getCollection("orders");
    const cart = db.getCollection("cart");
    
    let totalAmount = 0;
    const orderItems = [];
    
    for (const item of cartItems) {
      const product = products.findOneAndUpdate(
        { _id: item.productId, stock: { $gte: item.quantity } },
        { $inc: { stock: -item.quantity } }
      );
      
      if (!product.value) {
        throw new Error(`Product ${item.productId} out of stock`);
      }
      
      totalAmount += product.value.price * item.quantity;
      orderItems.push({
        productId: item.productId,
        quantity: item.quantity,
        price: product.value.price
      });
    }
    
    const order = {
      userId: userId,
      items: orderItems,
      totalAmount: totalAmount,
      status: "placed",
      createdAt: new Date()
    };
    
    orders.insertOne(order);
    
    cart.deleteOne({ userId: userId });
    
    session.commitTransaction();
    return order;
  } catch (error) {
    session.abortTransaction();
    throw error;
  } finally {
    session.endSession();
  }
}
```

---

## 四、分布式事务

### 4.1 分片集群事务

```javascript
const session = db.getMongo().startSession();

try {
  session.startTransaction({
    readConcern: { level: "snapshot" },
    writeConcern: { w: "majority" }
  });
  
  const db = session.getDatabase("ecommerce");
  
  db.getCollection("users").updateOne(
    { _id: 1 },
    { $set: { status: "premium" } }
  );
  
  db.getCollection("orders").updateMany(
    { userId: 1 },
    { $set: { discount: 0.1 } }
  );
  
  session.commitTransaction();
} catch (error) {
  session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

### 4.2 跨分片事务

```javascript
async function crossShardTransaction() {
  const session = db.getMongo().startSession();
  
  try {
    session.startTransaction();
    
    const db = session.getDatabase("global");
    
    db.getCollection("europe_orders").insertOne({
      _id: "order_eu_001",
      product: "laptop",
      quantity: 5
    });
    
    db.getCollection("us_orders").insertOne({
      _id: "order_us_001",
      product: "phone",
      quantity: 10
    });
    
    db.getCollection("asia_orders").insertOne({
      _id: "order_as_001",
      product: "tablet",
      quantity: 15
    });
    
    session.commitTransaction();
  } catch (error) {
    session.abortTransaction();
    throw error;
  } finally {
    session.endSession();
  }
}
```

---

## 五、并发控制机制

### 5.1 乐观锁模式

```javascript
async function updateWithOptimisticLock(collection, query, update) {
  let retries = 3;
  let lastError;
  
  while (retries > 0) {
    try {
      const doc = collection.findOne(query);
      if (!doc) {
        throw new Error("Document not found");
      }
      
      const currentVersion = doc.version || 0;
      const result = collection.updateOne(
        { ...query, version: currentVersion },
        {
          ...update,
          $inc: { version: 1 }
        }
      );
      
      if (result.modifiedCount === 1) {
        return result;
      }
      
      retries--;
      await new Promise(resolve => setTimeout(resolve, 100));
    } catch (error) {
      lastError = error;
      retries--;
    }
  }
  
  throw lastError || new Error("Update failed after retries");
}

updateWithOptimisticLock(
  db.products,
  { _id: 1 },
  { $set: { price: 99.99 } }
);
```

### 5.2 悲观锁（分布式锁）

```javascript
class DistributedLock {
  constructor(collection, lockKey) {
    this.collection = collection;
    this.lockKey = lockKey;
    this.lockId = null;
  }
  
  async acquire(ttl = 5000) {
    this.lockId = Math.random().toString(36).substr(2, 9);
    const lock = await this.collection.findOneAndUpdate(
      { _id: this.lockKey },
      {
        $setOnInsert: {
          lockId: this.lockId,
          createdAt: new Date(),
          expiresAt: new Date(Date.now() + ttl)
        }
      },
      { upsert: true, returnDocument: "after" }
    );
    
    if (lock.value.lockId !== this.lockId) {
      throw new Error("Failed to acquire lock");
    }
    
    return true;
  }
  
  async release() {
    await this.collection.deleteOne({
      _id: this.lockKey,
      lockId: this.lockId
    });
  }
}

const lock = new DistributedLock(db.locks, "resource:123");

async function withLock(fn) {
  await lock.acquire();
  try {
    return await fn();
  } finally {
    await lock.release();
  }
}

await withLock(async () => {
  db.accounts.updateOne({ _id: 1 }, { $inc: { balance: 100 } });
  db.accounts.updateOne({ _id: 2 }, { $inc: { balance: -100 } });
});
```

### 5.3 读写冲突处理

```javascript
async function transactionWithRetry() {
  const session = db.getMongo().startSession();
  let retries = 3;
  
  while (retries > 0) {
    try {
      session.startTransaction();
      
      const db = session.getDatabase("test");
      db.collection.updateOne({ _id: 1 }, { $inc: { counter: 1 } });
      
      session.commitTransaction();
      return;
    } catch (error) {
      if (error.errorLabels?.includes("TransientTransactionError") && retries > 1) {
        retries--;
        await new Promise(resolve => setTimeout(resolve, 100));
        continue;
      }
      session.abortTransaction();
      throw error;
    } finally {
      session.endSession();
    }
  }
}
```

---

## 六、事务监控与诊断

### 6.1 事务状态查询

```javascript
db.currentOp({"active": true, "lsid": {$exists: true}});
db.adminCommand({currentOp: 1, active: true, transaction: true});
```

### 6.2 慢事务分析

```javascript
db.setProfilingLevel(1, { slowms: 100 });
db.system.profile.find({ "transaction": { $exists: true } }).sort({ ts: -1 });
```

### 6.3 事务最佳实践

```javascript
const session = db.getMongo().startSession();

try {
  session.startTransaction({
    readConcern: { level: "snapshot" },
    writeConcern: { w: "majority", j: true },
    maxCommitTimeMS: 10000
  });
  
  const result = performTransactionOperations(session);
  session.commitTransaction();
  return result;
} catch (error) {
  if (error.errorLabels?.includes("UnknownTransactionCommitResult")) {
    return retryCommitTransaction(session);
  }
  session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

---

## 七、事务限制与注意事项

### 7.1 事务时间限制

- 默认事务超时：60秒
- 单个事务操作数上限：1000个
- 单个事务修改文档大小：16MB

### 7.2 不支持事务的操作

```javascript
// 以下操作不能在事务中执行
// db.createCollection()
// db.createIndex()
// db.dropDatabase()
// db.dropCollection()
// db.collection.drop()
```

### 7.3 事务性能优化

```javascript
// 1. 保持事务简短
// 2. 使用合适的读写关注级别
// 3. 避免在事务中执行耗时操作
// 4. 使用批量操作减少事务大小
// 5. 合理设置事务超时时间
```

---

## 总结

MongoDB 事务提供了从单文档原子操作到分布式事务的完整解决方案。通过合理使用事务，可以确保数据的一致性和可靠性，但需要注意事务的限制和性能考虑。
