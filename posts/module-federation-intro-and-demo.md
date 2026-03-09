# 模块联邦（Module Federation）详解：从概念到手把手 Demo

> 一文搞清 Webpack 5 的模块联邦是什么、能解决什么问题；并手把手用 Host + Remote 两个小项目跑通一个「远程组件」Demo，可直接按步骤复现。

---

## 一、模块联邦是什么

**模块联邦（Module Federation）** 是 **Webpack 5** 内置的能力，让多个**独立构建、独立部署**的前端应用，在**运行时**像用本地模块一样去加载彼此的代码。也就是说：应用 A 不用把组件发到 NPM，应用 B 也不用先 `npm install`，只要在构建时配置好「谁暴露、谁消费」，运行时 B 就能动态拉取 A 暴露的模块并执行。

**和常见方案的差异**：

- **NPM 发包**：需要先发布、再安装、再构建，版本强耦合，发版节奏绑在一起。
- **iframe / 微前端子应用**：隔离强但通信麻烦，样式、路由、性能都有一堆坑。
- **模块联邦**：运行时按需拉取远程入口（如 `remoteEntry.js`），通过 **exposes** 暴露、**remotes** 消费，共享依赖（如 React）可配成单例，**独立构建、独立部署**，适合微前端、跨应用组件共享、多团队协作。

一句话：**把「远程应用」当成一个「模块容器」，按需拉取其中暴露的模块，并和当前应用共享同一份依赖。**

---

## 二、有什么用、典型场景

- **微前端**：主应用（Host）集成多个子应用（Remote），子应用可独立开发、独立上线，主应用只负责拉取对应 `remoteEntry.js` 和路由。
- **跨应用共享组件/工具**：设计系统、公共组件库以 Remote 形式部署，业务应用按需 `import('designSystem/Button')`，无需发 NPM 也能同步更新。
- **多团队并行**：各团队维护自己的 Remote，Host 通过 remotes 配置按环境指向不同地址，便于灰度与 A/B 测试。
- **渐进式拆分**：老项目逐步拆成多个 Remote，新功能用 Host 动态加载，无需一次性重构。

---

## 三、核心概念与官方链接

| 概念 | 说明 |
|------|------|
| **Remote（远程应用）** | 通过 `ModuleFederationPlugin` 的 **exposes** 暴露模块，打包出 `remoteEntry.js`，供别人加载。 |
| **Host（宿主应用）** | 通过 **remotes** 配置要用的 Remote 的入口 URL，运行时用 `import('remoteName/ExposedModule')` 消费。 |
| **shared** | 双方声明共享依赖（如 react、react-dom），可配 `singleton: true` 保证只加载一份，避免多实例冲突。 |

**官方与社区**：

