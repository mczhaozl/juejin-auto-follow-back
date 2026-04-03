# Node.js 性能调优完全实战指南

Node.js 性能调优是构建高性能应用的关键。本文将带你从基础监控到深度优化，全面提升 Node.js 应用性能。

## 一、性能监控

### 1. 内置工具

```javascript
// process.memoryUsage()
console.log(process.memoryUsage());
// {
//   rss: 4935680,
//   heapTotal: 1826816,
//   heapUsed: 650472,
//   external: 49879,
//   arrayBuffers: 9386
// }

// process.cpuUsage()
const startUsage = process.cpuUsage();
// 执行一些操作
const endUsage = process.cpuUsage(startUsage);
console.log('CPU usage:', endUsage);

// process.hrtime()
const start = process.hrtime();
// 执行操作
const [sec, nanosec] = process.hrtime(start);
console.log(`Time: ${sec}s ${nanosec / 1e6}ms`);
```

### 2. console.time

```javascript
console.time('loop');
for (let i = 0; i < 1000000; i++) {
  // do something
}
console.timeEnd('loop'); // loop: 12.345ms
```

### 3. Performance API

```javascript
const { performance, PerformanceObserver } = require('perf_hooks');

// 测量函数执行时间
function measure(fn) {
  const start = performance.now();
  fn();
  const end = performance.now();
  console.log(`Took ${end - start}ms`);
}

// PerformanceObserver
const obs = new PerformanceObserver((list) => {
  console.log(list.getEntries()[0]);
});
obs.observe({ entryTypes: ['measure'] });

performance.mark('A');
// do something
performance.mark('B');
performance.measure('A to B', 'A', 'B');
```

### 4. 监控工具

```bash
# 安装 clinic.js
npm install -g clinic

# 运行
clinic doctor -- node app.js
clinic flame -- node app.js
clinic bubbleprof -- node app.js

# 0x
npm install -g 0x
0x app.js

# Chrome DevTools
node --inspect app.js
# 打开 chrome://inspect
```

## 二、事件循环优化

### 1. 避免阻塞事件循环

```javascript
// ❌ 不好：同步操作阻塞事件循环
const fs = require('fs');
const data = fs.readFileSync('large-file.txt');

// ✅ 好：使用异步操作
const fs = require('fs').promises;
async function readFile() {
  const data = await fs.readFile('large-file.txt');
  return data;
}

// ❌ 不好：大量同步计算
function heavyComputation() {
  for (let i = 0; i < 1e9; i++) {
    // ...
  }
}

// ✅ 好：分块处理
async function heavyComputation() {
  const chunks = 10;
  const chunkSize = 1e8;
  
  for (let i = 0; i < chunks; i++) {
    for (let j = 0; j < chunkSize; j++) {
      // ...
    }
    await setImmediate();
  }
}
```

### 2. 使用 Worker Threads

```javascript
// main.js
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

if (isMainThread) {
  const worker = new Worker(__filename, {
    workerData: { data: [1, 2, 3, 4, 5] }
  });
  
  worker.on('message', (result) => {
    console.log('Result:', result);
  });
  
  worker.on('error', (error) => {
    console.error('Worker error:', error);
  });
} else {
  const result = workerData.data.map(x => x * 2);
  parentPort.postMessage(result);
}

// 使用 workerpool
const WorkerPool = require('workerpool');
const pool = WorkerPool.pool();

pool.exec((a, b) => a + b, [1, 2])
  .then(result => console.log(result))
  .then(() => pool.terminate());
```

### 3. setImmediate vs process.nextTick

```javascript
console.log('1');

process.nextTick(() => {
  console.log('2');
});

setImmediate(() => {
  console.log('3');
});

console.log('4');
// 输出: 1, 4, 2, 3

// process.nextTick 在当前阶段结束后立即执行
// setImmediate 在 check 阶段执行
```

## 三、内存优化

### 1. 避免内存泄漏

```javascript
// ❌ 不好：全局变量导致内存泄漏
let cache = {};

function addToCache(key, value) {
  cache[key] = value;
}

// ✅ 好：使用 LRU 缓存
const LRU = require('lru-cache');
const cache = new LRU({
  max: 500,
  ttl: 1000 * 60 * 60
});

function addToCache(key, value) {
  cache.set(key, value);
}

// ❌ 不好：闭包导致的泄漏
let leak;
function outer() {
  const largeData = new Array(1e6).fill('x');
  leak = function() {
    return largeData;
  };
}
outer();

// ✅ 好：避免不必要的闭包
function outer() {
  const largeData = new Array(1e6).fill('x');
  return function() {
    // 只保留需要的数据
  };
}
```

### 2. 流处理大文件

