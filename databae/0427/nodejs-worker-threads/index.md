# Node.js Worker Threads 深度实战指南

> 深入理解 Node.js Worker Threads，掌握多线程编程，充分利用多核 CPU 提升性能。

## 一、Node.js 的单线程与多线程

Node.js 是单线程的，但通过 Worker Threads 可以实现真正的多线程编程。

### 1.1 为什么需要 Worker Threads

- CPU 密集型任务阻塞主线程
- 充分利用多核 CPU
- 并行处理提升性能
- 避免事件循环被阻塞

### 1.2 Worker Threads 与 Cluster 的区别

| 特性 | Worker Threads | Cluster |
|------|----------------|---------|
| 内存 | 共享内存 | 独立内存 |
| 通信 | MessageChannel | IPC |
| 适用场景 | CPU 密集型 | 网络请求 |

---

## 二、Worker Threads 基础

### 2.1 创建第一个 Worker

```javascript
// main.js
const { Worker } = require('worker_threads');
const path = require('path');

const worker = new Worker(path.join(__dirname, 'worker.js'));

worker.on('message', (message) => {
  console.log('收到消息:', message);
});

worker.on('error', (error) => {
  console.error('Worker 错误:', error);
});

worker.on('exit', (code) => {
  console.log('Worker 退出，代码:', code);
});

worker.postMessage('Hello Worker');
```

```javascript
// worker.js
const { parentPort } = require('worker_threads');

parentPort.on('message', (message) => {
  console.log('Worker 收到:', message);
  parentPort.postMessage('Hello Main');
});
```

### 2.2 内联 Worker 代码

```javascript
const { Worker } = require('worker_threads');

const workerCode = `
  const { parentPort } = require('worker_threads');
  parentPort.on('message', (msg) => {
    parentPort.postMessage(msg.toUpperCase());
  });
`;

const worker = new Worker(workerCode, { eval: true });

worker.postMessage('hello');
worker.on('message', (msg) => console.log(msg)); // HELLO
```

---

## 三、消息传递与通信

### 3.1 消息类型

```javascript
// 基本类型
worker.postMessage('string');
worker.postMessage(123);
worker.postMessage({ key: 'value' });
worker.postMessage([1, 2, 3]);

// 错误处理
try {
  worker.postMessage({ data: 'test' });
} catch (e) {
  console.error('发送失败:', e);
}
```

### 3.2 结构化克隆

```javascript
// 支持的类型
worker.postMessage({
  string: 'text',
  number: 123,
  boolean: true,
  null: null,
  object: { a: 1 },
  array: [1, 2, 3],
  date: new Date(),
  regex: /test/,
  map: new Map([['key', 'value']]),
  set: new Set([1, 2, 3])
});
```

### 3.3 MessageChannel

```javascript
const { Worker, MessageChannel } = require('worker_threads');

const { port1, port2 } = new MessageChannel();

const worker = new Worker('./worker.js', {
  workerData: { port: port2 },
  transferList: [port2]
});

port1.on('message', (msg) => console.log('Port1 收到:', msg));
port1.postMessage('Hello from Port1');
```

---

## 四、SharedArrayBuffer 共享内存

### 4.1 基础使用

```javascript
// main.js
const { Worker } = require('worker_threads');

const buffer = new SharedArrayBuffer(4);
const view = new Int32Array(buffer);

const worker = new Worker('./worker.js', {
  workerData: { buffer }
});

worker.on('message', () => {
  console.log('Main 读取:', view[0]);
});
```

```javascript
// worker.js
const { parentPort, workerData } = require('worker_threads');

const view = new Int32Array(workerData.buffer);
view[0] = 42;
parentPort.postMessage('done');
```

### 4.2 Atomics 原子操作

```javascript
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

if (isMainThread) {
  const buffer = new SharedArrayBuffer(4);
  const view = new Int32Array(buffer);
  
  const worker = new Worker(__filename, { workerData: { buffer } });
  
  for (let i = 0; i < 1000; i++) {
    Atomics.add(view, 0, 1);
  }
  
  worker.on('message', () => {
    console.log('最终值:', view[0]);
  });
} else {
  const view = new Int32Array(workerData.buffer);
  for (let i = 0; i < 1000; i++) {
    Atomics.add(view, 0, 1);
  }
  parentPort.postMessage('done');
}
```

---

## 五、实战案例一：CPU 密集型计算

### 5.1 斐波那契数列

```javascript
// main.js
const { Worker } = require('worker_threads');
const path = require('path');

function fibonacciInWorker(n) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(path.join(__dirname, 'fib-worker.js'), {
      workerData: n
    });
    
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker stopped with ${code}`));
    });
  });
}

// 使用
async function main() {
  console.time('fib');
  const result = await fibonacciInWorker(40);
  console.timeEnd('fib');
  console.log('结果:', result);
}

main();
```

```javascript
// fib-worker.js
const { parentPort, workerData } = require('worker_threads');

function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

