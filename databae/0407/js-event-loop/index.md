# 一文搞懂JavaScript事件循环：从原理到实践

> 深入解析JavaScript事件循环、宏任务与微任务的执行机制，通过实际案例帮助你彻底掌握异步编程的核心概念。

## 一、为什么需要事件循环

JavaScript是一门**单线程**语言，这意味着同一时刻只能执行一段代码。如果一段代码执行时间过长，就会阻塞后续代码的执行。

为了解决这个问题，JavaScript引入了**事件循环（Event Loop）**机制，实现非阻塞（non-blocking）异步编程。

## 二、事件循环的核心概念

### 2.1 执行栈与任务队列

```
┌─────────────────────────────────────┐
│            执行栈                     │
│      (Execution Context Stack)       │
│    代码同步执行的地方                  │
└─────────────────────────────────────┘
                ↑
                │ 执行完成
                ↓
┌─────────────────────────────────────┐
│           Web APIs                   │
│     (setTimeout, fetch, DOM)         │
└─────────────────────────────────────┘
                ↑
                │ 回调完成
                ↓
┌─────────────────────────────────────┐
│          任务队列                      │
│     (Task Queue / Callback Queue)   │
│   宏任务：setTimeout, setInterval    │
│   微任务：Promise, async/await        │
└─────────────────────────────────────┘
```

### 2.2 事件循环的工作流程

```javascript
console.log('1. 开始');

setTimeout(() => {
  console.log('2. setTimeout 回调');
}, 0);

Promise.resolve().then(() => {
  console.log('3. Promise 回调');
});

console.log('4. 结束');

// 输出顺序：1 -> 4 -> 3 -> 2
```

## 三、宏任务与微任务

### 3.1 宏任务（Macro Tasks）

| 来源 | 说明 |
|------|------|
| setTimeout | 定时器 |
| setInterval | 间隔定时器 |
| I/O | 文件读写、网络请求 |
| UI渲染 | 浏览器重绘/重排 |
| setImmediate | Node.js 特有 |

### 3.2 微任务（Micro Tasks）

| 来源 | 说明 |
|------|------|
| Promise | Promise 回调 |
| async/await | async 函数的隐式 Promise |
| MutationObserver | DOM 变化观察 |
| queueMicrotask | 队列微任务 |
| process.nextTick | Node.js 特有 |

### 3.3 执行顺序

```
┌──────────────────────────────────────┐
│         当前宏任务执行完毕             │
└──────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────┐
│         检查并执行所有微任务           │
│    (清空微任务队列)                   │
└──────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────┐
│     尝试进行 DOM 更新/渲染            │
│  (浏览器：requestAnimationFrame)    │
└──────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────┐
│       执行下一个宏任务                 │
└──────────────────────────────────────┘
```

## 四、经典案例分析

### 4.1 案例一：基础顺序

```javascript
console.log('1. 同步代码1');

setTimeout(() => {
  console.log('2. setTimeout');
}, 0);

Promise.resolve().then(() => {
  console.log('3. Promise.then');
});

console.log('4. 同步代码2');

// 执行顺序：
// 1. 同步代码1
// 4. 同步代码2
// 3. Promise.then (微任务)
// 2. setTimeout (宏任务)
```

### 4.2 案例二：嵌套Promise

```javascript
console.log('1. start');

Promise.resolve()
  .then(() => {
    console.log('2. then1');
    Promise.resolve()
      .then(() => {
        console.log('3. inner promise');
      });
  })
  .then(() => {
    console.log('4. then2');
  });

console.log('5. end');

// 1 -> 5 -> 2 -> 3 -> 4
```

### 4.3 案例三：async/await

