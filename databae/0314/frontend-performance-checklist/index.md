# 前端性能优化终极清单：从 3 秒到 0.5 秒的实战经验

> 一份经过实战验证的性能优化清单，帮你的网站从"能用"变成"好用"。

---

## 一、为什么要优化性能

### 1.1 数据说话

- 页面加载时间每增加 1 秒，转化率下降 7%
- 53% 的移动用户会放弃加载超过 3 秒的页面
- Google 将页面速度作为搜索排名因素

### 1.2 真实案例

我们优化了一个电商网站：

- 优化前：首屏 3.2 秒，跳出率 45%
- 优化后：首屏 0.8 秒，跳出率 28%
- 结果：转化率提升 35%，营收增加 ¥200 万/月

## 二、性能指标

### 2.1 核心 Web Vitals

Google 定义的三个关键指标：

| 指标 | 含义 | 目标 |
|------|------|------|
| LCP | 最大内容绘制 | < 2.5s |
| FID | 首次输入延迟 | < 100ms |
| CLS | 累积布局偏移 | < 0.1 |

### 2.2 其他重要指标

- **FCP**（首次内容绘制）：< 1.8s
- **TTI**（可交互时间）：< 3.8s
- **TBT**（总阻塞时间）：< 200ms
- **Speed Index**（速度指数）：< 3.4s

### 2.3 测量工具

- **Lighthouse**：Chrome 内置，综合评分
- **WebPageTest**：详细的瀑布图和视频
- **Chrome DevTools**：Performance 面板
- **Real User Monitoring**：真实用户数据（如 Google Analytics）

## 三、资源优化

### 3.1 图片优化

#### 选择合适的格式

```
JPEG：照片、复杂图像
PNG：需要透明背景
WebP：现代浏览器，体积小 30%
AVIF：最新格式，体积更小，但兼容性差
SVG：图标、Logo
```

#### 响应式图片

```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="描述" loading="lazy">
</picture>

<!-- 或用 srcset -->
<img
  srcset="small.jpg 480w, medium.jpg 800w, large.jpg 1200w"
  sizes="(max-width: 600px) 480px, (max-width: 1000px) 800px, 1200px"
  src="medium.jpg"
  alt="描述"
>
```

#### 懒加载

```html
<img src="image.jpg" loading="lazy" alt="描述">
```

或用 Intersection Observer：

```javascript
const images = document.querySelectorAll('img[data-src]');

const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      imageObserver.unobserve(img);
    }
  });
});

images.forEach(img => imageObserver.observe(img));
```

#### 压缩工具

- **在线**：TinyPNG、Squoosh
- **CLI**：imagemin、sharp
- **构建工具**：webpack 的 image-webpack-loader

### 3.2 字体优化

#### 使用 font-display

```css
@font-face {
  font-family: 'MyFont';
  src: url('font.woff2') format('woff2');
  font-display: swap; /* 立即显示备用字体 */
}
```

#### 预加载关键字体

```html
<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>
```

#### 子集化

只包含需要的字符：

```bash
# 用 glyphhanger 生成子集
npx glyphhanger --subset=font.ttf --formats=woff2 --whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
```

### 3.3 JavaScript 优化

#### 代码分割

```javascript
// 路由级别分割
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));

// 组件级别分割
const HeavyComponent = lazy(() => import('./components/HeavyComponent'));

<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>
```

#### Tree Shaking

```javascript
// ❌ 差：导入整个库
import _ from 'lodash';

// ✅ 好：只导入需要的
import debounce from 'lodash/debounce';
```

#### 压缩和混淆

```javascript
// webpack.config.js
module.exports = {
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true, // 移除 console
          },
        },
      }),
    ],
  },
};
```

### 3.4 CSS 优化

#### 移除未使用的 CSS

```bash
# 用 PurgeCSS
npm install @fullhuman/postcss-purgecss
```

```javascript
// postcss.config.js
module.exports = {
  plugins: [
    require('@fullhuman/postcss-purgecss')({
      content: ['./src/**/*.html', './src/**/*.js'],
    }),
  ],
};
```

#### 关键 CSS 内联

```html
<style>
  /* 首屏关键样式 */
  .header { ... }
  .hero { ... }
</style>

<link rel="stylesheet" href="main.css">
```

#### CSS 压缩

```javascript
// webpack.config.js
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  optimization: {
    minimizer: [new CssMinimizerPlugin()],
  },
};
```

## 四、加载策略

### 4.1 预加载

```html
<!-- 预加载关键资源 -->
<link rel="preload" href="critical.css" as="style">
<link rel="preload" href="hero.jpg" as="image">
<link rel="preload" href="app.js" as="script">
```

### 4.2 预连接

```html
<!-- 提前建立连接 -->
<link rel="preconnect" href="https://api.example.com">
<link rel="dns-prefetch" href="https://cdn.example.com">
```

### 4.3 预获取

```html
<!-- 空闲时加载下一页资源 -->
<link rel="prefetch" href="next-page.js">
```

### 4.4 异步和延迟

```html
<!-- 异步加载，不阻塞解析 -->
<script src="analytics.js" async></script>

<!-- 延迟到 DOMContentLoaded 后执行 -->
<script src="non-critical.js" defer></script>
```

## 五、渲染优化

### 5.1 避免布局抖动

```javascript
// ❌ 差：强制同步布局
for (let i = 0; i < elements.length; i++) {
  const height = elements[i].offsetHeight; // 读
  elements[i].style.height = height + 10 + 'px'; // 写
}

// ✅ 好：批量读写
const heights = elements.map(el => el.offsetHeight); // 批量读
elements.forEach((el, i) => {
  el.style.height = heights[i] + 10 + 'px'; // 批量写
});
```

