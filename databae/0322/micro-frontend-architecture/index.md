# 微前端架构实战：从单体应用到微前端架构的演进

> 深入解析微前端架构设计，从单体应用到微前端架构的演进，实现前端应用的模块化、独立部署和团队自治。

---

## 一、微前端架构概述

### 1.1 什么是微前端

微前端是一种将前端应用拆分为多个独立、可独立开发、独立部署、独立运行的小型应用，然后通过某种方式组合成一个完整应用的架构模式。

### 1.2 为什么需要微前端

```typescript
// 传统单体应用的问题
class MonolithicApp {
  // 1. 代码库庞大，构建缓慢
  // 2. 团队协作困难
  // 3. 技术栈升级困难
  // 4. 部署风险高
  // 5. 技术栈锁定
}

// 微前端解决方案
class MicroFrontend {
  // 1. 独立开发：每个团队可以独立开发
  // 2. 独立部署：每个应用可以独立部署
  // 3. 技术栈自由：不同团队可以使用不同技术栈
  // 4. 增量升级：可以逐步升级技术栈
}
```

## 二、微前端架构模式

### 2.1 架构模式对比

```typescript
// 1. 服务端组合模式
class ServerSideComposition {
  // 服务端渲染时组合
  // 优点：SEO友好，首屏加载快
  // 缺点：服务端压力大，技术栈耦合
}

// 2. 构建时组合
class BuildTimeComposition {
  // 构建时组合
  // 优点：性能好，技术栈统一
  // 缺点：构建复杂，部署耦合
}

// 3. 运行时组合（微前端）
class RuntimeComposition {
  // 运行时动态加载
  // 优点：独立部署，技术栈无关
  // 缺点：通信复杂，性能开销
}
```

### 2.2 微前端架构模式

```typescript
// 1. 基座模式（Single-SPA）
class SingleSPA {
  registerApplication(
    appName: string,
    app: () => Promise<any>,
    activeWhen: (location: Location) => boolean
  ) {
    // 注册微应用
  }
}

// 2. 模块联邦（Webpack 5）
class ModuleFederation {
  constructor() {
    // 模块联邦配置
    this.remotes = {
      app1: 'app1@http://localhost:3001/remoteEntry.js',
      app2: 'app2@http://localhost:3002/remoteEntry.js'
    };
  }
}

// 3. iframe 集成
class IframeIntegration {
  // 使用iframe隔离
  // 优点：完全隔离，技术栈无关
  // 缺点：通信复杂，性能开销
}
```

## 三、微前端实现方案

### 3.1 基于Web Components的实现

```typescript
// 基于Web Components的微前端
class MicroFrontendApp extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.loadApp();
  }
  
  async loadApp() {
    // 动态加载微应用
    const app = await this.loadAppBundle();
    this.shadowRoot.innerHTML = app;
  }
  
  async loadAppBundle() {
    // 动态加载微应用
    const response = await fetch(this.getAttribute('src'));
    return response.text();
  }
}

customElements.define('micro-app', MicroFrontendApp);
```

### 3.2 基于Module Federation的实现

```javascript
// webpack.config.js - 主应用
module.exports = {
  // 主应用配置
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      remotes: {
        app1: 'app1@http://localhost:3001/remoteEntry.js',
        app2: 'app2@http://localhost:3002/remoteEntry.js'
      },
      shared: {
        react: { singleton: true, requiredVersion: '^17.0.0' },
        'react-dom': { singleton: true, requiredVersion: '^17.0.0' }
      }
    })
  ]
};

// 微应用配置
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'app1',
      filename: 'remoteEntry.js',
      exposes: {
        './App': './src/App'
      },
      shared: {
        react: { singleton: true },
        'react-dom': { singleton: true }
      }
    })
  ]
};
```

## 四、路由与状态管理

### 4.1 路由配置

