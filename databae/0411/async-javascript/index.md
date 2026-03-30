# JavaScript 异步编程完全指南：Promise、async/await 与事件循环

> 深入讲解 JavaScript 异步编程，包括 Promise、async/await、事件循环、宏任务与微任务的原理与实践。

## 一、事件循环

### 1.1 执行机制

```
┌─────────────────────┐
│        Call Stack   │  ← 执行代码
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    MicroTask Queue  │  ← Promise、async
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    MacroTask Queue │  ← setTimeout、I/O
└─────────────────────┘
```

### 1.2 执行顺序

```javascript
console.log('1: 同步开始');

setTimeout(() => console.log('2: setTimeout'), 0);

Promise.resolve().then(() => console.log('3: Promise'));

async function asyncFn() {
  console.log('4: async start');
  await Promise.resolve();
  console.log('5: async end');
}

asyncFn();

console.log('6: 同步结束');

// 输出顺序:
// 1: 同步开始
// 4: async start
// 6: 同步结束
// 3: Promise
// 5: async end
// 2: setTimeout
```

## 二、Promise

### 2.1 创建 Promise

```javascript
const promise = new Promise((resolve, reject) => {
  const success = true;
  
  if (success) {
    resolve('成功!');
  } else {
    reject('失败!');
  }
});
```

### 2.2 then/catch/finally

```javascript
promise
  .then(result => {
    console.log(result);
    return result;
  })
  .catch(error => {
    console.error(error);
  })
  .finally(() => {
    console.log('完成');
  });
```

### 2.3 Promise 方法

```javascript
// all - 全部完成
Promise.all([p1, p2, p3])
  .then(([r1, r2, r3]) => console.log('全部成功'));

// race - 最先完成
Promise.race([p1, p2, p3])
  .then(result => console.log('最先完成'));

// allSettled - 全部结束
Promise.allSettled([p1, p2, p3])
  .then(results => {
    results.forEach(r => {
      if (r.status === 'fulfilled') console.log(r.value);
    });
  });

// any - 任意一个成功
Promise.any([p1, p2, p3])
  .then(result => console.log('任意一个成功'));
```

## 三、async/await

### 3.1 基本用法

```javascript
async function fetchData() {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('错误:', error);
  }
}
```

### 3.2 并行执行

```javascript
// 顺序执行 - 慢
const user = await fetchUser();
const posts = await fetchPosts();

// 并行执行 - 快
const [userRes, postsRes] = await Promise.all([
  fetchUser(),
  fetchPosts()
]);
```

### 3.3 错误处理

```javascript
async function fetchData() {
  try {
    const res = await fetch('/api/data');
    const data = await res.json();
    return data;
  } catch (err) {
    // 处理错误
    if (err instanceof TypeError) {
      console.log('网络错误');
    } else {
      console.log('其他错误');
    }
  }
}
```

## 四、宏任务与微任务

### 4.1 宏任务

```javascript
setTimeout(() => console.log('setTimeout'), 0);
setInterval(() => console.log('setInterval'), 0);
requestAnimationFrame(() => console.log('RAF'));
I/O 操作;
UI 渲染;
```

### 4.2 微任务

```javascript
Promise.then();
Promise.catch();
Promise.finally();
async/await;
queueMicrotask();
MutationObserver;
```

### 4.3 经典面试题

```javascript
console.log('1');

setTimeout(() => {
  console.log('2');
}, 0);

Promise.resolve().then(() => {
  console.log('3');
});

queueMicrotask(() => {
  console.log('4');
});

console.log('5');

// 1 → 5 → 3 → 4 → 2
```

## 五、async 函数返回值

### 5.1 返回 Promise

```javascript
async function fn() {
  return 'hello';
}

// 等价于
function fn() {
  return Promise.resolve('hello');
}
```

### 5.2 抛出错误

```javascript
async function fn() {
  throw new Error('错误');
}

// 等价于
function fn() {
  return Promise.reject(new Error('错误'));
}
```

## 六、实战案例

### 6.1 重试机制

```javascript
async function retry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === maxRetries - 1) throw err;
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
}

const data = await retry(() => fetch('/api/data'));
```

### 6.2 超时处理

```javascript
async function withTimeout(promise, ms) {
  const timeout = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('超时')), ms);
  });
  
  return Promise.race([promise, timeout]);
}
```

### 6.3 顺序执行任务

```javascript
async function sequential(tasks) {
  const results = [];
  
  for (const task of tasks) {
    const result = await task();
    results.push(result);
  }
  
  return results;
}
```

## 七、总结

异步编程核心要点：

1. **事件循环**：执行机制
2. **Promise**：异步处理对象
3. **async/await**：同步写法
4. **Promise.all/race**：组合多个 Promise
5. **宏任务**：setTimeout、I/O
6. **微任务**：Promise、async
7. **错误处理**：try/catch

掌握这些，异步编程不再难！

---

**推荐阅读**：
- [MDN 异步编程](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous)
- [事件循环详解](https://jakearchibald.com/2015/tasks-microtasks-queues-and-schedules/)

**如果对你有帮助，欢迎点赞收藏！**
