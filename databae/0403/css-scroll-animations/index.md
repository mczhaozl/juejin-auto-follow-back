# CSS Scroll-driven Animations：纯 CSS 实现视差滚动与进度条

> 曾经，实现一个随滚动进度变化的顶部进度条或复杂的视差滚动动效，我们需要引入 `GSAP`、`ScrollMagic` 或者至少编写繁琐的 `window.addEventListener('scroll', ...)` 逻辑。现在，借助 CSS Scroll-driven Animations API，我们可以完全在 CSS 层面以声明式的方式实现高性能的滚动关联动画。

---

## 目录 (Outline)
- [一、 滚动动画的演进：从 JS 监听器到声明式 API](#一-滚动动画的演进从-js-监听器到声明式-api)
- [二、 核心概念：Scroll Progress Timeline 与 View Timeline](#二-核心概念scroll-progress-timeline-与-view-timeline)
- [三、 实战 1：零 JS 实现页面顶部阅读进度条](#三-实战-1零-js-实现页面顶部阅读进度条)
- [四、 实战 2：图片随进入视口而淡入放大 (View Timeline)](#四-实战-2图片随进入视口而淡入放大-view-timeline)
- [五、 性能优势：为什么 CSS 方案更流畅？](#五-性能优势为什么-css-方案更流畅)
- [六、 总结与浏览器支持建议](#六-总结与浏览器支持建议)

---

## 一、 滚动动画的演进：从 JS 监听器到声明式 API

### 1. 历史背景
在 JS 方案中，浏览器必须在主线程执行 JS 逻辑，计算滚动偏移量，然后再修改元素的样式。
- **痛点**：由于主线程可能繁忙，动画容易出现掉帧、卡顿感（特别是快速滚动时）。

### 2. 标志性事件
- **2023 年**：Chrome 115+ 正式支持滚动驱动动画（Scroll-driven Animations）规范。
- **2024 年**：随着规范趋于稳定，该 API 成为现代 Web 动效的首选方案。

---

## 二、 核心概念：Scroll Progress Timeline 与 View Timeline

该 API 引入了两种核心的时间轴：
1. **Scroll Progress Timeline**：动画进度与整个容器的滚动进度绑定（从 0% 到 100%）。
2. **View Timeline**：动画进度与特定元素在视口（Viewport）中的可见性绑定（从进入到离开）。

---

## 三、 实战 1：零 JS 实现页面顶部阅读进度条

### 代码示例
```css
/* 定义进度条拉长动画 */
@keyframes progress-grow {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

.progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: #ff0000;
  transform-origin: 0 50%;
  
  /* 魔法发生的地方 */
  animation: progress-grow auto linear;
  animation-timeline: scroll(); /* 绑定到默认的根滚动条 */
}
```

---

## 四、 实战 2：图片随进入视口而淡入放大 (View Timeline)

### 代码示例
```css
@keyframes fade-in-scale {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.reveal-image {
  /* 绑定视图时间轴 */
  view-timeline-name: --image-view;
  view-timeline-axis: block;

  animation: fade-in-scale auto linear both;
  /* 动画进度的范围：从元素底部进入视口，到元素中心点位置 */
  animation-range: entry 0% contain 50%;
  animation-timeline: --image-view;
}
```

---

## 五、 性能优势：为什么 CSS 方案更流畅？

### 1. 合成线程执行
不同于 JS 方案，滚动驱动动画由浏览器的**合成线程 (Compositor Thread)** 直接处理。
- 即使你的主线程正忙于执行复杂的 JS 计算，滚动动画依然能保持丝滑的 60FPS。

### 2. 内存与功耗
由于无需频繁触发 JS 回调，手机端的电量消耗和 CPU 负载也会更低。

---

## 六、 总结与浏览器支持建议

- **支持情况**：目前 Chrome, Edge, Safari (17+) 均已支持。Firefox 也在积极跟进。
- **最佳实践**：
  - 简单的进度反馈、视差背景优先使用 CSS。
  - 复杂的业务交互逻辑（如滚动到某处触发接口请求）仍需使用 JS。

CSS Scroll-driven Animations 的出现，让 Web 动效回归了它本该有的样子：**高性能、声明式、易维护。**

---

> **参考资料：**
> - *Scroll-driven Animations - web.dev*
> - *MDN: animation-timeline property*
> - *Chrome for Developers: A Guide to Scroll-driven Animations*