```typescript
// 主应用路由配置
const routes = [
  {
    path: '/app1/*',
    loadApp: () => import('app1/App'),
    activeWhen: (location) => location.pathname.startsWith('/app1')
  },
  {
    path: '/app2/*',
    loadApp: () => import('app2/App'),
    activeWhen: (location) => location.pathname.startsWith('/app2')
  }
];

// 路由管理器
class RouterManager {
  private routes: Route[];
  private currentApp: string | null = null;
  
  constructor(routes: Route[]) {
    this.routes = routes;
    this.setupRouter();
  }
  
  setupRouter() {
    // 监听路由变化
    window.addEventListener('popstate', this.handleRouteChange);
    window.addEventListener('hashchange', this.handleRouteChange);
    
    // 初始路由
    this.handleRouteChange();
  }
  
  handleRouteChange() {
    const path = window.location.pathname;
    
    for (const route of this.routes) {
      if (route.activeWhen({ pathname: path })) {
        this.loadApp(route);
        break;
      }
    }
  }
  
  async loadApp(route: Route) {
    if (this.currentApp === route.name) return;
    
    // 卸载当前应用
    if (this.currentApp) {
      this.unmountApp(this.currentApp);
    }
    
    // 加载新应用
    const app = await route.loadApp();
    this.mountApp(app);
    this.currentApp = route.name;
  }
}
```

### 4.2 状态管理

```typescript
// 跨应用状态管理
class MicroFrontendState {
  private state: Record<string, any> = {};
  private listeners: Function[] = [];
  
  // 共享状态
  setState(key: string, value: any) {
    this.state[key] = value;
    this.notifyListeners();
  }
  
  getState(key: string) {
    return this.state[key];
  }
  
  subscribe(listener: Function) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
  
  private notifyListeners() {
    this.listeners.forEach(listener => listener(this.state));
  }
}

// 使用发布-订阅模式进行应用间通信
class EventBus {
  private events: Map<string, Function[]> = new Map();
  
  emit(event: string, data?: any) {
    const listeners = this.events.get(event) || [];
    listeners.forEach(callback => callback(data));
  }
  
  on(event: string, callback: Function) {
    if (!this.events.has(event)) {
      this.events.set(event, []);
    }
    this.events.get(event)!.push(callback);
  }
}
```

## 五、样式与样式隔离

### 5.1 CSS隔离方案

```css
/* 使用CSS Modules */
/* 主应用样式 */
:host {
  /* 主应用样式 */
}

/* 使用Shadow DOM实现样式隔离 */
.shadow-host {
  /* 样式隔离 */
}

/* 使用CSS-in-JS */
const styles = css`
  .container {
    padding: 20px;
  }
  
  .button {
    background: ${theme.primary};
  }
`;
```

### 5.2 样式隔离策略

```typescript
// 1. CSS命名空间
const styles = `
  .app1-button { /* 应用1的按钮样式 */ }
  .app2-button { /* 应用2的按钮样式 */ }
`;

// 2. Shadow DOM
class MicroFrontendElement extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  connectedCallback() {
    this.shadowRoot!.innerHTML = `
      <style>
        /* 样式被隔离在Shadow DOM中 */
        .button { color: blue; }
      </style>
      <button class="button">Click me</button>
    `;
  }
}

// 3. CSS-in-JS
const styled = {
  button: styled.button`
    background: ${props => props.primary ? 'blue' : 'gray'};
    color: white;
    padding: 10px 20px;
  `
};
```

## 六、构建与部署

### 6.1 独立构建配置

```javascript
// webpack.config.js
module.exports = {
  output: {
    // 使用contenthash确保缓存更新
    filename: '[name].[contenthash:8].js',
    chunkFilename: '[name].[contenthash:8].chunk.js'
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    }
  }
};
```

### 6.2 部署策略

