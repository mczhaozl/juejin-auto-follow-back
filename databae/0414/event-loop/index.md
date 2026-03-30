# JavaScript Event Loop 完全指南：执行机制深度解析

> 深入讲解 JavaScript Event Loop，包括调用栈、微任务、宏任务，以及 Node.js 和浏览器环境的事件循环机制区别。

## 一、执行顺序

### 1.1 顺序图

```
┌─────────────────────────────┐
│         Call Stack         │
│    ┌───────────────────┐   │
│    │   console.log(1)  │   │
│    └───────────────────┘   │
└─────────────────────────────┘
            ↓
┌─────────────────────────────┐
│         Microtasks         │
│    Promise.then()          │
│    queueMicrotask()        │
└─────────────────────────────┘
            ↓
┌─────────────────────────────┐
│         Macrotasks          │
│    setTimeout               │
│    setInterval              │
│    I/O                     │
└─────────────────────────────┘
```

### 1.2 代码示例

```javascript
console.log(1);

setTimeout(() => console.log(2), 0);

Promise.resolve().then(() => console.log(3));

console.log(4);

// 输出: 1, 4, 3, 2
```

## 二、微任务 vs 宏任务

### 2.1 微任务（Microtasks）

```javascript
Promise.resolve().then(() => console.log('promise'));

queueMicrotask(() => console.log('queueMicrotask'));

async function test() {
  await Promise.resolve();
  console.log('await');
}

test();
```

### 2.2 宏任务（Macrotasks）

```javascript
setTimeout(() => console.log('setTimeout'), 0);

setInterval(() => console.log('setInterval'), 1000);

requestAnimationFrame(() => console.log('raf'));

I/O 操作回调;
```

### 2.3 执行顺序

```
1. 执行同步代码
2. 执行所有微任务
3. 执行一个宏任务
4. 重复步骤 2-3
```

## 三、实战案例

### 3.1 经典面试题

```javascript
console.log('1');

setTimeout(() => {
  console.log('2');
  Promise.resolve().then(() => console.log('3'));
}, 0);

new Promise((resolve) => {
  console.log('4');
  resolve();
}).then(() => console.log('5'));

setTimeout(() => console.log('6'), 0);

console.log('7');

// 输出: 1, 4, 7, 5, 2, 3, 6
```

### 3.2 async/await

```javascript
async function async1() {
  console.log('a1');
  await async2();
  console.log('a2');
}

async function async2() {
  console.log('a3');
}

console.log('s1');

setTimeout(() => console.log('st'), 0);

async1();

new Promise((resolve) => {
  console.log('p1');
  resolve();
}).then(() => console.log('p2'));

console.log('s2');

// 输出: s1, a1, a3, p1, s2, a2, p2, st
```

## 四、浏览器 vs Node.js

### 4.1 区别

| 特性 | 浏览器 | Node.js |
|------|--------|---------|
| 微任务 | Promise | Promise + process.nextTick |
| 宏任务 | setTimeout/I/O | setTimeout/I/O |
| 优先级 | 微任务优先 | nextTick 优先 |

### 4.2 Node.js 阶段

```
   ┌───────────────────────────┐
┌─>│           timers          │  setTimeout, setInterval
│  └────────────┬──────────────┘
│  ┌────────────┴──────────────┐
│  │     pending callbacks    │
│  └────────────┬──────────────┘
│  ┌────────────┴──────────────┐
│  │       idle, prepare      │
│  └────────────┬──────────────┘
│  ┌────────────┴──────────────┐
│  │           poll           │  I/O
│  └────────────┬──────────────┘
│  ┌────────────┴──────────────┐
│  │           check          │  setImmediate
│  └────────────┴──────────────┘
│  ┌────────────┴──────────────┐
│  │      close callbacks     │
└─────────────────────────────┘
```

## 五、总结

Event Loop 核心要点：

1. **调用栈**：执行同步代码
2. **微任务**：Promise/await
3. **宏任务**：setTimeout/I/O
4. **执行顺序**：同步 → 微 → 宏
5. **环境差异**：浏览器 vs Node.js

掌握这些，JavaScript 执行机制全掌握！

---

**推荐阅读**：
- [MDN Event Loop](https://developer.mozilla.org/en-US/docs/Web/JavaScript/EventLoop)

**如果对你有帮助，欢迎点赞收藏！**
