# Core Web Vitals 完全指南：前端性能度量新标准

> 一句话摘要：深入解析 Google Core Web Vitals (LCP、INP、CLS) 的定义、测量方法、优化策略及工具，帮助你全面提升网页用户体验和 SEO 表现。

## 一、引言

### 1.1 什么是 Core Web Vitals

Core Web Vitals 是 Google 定义的衡量用户体验的核心指标：

| 指标 | 全称 | 含义 | 目标 |
|------|------|------|------|
| LCP | Largest Contentful Paint | 最大内容绘制 | < 2.5s |
| INP | Interaction to Next Paint | 交互到下一帧 | < 200ms |
| CLS | Cumulative Layout Shift | 累计布局偏移 | < 0.1 |

### 1.2 为什么 Core Web Vitals 重要

```
┌─────────────────────────────────────────────────────────┐
│              Core Web Vitals 的影响                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   用户体验 ──→ 业务指标 ──→ SEO 排名                     │
│      ↓              ↓              ↓                    │
│   LCP/INP/CLS ──→ 转化率 ──→ 搜索排名                  │
│      ↓              ↓              ↓                    │
│   跳出率 ──→ 收入 ──→ 可见度                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 1.3 本文目标

1. 深入理解每个 Core Web Vitals 指标
2. 掌握测量方法和工具
3. 学习优化技术和最佳实践
4. 建立持续监控体系

## 二、LCP (Largest Contentful Paint)

### 2.1 定义

LCP 衡量**视口内最大图片或文本块的渲染时间**。

影响 LCP 的元素类型：
- 图片（`<img>`）
- `<image>` 在 `<svg>`
- `<video>` 的封面图
- 通过 `url()` 加载的背景图
- 包含文本节点的块级元素

### 2.2 测量方法

#### 使用 Performance Observer

```javascript
// 获取 LCP
const observer = new PerformanceObserver((list) => {
    const entries = list.getEntries();
    const lastEntry = entries[entries.length - 1];

    console.log('LCP:', lastEntry.startTime);
    console.log('LCP Element:', lastEntry.element);
    console.log('LCP Size:', lastEntry.size);
});

observer.observe({ type: 'largest-contentful-paint', buffered: true });
```

#### 使用 web-vitals 库

```javascript
import { onLCP } from 'web-vitals';

onLCP((metric) => {
    console.log('LCP:', metric.value);
    console.log('Rating:', metric.rating); // 'good' | 'needs-improvement' | 'poor'

    // 上报数据
    sendToAnalytics({
        name: metric.name,
        value: metric.value,
        rating: metric.rating,
        delta: metric.delta,
        id: metric.id,
        entries: metric.entries
    });
});
```

### 2.3 优化策略

#### 2.3.1 优化服务器响应时间

```javascript
// 使用 CDN
const response = await fetch('https://cdn.example.com/resource', {
    // CDN 减少 TTFB
});

// 服务端渲染优化
// Node.js
app.enable('trust proxy');
app.use(compression());

// 静态资源缓存
app.use(express.static('public', {
    maxAge: '1 year',
    etag: true
}));
```

#### 2.3.2 优化资源加载

```html
<!-- 预加载关键资源 -->
<link rel="preload" href="/fonts/main.woff2" as="font" crossorigin>
<link rel="preload" href="/images/hero.webp" as="image">

<!-- 预连接关键域 -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="dns-prefetch" href="https://fonts.gstatic.com">
```

#### 2.3.3 优化图片

```html
<!-- 使用现代格式 -->
<img
    src="/images/hero.webp"
    srcset="/images/hero-480.webp 480w,
            /images/hero-800.webp 800w,
            /images/hero-1200.webp 1200w"
    sizes="(max-width: 600px) 480px,
           (max-width: 1200px) 800px,
           1200px"
    loading="eager"
    fetchpriority="high"
    alt="Hero image"
>

<!-- 使用 picture 元素 -->
<picture>
    <source srcset="/images/hero.avif" type="image/avif">
    <source srcset="/images/hero.webp" type="image/webp">
    <img src="/images/hero.jpg" alt="Hero image">
</picture>
```

#### 2.3.4 CSS 优化

```css
/* 避免布局偏移导致 LCP 延迟 */
.hero-container {
    /* 预留空间 */
    min-height: 400px;
    contain: layout;
}

/* 使用 content-visibility 优化渲染 */
.offscreen-content {
    content-visibility: auto;
    contain-intrinsic-size: 1000px;
}

