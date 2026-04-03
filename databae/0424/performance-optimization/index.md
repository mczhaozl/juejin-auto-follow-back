# Web 性能优化完全实战指南：从前端到后端全方位优化

Web 性能优化是提升用户体验的关键。本文将带你全面掌握从前端到后端的全方位性能优化技巧。

## 一、性能指标与测量

### 1. 核心 Web 指标（Core Web Vitals）

```
LCP (Largest Contentful Paint): 最大内容绘制
  - 优秀: ≤2.5s
  - 良好: ≤4s
  - 较差: >4s

FID (First Input Delay): 首次输入延迟
  - 优秀: ≤100ms
  - 良好: ≤300ms
  - 较差: >300ms

CLS (Cumulative Layout Shift): 累积布局偏移
  - 优秀: ≤0.1
  - 良好: ≤0.25
  - 较差: >0.25
```

### 2. 使用 Lighthouse

```bash
# 安装 Lighthouse
npm install -g lighthouse

# 运行 Lighthouse
lighthouse https://example.com --view

# 或使用 Chrome DevTools
# 打开 Chrome DevTools → Lighthouse 面板
```

### 3. 使用 Web Vitals 库

```javascript
import { getCLS, getFID, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  console.log(metric);
  // 发送到你的分析服务
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### 4. Performance API

```javascript
// Performance Timeline
const perfEntries = performance.getEntriesByType('navigation');
const [navigation] = perfEntries;

console.log('DNS:', navigation.domainLookupEnd - navigation.domainLookupStart);
console.log('TCP:', navigation.connectEnd - navigation.connectStart);
console.log('TTFB:', navigation.responseStart - navigation.requestStart);
console.log('Response:', navigation.responseEnd - navigation.responseStart);
console.log('DOM Loaded:', navigation.domContentLoadedEventEnd - navigation.fetchStart);
console.log('Load Complete:', navigation.loadEventEnd - navigation.fetchStart);

// 使用 PerformanceObserver
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log(entry.name, entry.startTime, entry.duration);
  }
});

observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
```

## 二、前端优化：加载性能

### 1. 代码分割（Code Splitting）

```javascript
// React 16.6+
import React, { Suspense, lazy } from 'react';

const Home = lazy(() => import('./Home'));
const About = lazy(() => import('./About'));
const Dashboard = lazy(() => import('./Dashboard'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Suspense>
  );
}

// 基于路由的代码分割
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        path: 'about',
        async lazy() {
          let { About } = await import('./About');
          return { Component: About };
        },
      },
    ],
  },
]);

// Webpack 配置
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: 'react',
          chunks: 'all',
        },
      },
    },
  },
};
```

### 2. 资源压缩

```javascript
// webpack.config.js
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
          },
        },
      }),
      new CssMinimizerPlugin(),
    ],
  },
  plugins: [
    new CompressionPlugin({
      filename: '[path][base].gz',
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
    }),
    new CompressionPlugin({
      filename: '[path][base].br',
      algorithm: 'brotliCompress',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
    }),
  ],
};

// Next.js 配置
// next.config.js
module.exports = {
  compress: true,
  swcMinify: true,
};
```

### 3. 图片优化

```html
<!-- 使用适当的格式 -->
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description" loading="lazy">
</picture>

<!-- 使用响应式图片 -->
<img
  srcset="small.jpg 400w,
          medium.jpg 800w,
          large.jpg 1200w"
  sizes="(max-width: 600px) 400px,
         (max-width: 1000px) 800px,
         1200px"
  src="medium.jpg"
  alt="Responsive image"
>

<!-- 固定尺寸防止 CLS -->
<img
  src="image.jpg"
  alt="Description"
  width="800"
  height="600"
  style="width: 100%; height: auto;"
>

<!-- Next.js Image 组件 -->
import Image from 'next/image';

<Image
  src="/profile.jpg"
  alt="Profile"
  width={500}
  height={500}
  priority={true}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

### 4. 字体优化

```css
/* 使用 font-display */
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/inter.woff2') format('woff2');
}

/* 预加载字体 */
<link
  rel="preload"
  href="/fonts/inter.woff2"
  as="font"
  type="font/woff2"
  crossorigin
>

/* 使用系统字体栈 */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
               Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', 
               sans-serif;
}
```

### 5. 预加载关键资源

```html
<!-- 预加载关键 JS/CSS -->
<link rel="preload" href="/critical.js" as="script">
<link rel="preload" href="/critical.css" as="style">

<!-- 预连接 -->
<link rel="preconnect" href="https://api.example.com">
<link rel="dns-prefetch" href="https://analytics.example.com">

<!-- 预取 -->
<link rel="prefetch" href="/about-page">
<link rel="prerender" href="/next-page">

<!-- 使用 fetchpriority -->
<img
  src="hero.jpg"
  fetchpriority="high"
  alt="Hero"
>
<img
  src="thumbnail.jpg"
  fetchpriority="low"
  alt="Thumbnail"
>
```