### 5.2 使用 CSS Transform

```css
/* ❌ 差：触发重排 */
.box {
  left: 100px;
  top: 100px;
}

/* ✅ 好：只触发合成 */
.box {
  transform: translate(100px, 100px);
}
```

### 5.3 虚拟滚动

```javascript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={10000}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>Item {index}</div>
  )}
</FixedSizeList>
```

### 5.4 防抖和节流

```javascript
// 防抖：延迟执行
const debounce = (fn, delay) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
};

// 节流：限制频率
const throttle = (fn, delay) => {
  let last = 0;
  return (...args) => {
    const now = Date.now();
    if (now - last >= delay) {
      fn(...args);
      last = now;
    }
  };
};

// 使用
window.addEventListener('scroll', throttle(() => {
  console.log('滚动');
}, 200));
```

## 六、网络优化

### 6.1 HTTP/2

启用 HTTP/2，支持多路复用、头部压缩。

```nginx
# Nginx 配置
server {
  listen 443 ssl http2;
  # ...
}
```

### 6.2 CDN

将静态资源部署到 CDN：

```html
<script src="https://cdn.example.com/app.js"></script>
```

### 6.3 Gzip / Brotli 压缩

```nginx
# Nginx 配置
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Brotli（更高压缩率）
brotli on;
brotli_types text/plain text/css application/json application/javascript;
```

### 6.4 缓存策略

```nginx
# 静态资源长期缓存
location ~* \.(js|css|png|jpg|jpeg|gif|svg|woff2)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}

# HTML 不缓存
location ~* \.html$ {
  expires -1;
  add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

## 七、框架优化

### 7.1 React

#### 使用 memo 和 useMemo

```javascript
const ExpensiveComponent = memo(({ data }) => {
  return <div>{data}</div>;
});

const result = useMemo(() => {
  return expensiveCalculation(data);
}, [data]);
```

#### 虚拟化长列表

```javascript
import { Virtuoso } from 'react-virtuoso';

<Virtuoso
  data={items}
  itemContent={(index, item) => <div>{item.name}</div>}
/>
```

#### 懒加载路由

```javascript
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
```

### 7.2 Vue

#### 使用 v-once 和 v-memo

```vue
<!-- 只渲染一次 -->
<div v-once>{{ staticContent }}</div>

<!-- 条件缓存 -->
<div v-memo="[value]">{{ expensiveComputation }}</div>
```

#### 异步组件

```javascript
const AsyncComponent = defineAsyncComponent(() =>
  import('./components/Heavy.vue')
);
```

### 7.3 Next.js

#### 使用 ISR

```javascript
export async function getStaticProps() {
  return {
    props: { data },
    revalidate: 60, // 60 秒后重新生成
  };
}
```

#### 图片优化

```javascript
import Image from 'next/image';

<Image
  src="/hero.jpg"
  width={800}
  height={600}
  priority // 预加载
  placeholder="blur" // 模糊占位
/>
```

## 八、监控和分析

### 8.1 性能监控

```javascript
// 使用 Performance API
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log(entry.name, entry.startTime);
  }
});

observer.observe({ entryTypes: ['navigation', 'resource', 'paint'] });
```

### 8.2 错误监控

```javascript
// 使用 Sentry
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: 'your-dsn',
  tracesSampleRate: 1.0,
});
```

### 8.3 用户体验监控

```javascript
// Web Vitals
import { getCLS, getFID, getLCP } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getLCP(console.log);
```

## 九、优化清单

### 资源优化

- [ ] 图片使用 WebP/AVIF 格式
- [ ] 图片懒加载
- [ ] 图片响应式（srcset）
- [ ] 字体子集化
- [ ] 字体 font-display: swap
- [ ] JavaScript 代码分割
- [ ] Tree Shaking
- [ ] 移除未使用的 CSS
- [ ] 关键 CSS 内联

### 加载策略

- [ ] 预加载关键资源
- [ ] 预连接第三方域名
- [ ] 异步加载非关键脚本
- [ ] 延迟加载非首屏内容

### 渲染优化

- [ ] 避免布局抖动
- [ ] 使用 CSS Transform
- [ ] 虚拟滚动长列表
- [ ] 防抖节流高频事件

### 网络优化

- [ ] 启用 HTTP/2
- [ ] 使用 CDN
- [ ] Gzip/Brotli 压缩
- [ ] 合理的缓存策略

### 监控

- [ ] 性能监控（Lighthouse）
- [ ] 错误监控（Sentry）
- [ ] 用户体验监控（Web Vitals）

## 十、实战案例

### 案例：电商首页优化

优化前：

- LCP: 4.2s
- FID: 180ms
- CLS: 0.25
- 总分: 45/100

优化措施：

1. 图片转 WebP，体积减少 40%
2. 首屏图片预加载，LCP 降到 1.8s
3. 代码分割，首包体积从 800KB 降到 200KB
4. 关键 CSS 内联，FCP 降到 0.9s
5. 固定图片尺寸，CLS 降到 0.05

优化后：

- LCP: 1.8s
- FID: 50ms
- CLS: 0.05
- 总分: 92/100

## 总结

性能优化的核心：

- **资源优化**：图片、字体、JS、CSS 都要压缩和优化
- **加载策略**：预加载、预连接、异步、延迟
- **渲染优化**：避免重排、虚拟滚动、防抖节流
- **网络优化**：HTTP/2、CDN、压缩、缓存
- **持续监控**：用数据驱动优化

记住：性能优化不是一次性的，而是持续的过程。

从今天开始，用这份清单优化你的网站吧！