/* 关键 CSS 内联 */
<style>
    .critical-css { color: red; }
</style>
```

### 2.4 常见问题

```javascript
// 问题 1：懒加载影响 LCP
// ❌ 错误：hero 图片被懒加载
<img src="/hero.jpg" loading="lazy" alt="Hero">

// ✅ 正确：hero 图片 eager 加载
<img src="/hero.jpg" loading="eager" fetchpriority="high" alt="Hero">

// 问题 2：字体加载阻塞渲染
// ❌ 错误
<link rel="stylesheet" href="/fonts.css">

// ✅ 正确：预加载字体
<link rel="preload" href="/fonts/main.woff2" as="font" crossorigin>
<link rel="stylesheet" href="/fonts.css">
```

## 三、INP (Interaction to Next Paint)

### 3.1 定义

INP 衡量从用户交互到浏览器绘制下一帧的时间。

**注意**：INP 替代了 FID（First Input Delay），更能反映真实用户体验。

```javascript
// INP 计算逻辑
// INP = max(所有交互的 (nextPaint - interactionTime))
// 排除长时间交互（如长按）

const firstInput = performance.getEntriesByType('first-input')[0];
if (firstInput) {
    const fid = firstInput.processingStart - firstInput.startTime;
    console.log('FID:', fid);
}
```

### 3.2 交互类型

| 交互类型 | 触发事件 |
|---------|---------|
| 点击 | click |
| 键盘 | keydown, keyup |
| 指针 | pointerdown, pointerup |
| 拖拽 | dragstart |

### 3.3 测量方法

```javascript
import { onINP } from 'web-vitals';

onINP((metric) => {
    console.log('INP:', metric.value);
    console.log('Interaction:', metric.entries[0]);

    // 详细分析
    metric.entries.forEach(entry => {
        console.log('类型:', entry.name);
        console.log('开始:', entry.startTime);
        console.log('处理时间:', entry.processingStart - entry.startTime);
        console.log('总时间:', entry.processingEnd - entry.startTime);
    });
});
```

### 3.4 优化策略

#### 3.4.1 分解长任务

```javascript
// ❌ 长任务阻塞主线程
function processLargeData() {
    const data = fetchLargeData();
    data.forEach(item => heavyComputation(item));
    updateUI();
}

// ✅ 使用 requestIdleCallback 分解任务
function processLargeData() {
    const data = fetchLargeData();
    let index = 0;

    function processBatch() {
        const batchSize = 50;
        for (let i = 0; i < batchSize && index < data.length; i++) {
            heavyComputation(data[index++]);
        }

        if (index < data.length) {
            requestIdleCallback(processBatch);
        } else {
            updateUI();
        }
    }

    requestIdleCallback(processBatch);
}

// ✅ 使用 Web Worker
const worker = new Worker('worker.js');
worker.postMessage({ data: largeData });
worker.onmessage = (e) => {
    updateUI(e.data);
};
```

#### 3.4.2 优化事件处理

```javascript
// ❌ 同步处理耗时操作
button.addEventListener('click', (e) => {
    const result = heavyComputation();
    updateUI(result);
});

// ✅ 异步处理
button.addEventListener('click', (e) => {
    // 立即反馈
    showLoading();

    // 异步处理
    setTimeout(() => {
        const result = heavyComputation();
        updateUI(result);
    }, 0);
});

// ✅ 使用 Promise
button.addEventListener('click', async (e) => {
    showLoading();

    await scheduler.yield(); // 让出主线程

    const result = heavyComputation();
    updateUI(result);
});
```

#### 3.4.3 减少重排重绘

```javascript
// ❌ 多次触发布局
function updateList(items) {
    items.forEach(item => {
        const el = document.createElement('div');
        el.textContent = item.name;
        container.appendChild(el);  // 每次添加都触发布局
    });
}

// ✅ 文档片段批量添加
function updateList(items) {
    const fragment = document.createDocumentFragment();
    items.forEach(item => {
        const el = document.createElement('div');
        el.textContent = item.name;
        fragment.appendChild(el);
    });
    container.appendChild(fragment);  // 只触发一次布局
}

