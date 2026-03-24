# 性能优化：如何通过 Web Workers 处理大批量数据计算以避免界面卡顿

> JavaScript 是单线程的，这就意味着复杂的计算会阻塞 UI 渲染，导致用户感到卡顿。本文将分享如何利用 Web Workers 实现多线程并行计算，彻底告别复杂的算法对主线程的影响。

## 一、场景：痛点在哪里？

假设你需要对 100 万条数据进行排序、加密或者复杂的统计分析。

```javascript
// 在主线程中执行
const start = performance.now();
const result = heavyComputation(data); // 假设耗时 3 秒
console.log('Done in', performance.now() - start);
```

**问题：** 
- **卡顿**：在这 3 秒内，用户无法点击按钮、无法滚动页面，浏览器甚至会弹出「页面未响应」。
- **掉帧**：动画效果会瞬间卡住。

## 二、方案：将计算任务搬到 Web Worker

Web Worker 允许你在后台线程中运行 JavaScript，不影响主线程的 UI 渲染。

### 1. 编写 Worker 文件 (worker.js)
```javascript
// worker.js
self.onmessage = function(e) {
  const { data } = e;
  // 执行耗时计算
  const result = heavyComputation(data);
  // 返回结果给主线程
  self.postMessage(result);
};

function heavyComputation(data) {
  // 复杂的排序/统计逻辑...
  return data.sort();
}
```

### 2. 在主线程中调用 (main.js)
```javascript
const worker = new Worker('worker.js');

worker.postMessage(largeData); // 发送数据给 Worker

worker.onmessage = function(e) {
  const result = e.data;
  console.log('Received result from worker:', result);
};

// 这时主线程依然是流畅的，你可以继续处理用户交互！
```

## 三、进阶：Transferable Objects (零拷贝传输)

默认情况下，`postMessage` 是通过结构化克隆（Structured Clone）传递数据的，如果数据量巨大，克隆本身也会耗时。

**优化方案：** 
利用 `ArrayBuffer` 的所有权转移，实现「零拷贝」。

```javascript
const buffer = new Uint8Array(1024 * 1024 * 10).buffer; // 10MB
// 第二个参数表示转移所有权
worker.postMessage(buffer, [buffer]);
// 此时主线程中的 buffer 变为空，Worker 获得了该内存区域！
```

## 四、工具推荐：Comlink

原生 Web Worker 的消息机制（`onmessage` / `postMessage`）写起来比较繁琐。Google 开源的 **Comlink** 可以让你像调用本地函数一样调用 Worker。

```javascript
import * as Comlink from 'comlink';

const worker = new Worker('worker.js');
const api = Comlink.wrap(worker);

const result = await api.heavyComputation(data);
```

## 五、总结

Web Workers 是前端处理计算密集型任务的终极利器。配合 Comlink，你可以在不增加太多开发成本的情况下，让你的应用响应速度翻倍。

**你是否在项目中使用过 Web Workers？欢迎分享你的实战案例！**
