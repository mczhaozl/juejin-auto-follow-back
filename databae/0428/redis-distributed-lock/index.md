# Redis 分布式锁深度解析：从 SETNX 到 RedLock 算法

## 一、分布式锁概述

分布式锁用于在分布式环境下协调多个进程或节点对共享资源的访问。

### 1.1 为什么需要分布式锁

- 防止资源竞争
- 保证数据一致性
- 避免重复处理
- 控制并发访问

### 1.2 分布式锁要求

| 特性 | 描述 |
|-----|------|
| 互斥性 | 同一时间只有一个持有者 |
| 安全性 | 不会死锁 |
| 可用性 | 高可用 |
| 解铃还须系铃人 | 只有持有者能释放 |

---

## 二、基础实现

### 2.1 SETNX 实现

```javascript
// 简单的 SETNX 实现（有问题）
async function lock1(key, timeout = 10000) {
  const result = await redis.setnx(key, 1);
  if (result === 1) {
    await redis.pexpire(key, timeout);
    return true;
  }
  return false;
}

// 问题：如果 SETNX 之后 pexpire 之前崩溃，会导致死锁
```

### 2.2 原子操作 SET

```javascript
// 正确的基础实现（原子操作）
async function lock2(key, value, timeout = 10000) {
  // NX: 仅不存在时设置
  // PX: 过期时间毫秒
  const result = await redis.set(key, value, 'NX', 'PX', timeout);
  return result === 'OK';
}

async function unlock2(key, value) {
  // 使用 Lua 脚本保证原子性
  const script = `
    if redis.call("get", KEYS[1]) == ARGV[1] then
      return redis.call("del", KEYS[1])
    else
      return 0
    end
  `;
  const result = await redis.eval(script, 1, key, value);
  return result === 1;
}
```

---

## 三、完整实现

### 3.1 重试与回退

```javascript
const crypto = require('crypto');

class RedisLock {
  constructor(redisClient, options = {}) {
    this.redis = redisClient;
    this.retryDelay = options.retryDelay || 100;
    this.maxRetries = options.maxRetries || 10;
  }

  async acquire(key, timeout = 10000) {
    const value = crypto.randomUUID();
    let retries = 0;

    while (retries < this.maxRetries) {
      const ok = await this.redis.set(
        key,
        value,
        'NX',
        'PX',
        timeout
      );

      if (ok === 'OK') {
        return { ok: true, value, key };
      }

      retries++;
      await this.sleep(this.retryDelay * retries);
    }

    return { ok: false };
  }

  async release(lock) {
    if (!lock.ok) return;

    const script = `
      if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("DEL", KEYS[1])
      else
        return 0
      end
    `;

    await this.redis.eval(script, 1, lock.key, lock.value);
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### 3.2 使用示例

```javascript
const lock = new RedisLock(redis);

async function processResource(resourceId) {
  const key = `lock:resource:${resourceId}`;
  const acquireResult = await lock.acquire(key, 15000);

  if (!acquireResult.ok) {
    throw new Error('Failed to acquire lock');
  }

  try {
    // 业务逻辑
    await doSomeWork(resourceId);
  } finally {
    await lock.release(acquireResult);
  }
}
```

---

## 四、RedLock 算法

### 4.1 原理

在多个独立 Redis 实例上获取锁，大多数成功才算获取成功。

```javascript
class RedLock {
  constructor(instances, options = {}) {
    this.instances = instances;
    this.quorum = Math.floor(instances.length / 2) + 1;
    this.retryDelay = options.retryDelay || 200;
    this.driftFactor = options.driftFactor || 0.01;
  }

  async acquire(key, ttl = 10000) {
    const value = crypto.randomUUID();
    const startTime = Date.now();

    // 尝试从所有实例获取锁
    const promises = this.instances.map(
      redis => redis.set(key, value, 'NX', 'PX', ttl)
    );

    const results = await Promise.allSettled(promises);
    const successful = results.filter(r => r.value === 'OK').length;

    const drift = ttl * this.driftFactor + 2;
    const elapsed = Date.now() - startTime;
    const valid = elapsed < (ttl - drift);

    if (successful >= this.quorum && valid) {
      return { ok: true, value, key };
    }

    // 失败，释放所有锁
    await this.releaseAll(key, value);
    return { ok: false };
  }

