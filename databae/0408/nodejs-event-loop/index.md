# Node.js 事件循环深度解析：从原理到实践，全面理解异步编程

> 深入讲解 Node.js 事件循环的各个阶段，微任务与宏任务的执行顺序，以及常见的异步编程模式与最佳实践。

## 一、为什么事件循环重要

Node.js 是单线程、非阻塞 I/O 模型，事件循环是其核心：

```javascript
console.log('1');

setTimeout(() => {
  console.log('2');
}, 0);

Promise.resolve().then(() => {
  console.log('3');
});

console.log('4');

// 输出顺序: 1, 4, 3, 2
```

理解事件循环，才能掌握异步代码的执行顺序。

## 二、事件循环阶段

### 2.1 六个主要阶段

```
   ┌───────────────────────────┐
   │   1. Timers (定时器)       │ ← setTimeout, setInterval
   └─────────────┬─────────────┘
                 ▼
   ┌───────────────────────────┐
   │ 2. Pending callbacks     │ ← I/O 回调
   └─────────────┬─────────────┘
                 ▼
   ┌───────────────────────────┐
   │ 3. Idle, prepare          │ ← 内部使用
   └─────────────┬─────────────┘
                 ▼
   ┌───────────────────────────┐
   │ 4. Poll (轮询)            │ ← 获取新 I/O 事件
   │                           │   处理 callbacks
   └─────────────┬─────────────┘
                 ▼
   ┌───────────────────────────┐
   │ 5. Check (检查)           │ ← setImmediate
   └─────────────┬─────────────┘
                 ▼
   ┌───────────────────────────┐
   │ 6. Close callbacks        │ ← socket.close
   └───────────────────────────┘
```

### 2.2 各阶段详解

**1. Timers 阶段**

```javascript
setTimeout(() => {
  console.log('timeout');
}, 0);

setImmediate(() => {
  console.log('immediate');
});

// 输出: timeout, immediate
```

**2. Poll 阶段**

```javascript
const fs = require('fs');

fs.readFile(__filename, () => {
  console.log('readFile callback');
});

setTimeout(() => {
  console.log('timeout');
}, 0);

// 输出: timeout, readFile callback
```

**3. Check 阶段**

```javascript
setImmediate(() => {
  console.log('check 1');
});

setTimeout(() => {
  console.log('timeout');
  process.nextTick(() => {
    console.log('nextTick in timeout');
  });
}, 0);

setImmediate(() => {
  console.log('check 2');
});

// 输出: timeout, nextTick in timeout, check 1, check 2
```

## 三、微任务 vs 宏任务

### 3.1 任务分类

| 类型 | 示例 |
|------|------|
| 宏任务 (MacroTask) | setTimeout, setImmediate, I/O, UI rendering |
| 微任务 (MicroTask) | Promise, process.nextTick, MutationObserver |

### 3.2 执行顺序

```javascript
console.log('1. start');

setTimeout(() => console.log('2. timeout'), 0);

Promise.resolve().then(() => console.log('3. promise'));

process.nextTick(() => console.log('4. nextTick'));

console.log('5. end');

// 输出顺序:
// 1. start
// 5. end
// 4. nextTick
// 3. promise
// 2. timeout
```

### 3.3 每个阶段之间执行微任务

```javascript
setTimeout(() => console.log('1. timeout'), 0);

new Promise((resolve) => {
  resolve();
}).then(() => console.log('2. promise'));

process.nextTick(() => console.log('3. nextTick'));

setTimeout(() => console.log('4. timeout2'), 0);

// 输出: 3, 2, 1, 4
```

## 四、process.nextTick vs setImmediate

### 4.1 nextTick

```javascript
process.nextTick(() => {
  console.log('nextTick');
});

// 在当前操作完成后、事件循环继续前执行
// 优先级高于其他微任务
```

### 4.2 setImmediate

```javascript
setImmediate(() => {
  console.log('immediate');
});

// 在 Check 阶段执行
// 紧跟 Poll 阶段之后
```

### 4.3 对比

```javascript
process.nextTick(() => console.log('nextTick'));
setImmediate(() => console.log('immediate'));

// 输出: nextTick, immediate
// nextTick 在每个阶段结束后立即执行
// setImmediate 在 Check 阶段执行
```

### 4.4 实际使用场景

**process.nextTick**:

```javascript
class MyEmitter {
  constructor() {
    this.events = {};
  }
  
  on(event, fn) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(fn);
    return this;
  }
  
  emit(event, ...args) {
    if (this.events[event]) {
      this.events[event].forEach(fn => fn(...args));
    }
    return this;
  }
}

// 确保回调在事件循环继续前执行
const myEmitter = new MyEmitter();
myEmitter.on('event', () => {
  console.log('emitted');
});
myEmitter.emit('event');
```