```javascript
// ❌ 不好：一次性读取大文件
const fs = require('fs');
const data = fs.readFileSync('large-file.txt', 'utf8');

// ✅ 好：使用流
const fs = require('fs');
const readline = require('readline');

const rl = readline.createInterface({
  input: fs.createReadStream('large-file.txt'),
  crlfDelay: Infinity
});

rl.on('line', (line) => {
  console.log(`Line: ${line}`);
});

// pipeline 处理
const { pipeline } = require('stream/promises');
const zlib = require('zlib');

async function compress() {
  await pipeline(
    fs.createReadStream('large-file.txt'),
    zlib.createGzip(),
    fs.createWriteStream('large-file.txt.gz')
  );
}
```

### 3. Buffer 使用

```javascript
// 使用 Buffer 而非字符串
const buf = Buffer.alloc(1024);
fs.read(fd, buf, 0, buf.length, 0, (err, bytes) => {
  console.log(buf.toString('utf8', 0, bytes));
});

// Buffer.from
const buf1 = Buffer.from('hello');
const buf2 = Buffer.from([0x68, 0x65, 0x6c, 0x6c, 0x6f]);
```

## 四、异步优化

### 1. Promise.all 并行执行

```javascript
// ❌ 不好：串行执行
async function fetchSerial() {
  const user = await fetchUser();
  const posts = await fetchPosts();
  const comments = await fetchComments();
  return { user, posts, comments };
}

// ✅ 好：并行执行
async function fetchParallel() {
  const [user, posts, comments] = await Promise.all([
    fetchUser(),
    fetchPosts(),
    fetchComments()
  ]);
  return { user, posts, comments };
}

// Promise.allSettled
async function fetchAllSettled() {
  const results = await Promise.allSettled([
    fetchUser(),
    fetchPosts(),
    fetchComments()
  ]);
  
  const successful = results
    .filter(r => r.status === 'fulfilled')
    .map(r => r.value);
    
  return successful;
}
```

### 2. 连接池

```javascript
// 数据库连接池
const { Pool } = require('pg');

const pool = new Pool({
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});

async function query(text, params) {
  const client = await pool.connect();
  try {
    return await client.query(text, params);
  } finally {
    client.release();
  }
}

// HTTP 代理
const http = require('http');
const agent = new http.Agent({
  keepAlive: true,
  maxSockets: 50
});

const options = {
  hostname: 'example.com',
  port: 80,
  path: '/',
  agent: agent
};

http.request(options, (res) => {
  // ...
}).end();
```

## 五、代码优化

### 1. 算法优化

```javascript
// ❌ 不好：O(n²)
function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}

// ✅ 好：O(n)
function findDuplicates(arr) {
  const seen = new Set();
  const duplicates = new Set();
  
  for (const item of arr) {
    if (seen.has(item)) {
      duplicates.add(item);
    } else {
      seen.add(item);
    }
  }
  
  return Array.from(duplicates);
}
```

### 2. 对象访问优化

```javascript
// 避免深层嵌套
const user = {
  address: {
    street: {
      name: 'Main St'
    }
  }
};

// ❌ 不好
const streetName = user && user.address && user.address.street && user.address.street.name;

// ✅ 好
const streetName = user?.address?.street?.name;

// 缓存对象属性
function processUsers(users) {
  const results = [];
  for (let i = 0; i < users.length; i++) {
    const user = users[i];
    results.push({
      id: user.id,
      name: user.name
    });
  }
  return results;
}
```

## 六、生产环境优化

### 1. 集群模式

```javascript
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  console.log(`Master ${process.pid} is running`);
  
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died`);
    cluster.fork();
  });
} else {
  const express = require('express');
  const app = express();
  
  app.get('/', (req, res) => {
    res.send('Hello from Worker ' + process.pid);
  });
  
  app.listen(3000);
  console.log(`Worker ${process.pid} started`);
}

// 使用 PM2
npm install -g pm2
pm2 start app.js -i max
pm2 monit
pm2 logs
```

### 2. 环境变量

```javascript
// 使用 dotenv
require('dotenv').config();

const config = {
  port: process.env.PORT || 3000,
  database: {
    host: process.env.DB_HOST,
    port: process.env.DB_PORT
  }
};

// 环境区分
const NODE_ENV = process.env.NODE_ENV || 'development';

if (NODE_ENV === 'production') {
  // 生产环境配置
} else if (NODE_ENV === 'test') {
  // 测试环境配置
} else {
  // 开发环境配置
}
```

## 七、最佳实践

1. 始终使用异步 I/O
2. 避免阻塞事件循环
3. 使用 Worker Threads 处理 CPU 密集型任务
4. 使用流处理大文件
5. 并行执行 Promise
6. 使用连接池
7. 监控内存和 CPU 使用
8. 避免内存泄漏
9. 使用集群模式
10. 生产环境使用 PM2

## 八、总结

Node.js 性能调优核心要点：
- 性能监控（clinic、0x、Chrome DevTools）
- 事件循环优化（避免阻塞）
- 内存优化（流、Buffer、LRU 缓存）
- 异步优化（Promise.all、连接池）
- 代码优化（算法、对象访问）
- 生产环境优化（集群、PM2）

开始优化你的 Node.js 应用吧！
