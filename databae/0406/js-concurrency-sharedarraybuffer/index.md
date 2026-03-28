# SharedArrayBuffer 与 Atomics：JS 多线程高性能并发实战

> 在高性能 Web 应用中，主线程的瓶颈一直是开发者难以逾越的鸿沟。本文将带你深度实战 SharedArrayBuffer 与 Atomics API，看它们如何打破 Web Worker 间的数据隔离，实现真正的多线程并发与无锁同步。

---

## 目录 (Outline)
- [一、 JS 的「并发困境」：为什么普通的 Web Worker 还不够快？](#一-js-的并发困境为什么普通的-web-worker-还不够快)
- [二、 SharedArrayBuffer：打破内存隔离的「任意门」](#二-sharedarraybuffer打破内存隔离的任意门)
- [三、 Atomics API：多线程环境下的「交通警察」](#三-atomics-api多线程环境下的交通警察)
- [四、 快速上手：构建一个简单的多线程计数器](#四-快速上手构建一个简单的多线程计数器)
- [五、 核心机制：Wait 与 Notify 实现高效线程通信](#五-核心机制wait-与-notify-实现高效线程通信)
- [六、 实战 1：高性能图像处理中的并发优化](#六-实战-1高性能图像处理中的并发优化)
- [七、 总结：多线程并发在 Web 前端的应用前景](#七-总结多线程并发在-web-前端的应用前景)

---

## 一、 JS 的「并发困境」：为什么普通的 Web Worker 还不够快？

### 1. 历史局限
Web Worker 诞生之初，为了保证安全，采用了「完全隔离」的模型。
- **数据拷贝**：Worker 间传递数据使用 `postMessage`，这会触发结构化克隆（Structured Clone），产生巨大的内存和时间开销。
- **所有权转移 (Transferables)**：虽然快，但数据在发送方会被销毁，无法实现真正的「共享」。

### 2. 标志性事件
- **2017 年**：SharedArrayBuffer 首次进入标准。
- **2018 年**：受 Spectre/Meltdown 漏洞影响，该特性被紧急下架。
- **2021 年**：随着「跨源隔离 (COOP/COEP)」策略的成熟，SharedArrayBuffer 重新回归主流浏览器。

---

## 二、 SharedArrayBuffer：打破内存隔离的「任意门」

`SharedArrayBuffer` 允许不同线程（主线程与多个 Worker）访问**同一块物理内存**。

### 核心特性
- **零拷贝**：数据修改立即可见，无需发送消息。
- **高性能**：适合处理音视频流、物理引擎或大规模科学计算。

---

## 三、 Atomics API：多线程环境下的「交通警察」

如果多个线程同时修改同一块内存，会产生「竞态条件 (Race Condition)」。`Atomics` 对象提供了一系列原子操作来确保安全性。

### 核心方法
1. **`Atomics.add/sub`**：原子加减。
2. **`Atomics.load/store`**：原子的读写。
3. **`Atomics.compareExchange`**：比较并交换（CAS），这是实现无锁算法的基础。

---

## 四、 快速上手：构建一个简单的多线程计数器

### 代码示例：主线程
```javascript
const sab = new SharedArrayBuffer(4); // 4 字节的共享内存
const int32 = new Int32Array(sab);

const worker = new Worker('worker.js');
worker.postMessage(sab); // 发送内存句柄而非数据副本

// 定时读取共享内存
setInterval(() => {
  console.log('Main Thread Count:', Atomics.load(int32, 0));
}, 1000);
```

### 代码示例：Worker 线程
```javascript
self.onmessage = (e) => {
  const int32 = new Int32Array(e.data);
  
  setInterval(() => {
    // 原子性加 1，确保不会因为线程冲突导致计数错误
    Atomics.add(int32, 0, 1);
  }, 100);
};
```

---

## 五、 核心机制：Wait 与 Notify 实现高效线程通信

除了修改数据，Atomics 还提供了原生的「睡眠与唤醒」机制。

- **`Atomics.wait()`**：让当前线程睡眠，直到内存值发生变化或被唤醒。
- **`Atomics.notify()`**：唤醒正在该内存地址上睡眠的线程。

这种方式比传统的 `postMessage` 回调要快得多，因为它是在**内核级别**实现的同步。

---

## 六、 实战 1：高性能图像处理中的并发优化

在处理 4K 图像的滤镜时，我们可以：
1. 创建一个 `SharedArrayBuffer` 存储像素数据。
2. 将图像拆分为 4 个区域，交给 4 个 Web Worker 处理。
3. 由于内存共享，Worker 处理完后，主线程无需任何操作即可直接将 Buffer 绘制到 Canvas。

**性能表现**：比传统的 `postMessage` 方案快了 3 倍以上。

---

## 七、 总结：多线程并发在 Web 前端的应用前景

`SharedArrayBuffer` 与 `Atomics` 标志着 JS 已经具备了处理「重度计算」的能力。虽然目前主要应用于 WebGL、WebAssembly 和音视频领域，但随着 Web 应用日益复杂，掌握多线程并发控制将成为高级前端开发的必修课。

---
> 关注我，深挖 JS 底层黑科技，带你构建极致性能的 Web 应用。
