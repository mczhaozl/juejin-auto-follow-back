# 当「多应用共享组件」成了刚需：我们从需求到模块联邦的落地小史

> 以真实项目需求为背景，讲我们如何从「NPM 发包、iframe 子应用」的坑里走出来，用 Webpack 5 的模块联邦实现多应用运行时共享组件，并给出落地要点与避坑小结。

---

## 一、需求从哪来：多产品线要共用一套「家当」

我们这边有一条业务线，同时维护着**中台配置端**、**运营活动页**、**数据看板** 等多个独立前端应用。这些应用技术栈统一（React + Webpack），但**各自独立仓库、独立部署**。产品希望：设计系统里的按钮、表格、图表组件能在各应用里**共用**，且**改一处、处处生效**，而不是每个项目 copy 一份或各维护各的。

换句话说：**多应用共享组件**成了刚需，而且要尽量**少耦合发版节奏**——中台发版不能绑死活动页的发版。

---

## 二、我们试过的方案与痛点

在接触模块联邦之前，我们试过两种常见做法，都遇到了明显的瓶颈。

### 2.1 方案一：NPM 发包

把设计系统打成 `@company/design-system` 发到内网 NPM，各应用 `npm install` 后按需引用。

**痛点**：

- **版本强耦合**：设计系统修个 bug 或加个组件，要发一版 NPM，各应用再升级依赖、再构建发布，链条长、节奏难对齐。
- **多应用不同步**：有的应用还在用旧版，有的已升级，线上会同时存在多版本，排查问题时要先看「当前应用装的是哪一版」。
- **发版心理负担**：小改动也要走发包流程，大家更倾向于在业务项目里 copy 一份改，时间一长又变成多份实现。

### 2.2 方案二：iframe 嵌子应用

把「组件展示页」做成独立应用，主应用用 iframe 嵌进去。

**痛点**：

- **隔离过重**：样式、主题、路由、登录态都要额外打通，通信靠 `postMessage`，心智负担大。
- **体验和性能**：多一层 iframe，布局、滚动、弹窗都要特殊处理；首屏多一次文档加载，观感上也容易「慢一截」。
- **不适合「组件级」复用**：我们更需要的是「在页面里嵌一个按钮、一个图表」，而不是「嵌一整页」，iframe 更适合整页级的隔离。

这两条路走下来，我们意识到：需要一种**运行时按需拉取、独立构建部署、又能像本地模块一样用**的机制。后来在 Webpack 5 的文档里看到了 **Module Federation（模块联邦）**，和我们要的场景非常契合。

---

## 三、模块联邦是什么：一句话 + 三个角色

**模块联邦**是 Webpack 5 内置的能力，让多个**独立构建、独立部署**的应用，在**运行时**像用本地模块一样加载彼此的代码。不用先发 NPM、不用 `npm install`，只要构建时配置好「谁暴露、谁消费」，运行时就能动态拉取并执行。

三个角色可以这么记：

| 角色 | 做什么 |
|------|--------|
| **Remote（远程应用）** | 通过 `exposes` 把组件/模块暴露出去，打包出 `remoteEntry.js`，供别人加载。 |
| **Host（宿主应用）** | 通过 `remotes` 配置 Remote 的入口地址，用 `import('remoteName/Button')` 消费。 |
| **shared** | 双方声明共享依赖（如 React），可配 `singleton: true`，保证只加载一份，避免多实例冲突。 |

我们落地的形态是：**设计系统**单独一个应用作为 Remote，打包并部署 `remoteEntry.js`；**中台、活动页、看板**等作为 Host，在需要的地方 `import('designSystem/Button')`，运行时从 CDN 拉取设计系统的 chunk，和本地代码一起跑在同一页面里。

---

## 四、我们怎么落地的：配置要点与坑

### 4.1 Remote 侧：暴露入口与 shared

设计系统项目里用 `ModuleFederationPlugin` 暴露组件，并和 Host 约定好 **shared**（React、ReactDOM 等）版本一致且设为单例，否则容易出现「Invalid hook call」之类的问题。

```javascript
const { ModuleFederationPlugin } = require('webpack').container;

// Remote 的 webpack 配置片段
new ModuleFederationPlugin({
    name: 'designSystem',
    filename: 'remoteEntry.js',
    exposes: {
        './Button': './src/Button.jsx',
        './Table': './src/Table.jsx',
    },
    shared: {
        react: { singleton: true, requiredVersion: '^18.0.0' },
        'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
    },
});
```

**注意**：`output.publicPath` 必须能让 Host 正确拼出所有 chunk 的完整 URL（我们生产环境用 CDN 域名），否则运行时会 404。

### 4.2 Host 侧：配置 remotes 与动态加载

各业务应用在 Webpack 里配置 `remotes` 指向设计系统的 `remoteEntry.js` 地址（开发环境用本机或内网地址，生产用 CDN），然后用 `React.lazy` + `Suspense` 加载远程组件，对业务代码来说就像在用异步组件。

```javascript
// Host 的 webpack 配置片段
new ModuleFederationPlugin({
    name: 'hostApp',
    remotes: {
        designSystem: 'designSystem@https://cdn.example.com/design-system/remoteEntry.js',
    },
    shared: {
        react: { singleton: true, requiredVersion: '^18.0.0' },
        'react-dom': { singleton: true, requiredVersion: '^18.0.0' },
    },
});
```

```jsx
// 业务里使用
const RemoteButton = lazy(() => import('designSystem/Button'));

<Suspense fallback={<Spin />}>
    <RemoteButton>来自设计系统</RemoteButton>
</Suspense>
```

### 4.3 我们踩过的坑

- **publicPath**：Remote 上线后若没配对，Host 拉 chunk 会 404，我们是在 CI 里把 Remote 的 `publicPath` 打成当前 CDN 前缀。
- **shared 版本**：Host 和 Remote 的 `requiredVersion` 要兼容，否则可能加载两份 React，导致 hook 报错；我们统一用 `^18.0.0` 并锁大版本。
- **CORS**：Remote 的静态资源要允许业务域名的 origin，我们 Nginx 里对 `remoteEntry.js` 和 chunk 加了对应 `Access-Control-Allow-Origin`。

---

## 五、结果与小结

落地模块联邦之后：设计系统**单独发版、单独部署**，各业务应用**不用改依赖、不用重新装包**，刷新页面即可拿到最新组件；多应用共享组件、发版解耦这两个目标都满足了。后续我们也在部分场景下用同一套机制做了「活动页作为 Remote、中台作为 Host」的集成，实现了一应用既可当 Host 也可当 Remote。

**小结几句**：

- **需求驱动**：多应用共享组件、又要独立发版时，NPM 发包和 iframe 各有短板，模块联邦的「运行时拉取 + 独立构建部署」很贴这类场景。
- **核心三件套**：Remote 用 **exposes** 暴露并产出 `remoteEntry.js`，Host 用 **remotes** 拉取并用 `import('remote/xx')` 消费，**shared** 配成单例避免多实例。
- **落地注意**：publicPath、shared 版本、CORS 三点配好，再配合 CDN 和 CI，线上就能稳定跑。

如果你也在做多应用组件共享或微前端选型，希望这篇「从需求到落地」的小史能给你一点参考。更细的配置与手把手 Demo 可以看 [Webpack 官方 Module Federation 文档](https://webpack.js.org/concepts/module-federation/) 和 [module-federation-examples](https://github.com/module-federation/module-federation-examples)。觉得有用的话，欢迎点赞、收藏或评论区聊聊你的场景。
