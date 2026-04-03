# Node.js 事件循环完全指南：深入理解 libuv 与异步机制

Node.js 的事件循环是其高性能的核心，理解它对于编写高效的 Node.js 应用至关重要。

## 一、事件循环简介

### 1. 什么是事件循环

```javascript
console.log('1');

setTimeout(() => {
  console.log('2');
}, 0);

Promise.resolve().then(() => {
  console.log('3');
});

console.log('4');

// 输出：1, 4, 3, 2
```

### 2. 为什么需要事件循环

Node.js 是单线程的，但通过事件循环可以处理大量并发连接。

## 二、事件循环的阶段

```
   ┌───────────────────────────┐
┌─>│           timers          │
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │     pending callbacks     │
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │       idle, prepare       │
│  └─────────────┬─────────────┘      ┌───────────────┐
│  ┌─────────────┴─────────────┐      │   incoming:   │
│  │           poll            │<─────┤  connections, │
│  └─────────────┬─────────────┘      │   data, etc.  │
│  ┌─────────────┴─────────────┐      └───────────────┘
│  │           check           │
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
└──┤      close callbacks      │
   └───────────────────────────┘
```

### 1. Timers 阶段

```javascript
setTimeout(() => {
  console.log('timeout');
}, 100);

setInterval(() => {
  console.log('interval');
}, 1000);
```

### 2. Pending Callbacks 阶段

执行一些系统操作的回调，如 TCP 错误。

### 3. Poll 阶段

获取新的 I/O 事件，Node.js 会在这里阻塞。

### 4. Check 阶段

执行 setImmediate() 的回调。

```javascript
setImmediate(() => {
  console.log('immediate');
});
```

### 5. Close Callbacks 阶段

执行 close 事件的回调。

## 三、微任务与宏任务

### 1. 微任务

```javascript
Promise.resolve().then(() => {
  console.log('microtask 1');
});

process.nextTick(() => {
  console.log('nextTick');
});

Promise.resolve().then(() => {
  console.log('microtask 2');
});
```

### 2. 宏任务

```javascript
setTimeout(() => {
  console.log('macrotask 1');
}, 0);

setImmediate(() => {
  console.log('macrotask 2');
});
```

### 3. 执行顺序

```javascript
console.log('1');

setTimeout(() => console.log('2'), 0);

Promise.resolve().then(() => console.log('3'));

process.nextTick(() => console.log('4'));

setImmediate(() => console.log('5'));

console.log('6');

// 输出：1, 6, 4, 3, 2, 5
```

## 四、实战案例

### 1. 防止阻塞事件循环

```javascript
// ❌ 会阻塞事件循环
function badBlockingOperation() {
  for (let i = 0; i < 1e9; i++) {
    // 大量计算
  }
}

// ✅ 使用 setImmediate 分块处理
function goodAsyncOperation(cb, i = 0) {
  if (i >= 1e6) {
    cb();
    return;
  }
  
  for (let j = 0; j < 1000; j++, i++) {
    // 处理一块
  }
  
  setImmediate(() => goodAsyncOperation(cb, i));
}
```

### 2. 使用 Worker Threads

```javascript
const { Worker, isMainThread, parentPort } = require('worker_threads');

if (isMainThread) {
  const worker = new Worker(__filename);
  worker.on('message', (result) => {
    console.log('Result:', result);
  });
  worker.postMessage({ data: 'heavy computation' });
} else {
  parentPort.on('message', (task) => {
    const result = heavyComputation(task.data);
    parentPort.postMessage(result);
  });
}
```

## 五、监控与调试

### 1. event-loop-delay

```javascript
const { monitorEventLoopDelay } = require('perf_hooks');

const histogram = monitorEventLoopDelay();
histogram.enable();

setInterval(() => {
  console.log('Event loop delay:', histogram.mean);
  histogram.reset();
}, 1000);
```

### 2. Chrome DevTools

使用 `--inspect` 启动，在 Chrome 中调试。

## 六、最佳实践

1. 不要在主线程做 CPU 密集型任务
2. 使用流处理大文件
3. 合理使用缓存
4. 监控事件循环延迟

## 七、总结

理解 Node.js 事件循环是写出高性能应用的关键：
- 掌握各阶段的执行顺序
- 区分微任务和宏任务
- 避免阻塞事件循环
- 合理使用异步 API

掌握事件循环，让你的 Node.js 应用飞起来！