// ✅ 使用 transform 替代 top/left
element.style.transform = 'translateX(100px)';  // 合成层
element.style.top = '100px';  // 触发布局
```

#### 3.4.4 虚拟滚动

```javascript
// 对于长列表，使用虚拟滚动
class VirtualList {
    constructor(container, items, itemHeight) {
        this.container = container;
        this.items = items;
        this.itemHeight = itemHeight;
        this.visibleCount = Math.ceil(container.clientHeight / itemHeight);
        this.scrollTop = 0;

        this.container.addEventListener('scroll', this.onScroll.bind(this));
        this.render();
    }

    onScroll() {
        this.scrollTop = this.container.scrollTop;
        this.render();
    }

    render() {
        const startIndex = Math.floor(this.scrollTop / this.itemHeight);
        const endIndex = startIndex + this.visibleCount + 1;

        // 只渲染可见项
        const visibleItems = this.items.slice(startIndex, endIndex);

        this.container.style.height = `${this.items.length * this.itemHeight}px`;
        // ... 渲染逻辑
    }
}
```

### 3.5 最佳实践

```javascript
// 使用 scheduler.yield() (Chrome 115+)
async function handleClick() {
    showFeedback();

    // 让出主线程
    await scheduler.yield();

    // 执行耗时操作
    heavyComputation();
    updateUI();
}

// 使用 navigator.scheduling.isInputPending
async function processTasks() {
    while (tasks.length > 0) {
        const task = tasks.shift();
        processTask(task);

        // 检查是否有更高优先级的输入
        if (navigator.scheduling?.isInputPending()) {
            await scheduler.yield();
        }
    }
}
```

## 四、CLS (Cumulative Layout Shift)

### 4.1 定义

CLS 衡量页面视觉稳定性，计算所有意外布局偏移的累加分数。

```
CLS = sum(impact fraction × distance fraction)

impact fraction: 发生偏移的元素影响的视口比例
distance fraction: 元素偏移的距离（相对于视口）
```

### 4.2 测量方法

```javascript
import { onCLS } from 'web-vitals';

let clsValue = 0;

const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
        // 只计算非用户交互导致的偏移
        if (!entry.hadRecentInput) {
            clsValue += entry.value;
            console.log('CLS:', clsValue);
        }
    }
});

observer.observe({ type: 'layout-shift', buffered: true });

onCLS((metric) => {
    console.log('CLS:', metric.value);
    console.log('Entries:', metric.entries);
});
```

### 4.3 常见问题

```html
<!-- 问题 1：图片无尺寸 -->
<!-- ❌ 错误：图片加载后导致布局偏移 -->
<img src="/image.jpg" alt="Image">

<!-- ✅ 正确：指定宽高 -->
<img src="/image.jpg" width="800" height="400" alt="Image">

<!-- 问题 2：动态内容插入 -->
<!-- ❌ 错误：广告动态插入 -->
<div id="ad-container"></div>

<!-- ✅ 正确：预留空间 -->
<div id="ad-container" style="min-height: 250px;"></div>
```

### 4.4 优化策略

#### 4.4.1 图片和视频尺寸

```html
<!-- 始终指定图片和视频的尺寸 -->
<img
    src="/image.jpg"
    width="800"
    height="400"
    alt="..."
>

<video
    src="/video.mp4"
    width="640"
    height="360"
    poster="/poster.jpg"
>
</video>

<!-- 使用 aspect-ratio CSS -->
.image-container {
    aspect-ratio: 16 / 9;
    width: 100%;
    background-color: #f0f0f0; /* 占位色 */
}
```

#### 4.4.2 字体加载

```css
/* 使用 font-display: optional 避免 FOIT/FOUT */
@font-face {
    font-family: 'MyFont';
    src: url('/fonts/myfont.woff2') format('woff2');
    font-display: optional;
}

/* 或使用 font-display: swap 并测量 FOUT */
@font-face {
    font-family: 'MyFont';
    src: url('/fonts/myfont.woff2') format('woff2');
    font-display: swap;
}

/* 使用 size-adjust 减少 FOUT 时的布局偏移 */
@font-face {
    font-family: 'MyFont-fallback';
    src: local('Arial');
    size-adjust: 110%;
    ascent-override: 90%;
    descent-override: 10%;
}
```

#### 4.4.3 动态内容

```css
/* 预留动态内容空间 */
.ad-container {
    min-height: 250px;
    /* 或使用固定高度 */
    height: 250px;
}

.notification-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
}

/* 骨架屏 */
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    min-height: 200px;
}
```

#### 4.4.4 动画和过渡

```css
/* ❌ 使用动画导致布局偏移 */
.animated-element {
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        transform: translateY(-100%);
    }
    to {
        transform: translateY(0);
    }
}

