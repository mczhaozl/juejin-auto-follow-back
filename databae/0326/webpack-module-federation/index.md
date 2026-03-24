# Webpack 实战：利用 Module Federation 实现微前端架构的模块共享

> Module Federation（模块联邦）是 Webpack 5 最具革命性的特性。它允许不同的 Webpack 构建之间动态共享代码，无需将共享库发布到 npm。本文将带你通过一个实战案例，掌握这一微前端架构的核心技术。

## 一、背景：微前端的共享难题

在微前端架构中，我们经常需要在多个子应用之间共享同一个组件库或公共状态管理。

**传统方案：** 
- **npm 包**：更新缓慢，每次修改都需要重新发布并安装。
- **Git Submodules**：管理复杂，同步不便。
- **CDN 引入**：版本管理混乱，容易造成依赖冲突。

**Module Federation 的方案：** 
- **动态共享**：在运行时加载其他应用的模块，像调用本地模块一样。
- **版本解耦**：宿主应用不需要在构建时知道子应用的具体实现。
- **公共依赖自动合并**：多个应用共享同一个 React 实例，避免重复加载。

## 二、核心配置：webpack.config.js

假设我们有两个应用：`app1` (Host) 和 `app2` (Remote)。

### 1. Remote 端 (app2)：暴露模块
```javascript
// app2/webpack.config.js
const ModuleFederationPlugin = require("webpack/lib/container/ModuleFederationPlugin");

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: "app2",
      filename: "remoteEntry.js",
      exposes: {
        "./Button": "./src/components/Button",
      },
      shared: ["react", "react-dom"],
    }),
  ],
};
```

### 2. Host 端 (app1)：引用模块
```javascript
// app1/webpack.config.js
const ModuleFederationPlugin = require("webpack/lib/container/ModuleFederationPlugin");

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: "app1",
      remotes: {
        app2: "app2@http://localhost:3002/remoteEntry.js",
      },
      shared: ["react", "react-dom"],
    }),
  ],
};
```

## 三、在 React 中动态加载

在宿主应用中，我们可以像引入异步组件一样引入远程模块：

```javascript
import React, { lazy, Suspense } from "react";

const RemoteButton = lazy(() => import("app2/Button"));

function App() {
  return (
    <div>
      <h1>Host Application</h1>
      <Suspense fallback="Loading Button...">
        <RemoteButton />
      </Suspense>
    </div>
  );
}
```

## 四、最佳实践：Shared 配置

在 `shared` 配置中，建议显式指定版本要求：

```javascript
shared: {
  react: { singleton: true, requiredVersion: "^18.0.0" },
  "react-dom": { singleton: true, requiredVersion: "^18.0.0" },
}
```
- **singleton**: 确保整个应用只加载一个版本的库（如 React）。
- **requiredVersion**: 指定版本兼容范围，避免运行时崩溃。

## 五、总结

模块联邦（Module Federation）彻底打破了构建边界，为微前端架构提供了原生的、高性能的解决方案。

**如果你对 Vite 版本的模块联邦（Vite Federation）感兴趣，欢迎在评论区留言！**
