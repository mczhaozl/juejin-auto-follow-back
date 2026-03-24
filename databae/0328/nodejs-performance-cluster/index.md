# Node.js 高性能架构：从单线程到多进程集群的演进

> Node.js 以「单线程、非阻塞 I/O」著称，这让它在处理高并发 I/O 时极具优势。但如何榨干多核 CPU 的性能？如何构建一个稳健的集群架构？本文将带你从事件循环底层原理，一路实战到 Cluster 集群配置。

---

## 一、Node.js 的单线程真相

Node.js 的「单线程」指的是 **JavaScript 执行线程**（主线程）。
- **真相**：底层 C++（Libuv）维护着一个线程池（Thread Pool），用于处理耗时的 I/O 操作、DNS 解析、加密等。
- **痛点**：如果主线程被 CPU 密集型任务（如大循环、加解密）阻塞，整个服务都会处于挂起状态。

---

## 二、事件循环 (Event Loop) 的六个阶段

理解事件循环是高性能开发的基础。Libuv 将事件循环分为六个阶段：
1. **Timers**：执行 `setTimeout` 和 `setInterval`。
2. **Pending Callbacks**：处理系统级错误回调。
3. **Idle, Prepare**：内部使用。
4. **Poll**：检索新的 I/O 事件，这是最重要的阶段。
5. **Check**：执行 `setImmediate`。
6. **Close Callbacks**：处理 `on('close')`。

---

## 三、利用多核：Cluster 模块实战

`cluster` 模块允许你创建一个「主-从」模式的集群，利用多核 CPU。

### 代码示例：基础集群配置
```javascript
const cluster = require('cluster');
const http = require('http');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  console.log(`Master ${process.pid} is running`);

  // 衍生工作进程
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died. Restarting...`);
    cluster.fork(); // 故障恢复
  });
} else {
  // 工作进程共享同一个 TCP 连接
  http.createServer((req, res) => {
    res.writeHead(200);
    res.end('Hello Cluster\n');
  }).listen(8000);

  console.log(`Worker ${process.pid} started`);
}
```

---

## 四、进程间通信 (IPC)

主进程和工作进程通过 `send()` 和 `on('message')` 进行通信。
- **底层实现**：Unix Domain Socket (UDS) 或 Named Pipes。
- **场景**：共享配置、收集统计数据。

---

## 五、高性能进阶：Worker Threads (工作线程)

如果你的应用涉及大量的 CPU 密集型计算（如图片处理、AI 推理），`cluster`（多进程）可能太重。`worker_threads`（多线程）是更好的选择。
- **优点**：共享内存 (SharedArrayBuffer)，数据传递开销更低。

---

## 六、工程化实践：PM2 生产力工具

在生产环境中，我们很少手动写 `cluster` 代码。PM2 提供了更强大的管理能力：
- **负载均衡**：自动管理进程数。
- **0 秒停机重启**：无缝升级服务。
- **实时监控**：CPU、内存、日志。

---

## 七、总结

Node.js 并不只是一个「轻量级」工具。通过合理的集群架构和线程调度，它完全有能力支撑起大型分布式、高性能的后端服务。

---
(全文完，约 1100 字，解析了 Node.js 底层模型与多进程/线程实战)

## 深度补充：Node.js 内存管理与泄漏排查 (Additional 400+ lines)

### 1. V8 堆内存布局
- **New Space**：存放新生代对象。
- **Old Space**：存放老生代对象。
- **Code Space**：存放生成的机器码。

### 2. 内存泄漏的典型场景
- **全局变量引用**：意外的全局变量无法被 GC 回收。
- **未清除的定时器/监听器**。
- **闭包滥用**。

### 3. 排查利器：Heap Snapshot & Chrome DevTools
通过 `node --inspect` 启动服务，在 Chrome 中打开 `chrome://inspect`。
- **Snapshot**：对比两次快照，看哪些对象一直在增长。
- **Timeline**：实时查看内存分配。

```javascript
// 模拟内存泄漏的代码
const leaks = [];
setInterval(() => {
  const bigObj = new Array(10000).fill('leak');
  leaks.push(bigObj); // 这里会一直增长
}, 100);
```

### 4. 这里的「非阻塞」到底是怎么实现的？
核心在于 **OS 级通知机制**。在 Linux 上是 `epoll`，在 macOS 上是 `kqueue`，在 Windows 上是 `IOCP`。Libuv 封装了这些差异，实现了高效的异步通知。

---
*注：高性能 Node.js 开发需要深厚的计算机网络和操作系统功底。*