parentPort.postMessage(fibonacci(workerData));
```

### 5.2 多 Worker 并行

```javascript
// 并行计算多个任务
async function parallelFibonacci(numbers) {
  const promises = numbers.map(n => fibonacciInWorker(n));
  return Promise.all(promises);
}

parallelFibonacci([35, 36, 37, 38]).then(results => {
  console.log('并行结果:', results);
});
```

---

## 六、实战案例二：图片处理

### 6.1 批量图片压缩

```javascript
// main.js
const { Worker } = require('worker_threads');
const fs = require('fs');
const path = require('path');

const imageFiles = fs.readdirSync('./images');

async function processImages(files) {
  const workers = files.map(file => {
    return new Promise((resolve) => {
      const worker = new Worker('./image-worker.js', {
        workerData: { file }
      });
      worker.on('message', resolve);
    });
  });
  
  return Promise.all(workers);
}

processImages(imageFiles).then(results => {
  console.log('处理完成:', results);
});
```

```javascript
// image-worker.js
const { parentPort, workerData } = require('worker_threads');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

async function processImage(file) {
  const inputPath = path.join('./images', file);
  const outputPath = path.join('./output', file);
  
  await sharp(inputPath)
    .resize(800, 600)
    .jpeg({ quality: 80 })
    .toFile(outputPath);
  
  return { file, status: 'done' };
}

processImage(workerData.file).then(result => {
  parentPort.postMessage(result);
});
```

---

## 七、Worker 池管理

### 7.1 简单的 Worker 池

```javascript
class WorkerPool {
  constructor(workerPath, poolSize = 4) {
    this.workerPath = workerPath;
    this.poolSize = poolSize;
    this.workers = [];
    this.taskQueue = [];
    this.init();
  }

  init() {
    for (let i = 0; i < this.poolSize; i++) {
      this.createWorker();
    }
  }

  createWorker() {
    const worker = new Worker(this.workerPath);
    worker.on('message', (result) => {
      const task = worker.currentTask;
      worker.currentTask = null;
      task.resolve(result);
      this.processNextTask(worker);
    });
    worker.on('error', (error) => {
      const task = worker.currentTask;
      worker.currentTask = null;
      task.reject(error);
      this.createWorker();
      this.processNextTask(worker);
    });
    this.workers.push(worker);
  }

  processNextTask(worker) {
    if (this.taskQueue.length > 0 && !worker.currentTask) {
      const task = this.taskQueue.shift();
      worker.currentTask = task;
      worker.postMessage(task.data);
    }
  }

  runTask(data) {
    return new Promise((resolve, reject) => {
      const task = { data, resolve, reject };
      const availableWorker = this.workers.find(w => !w.currentTask);
      
      if (availableWorker) {
        availableWorker.currentTask = task;
        availableWorker.postMessage(data);
      } else {
        this.taskQueue.push(task);
      }
    });
  }

  close() {
    this.workers.forEach(worker => worker.terminate());
  }
}
```

### 7.2 使用 Worker 池

```javascript
const pool = new WorkerPool('./worker.js', 4);

// 提交多个任务
const tasks = Array.from({ length: 10 }, (_, i) => i);
Promise.all(tasks.map(task => pool.runTask(task)))
  .then(results => {
    console.log('所有任务完成:', results);
    pool.close();
  });
```

---

## 八、错误处理与调试

### 8.1 错误处理

```javascript
// main.js
const worker = new Worker('./worker.js');

worker.on('error', (error) => {
  console.error('Worker 错误:', error);
  console.error('堆栈:', error.stack);
});

worker.on('exit', (code) => {
  if (code !== 0) {
    console.error(`Worker 异常退出，代码: ${code}`);
  }
});
```

### 8.2 调试 Worker

```javascript
// 使用 --inspect
node --inspect main.js

// 或者单独调试 Worker
const worker = new Worker('./worker.js', {
  execArgv: ['--inspect=9229']
});
```

---

## 九、性能优化

### 9.1 避免频繁创建 Worker

```javascript
// 不推荐：每次都创建新 Worker
async function badApproach() {
  for (let i = 0; i < 100; i++) {
    const worker = new Worker('./worker.js');
    // ...
    worker.terminate();
  }
}

// 推荐：使用 Worker 池
async function goodApproach() {
  const pool = new WorkerPool('./worker.js', 4);
  for (let i = 0; i < 100; i++) {
    await pool.runTask(i);
  }
  pool.close();
}
```

### 9.2 优化消息传递

```javascript
// 避免大对象复制
const buffer = new SharedArrayBuffer(1024);
// 使用 SharedArrayBuffer 代替复制大对象
```

---

## 十、最佳实践

1. **Worker 池**：避免频繁创建销毁
2. **SharedArrayBuffer**：大数据使用共享内存
3. **Atomics**：同步访问共享内存
4. **错误处理**：完善的错误监听
5. **合理使用**：只在 CPU 密集任务使用

---

## 十一、总结

Worker Threads 让 Node.js 可以充分利用多核 CPU，处理 CPU 密集型任务。掌握 Worker Threads，可以显著提升应用性能。

希望这篇文章对你有帮助！
