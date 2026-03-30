# Web 性能优化完全指南：核心指标与优化策略

> 深入讲解 Web 性能优化，包括 Core Web Vitals、加载性能、渲染性能优化，以及实际项目的性能提升实战案例。

## 一、Core Web Vitals

### 1.1 三大指标

| 指标 | 说明 | 目标 |
|------|------|------|
| LCP | 最大内容绘制 | < 2.5s |
| FID | 首次输入延迟 | < 100ms |
| CLS | 累积布局偏移 | < 0.1 |

### 1.2 测量工具

```javascript
import { getCLS, getFID, getLCP } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getLCP(console.log);
```

## 二、加载优化

### 2.1 资源压缩

```javascript
// Webpack 配置
module.exports = {
  optimization: {
    minimizer: [
      new TerserPlugin(),
      new CssMinimizerPlugin()
    ]
  }
};
```

### 2.2 代码分割

```javascript
// 路由懒加载
const Home = () => import('./Home');
const About = () => import('./About');

// 组件懒加载
const HeavyComponent = () => import('./HeavyComponent');
```

### 2.3 图片优化

```html
<!-- 响应式图片 -->
<img 
  srcset="img-400.jpg 400w, img-800.jpg 800w"
  sizes="(max-width: 600px) 400px, 800px"
  src="img-800.jpg"
  alt="图片"
>

<!-- 现代格式 -->
<picture>
  <source srcset="img.avif" type="image/avif">
  <source srcset="img.webp" type="image/webp">
  <img src="img.jpg" alt="图片">
</picture>
```

## 三、渲染优化

### 3.1 减少重排重绘

```javascript
// 不好 - 多次重排
element.style.width = '100px';
element.style.height = '100px';
element.style.padding = '10px';

// 好 - 一次性修改
element.style.cssText = 'width: 100px; height: 100px; padding: 10px;';

// 使用 CSS 类
element.classList.add('active');
```

### 3.2 requestAnimationFrame

```javascript
function animate() {
  // 更新动画
  element.style.transform = `translateX(${position}px)`;
  requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
```

### 3.3 DocumentFragment

```javascript
// 不好
for (const item of items) {
  const li = document.createElement('li');
  li.textContent = item;
  ul.appendChild(li);  // 每次触发重排
}

// 好
const fragment = document.createDocumentFragment();
for (const item of items) {
  const li = document.createElement('li');
  li.textContent = item;
  fragment.appendChild(li);
}
ul.appendChild(fragment);  // 一次重排
```

## 四、缓存优化

### 4.1 Service Worker

```javascript
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});
```

### 4.2 浏览器缓存

```http
# 强缓存
Cache-Control: max-age=3600, public

# 协商缓存
ETag: "abc123"
If-None-Match: "abc123"
```

## 五、网络优化

### 5.1 DNS 预解析

```html
<link rel="dns-prefetch" href="//cdn.example.com">
```

### 5.2 预连接

```html
<link rel="preconnect" href="https://api.example.com">
```

### 5.3 预加载

```html
<link rel="preload" href="main.js" as="script">
```

## 六、实战技巧

### 6.1 防抖节流

```javascript
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function throttle(fn, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      fn.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}
```

### 6.2 虚拟列表

```javascript
// 只渲染可见区域的列表项
const visibleItems = allItems.slice(startIndex, endIndex);
```

### 6.3 Web Worker

```javascript
// 主线程
const worker = new Worker('worker.js');
worker.postMessage({ data: 'large' });
worker.onmessage = result => console.log(result);

// worker.js
self.onmessage = e => {
  const result = heavyComputation(e.data);
  self.postMessage(result);
};
```

## 七、总结

性能优化核心要点：

1. **Core Web Vitals**：LCP、FID、CLS
2. **加载优化**：压缩、分割、图片
3. **渲染优化**：减少重排重绘
4. **缓存**：Service Worker、HTTP 缓存
5. **网络**：DNS 预解析、预连接
6. **防抖节流**：高频事件处理

掌握这些，性能飞起来！

---

**推荐阅读**：
- [web.dev 性能](https://web.dev/explore/performance)
- [MDN 性能](https://developer.mozilla.org/en-US/docs/Web/Performance)

**如果对你有帮助，欢迎点赞收藏！**