/* ✅ 使用 transform，不会导致布局偏移 */
.animated-element {
    animation: slideInTransform 0.3s ease-out;
}

@keyframes slideInTransform {
    from {
        transform: translateY(-100%);
    }
    to {
        transform: translateY(0);
    }
}

/* 使用 will-change 提示浏览器优化 */
.animated-element {
    will-change: transform;
}
```

### 4.5 常见问题修复

```javascript
// 问题：iframe 嵌入导致布局偏移
// ✅ 使用容器预留空间
<iframe
    src="https://example.com"
    width="560"
    height="315"
    style="border: none;"
    allowfullscreen
></iframe>

// 问题：Web Components 导致布局偏移
// ✅ 在 shadow DOM 中处理
class MyElement extends HTMLElement {
    constructor() {
        super();
        const shadow = this.attachShadow({ mode: 'open' });
        // 保持内容在 shadow DOM 中
    }
}
```

## 五、测量工具

### 5.1 Chrome DevTools

```javascript
// Lighthouse
// 位置：DevTools -> Lighthouse -> Analyze page load

// Performance Panel
// 位置：DevTools -> Performance -> 录制交互

// Core Web Vitals Panel (Chrome 99+)
// 位置：DevTools -> Performance -> Insights
```

### 5.2 PageSpeed Insights

```bash
# 使用 PSI API
curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&key=YOUR_API_KEY"
```

### 5.3 web-vitals 库

```javascript
import { onLCP, onINP, onCLS, onFCP, onTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
    const body = JSON.stringify({
        name: metric.name,
        value: metric.value,
        rating: metric.rating,
        delta: metric.delta,
        id: metric.id
    });

    // 使用 navigator.sendBeacon 确保数据发送
    if (navigator.sendBeacon) {
        navigator.sendBeacon('/analytics', body);
    } else {
        fetch('/analytics', {
            method: 'POST',
            body,
            keepalive: true
        });
    }
}

onLCP(sendToAnalytics);
onINP(sendToAnalytics);
onCLS(sendToAnalytics);
```

### 5.4 Search Console

```javascript
// Search Console 提供真实用户数据
// 位置：Search Console -> Core Web Vitals
// 报告基于 CrUX (Chrome User Experience Report)
```

## 六、真实用户监控 (RUM)

### 6.1 实现 RUM

```javascript
class WebVitalsReporter {
    constructor(options = {}) {
        this.endpoint = options.endpoint || '/analytics';
        this.sampleRate = options.sampleRate || 1.0; // 采样率
        this.metrics = {};
    }

    shouldReport() {
        return Math.random() <= this.sampleRate;
    }

    report(metric) {
        if (!this.shouldReport()) return;

        const data = {
            name: metric.name,
            value: metric.value,
            rating: metric.rating,
            delta: metric.delta,
            id: metric.id,
            url: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: Date.now()
        };

        this.send(data);
    }

    send(data) {
        const body = JSON.stringify(data);

        if (navigator.sendBeacon) {
            navigator.sendBeacon(this.endpoint, body);
        } else {
            fetch(this.endpoint, {
                method: 'POST',
                body,
                keepalive: true
            });
        }
    }

    start() {
        onLCP((m) => this.report(m));
        onINP((m) => this.report(m));
        onCLS((m) => this.report(m));
    }
}

// 使用
const reporter = new WebVitalsReporter({
    endpoint: '/api/vitals',
    sampleRate: 0.1 // 10% 采样
});

reporter.start();
```

### 6.2 Dashboard 实现

```javascript
// 使用 IndexedDB 缓存数据
class MetricsStore {
    constructor() {
        this.dbName = 'web-vitals';
        this.storeName = 'metrics';
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    db.createObjectStore(this.storeName, { keyPath: 'id' });
                }
            };
        });
    }

    async add(metric) {
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction(this.storeName, 'readwrite');
            const store = tx.objectStore(this.storeName);
            const request = store.add({
                id: metric.id,
                name: metric.name,
                value: metric.value,
                rating: metric.rating,
                timestamp: Date.now()
            });

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async getAll(name) {
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction(this.storeName, 'readonly');
            const store = tx.objectStore(this.storeName);
            const request = store.getAll();

            request.onsuccess = () => {
                const results = request.result.filter(r => r.name === name);
                resolve(results);
            };
            request.onerror = () => reject(request.error);
        });
    }
}
```

## 七、SEO 影响

### 7.1 排名因素

Google 将 Core Web Vitals 作为页面体验信号的一部分：

```
┌─────────────────────────────────────────────────────────┐
│                  页面体验信号                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   Core Web Vitals                                        │
│   ├── LCP < 2.5s ✅                                      │
│   ├── INP < 200ms ✅                                     │
│   └── CLS < 0.1 ✅                                       │
│                                                          │
│   + HTTPS ✅                                             │
│   + 无侵入性插页式广告 ✅                                 │
│   + 移动端友好 ✅                                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 7.2 CrUX 数据

