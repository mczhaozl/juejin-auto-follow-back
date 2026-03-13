# Vite 原理与生态：从 ESM 开发服务器到 Rollup 构建的完整链路

> 开发阶段 ESM 按需编译、预构建、HMR，生产阶段 Rollup 打包与插件生态，一篇当 Vite 说明书用。

---

## 一、为什么是 Vite

传统打包器（如 Webpack）的流程是：**先整体打包再启动 dev**，项目一大，冷启动和 HMR 都会变慢。Vite 的思路是：**开发时用浏览器原生 ESM**，按需请求文件，服务器按需编译（如 TS、JSX、Vue），这样启动几乎是秒开，热更新只涉及改动的模块。

生产环境则仍需要打包（为了兼容、 Tree-shaking、分块等），Vite 选用 **Rollup** 做生产构建，所以你会看到「开发一套、生产一套」：开发是 ESM 服务器，生产是 Rollup 管线。

## 二、开发阶段：ESM 与按需编译

### 2.1 入口与依赖解析

`index.html` 作为入口，通过 `<script type="module" src="/src/main.ts">` 引用应用入口。浏览器请求 `/src/main.ts`，Vite 收到请求后：

- 若是 **裸模块**（如 `import vue from 'vue'`），会重写为 `/node_modules/.vite/deps/vue.js` 这类**预构建后的路径**。
- 若是项目内文件（如 `./App.vue`），按需编译（TS → JS、Vue SFC → JS 等）再返回。

所以**首屏只编译用到的文件**，而不是整个项目，这是启动快的原因。

### 2.2 预构建（Dependency Pre-Bundling）

`node_modules` 里很多包是 CommonJS 或有很多小文件，浏览器无法直接跑。Vite 会用 **esbuild** 把依赖预构建成少量 ESM 文件（通常一个包一个），并做**强缓存**（根据 lockfile 的 hash 判断是否要重建）。预构建后，裸模块的 import 会被解析到这些产物，请求数少、格式统一。

### 2.3 HMR（热更新）

Vite 通过 **WebSocket** 和客户端建立连接。文件变更时，服务器推一条「哪个模块变了」的消息，客户端用 `import.meta.hot` 的 API 做**模块替换**或**回调**，只更新改动的子树，不整页刷新。对 Vue/React 等框架，Vite 内置或通过插件做了「组件级」HMR，体验接近「改代码即见效果」。

## 三、生产构建：Rollup 管线

`vite build` 走的是 **Rollup**：入口是应用入口（或库入口），Rollup 做依赖分析、Tree-shaking、分块（code splitting）、生成 asset。Vite 在 Rollup 外面包了一层配置转换（如把 `vite.config` 转成 Rollup 能用的选项）和插件适配，所以很多 Rollup 插件也能在 Vite 里用。

**和开发的差异**：开发是「单文件编译 + 浏览器 ESM」，生产是「整包分析 + 打包」。所以开发很快，生产则和传统打包器类似，重在 Tree-shaking 和分块策略。

## 四、配置要点

- **根目录**：默认以项目根为根，可通过 `root` 改。
- **别名**：`resolve.alias`，和 Webpack 类似。
- **环境变量**：`import.meta.env`，以 `VITE_` 开头的才会暴露给客户端。
- **插件**：`vite.config` 的 `plugins` 数组，顺序敏感；官方有 Vue、React、Legacy 等插件，社区有大量 Rollup/独有插件。

## 五、常用插件与生态

- **@vitejs/plugin-vue**：Vue SFC 支持。
- **@vitejs/plugin-react**：React Fast Refresh。
- **vite-plugin-legacy**：为旧浏览器再打一份 bundle（如 SystemJS）。
- **vite-plugin-pwa**：PWA、workbox。
- 各种「按需加载 CDN」「DLL」「Monorepo 联动」的插件，按项目需求选。

## 六、和 Webpack 的对比

| 维度 | Vite | Webpack |
|------|------|---------|
| 开发启动 | 按需编译，秒开 | 先整体打包再 dev |
| HMR | 模块级，基于 ESM | 模块级，基于 bundle |
| 生产 | Rollup 打包 | 自建打包管线 |
| 配置 | 偏约定，插件链 | 功能全但配置多 |

适合：新项目、以 ESM 为主的栈、追求开发体验。老项目或强依赖 Webpack 生态的可以继续用 Webpack，或逐步迁到 Vite。

## 七、总结

Vite = **开发时 ESM 服务器 + 按需编译 + 预构建 + HMR**，**生产时 Rollup 打包**。搞清楚「开发为什么快」「预构建在干什么」「生产为什么还要打包」，就能用好 Vite 并排掉大部分坑。建议动手起一个 Vite 项目，改改配置、加几个插件，再和 Webpack 项目对比一下体感，印象会更深。

## 八、从零跑一个 Vite 项目

```bash
npm create vite@latest my-app -- --template vue   # 或 react、vanilla
cd my-app && npm i && npm run dev
```

生成的结构里会有 `index.html` 在根目录、`src/main.ts` 作为入口，以及 `vite.config.ts`。开发时执行 `npm run dev` 就是启动 ESM 服务器；`npm run build` 即 Rollup 打包。可以试着加一个 `resolve.alias`、改一下 `build.rollupOptions.output.manualChunks`，观察产物变化。

## 九、常见问题与排错

- **裸模块 404**：多半是依赖没被预构建，检查是否在 `optimizeDeps.include` 里补上，或排除在 `optimizeDeps.exclude` 外的异常包。
- **生产环境白屏/路径错**：检查 `base` 是否和部署路径一致（如子路径要设 `base: '/subpath/'`）。
- **CORS 或代理**：开发时用 `server.proxy` 把接口代理到后端，避免跨域。
- **旧浏览器**：用 `@vitejs/plugin-legacy` 打一份降级 bundle，并在 HTML 里按需加载。

把这几个点摸清，Vite 在项目里就能稳定撑起开发和构建了。

## 十、库模式与多入口

除了应用，Vite 也可以打**库**：在 `vite.config` 里配 `build.lib`，指定入口和产物格式（如 ESM + CJS + 类型声明）。这样组件库、工具库都可以用 Vite 构建，和主应用共享同一套配置与插件。多入口时用数组或对象形式指定多个 entry，Rollup 会分别打出对应 chunk，适合「按需引入」的包结构。

## 十一、与 Node 的边界

开发时 Vite 只处理「会进浏览器的模块」；若代码里用了 Node 内置模块（如 `fs`、`path`）或 `node_modules` 里仅支持 Node 的包，浏览器会报错。这时要么用 Vite 的 `resolve.alias` 把 Node 模块指到浏览器兼容实现（如 polyfill），要么把这类逻辑放到「只在构建时跑」的插件或脚本里，不进入前端 bundle。分清「浏览器环境」和「Node 环境」的边界，能少踩很多坑。
