# 微前端架构完全指南：从原理到实战实现

## 一、微前端概述

### 1.1 什么是微前端
微前端是将前端应用拆分为更小、更易管理的独立部分的架构风格。

### 1.2 优势
- 独立部署与开发
- 技术栈灵活
- 增量升级
- 团队自治

---

## 二、Module Federation

### 2.1 Webpack 5 Module Federation

```javascript
// Container webpack.config.js
const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'container',
      remotes: {
        products: 'products@http://localhost:3001/remoteEntry.js',
        cart: 'cart@http://localhost:3002/remoteEntry.js'
      },
      shared: ['react', 'react-dom']
    })
  ]
};

// Products microapp webpack.config.js
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'products',
      filename: 'remoteEntry.js',
      exposes: {
        './ProductsIndex': './src/bootstrap'
      },
      shared: ['react', 'react-dom']
    })
  ]
};
```

### 2.2 容器应用

```jsx
// container/src/App.jsx
import { lazy, Suspense } from 'react';

const ProductsLazy = lazy(() => import('products/ProductsIndex'));

function App() {
  return (
    <div>
      <h1>Container App</h1>
      <Suspense fallback={<div>Loading...</div>}>
        <ProductsLazy />
      </Suspense>
    </div>
  );
}

export default App;
```

### 2.3 产品微应用

```jsx
// products/src/bootstrap.jsx
import React from 'react';
import ReactDOM from 'react-dom';

function Products() {
  return (
    <div>
      <h2>Products Microapp</h2>
      <ul>
        <li>Product 1</li>
        <li>Product 2</li>
      </ul>
    </div>
  );
}

ReactDOM.render(<Products />, document.getElementById('root'));

export default Products;
```

---

## 三、Single SPA

### 3.1 根配置

```javascript
import { registerApplication, start } from 'single-spa';

registerApplication({
  name: '@myorg/products',
  app: () => System.import('@myorg/products'),
  activeWhen: ['/products']
});

registerApplication({
  name: '@myorg/cart',
  app: () => System.import('@myorg/cart'),
  activeWhen: ['/cart']
});

start();
```

### 3.2 微应用配置

```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import singleSpaReact from 'single-spa-react';
import Root from './root.component';

const lifecycles = singleSpaReact({
  React,
  ReactDOM,
  rootComponent: Root
});

export const { bootstrap, mount, unmount } = lifecycles;
```

---

## 四、Iframe 方案

```html
<iframe src="http://microapp1:3001" style="border: none; width: 100%; height: 500px;"></iframe>

<!-- 通信 -->
<script>
  window.addEventListener('message', (event) => {
    if (event.origin === 'http://microapp1:3001') {
      console.log('Message from microapp:', event.data);
    }
  });
</script>
```

---

## 五、路由集成

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/products" element={<ProductsApp />} />
        <Route path="/cart" element={<CartApp />} />
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 六、状态管理

### 6.1 共享状态

```javascript
// container/src/store.js
import { createStore } from 'redux';

const initialState = { cart: [] };

function reducer(state = initialState, action) {
  switch (action.type) {
    case 'ADD_TO_CART':
      return { ...state, cart: [...state.cart, action.payload] };
    default:
      return state;
  }
}

export const store = createStore(reducer);
```

### 6.2 事件总线

```javascript
class EventBus {
  constructor() {
    this.events = {};
  }
  
  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }
  
  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(callback => callback(data));
    }
  }
}

export const eventBus = new EventBus();
```

---

## 七、样式隔离

### 7.1 CSS Modules

```css
/* Products.module.css */
.productsContainer {
  background: white;
  padding: 20px;
}

/* 使用 */
import styles from './Products.module.css';

function Products() {
  return <div className={styles.productsContainer}>Products</div>;
}
```

### 7.2 Shadow DOM

```javascript
class MicroApp extends HTMLElement {
  connectedCallback() {
    const shadow = this.attachShadow({ mode: 'open' });
    
    const style = document.createElement('style');
    style.textContent = `
      .container {
        background: white;
      }
    `;
    
    const content = document.createElement('div');
    content.className = 'container';
    content.textContent = 'Microapp content';
    
    shadow.appendChild(style);
    shadow.appendChild(content);
  }
}

customElements.define('micro-app', MicroApp);
```

---

## 八、部署与 CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy Microapps

on:
  push:
    branches: [main]

jobs:
  deploy-products:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: cd products && npm ci && npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          deploy_key: ${{ secrets.ACTIONS_DEPLOY_KEY }}
  deploy-cart:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: cd cart && npm ci && npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          deploy_key: ${{ secrets.ACTIONS_DEPLOY_KEY }}
```

---

## 九、性能优化

```javascript
// 预加载
<link rel="preload" href="http://microapp1:3001/remoteEntry.js" as="script" />

// 懒加载
const MicroApp = React.lazy(() => import('microapp/App'));
```

---

## 十、错误边界

```jsx
class MicroAppErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  
  render() {
    if (this.state.hasError) {
      return <div>Microapp failed to load</div>;
    }
    return this.props.children;
  }
}
```

---

## 十一、最佳实践

1. 使用 Module Federation 或 Single SPA
2. 实现样式隔离
3. 设计好微应用间通信机制
4. 独立部署每个微应用
5. 提供错误处理和降级方案

---

## 十二、总结

微前端架构能让大型前端应用更易维护，但需要合理设计应用边界和通信方式。