```yaml
# docker-compose.yml
version: '3.8'
services:
  main-app:
    build: ./main-app
    ports:
      - "3000:80"
    depends_on:
      - app1
      - app2
  
  app1:
    build: ./app1
    environment:
      PUBLIC_URL: http://app1.local
      
  app2:
    build: ./app2
    environment:
      PUBLIC_URL: http://app2.local

# Nginx配置
server {
    listen 80;
    server_name app.example.com;
    
    location / {
        proxy_pass http://main-app:3000;
    }
    
    location /app1/ {
        proxy_pass http://app1:3001;
    }
    
    location /app2/ {
        proxy_pass http://app2:3002;
    }
}
```

## 七、性能优化

### 7.1 代码分割与懒加载

```javascript
// 动态导入实现懒加载
const App1 = React.lazy(() => import('app1/App'));
const App2 = React.lazy(() => import('app2/App'));

// 预加载策略
const preloadApp = (appName) => {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = `/apps/${appName}/bundle.js`;
  link.as = 'script';
  document.head.appendChild(link);
};

// 按需加载
const loadApp = async (appName) => {
  const app = await import(/* webpackChunkName: "app" */ `./apps/${appName}`);
  return app;
};
```

### 7.2 缓存策略

```typescript
// 缓存管理
class AssetCache {
  private cache = new Map<string, any>();
  
  async getOrLoad(url: string): Promise<any> {
    if (this.cache.has(url)) {
      return this.cache.get(url);
    }
    
    const response = await fetch(url);
    const data = await response.text();
    this.cache.set(url, data);
    return data;
  }
  
  // 版本化缓存
  getCacheKey(url: string, version: string) {
    return `${url}?v=${version}`;
  }
}
```

## 八、监控与错误处理

### 8.1 性能监控

```typescript
class PerformanceMonitor {
  private metrics = new Map();
  
  startMonitoring() {
    // 监控应用加载时间
    performance.mark('app-start');
    
    // 监控资源加载
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        this.recordMetric(entry);
      }
    });
    
    observer.observe({ entryTypes: ['resource', 'paint', 'largest-contentful-paint'] });
  }
  
  recordError(error: Error, context: any) {
    // 记录错误到监控系统
    console.error('Microfrontend Error:', error, context);
  }
}
```

### 8.2 错误边界

```typescript
class ErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    // 记录错误
    console.error('Microfrontend Error:', error, errorInfo);
    
    // 上报错误
    this.reportError(error);
  }
  
  render() {
    if (this.state.hasError) {
      return <FallbackUI />;
    }
    return this.props.children;
  }
}
```

## 九、最佳实践

### 9.1 开发规范

```typescript
// 1. 统一的API接口
interface MicroFrontendAPI {
  mount: (container: HTMLElement, props: any) => void;
  unmount: () => void;
  updateProps: (props: any) => void;
}

// 2. 通信协议
interface MicroFrontendContract {
  version: string;
  mount: (container: HTMLElement, props: any) => void;
  unmount: () => void;
  update: (props: any) => void;
}

// 3. 错误处理
class ErrorHandler {
  static handleError(error: Error, context: string) {
    console.error(`[${context}]`, error);
    // 上报错误
    this.reportError(error);
  }
}
```

### 9.2 部署策略

```yaml
# 部署配置
deploy:
  strategy: canary
  canary:
    steps:
      - deploy: 10% traffic
      - monitor: 5m
      - deploy: 50% traffic
      - monitor: 10m
      - deploy: 100%
  
  rollback:
    on_error: auto_rollback
    timeout: 5m
```

## 十、总结

微前端架构通过将大型前端应用拆分为多个独立的小型应用，实现了：

1. **独立开发**：团队可以独立开发、测试和部署
2. **技术栈自由**：不同团队可以使用不同的技术栈
3. **增量升级**：可以逐步升级技术栈
4. **独立部署**：每个微前端可以独立部署
5. **容错性**：一个应用的错误不会影响整个系统

通过合理的架构设计和工具支持，微前端可以帮助大型团队更高效地协作，提高开发效率和系统稳定性。