  async releaseAll(key, value) {
    const script = `
      if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("DEL", KEYS[1])
      else
        return 0
      end
    `;

    const promises = this.instances.map(
      redis => redis.eval(script, 1, key, value)
    );
    await Promise.allSettled(promises);
  }
}
```

---

## 五、高级特性

### 5.1 锁续约/看门狗

```javascript
class RedisLockWithWatchdog extends RedisLock {
  async acquire(key, timeout = 10000) {
    const value = crypto.randomUUID();
    const ok = await this.redis.set(key, value, 'NX', 'PX', timeout);
    if (ok !== 'OK') return { ok: false };

    // 启动看门狗，自动续约
    const stop = this.startWatchdog(key, value, timeout);

    return {
      ok: true,
      value,
      key,
      stopWatchdog: stop
    };
  }

  startWatchdog(key, value, timeout) {
    const interval = Math.floor(timeout / 3);
    const timer = setInterval(async () => {
      try {
        await this.redis.pexpire(key, timeout);
      } catch {}
    }, interval);

    return () => clearInterval(timer);
  }

  async release(lock) {
    if (lock.stopWatchdog) lock.stopWatchdog();
    await super.release(lock);
  }
}
```

### 5.2 可重入锁

```javascript
class ReentrantRedisLock {
  constructor(redis) {
    this.redis = redis;
    this.localLocks = new Map();  // 线程本地计数
  }

  async acquire(key, timeout = 10000) {
    const localEntry = this.localLocks.get(key);

    if (localEntry) {
      localEntry.count++;
      return { ok: true, key, value: localEntry.value, local: true };
    }

    const value = crypto.randomUUID();
    const ok = await this.redis.set(key, value, 'NX', 'PX', timeout);

    if (ok === 'OK') {
      this.localLocks.set(key, { count: 1, value });
      return { ok: true, key, value };
    }

    return { ok: false };
  }

  async release(lock) {
    if (lock.local) {
      const entry = this.localLocks.get(lock.key);
      entry.count--;
      if (entry.count === 0) {
        this.localLocks.delete(lock.key);
        await this._releaseRemote(lock);
      }
      return;
    }

    await this._releaseRemote(lock);
  }

  async _releaseRemote(lock) {
    // 释放 Redis 锁（同之前）
  }
}
```

---

## 六、实际应用场景

### 6.1 任务调度防止重复执行

```javascript
async function scheduledJob(jobId) {
  const key = `lock:job:${jobId}`;
  const locker = new RedisLock(redis);
  const lockResult = await locker.acquire(key, 60000);

  if (!lockResult.ok) {
    console.log('Job already running');
    return;
  }

  try {
    console.log('Executing job');
    await executeJob(jobId);
  } finally {
    await locker.release(lockResult);
  }
}
```

### 6.2 秒杀库存扣减

```javascript
async function deductStock(productId, quantity) {
  const key = `lock:stock:${productId}`;
  const locker = new RedisLock(redis);
  const lockResult = await locker.acquire(key, 5000);

  if (!lockResult.ok) {
    throw new Error('System busy, please try again');
  }

  try {
    const stock = await db.getStock(productId);
    if (stock < quantity) {
      throw new Error('Insufficient stock');
    }
    await db.deductStock(productId, quantity);
  } finally {
    await locker.release(lockResult);
  }
}
```

---

## 七、最佳实践

1. **使用 SET NX PX 原子操作**
2. **Lua 脚本保证释放原子性**
3. **设置合理的超时时间**
4. **考虑锁续约机制**
5. **单个实例不足时使用 RedLock**
6. **监控锁获取情况**

---

## 八、总结

Redis 是实现分布式锁的常用方案，从简单的 SETNX 到完善的 RedLock 及看门狗机制，能满足不同场景需求。