- Webpack 文档：[Module Federation](https://webpack.js.org/concepts/module-federation/)
- 官方示例仓库：[module-federation/module-federation-examples](https://github.com/module-federation/module-federation-examples)（含 React、Vue、多应用等）

---

## 四、环境与准备

- **Node**：建议 16+，确保能跑 Webpack 5。
- **两个独立项目**：一个当 **Remote**（暴露组件），一个当 **Host**（消费远程组件）。下面用 React 18 + Webpack 5 举例，端口为 Remote **3002**、Host **3001**。

---

## 五、手把手 Demo

### 5.1 Remote 项目（端口 3002）

**1. 初始化并安装依赖**

```bash
mkdir remote-app && cd remote-app
npm init -y
npm i react react-dom
npm i -D webpack webpack-cli webpack-dev-server html-webpack-plugin babel-loader @babel/core @babel/preset-react
```

**2. 暴露一个简单组件**

`src/Button.jsx`：

```jsx
import React from 'react';

export function Button({ children, onClick }) {
  return <button onClick={onClick}>{children}</button>;
}
```

**3. 入口与 HTML**

`public/index.html` 里有一个 `<div id="root"></div>` 即可。`src/index.js` 若需要本地预览 Remote，可写：

```javascript
import React from 'react';
import { createRoot } from 'react-dom/client';
import { Button } from './Button.jsx';
createRoot(document.getElementById('root')).render(<Button>Remote 本地预览</Button>);
```

否则只保留空入口也行，Host 只关心暴露的 `./Button`。接着在项目根目录新建 `webpack.config.js`：

```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { ModuleFederationPlugin } = require('webpack').container;

module.exports = {
  entry: './src/index.js',
  mode: 'development',
  devServer: { port: 3002, historyApiFallback: true },
  output: {
    publicPath: 'http://localhost:3002/',
    clean: true,
  },
  module: {
    rules: [
      { test: /\.jsx?$/, use: 'babel-loader', exclude: /node_modules/ },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({ template: './public/index.html' }),
    new ModuleFederationPlugin({
      name: 'remoteApp',
      filename: 'remoteEntry.js',
      exposes: {
        './Button': './src/Button.jsx',
      },
      shared: {
        react: { singleton: true, requiredVersion: '^18.0.0', eager: true },
        'react-dom': { singleton: true, requiredVersion: '^18.0.0', eager: true },
      },
    }),
  ],
};
```

**说明**：`eager: true` 表示把该依赖**同步**打进当前应用的 bundle 并放入 shared scope，不单独异步加载。这样 Remote 的 `remoteEntry.js` 被 Host 拉取时，Host 里已经存在 `react` / `react-dom`，可避免报错「Shared module react doesn't exist in shared scope default」。

**4. 启动 Remote**

```bash
npx webpack serve
```

浏览器访问 `http://localhost:3002`，确认能打开且控制台无报错；同时 `http://localhost:3002/remoteEntry.js` 可访问。

---

### 5.2 Host 项目（端口 3001）

**1. 初始化并安装依赖**

```bash
mkdir host-app && cd host-app
npm init -y
npm i react react-dom
npm i -D webpack webpack-cli webpack-dev-server html-webpack-plugin babel-loader @babel/core @babel/preset-react
```

**2. 入口与消费远程组件**

`src/index.js`：`import React from 'react'; import { createRoot } from 'react-dom/client'; import { App } from './App.jsx'; createRoot(document.getElementById('root')).render(<App />);`  
`public/index.html`：含 `<div id="root"></div>` 即可。

`src/App.jsx`：

```jsx
import React, { Suspense, lazy } from 'react';

const RemoteButton = lazy(() => import('remoteApp/Button'));

export function App() {
  return (
    <div>
      <h1>Host 应用</h1>
      <Suspense fallback={<span>加载远程组件中…</span>}>
        <RemoteButton onClick={() => alert('来自 Remote')}>
          远程按钮
        </RemoteButton>
      </Suspense>
    </div>
  );
}
```

**3. Babel 配置**

在 Host 根目录建 `.babelrc`：`{ "presets": ["@babel/preset-react"] }`（Remote 同样需要，以便编译 JSX）。

**4. Host 的 webpack 配置**

```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { ModuleFederationPlugin } = require('webpack').container;

module.exports = {
  entry: './src/index.js',
  mode: 'development',
  devServer: { port: 3001, historyApiFallback: true },
  output: { publicPath: 'http://localhost:3001/', clean: true },
  module: {
    rules: [
      { test: /\.jsx?$/, use: 'babel-loader', exclude: /node_modules/ },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({ template: './public/index.html' }),
    new ModuleFederationPlugin({
      name: 'hostApp',
      remotes: {
        remoteApp: 'remoteApp@http://localhost:3002/remoteEntry.js',
      },
      shared: {
        react: { singleton: true, requiredVersion: '^18.0.0', eager: true },
        'react-dom': { singleton: true, requiredVersion: '^18.0.0', eager: true },
      },
    }),
  ],
};
```

**说明**：Host 侧同样给 `react` / `react-dom` 加上 `eager: true`，保证 Host 启动时就把 React 放进 shared scope，Remote 加载时能直接复用。

**5. 启动 Host**

先保持 Remote 在 3002 运行，再在 Host 目录执行：

```bash
npx webpack serve
```

访问 `http://localhost:3001`，页面应出现「Host 应用」和「远程按钮」；点击按钮能弹出「来自 Remote」，即说明 Host 已正确加载 Remote 暴露的 `Button`。

---

## 六、关键点与注意点

- **publicPath**：Remote 的 `output.publicPath` 必须能让 Host 正确拼出 chunk 的完整 URL（开发时用 `http://localhost:3002/`），否则运行时加载 chunk 会 404。
- **shared 与版本**：Host 和 Remote 的 `shared` 尽量一致，`requiredVersion` 与本地安装的版本兼容；`singleton: true` 保证 React 只加载一份，避免「Invalid hook call」等问题。
- **「Shared module react doesn't exist in shared scope default」**：若出现此报错，多半是 Remote 加载时 Host 的 shared scope 里还没有 react。给 `react`、`react-dom` 加上 **`eager: true`**（两端都加），让它们同步打进 bundle 并放入 shared scope，Remote 再加载时就能从 Host 拿到 react。
- **CORS**：开发时 `webpack-dev-server` 默认允许跨域；若 Remote 是单独域名/端口，需保证 Remote 服务端允许 Host 的 origin。
- **生产环境**：remotes 的 URL 改为线上地址（如 CDN），例如 `remoteApp@https://cdn.example.com/remote-app/remoteEntry.js`。
- **一个应用既可当 Host 也可当 Remote**：同时配置 `exposes` 和 `remotes` 即可。

---

## 七、总结

- **模块联邦**是 Webpack 5 的「运行时模块共享」能力：Remote 通过 **exposes** 暴露模块并产出 `remoteEntry.js`，Host 通过 **remotes** 拉取并 `import('remoteName/ExposedModule')` 使用；**shared** 可配 React 等依赖为单例，避免重复加载与冲突。
- 适合**微前端、跨应用组件共享、多团队独立发布**；与 NPM 发包、iframe 子应用相比，更灵活、可独立构建部署。
- 手把手要点：Remote 先跑在 3002 并保证 `remoteEntry.js` 可访问 → Host 在 3001 配置 remotes 指向该 URL → 两边 **shared** 一致并启用 **singleton** → 用 **React.lazy + Suspense** 加载远程组件。

按上面步骤即可在本地跑通一个最小 Demo；再根据需要扩展更多 exposes、多个 Remote 或生产环境 URL。若对你有用，欢迎点赞、收藏或评论区交流你的使用场景。