```javascript
async function async1() {
  console.log('1. async1 start');
  await async2();
  console.log('2. async1 end');
}

async function async2() {
  console.log('3. async2');
}

console.log('4. script start');

setTimeout(() => {
  console.log('5. setTimeout');
}, 0);

async1();

new Promise((resolve) => {
  console.log('6. promise1');
  resolve();
}).then(() => {
  console.log('7. promise2');
});

console.log('8. script end');

// 执行顺序：
// 4 -> 1 -> 3 -> 6 -> 8 -> 7 -> 2 -> 5
```

### 4.4 案例四：综合演练

```javascript
console.log('1. start');

setTimeout(() => {
  console.log('2. timeout1');
  Promise.resolve().then(() => {
    console.log('3. promise in timeout');
  });
}, 0);

setTimeout(() => {
  console.log('4. timeout2');
}, 0);

Promise.resolve().then(() => {
  console.log('5. promise1');
});

Promise.resolve().then(() => {
  console.log('6. promise2');
});

console.log('7. end');

// 执行顺序：1 -> 7 -> 5 -> 6 -> 2 -> 3 -> 4
```

## 五、async/await 的原理

### 5.1 async/await 本质

`async/await` 是 Promise 的语法糖：

```javascript
// async 版本
async function fetchData() {
  const data = await fetch('/api/data');
  return data;
}

// 编译后的 Promise 版本
function fetchData() {
  return fetch('/api/data').then(data => data);
}
```

### 5.2 await 的执行时机

```javascript
async function test() {
  console.log('1. start');
  
  await console.log('2. await');
  
  console.log('3. after await');
}

test();
console.log('4. after call');

// 1 -> 2 -> 4 -> 3
```

**关键点**：`await` 后面的代码相当于 Promise 的 `.then()` 回调，会作为微任务执行。

## 六、常见面试题

### 6.1 面试题一

```javascript
async function async1() {
  console.log('1. async1 start');
  await async2();
  console.log('2. async1 end');
}

async function async2() {
  console.log('3. async2');
}

console.log('4. script start');
async1();
console.log('5. script end');

// 答案：4 -> 1 -> 3 -> 5 -> 2
```

### 6.2 面试题二

```javascript
setTimeout(() => {
  console.log('1. setTimeout');
}, 0);

new Promise((resolve) => {
  console.log('2. promise');
  resolve();
}).then(() => {
  console.log('3. promise then');
});

console.log('4. sync code');

// 答案：2 -> 4 -> 3 -> 1
```

## 七、实际应用建议

### 7.1 避免阻塞主线程

```javascript
// 不推荐：大量同步计算
function heavy() {
  let result = 0;
  for (let i = 0; i < 100000000; i++) {
    result += i;
  }
  return result;
}

// 推荐：使用 Web Worker
const worker = new Worker('worker.js');
worker.postMessage({ type: 'compute', data: 100000000 });
worker.onmessage = (e) => console.log(e.data);
```

### 7.2 合理利用微任务

```javascript
// 使用微任务确保 DOM 更新后执行
function updateAndLog() {
  document.body.innerHTML = '<div>Updated</div>';
  
  // 使用微任务
  queueMicrotask(() => {
    console.log('DOM 已更新');
  });
}
```

### 7.3 区分宏任务和微任务的使用场景

- **宏任务**：适合需要将执行推迟到下一个渲染帧的场景
- **微任务**：适合需要立即执行但不影响渲染的回调

## 八、总结

JavaScript 事件循环的核心要点：

1. **单线程**：JavaScript 同一时刻只能执行一段代码
2. **任务队列**：分为宏任务队列和微任务队列
3. **执行顺序**：同步代码 → 微任务 → 渲染 → 宏任务
4. **async/await**：本质是 Promise 的语法糖

理解事件循环对于解决异步编程问题、性能优化和面试准备都至关重要。

---

**推荐阅读**：
- [MDN 事件循环文档](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/EventLoop)
- [Philip Roberts: What the heck is the event loop?](https://www.youtube.com/watch?v=8aGhZQkoFbQ)

**如果对你有帮助，欢迎点赞收藏！**