## 三、前端优化：运行时性能

### 1. 减少重排重绘

```javascript
// ❌ 不好：多次修改 DOM
for (let i = 0; i < 100; i++) {
  document.getElementById('list').innerHTML += `<li>${i}</li>`;
}

// ✅ 好：批量更新
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
  const li = document.createElement('li');
  li.textContent = i;
  fragment.appendChild(li);
}
document.getElementById('list').appendChild(fragment);

// 使用 requestAnimationFrame
function updateAnimation() {
  element.style.transform = `translateX(${x}px)`;
  requestAnimationFrame(updateAnimation);
}

// 使用 CSS transforms 和 opacity
.element {
  transform: translateZ(0); /* 启用 GPU 加速 */
  will-change: transform;
}
```

### 2. 虚拟列表

```javascript
import { FixedSizeList as List } from 'react-window';

const VirtualList = ({ items }) => (
  <List
    height={600}
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

// 使用 react-virtual
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualScroll() {
  const parentRef = React.useRef();
  
  const virtualizer = useVirtualizer({
    count: 10000,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });
  
  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            Row {virtualRow.index}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 3. 防抖和节流

```javascript
// 防抖（debounce）
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 使用
const handleSearch = debounce((query) => {
  console.log('Searching:', query);
}, 300);

// 节流（throttle）
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// 使用
const handleScroll = throttle(() => {
  console.log('Scrolling...');
}, 100);

// 使用 Lodash
import { debounce, throttle } from 'lodash-es';

const search = debounce(doSearch, 300);
const scroll = throttle(doScroll, 100);
```

### 4. React 性能优化

```jsx
import React, { memo, useMemo, useCallback } from 'react';

// memo：组件记忆化
const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
  return <div>{data}</div>;
});

// useMemo：值记忆化
function App() {
  const [count, setCount] = useState(0);
  const [todos, setTodos] = useState([]);
  
  const expensiveValue = useMemo(() => {
    return expensiveCalculation(count);
  }, [count]);
  
  return (
    <div>
      <div>Count: {count}</div>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <Todos todos={todos} />
    </div>
  );
}

// useCallback：函数记忆化
const Todos = ({ todos }) => {
  const handleAddTodo = useCallback(() => {
    // ...
  }, []);
  
  return (
    <div>
      {todos.map(todo => (
        <Todo key={todo.id} todo={todo} />
      ))}
      <button onClick={handleAddTodo}>Add Todo</button>
    </div>
  );
};

// 使用 useTransition 优先级调度
import { useTransition } from 'react';

function App() {
  const [isPending, startTransition] = useTransition();
  const [query, setQuery] = useState('');
  
  const handleChange = (e) => {
    setQuery(e.target.value);
    startTransition(() => {
      // 低优先级更新
      setSearchResults(e.target.value);
    });
  };
  
  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending && <div>Loading...</div>}
    </div>
  );
}
```

## 四、后端优化

### 1. 缓存策略

```javascript
// 使用 Redis 缓存
const redis = require('redis');
const client = redis.createClient();

async function getCachedData(key, fetchFn, ttl = 3600) {
  const cached = await client.get(key);
  if (cached) {
    return JSON.parse(cached);
  }
  
  const data = await fetchFn();
  await client.setEx(key, ttl, JSON.stringify(data));
  
  return data;
}

// HTTP 缓存头
app.get('/api/data', (req, res) => {
  const data = generateData();
  
  res.setHeader('Cache-Control', 'public, max-age=3600');
  res.setHeader('ETag', generateETag(data));
  res.setHeader('Last-Modified', new Date().toUTCString());
  
  res.json(data);
});

// 条件请求
app.get('/api/data', (req, res) => {
  const data = generateData();
  const etag = generateETag(data);
  
  if (req.headers['if-none-match'] === etag) {
    return res.sendStatus(304);
  }
  
  res.setHeader('ETag', etag);
  res.json(data);
});
```

### 2. 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

-- 复合索引
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- EXPLAIN 分析查询
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- 使用连接池
const { Pool } = require('pg');
const pool = new Pool({
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

async function query(text, params) {
  const client = await pool.connect();
  try {
    return await client.query(text, params);
  } finally {
    client.release();
  }
}

-- 避免 N+1 查询
-- ❌ 不好
-- SELECT * FROM users;
-- 然后对每个用户: SELECT * FROM orders WHERE user_id = ?

-- ✅ 好
SELECT u.*, o.* 
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

### 3. API 优化

```javascript
// 分页
app.get('/api/items', async (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 20;
  const offset = (page - 1) * limit;
  
  const [items, count] = await Promise.all([
    Item.find().skip(offset).limit(limit),
    Item.countDocuments()
  ]);
  
  res.json({
    items,
    pagination: {
      page,
      limit,
      total: count,
      pages: Math.ceil(count / limit)
    }
  });
});

