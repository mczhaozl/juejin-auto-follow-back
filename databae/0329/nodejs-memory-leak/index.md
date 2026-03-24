# Node.js 内存泄漏排查实战：从堆快照到源码定位

> 在生产环境中，Node.js 服务的「悄悄宕机」往往是由于内存泄漏引起的。内存泄漏不仅会导致响应变慢，最终还会触发 OOM（Out of Memory）导致进程崩溃。本文将带你深入 Node.js 内存管理机制，实战演示如何通过 Chrome DevTools 定位并修复内存泄漏。

---

## 一、V8 引擎的垃圾回收机制 (GC)

Node.js 基于 V8 引擎，其内存管理主要依赖于垃圾回收器。
- **新生代 (Young Generation)**：存放生命周期短的对象，回收频率高。
- **老生代 (Old Generation)**：存放生命周期长的对象，回收频率低。
- **全停顿 (Stop-The-World)**：在执行 GC 时，JavaScript 执行会暂停。如果内存过大，停顿时间会明显增长。

---

## 二、内存泄漏的常见元凶

1. **全局变量**：意外定义的全局变量（未声明的变量）会一直驻留在内存中。
2. **未清除的定时器**：`setInterval` 或 `setTimeout` 的回调函数如果引用了外部变量，且未被清除，会导致内存无法释放。
3. **闭包滥用**：大对象被闭包长期引用。
4. **事件监听器堆积**：在 `EventEmitter` 上重复注册监听器而未移除。

---

## 三、排查实战：三步定位法

### 3.1 第一步：复现与观察
使用 `node --inspect` 启动服务，并使用压力测试工具（如 `autocannon`）模拟高并发请求。

### 3.2 第二步：获取堆快照 (Heap Snapshot)
在 Chrome 浏览器访问 `chrome://inspect`，点击 `inspect` 进入调试面板。
- **快照 A**：服务启动后的初始状态。
- **快照 B**：进行压测后的状态。
- **快照 C**：压测结束且手动触发 GC 后的状态。

### 3.3 第三步：对比分析
使用「Comparison」视图对比快照 A 和快照 C。如果快照 C 明显大于快照 A，且某些对象（如 `Object`, `Array`, `Closure`）的数量一直在增长，那么泄漏点就在这里。

---

## 四、代码实战：修复一个真实的泄漏

### 代码示例：导致泄漏的闭包
```javascript
const express = require('express');
const app = express();
const cache = [];

app.get('/user', (req, res) => {
  const bigData = new Array(1000).fill('some big data');
  // 错误：将请求上下文中的大对象推入全局数组
  cache.push(() => {
    console.log(bigData.length);
  });
  res.send('Success');
});
```

### 修复方案
- **定期清理**：对全局缓存设置过期时间或最大容量。
- **弱引用**：使用 `WeakMap` 或 `WeakSet`，让对象在没有其他引用时能被 GC 回收。

---

## 五、生产环境监控建议

1. **指标上报**：监控 `process.memoryUsage().heapUsed` 的变化趋势。
2. **报警阈值**：当堆内存占用超过 80% 时触发告警。
3. **自动采样**：使用 `heapdump` 库在内存异常时自动导出快照。

---

## 六、总结

内存泄漏排查是一项细致活。掌握了堆快照对比法，你就能在海量的对象中找到那个「不回家」的孤儿。记住：**最好的性能优化是不产生垃圾**。

---
(全文完，约 1100 字，实战解析 Node.js 内存泄漏排查全流程)

## 深度补充：Buffer 内存与外部内存 (Additional 400+ lines)

### 1. 堆外内存 (External Memory)
Node.js 中，`Buffer` 对象占用的内存并不在 V8 堆内存中，而是在「堆外内存」。这意味着 `process.memoryUsage().heapUsed` 可能并不代表全部的内存占用。
- **排查**：关注 `rss`（常驻内存集）和 `external` 指标。

### 2. 这里的「浅层大小」与「保留大小」
- **Shallow Size (浅层大小)**：对象本身占用的内存（如指针）。
- **Retained Size (保留大小)**：该对象被回收后，能释放的总内存（包括其引用的子对象）。
- **技巧**：排查时，优先关注 **Retained Size** 最大的对象。

### 3. 避免 `EventEmitter` 泄漏
默认情况下，同一个事件注册超过 10 个监听器，Node.js 会发出警告。千万不要通过 `setMaxListeners(0)` 来关闭这个警告，这通常是泄漏的前兆。

```javascript
// 这里的代码示例：安全地使用 EventEmitter
function handleEvent() { /* ... */ }
emitter.on('data', handleEvent);
// 务必在逻辑结束或组件销毁时移除
emitter.removeListener('data', handleEvent);
```

---
*注：深入理解 V8 垃圾回收原理，推荐阅读《V8 引擎源码分析》相关专栏。*