**setImmediate**:

```javascript
const fs = require('fs');

fs.readFile('file.txt', () => {
  setTimeout(() => console.log('timeout'), 0);
  setImmediate(() => console.log('immediate'));
});

// 输出: immediate, timeout
// setImmediate 比 setTimeout 先执行（在 I/O 回调中）
```

## 五、经典面试题

### 5.1 题目一

```javascript
console.log('1');

setTimeout(() => console.log('2'), 0);

Promise.resolve().then(() => {
  console.log('3');
  setTimeout(() => console.log('4'), 0);
});

setTimeout(() => console.log('5'), 0);

console.log('6');

// 答案: 1, 6, 3, 2, 5, 4
```

### 5.2 题目二

```javascript
async function async1() {
  console.log('1');
  await async2();
  console.log('2');
}

async function async2() {
  console.log('3');
}

console.log('4');

setTimeout(() => console.log('5'), 0);

async1();

new Promise((resolve) => {
  console.log('6');
  resolve();
}).then(() => console.log('7'));

console.log('8');

// 答案: 4, 1, 3, 6, 8, 2, 7, 5
```

### 5.3 题目三

```javascript
const p = new Promise((resolve) => {
  console.log('1');
  resolve();
});

p.then(() => {
  console.log('2');
});

console.log('3');

setTimeout(() => console.log('4'), 0);

// 答案: 1, 3, 2, 4
```

### 5.4 题目四

```javascript
console.log('1');

setTimeout(() => console.log('2'), 0);

new Promise((resolve, reject) => {
  console.log('3');
  reject();
}).catch(() => console.log('4'));

console.log('5');

// 答案: 1, 3, 5, 4, 2
```

## 六、异步编程最佳实践

### 6.1 使用 async/await

```javascript
// 避免回调地狱
async function fetchData() {
  try {
    const user = await getUser();
    const posts = await getPosts(user.id);
    const comments = await getComments(posts[0].id);
    return comments;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### 6.2 并发执行

```javascript
// 串行：慢
const user = await getUser(id);
const posts = await getPosts(user.id);

// 并发：快
const [user, posts] = await Promise.all([
  getUser(id),
  getPosts(user.id)
]);
```

### 6.3 错误处理

```javascript
// 正确处理异步错误
async function safeAsync(fn) {
  try {
    return [await fn(), null];
  } catch (error) {
    return [null, error];
  }
}

const [data, error] = await safeAsync(fetchData);
if (error) {
  console.error(error);
}
```

### 6.4 避免阻塞

```javascript
// 不好：阻塞事件循环
const bigData = JSON.parse(largeString);

// 好：分块处理
function parseInChunks(data) {
  let i = 0;
  function parse() {
    const chunk = data.slice(i, i + 10000);
    i += 10000;
    if (i < data.length) {
      setImmediate(parse);
    }
  }
  parse();
}
```

## 七、性能优化

### 7.1 减少 I/O 操作

```javascript
// 不好：多次 I/O
const user = await db.getUser(id);
const posts = await db.getPosts(user.id);

// 好：一次查询
const data = await db.query(`
  SELECT u.*, p.* 
  FROM users u 
  LEFT JOIN posts p ON u.id = p.user_id 
  WHERE u.id = ?
`, [id]);
```

### 7.2 使用流处理大文件

```javascript
const fs = require('fs');

const readStream = fs.createReadStream('big.txt');
const writeStream = fs.createWriteStream('output.txt');

readStream.on('data', (chunk) => {
  writeStream.write(chunk);
});

readStream.on('end', () => {
  console.log('Done');
});
```

### 7.3 连接池

```javascript
const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'password',
  database: 'test',
  connectionLimit: 10
});

// 使用连接池
const [rows] = await pool.query('SELECT * FROM users');
```

## 八、总结

Node.js 事件循环核心要点：

1. **六个阶段**：Timers → Pending → Idle → Poll → Check → Close
2. **微任务优先**：Promise, nextTick 在每个阶段后执行
3. **nextTick vs immediate**：nextTick 立即执行，immediate 在 Check 阶段
4. **异步模式**：async/await 是最佳实践
5. **性能优化**：减少阻塞、并发执行、连接池

掌握这些，你就能驾驭 Node.js 异步编程！

---

**推荐阅读**：
- [Node.js 官方文档 - 事件循环](https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick)
- [Philip Roberts: What the heck is the event loop?](https://www.youtube.com/watch?v=8aGhZQkoFbQ)

**如果对你有帮助，欢迎点赞收藏！**
