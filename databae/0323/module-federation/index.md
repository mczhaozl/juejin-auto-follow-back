# Webpack 5 Module Federation：微前端的最佳实践

> 模块联邦从入门到实战，实现跨应用共享组件

---

## 一、Module Federation 是什么

Webpack 5 的革命性特性，让多个独立应用能够共享代码。

### 解决的问题

- 重复打包相同依赖
- 跨应用共享组件困难
- 微前端集成复杂

---

## 二、基础配置

### Host 应用

```javascript
// webpack.config.js
const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remote      remohared: {
    react: { singleton: true },
    'react-dom': { singleton: true },
  },
}),
```

---

## 三、使用远程组件

```typescript
// Host 应用
import React, { lazy, Suspense } from 'react';

const RemoteButton = lazy(() => import('app1/Button'));

function App() {
  return (
    <Suspense fallback="Loading...">
      <RemoteButton />
    </Suspense>
  );
}
```

---

## 四、实战场景

### 场景 1：共享组件库

```javascript
// 组件库应用
new ModuleFederationPlugin({
  name: 'components',
  exposes: {
    './Button': './src/Button',
    './Input': './src/Input',
    './Modal': './src/Modal',
  },
}),
```

### 场景 2：微前端架构

```javascript
// 主应用
remotes: {
  dashboard: 'dashboard@http://localhost:3001/remoteEntry.js',
  settings: 'settings@http://localhost:3002/remoteEntry.js',
}
```

---

## 五、最佳实践

1. **版本管理**：使用 singleton 确保依赖唯一
2. **类型安全**：生成类型声明文件
3. **错误处理**：使用 Error Boundary
4. **性能优化**：按需加载

---

## 总结

Module Federation 是微前端的最佳方案，它让跨应用共享代码变得简单。

如果这篇文章对你有帮助，欢迎点赞收藏！
