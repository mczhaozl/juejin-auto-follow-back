# 微前端实战：qiankun 框架从入门到精通

> 手把手教你掌握微前端架构，使用 qiankun 框架实现应用拆分为独立部署，提升团队协作效率。

## 一、微前端简介

### 1.1 什么是微前端

微前端是将大型应用拆分为独立小应用的技术：

- **独立开发**：各团队独立开发
- **独立部署**：单独部署
- **技术无关**：React、Vue、Angular 皆可

### 1.2 为什么需要微前端

| 传统前端 | 微前端 |
|---------|--------|
| 单体应用 | 应用拆分 |
| 耦合高 | 低耦合 |
| 部署慢 | 独立部署 |

## 二、qiankun 基础

### 2.1 主应用配置

```javascript
import { registerMicroApps, start } from 'qiankun';

registerMicroApps([
  {
    name: 'react-app',
    entry: '//localhost:3001',
    container: '#container',
    activeRule: '/react'
  },
  {
    name: 'vue-app',
    entry: '//localhost:3002',
    container: '#container',
    activeRule: '/vue'
  }
]);

start();
```

### 2.2 子应用配置

**React 子应用**：

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

function render(props) {
  const { container } = props;
  ReactDOM.createRoot(container ? container.querySelector('#root') : document.getElementById('root'))
    .render(<App />);
}

if (!window.__POWERED_BY_QIANKUN__) {
  render({});
}

export async function bootstrap() {}
export async function mount(props) {
  render(props);
}
export async function unmount(props) {}
```

**Vue 子应用**：

```javascript
import { createApp } from 'vue';
import App from './App.vue';

let app;

export function bootstrap() {}
export async function mount(props) {
  app = createApp(App);
  app.mount(props.container ? props.container.querySelector('#app') : '#app');
}
export async function unmount() {
  if (app) {
    app.unmount();
  }
}
```

## 三、通信机制

### 3.1 主应用发送消息

```javascript
import { initGlobalState } from 'qiankun';

const state = { count: 1 };
const { onGlobalStateChange, setGlobalState } = initGlobalState(state);

onGlobalStateChange((state, prev) => {
  console.log('变化:', prev, '→', state);
});

// 发送消息
setGlobalState({ count: 2 });
```

### 3.2 子应用接收消息

```javascript
export async function mount(props) {
  props.onGlobalStateChange((state, prev) => {
    console.log('收到:', state);
  });
}
```

## 四、样式隔离

### 4.1 CSS Module

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {
              modules: true
            }
          }
        ]
      }
    ]
  }
};
```

### 4.2 qiankun 沙箱

```javascript
import { start } from 'qiankun';

start({
  sandbox: {
    strictStyleIsolation: true
  }
});
```

## 五、路由处理

### 5.1 主应用路由

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/react/*" element={<MicroApp />} />
        <Route path="/vue/*" element={<MicroApp />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### 5.2 子应用路由

**React 静态路由**：

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';

export function render() {
  ReactDOM.createRoot(document.getElementById('root')).render(
    <BrowserRouter basename={window.__POWERED_BY_QIANKUN__ ? '/react' : '/'}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## 六、实战案例

### 6.1 完整配置

```javascript
// 主应用
import { registerMicroApps, start } from 'qiankun';

const apps = [
  {
    name: 'order-app',
    entry: process.env.VUE_APP_ORDER_ENTRY,
    container: '#micro-container',
    activeRule: '/order',
    props: { routerBase: '/order' }
  },
  {
    name: 'user-app',
    entry: process.env.VUE_APP_USER_ENTRY,
    container: '#micro-container',
    activeRule: '/user',
    props: { routerBase: '/user' }
  }
];

registerMicroApps(apps);

start({
  prefetch: true,
  jsSandbox: true,
  singular: true
});
```

### 6.2 环境变量

```bash
# .env.development
VUE_APP_ORDER_ENTRY=//localhost:7101
VUE_APP_USER_ENTRY=//localhost:7102
```

## 七、总结

qiankun 核心要点：

1. **registerMicroApps**：注册子应用
2. **生命周期**：bootstrap/mount/unmount
3. **通信**：initGlobalState
4. **样式隔离**：沙箱机制
5. **路由**：basename 处理

掌握这些，微前端不再难！

---

**推荐阅读**：
- [qiankun 官方文档](https://qiankun.umijs.org/)

**如果对你有帮助，欢迎点赞收藏！**
