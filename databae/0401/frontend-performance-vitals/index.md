# 前端性能监控：自定义 Web Vitals 指标上报实战

> Google 提出的 Web Vitals 指标（LCP, FID, CLS）已经成为衡量网页性能的标准。然而，对于复杂的单页应用（SPA）或特定业务场景，仅靠这些通用指标往往无法真实反映用户的体感。本文将带你实战自定义性能监控方案，精准量化业务交互流畅度。

---

## 目录 (Outline)
- [一、 Web Vitals 的局限性：为什么需要自定义指标？](#一-web-vitals-的局限性为什么需要自定义指标)
- [二、 核心 API：PerformanceObserver 的深度应用](#二-核心-api-performanceobserver-的深度应用)
- [三、 实战 1：量化 SPA 路由切换性能 (Navigation Timing)](#三-实战-1量化-spa-路由切换性能-navigation-timing)
- [四、 实战 2：监控长任务 (Long Tasks) 与总阻塞时间 (TBT)](#四-实战-2监控长任务-long-tasks-与总阻塞时间-tbt)
- [五、 数据上报策略：Beacon API 与采样优化](#五-数据上报策略-beacon-api-与采样优化)
- [六、 总结与最佳实践](#六-总结与最佳实践)

---

## 一、 Web Vitals 的局限性：为什么需要自定义指标？

### 1. 历史背景
传统的性能指标（如 DOMContentLoaded）在现代前端框架下已经失去意义。LCP 虽然能衡量首屏，但在用户点击按钮后「白屏 2 秒才加载出弹窗」这种交互延迟上，LCP 无法感知。

### 2. 标志性事件
- **2020 年**：Google 正式推出 Core Web Vitals。
- **2024 年**：INP (Interaction to Next Paint) 取代 FID 成为核心指标。

### 3. 解决的问题 / 带来的变化
自定义指标解决了「业务逻辑无关」的问题。我们可以通过自定义指标，监控诸如：
- **关键数据加载时间**：从进入页面到首页首条接口数据渲染完成的时间。
- **复杂计算耗时**：例如 Canvas 绘图或大数据排序的阻塞时长。

---

## 二、 核心 API：PerformanceObserver 的深度应用

`PerformanceObserver` 是现代性能监控的基石。它允许我们以「订阅」的方式，实时获取浏览器的性能条目（Entries）。

### 代码示例：基础订阅框架
```javascript
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log(`收到性能条目: ${entry.name}`, entry);
  }
});

// 订阅感兴趣的类型
observer.observe({ entryTypes: ['paint', 'largest-contentful-paint', 'longtask'] });
```

---

## 三、 实战 1：量化 SPA 路由切换性能 (Navigation Timing)

SPA 的页面跳转不触发真实的浏览器导航。我们需要手动记录。

### 实战代码
```javascript
// 在路由跳转开始时
const startMark = performance.mark('route-change-start');

// 在路由跳转结束（如数据渲染完成）时
const endMark = performance.mark('route-change-end');

// 计算耗时
const measure = performance.measure(
  'route-change-duration', 
  'route-change-start', 
  'route-change-end'
);

console.log(`本次路由跳转耗时: ${measure.duration}ms`);
```

---

## 四、 实战 2：监控长任务 (Long Tasks) 与总阻塞时间 (TBT)

长任务（执行超过 50ms 的 JS）是导致页面卡顿的罪魁祸首。

### 实战代码
```javascript
let totalBlockingTime = 0;

const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    // 超过 50ms 的任务，其超出部分被视为阻塞时间
    if (entry.duration > 50) {
      totalBlockingTime += (entry.duration - 50);
      console.warn(`检测到长任务！阻塞时长: ${entry.duration - 50}ms`);
    }
  }
});

observer.observe({ entryTypes: ['longtask'] });
```

---

## 五、 数据上报策略：Beacon API 与采样优化

性能上报不能干扰用户正常的网络请求。

### 1. 使用 Navigator.sendBeacon
它能确保在页面卸载（Unload）时，异步地将少量数据发送到服务器，且不阻塞跳转。
```javascript
window.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    const data = JSON.stringify(performanceMetrics);
    navigator.sendBeacon('/api/metrics', data);
  }
});
```

### 2. 采样率控制
在大流量场景下，100% 上报会压垮后台。建议按 `Math.random() < 0.1`（10% 采样）进行控制。

---

## 六、 总结与最佳实践

- **核心原则**：性能监控本身不应该造成性能损耗。
- **建议**：优先利用浏览器内置指标，只有当内置指标无法覆盖核心业务路径时，再通过 `performance.mark` 补充。
- **展望**：随着 `Performance Timeline Level 3` 的落地，未来我们将能更精细地监控 CPU 压力和内存抖动。

前端性能优化不是一次性的任务，而是通过数据驱动、持续迭代的过程。

---

> **参考资料：**
> - *Web Vitals - web.dev*
> - *MDN: PerformanceObserver API*
> - *High Performance Browser Networking - Ilya Grigorik*