```javascript
// CrUX API
const url = 'https://www.googleapis.com/webfonts/v1/chromeuxreport';
const params = new URLSearchParams({
    key: 'YOUR_API_KEY',
    url: 'https://example.com'
});

fetch(`${url}?${params}`)
    .then(res => res.json())
    .then(data => {
        console.log('LCP:', data.record.metrics.lcp);
        console.log('INP:', data.record.metrics.interaction_to_next_paint);
        console.log('CLS:', data.record.metrics.cumulative_layout_shift);
    });
```

## 八、实战优化案例

### 8.1 电商网站优化

```javascript
// 问题：产品列表页 CLS 高
// 原因：图片未指定尺寸，促销 banner 动态插入

// 解决方案
function optimizeProductList() {
    // 1. 图片尺寸
    document.querySelectorAll('.product-image').forEach(img => {
        img.width = 300;
        img.height = 300;
    });

    // 2. 骨架屏占位
    const skeleton = `
        <div class="product-skeleton">
            <div class="skeleton skeleton-image"></div>
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-price"></div>
        </div>
    `;

    // 3. 预插入 banner 容器
    const bannerContainer = document.createElement('div');
    bannerContainer.id = 'promo-banner';
    bannerContainer.style.minHeight = '100px';
    document.querySelector('.header').after(bannerContainer);
}
```

### 8.2 新闻网站优化

```javascript
// 问题：文章页 LCP 高
// 原因：Hero 图片大，未优化

// 解决方案
function optimizeArticlePage() {
    // 1. 使用 picture 元素
    const heroPicture = document.createElement('picture');
    heroPicture.innerHTML = `
        <source srcset="${heroAvif}" type="image/avif">
        <source srcset="${heroWebp}" type="image/webp">
        <img src="${heroJpg}" alt="${heroAlt}" width="1200" height="630">
    `;

    // 2. 预加载
    const preloadLink = document.createElement('link');
    preloadLink.rel = 'preload';
    preloadLink.as = 'image';
    preloadLink.href = heroWebp;
    preloadLink.setAttribute('fetchpriority', 'high');
    document.head.appendChild(preloadLink);

    // 3. 字体优化
    const fontLink = document.createElement('link');
    fontLink.rel = 'preload';
    fontLink.href = '/fonts/article.woff2';
    fontLink.as = 'font';
    fontLink.crossOrigin = 'anonymous';
    document.head.appendChild(fontLink);
}
```

## 九、总结

### 9.1 核心要点

1. **LCP 衡量加载性能，目标 < 2.5s**
2. **INP 衡量交互性能，目标 < 200ms**
3. **CLS 衡量视觉稳定性，目标 < 0.1**
4. **使用 web-vitals 库进行真实用户监控**
5. **Core Web Vitals 影响 SEO 排名**

### 9.2 优化清单

```markdown
## LCP 优化
- [ ] 使用 CDN
- [ ] 预加载关键资源
- [ ] 图片使用现代格式 (WebP/AVIF)
- [ ] 指定图片尺寸
- [ ] 字体使用预加载

## INP 优化
- [ ] 分解长任务
- [ ] 使用 requestIdleCallback
- [ ] 避免同步操作
- [ ] 使用 Web Worker
- [ ] 优化事件处理

## CLS 优化
- [ ] 指定图片和视频尺寸
- [ ] 使用骨架屏
- [ ] 预留动态内容空间
- [ ] 字体使用 font-display
- [ ] 动画使用 transform
```

### 9.3 资源链接

- [web-vitals-js](https://github.com/GoogleChrome/web-vitals)
- [Core Web Vitals](https://web.dev/vitals/)
- [Chrome User Experience Report](https://developer.chrome.com/docs/crux)

> 如果对你有帮助，欢迎点赞、收藏！有任何问题欢迎在评论区讨论。
