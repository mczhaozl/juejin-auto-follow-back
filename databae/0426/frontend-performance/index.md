# 前端性能优化完全指南

前端性能优化是提升用户体验的关键。本文将带你从基础到高级，全面掌握前端性能优化。

## 一、性能指标

### 1. Core Web Vitals

```
LCP (Largest Contentful Paint): 最大内容绘制
- 目标: < 2.5s
- 衡量: 页面主要内容加载完成的时间

FID (First Input Delay): 首次输入延迟
- 目标: < 100ms
- 衡量: 用户首次交互到浏览器响应的时间

CLS (Cumulative Layout Shift): 累积布局偏移
- 目标: < 0.1
- 衡量: 页面元素意外移动的程度

INP (Interaction to Next Paint): 交互到下次绘制
- 目标: < 200ms
- FID 的替代指标
```

### 2. 其他指标

```
TTFB (Time to First Byte): 首字节时间
- 目标: < 800ms
- 衡量: 服务器响应时间

FCP (First Contentful Paint): 首次内容绘制
- 目标: < 1.8s
- 衡量: 首次出现文本/图片的时间

TTI (Time to Interactive): 可交互时间
- 目标: < 3s
- 衡量: 页面完全可交互的时间

TBT (Total Blocking Time): 总阻塞时间
- 目标: < 200ms
- 衡量: FCP 到 TTI 之间的长任务总和
```

### 3. 测量工具

```javascript
// Lighthouse
// Chrome DevTools → Lighthouse

// Web Vitals
import { getCLS, getFID, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  console.log(metric);
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);

// Performance API
performance.mark('start');
// ... 代码 ...
performance.mark('end');
performance.measure('total', 'start', 'end');

console.log(performance.getEntriesByName('total'));
```

## 二、加载性能优化

### 1. 资源压缩

```javascript
// Webpack 配置
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin(),
      new CssMinimizerPlugin(),
    ],
  },
  plugins: [
    new CompressionPlugin({
      algorithm: 'gzip',
    }),
    new CompressionPlugin({
      filename: '[path][base].br',
      algorithm: 'brotliCompress',
    }),
  ],
};

// Vite 配置
import { defineConfig } from 'vite';
import viteCompression from 'vite-plugin-compression';

export default defineConfig({
  plugins: [
    viteCompression({ algorithm: 'gzip' }),
    viteCompression({ algorithm: 'brotliCompress', filename: '[path][base].br' }),
  ],
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
      },
    },
  },
});
```

### 2. 代码分割

```javascript
// React.lazy
import { Suspense, lazy } from 'react';

const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  );
}

// 路由级分割
import { createBrowserRouter } from 'react-router-dom';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/about',
    element: lazy(() => import('./About')),
  },
]);

// Webpack 魔法注释
const Component = lazy(() => 
  import(/* webpackChunkName: "component" */ './Component')
);

// 预加载
<link rel="preload" href="script.js" as="script">
<link rel="prefetch" href="next-page.js" as="script">
```

### 3. 图片优化

```html
<!-- 响应式图片 -->
<img 
  srcset="image-300.jpg 300w,
          image-600.jpg 600w,
          image-1200.jpg 1200w"
  sizes="(max-width: 600px) 300px,
         (max-width: 1200px) 600px,
         1200px"
  src="image-600.jpg"
  alt="Description"
>

<!-- WebP 格式 -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <source srcset="image.jpg" type="image/jpeg">
  <img src="image.jpg" alt="Description">
</picture>

<!-- AVIF 格式 -->
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description">
</picture>

<!-- 懒加载 -->
<img 
  src="placeholder.jpg"
  data-src="image.jpg"
  loading="lazy"
  alt="Description"
>

<!-- 占位图 -->
<img 
  src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PC9zdmc+"
  data-src="image.jpg"
  alt="Description"
>
```

### 4. 字体优化

```css
/* 字体显示策略 */
@font-face {
  font-family: 'MyFont';
  src: url('myfont.woff2') format('woff2'),
       url('myfont.woff') format('woff');
  font-display: swap;
}

/* 预加载字体 */
<link rel="preload" href="myfont.woff2" as="font" type="font/woff2" crossorigin>

/* 系统字体栈 */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, sans-serif;
}
```

### 5. 第三方脚本优化

```html
<!-- 异步加载 -->
<script src="analytics.js" async></script>

<!-- 延迟加载 -->
<script src="chat.js" defer></script>

<!-- 动态加载 -->
<script>
  window.addEventListener('load', () => {
    const script = document.createElement('script');
    script.src = 'third-party.js';
    document.body.appendChild(script);
  });
</script>

<!-- 脚本装饰器 -->
<script type="partytown" src="analytics.js"></script>
```

## 三、渲染性能优化

### 1. 减少重排和重绘

```javascript
// ❌ 不好：多次重排
element.style.width = '100px';
element.style.height = '100px';
element.style.margin = '10px';

// ✅ 好：一次重排
element.style.cssText = 'width: 100px; height: 100px; margin: 10px;';

// ✅ 更好：使用 class
element.classList.add('box');

// 使用 requestAnimationFrame
function update() {
  requestAnimationFrame(() => {
    element.style.width = '100px';
    element.style.height = '100px';
  });
}

// 使用 documentFragment
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
  const div = document.createElement('div');
  fragment.appendChild(div);
}
document.body.appendChild(fragment);

// 隐藏后修改
element.style.display = 'none';
element.style.width = '100px';
element.style.height = '100px';
element.style.display = 'block';
```