// 字段选择
app.get('/api/users', async (req, res) => {
  const fields = req.query.fields?.split(',') || [];
  const projection = fields.length > 0 
    ? Object.fromEntries(fields.map(f => [f, 1])) 
    : {};
  
  const users = await User.find({}, projection);
  res.json(users);
});

// 压缩响应
const compression = require('compression');
app.use(compression());

// Gzip/Brotli 压缩
app.use(compression({
  level: 6,
  threshold: 1024,
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  }
}));
```

## 五、服务器配置优化

### 1. Nginx 配置

```nginx
http {
  # 启用 gzip 压缩
  gzip on;
  gzip_vary on;
  gzip_min_length 1024;
  gzip_types text/plain text/css text/xml text/javascript 
             application/javascript application/xml+rss application/json;
  
  # 启用 Brotli
  brotli on;
  brotli_comp_level 6;
  brotli_types text/plain text/css text/xml text/javascript
               application/javascript application/json;
  
  # 缓存静态资源
  server {
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
      expires 1y;
      add_header Cache-Control "public, immutable";
    }
    
    location ~* \.(html)$ {
      expires -1;
      add_header Cache-Control "no-cache";
    }
  }
  
  # 反向代理缓存
  proxy_cache_path /path/to/cache levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;
  
  server {
    location /api/ {
      proxy_cache my_cache;
      proxy_cache_valid 200 60m;
      proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
      proxy_cache_lock on;
      proxy_pass http://backend;
    }
  }
}
```

### 2. CDN 配置

```javascript
// 使用 CDN 加速静态资源
const cdnUrl = 'https://cdn.example.com';

const imageUrl = `${cdnUrl}/images/photo.jpg`;
const cssUrl = `${cdnUrl}/styles.css`;
const jsUrl = `${cdnUrl}/app.js`;

// Cloudflare 规则示例
// 缓存静态资源: *.jpg, *.css, *.js → 1 年
// 不缓存 HTML: *.html → 不缓存
```

## 六、性能监控与分析

### 1. 真实用户监控（RUM）

```javascript
// 自定义性能监控
class PerformanceMonitor {
  constructor() {
    this.metrics = [];
  }
  
  measure(name, fn) {
    const start = performance.now();
    const result = fn();
    const duration = performance.now() - start;
    
    this.metrics.push({ name, duration, timestamp: Date.now() });
    console.log(`${name} took ${duration.toFixed(2)}ms`);
    
    return result;
  }
  
  async measureAsync(name, fn) {
    const start = performance.now();
    const result = await fn();
    const duration = performance.now() - start;
    
    this.metrics.push({ name, duration, timestamp: Date.now() });
    console.log(`${name} took ${duration.toFixed(2)}ms`);
    
    return result;
  }
  
  sendToServer() {
    fetch('/api/metrics', {
      method: 'POST',
      body: JSON.stringify(this.metrics)
    });
  }
}

const monitor = new PerformanceMonitor();

// 使用
monitor.measure('renderList', () => {
  renderList();
});

await monitor.measureAsync('fetchData', async () => {
  await fetchData();
});
```

### 2. 使用 Sentry/New Relic

```javascript
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: 'your-dsn',
  tracesSampleRate: 1.0,
});

// 性能追踪
Sentry.startTransaction({
  name: 'My Transaction',
  op: 'test',
});

// 使用 New Relic
import newrelic from 'newrelic';

newrelic.setTransactionName('GET /api/data');
newrelic.incrementMetric('Custom/Metric');
```

## 七、性能优化检查清单

### 前端优化
- [ ] 代码分割和懒加载
- [ ] 资源压缩（gzip/brotli）
- [ ] 图片优化（格式、尺寸、懒加载）
- [ ] 字体优化（font-display、预加载）
- [ ] 预加载关键资源
- [ ] 减少重排重绘
- [ ] 虚拟列表（长列表）
- [ ] 防抖和节流
- [ ] React 优化（memo、useMemo、useCallback）

### 后端优化
- [ ] 数据库索引优化
- [ ] 查询优化（避免 N+1）
- [ ] 缓存策略（Redis、HTTP 缓存）
- [ ] API 分页和字段选择
- [ ] 响应压缩
- [ ] 连接池

### 服务器优化
- [ ] Nginx 缓存配置
- [ ] CDN 加速
- [ ] Gzip/Brotli 压缩
- [ ] 静态资源缓存

## 八、总结

性能优化核心要点：
- 测量和监控是基础
- 从加载性能开始优化
- 前端运行时优化
- 后端和数据库优化
- 服务器和 CDN 配置
- 持续监控和改进

性能优化是持续的过程，不是一次性的工作！