### 2. 虚拟列表

```jsx
// react-window
import { FixedSizeList as List } from 'react-window';

const VirtualList = ({ items }) => (
  <List
    height={400}
    itemCount={items.length}
    itemSize={50}
    width={300}
  >
    {({ index, style }) => (
      <div style={style}>
        {items[index]}
      </div>
    )}
  </List>
);

// react-virtualized
import { List } from 'react-virtualized';

const VirtualList = ({ items }) => (
  <List
    height={400}
    rowCount={items.length}
    rowHeight={50}
    width={300}
    rowRenderer={({ index, key, style }) => (
      <div key={key} style={style}>
        {items[index]}
      </div>
    )}
  />
);
```

### 3. React 优化

```jsx
// memo
const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{data}</div>;
});

// useMemo
const memoizedValue = useMemo(() => {
  return expensiveCalculation(a, b);
}, [a, b]);

// useCallback
const memoizedCallback = useCallback(() => {
  doSomething(a, b);
}, [a, b]);

// useTransition
import { useTransition } from 'react';

function App() {
  const [isPending, startTransition] = useTransition();
  const [count, setCount] = useState(0);

  function handleClick() {
    startTransition(() => {
      setCount(c => c + 1);
    });
  }

  return (
    <div>
      {isPending && <div>Loading...</div>}
      <button onClick={handleClick}>{count}</button>
    </div>
  );
}

// useDeferredValue
import { useDeferredValue } from 'react';

function SearchResults({ query }) {
  const deferredQuery = useDeferredValue(query);
  const results = useMemo(() => 
    searchData(deferredQuery), 
  [deferredQuery]);

  return <div>{results}</div>;
}
```

### 4. Vue 优化

```vue
<template>
  <!-- v-memo -->
  <div v-memo="[item.id]">
    {{ item.name }}
  </div>
</template>

<script setup>
// computed
import { computed } from 'vue';

const doubleCount = computed(() => count.value * 2);

// watch
import { watch } from 'vue';

watch(count, (newVal, oldVal) => {
  console.log(`count changed: ${oldVal} → ${newVal}`);
});

// 虚拟列表
import { RecycleScroller } from 'vue-virtual-scroller';

<RecycleScroller
  :items="items"
  :item-size="50"
  key-field="id"
  v-slot="{ item }"
>
  <div>{{ item.name }}</div>
</RecycleScroller>
</script>
```

## 四、缓存策略

### 1. HTTP 缓存

```nginx
# Nginx 配置
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}

location ~* \.(html)$ {
  expires -1;
  add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

```javascript
// Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('v1').then((cache) => {
      return cache.addAll([
        '/',
        '/styles.css',
        '/script.js',
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});

// Workbox
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { StaleWhileRevalidate } from 'workbox-strategies';

precacheAndRoute(self.__WB_MANIFEST);

registerRoute(
  ({ request }) => request.destination === 'script',
  new StaleWhileRevalidate()
);
```

### 2. 内存缓存

```javascript
// LRU 缓存
class LRUCache {
  constructor(capacity) {
    this.capacity = capacity;
    this.cache = new Map();
  }
  
  get(key) {
    if (!this.cache.has(key)) return -1;
    const value = this.cache.get(key);
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }
  
  put(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.capacity) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
}

const cache = new LRUCache(100);
cache.put('key', 'value');
```

## 五、网络优化

### 1. CDN

```html
<!-- 使用 CDN -->
<script src="https://cdn.example.com/react.min.js"></script>
<link href="https://cdn.example.com/styles.css" rel="stylesheet">

<!-- 预连接 -->
<link rel="preconnect" href="https://cdn.example.com">
<link rel="dns-prefetch" href="https://cdn.example.com">
```

### 2. HTTP/2 和 HTTP/3

```nginx
# Nginx HTTP/2 配置
server {
  listen 443 ssl http2;
  server_name example.com;
  
  ssl_certificate /path/to/cert.pem;
  ssl_certificate_key /path/to/key.pem;
}
```

### 3. 资源合并

```javascript
// Webpack 配置
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
  },
};
```

## 六、最佳实践检查清单

- [ ] 测量 Core Web Vitals
- [ ] 压缩资源（Gzip/Brotli）
- [ ] 代码分割和懒加载
- [ ] 图片优化（WebP/AVIF、响应式、懒加载）
- [ ] 字体优化（font-display、系统字体）
- [ ] 减少第三方脚本影响
- [ ] 避免不必要的重排重绘
- [ ] 使用虚拟列表
- [ ] React/Vue 优化（memo、useMemo、useCallback）
- [ ] HTTP 缓存和 Service Worker
- [ ] 使用 CDN
- [ ] 启用 HTTP/2

## 七、总结

前端性能优化核心要点：
- 性能指标（Core Web Vitals）
- 加载性能（压缩、代码分割、图片、字体）
- 渲染性能（重排重绘、虚拟列表、框架优化）
- 缓存策略（HTTP、Service Worker）
- 网络优化（CDN、HTTP/2）
- 最佳实践

开始优化你的前端性能吧！
