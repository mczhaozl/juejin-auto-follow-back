# Vite 插件系统与构建流水线源码解析：从 Rollup 插件到 HMR

> 解析 Vite 插件钩子体系、开发/生产流水线、Rollup 集成与 HMR 实现，理解现代前端构建工具的核心架构。

---

## 一、背景：Vite 的定位与双模式

Vite 以 **开发时无打包、生产时用 Rollup 打包** 著称。开发阶段通过 **ESM + 按需编译**：浏览器直接请求模块，Vite 在服务端按需转译（如 TS、JSX、vue）并返回，避免整包 bundle 带来的冷启动慢问题。生产阶段则把同一套源码交给 **Rollup** 做 tree-shaking、代码分割与压缩，得到可部署的静态资源。

因此 Vite 的架构可以拆成两条主线：**开发服务器**（connect/中间件、模块图、转换管道、HMR）与 **生产构建**（Rollup 的 config 生成、插件桥接、输出）。插件系统需要同时服务这两条线：部分钩子在开发时触发（如 `transform`、`handleHotUpdate`），部分在生产构建时触发（如 `buildStart`、`generateBundle`），还有的二者共用（如 `resolveId`、`load`）。理解 Vite 的插件 API 与执行顺序，是扩展与排查问题的关键。

## 二、插件钩子的分类与执行顺序

Vite 的插件兼容 **Rollup 的钩子**（如 `resolveId`、`load`、`transform`、`buildStart`、`buildEnd`、`generateBundle`、`writeBundle` 等），并在此基础上增加了 **Vite 专属钩子**（如 `config`、`configResolved`、`configureServer`、`transformIndexHtml`、`handleHotUpdate`）。按执行时机可粗略分为：

- **配置阶段**：`config`（可异步修改 config）→ `configResolved`（config 确定后）。
- **开发服务器**：`configureServer`（注入中间件）→ 请求时依次 `resolveId`、`load`、`transform`；HMR 时 `handleHotUpdate`。
- **生产构建**：`buildStart` → 对每个入口与依赖依次 `resolveId`、`load`、`transform` → `buildEnd` → `generateBundle`（可修改生成的 chunk）→ `writeBundle`（写入磁盘后）。

钩子又分 **async**、**sequential**、**parallel** 等：例如多个插件的 `transform` 会按注册顺序依次执行（前一个的输出作为后一个的输入）；`resolveId` 若有返回值则后续插件不再执行该钩子。源码中通过 **PluginContainer** 或类似对象统一调度这些钩子，保证顺序与 Rollup 行为一致。

## 三、开发时的模块解析与转换管道

浏览器请求 `/src/main.tsx` 时，Vite 的中间件会：

1. **解析 URL** 到文件路径与 query（如 `?t=xxx` 的 HMR 时间戳）。
2. **resolveId**：将 `/src/main.tsx` 解析为绝对路径；若未命中缓存则调用插件链的 `resolveId`，可能改写为 node_modules 中的路径或虚拟模块。
3. **load**：若该 id 未被任何插件的 load 返回内容，则从磁盘读取文件内容。
4. **transform**：对内容依次执行各插件的 `transform`（TS → JS、JSX → JS、CSS 注入等）；结果会缓存在内存（按文件路径 + 依赖的 hash）。
5. 返回 **HTTP 响应**：Content-Type 为 `application/javascript` 等，body 为转换后的代码。

**依赖预构建**：对 node_modules 中的裸导入（如 `import vue from 'vue'`），Vite 会先做一次 **esbuild 预打包**，把 CJS/多文件依赖打成单个 ESM，并写入 `node_modules/.vite/deps`；后续请求时通过 `resolveId` 指向该预构建产物，避免运行时对 node_modules 做大量请求。预构建的入口列表在首次启动时通过扫描入口文件中的 import 得到，并可通过 `optimizeDeps` 配置扩展。

## 四、生产构建：Rollup 的集成方式

生产构建时，Vite 会**基于用户配置与环境变量**生成一份 **Rollup 的 options**（input、plugins、output、external 等）。Vite 自带的插件（如 `vite:resolve`、`vite:esbuild`、`vite:json` 等）会先被加入 plugins 数组，再拼接用户配置的 plugins；这样用户插件可以包裹或插入到默认插件之间（通过 `enforce: 'pre'` 或 `enforce: 'post'` 调整顺序）。

**build 流程**：Rollup 的 `rollup.rollup(options)` 会触发 `buildStart`，然后从 input 出发做 **图遍历**：对每个模块 resolveId → load → transform，得到模块图；再 **generate** 生成 chunk 与 asset，触发 `generateBundle`；最后 **write** 到磁盘，触发 `writeBundle`。Vite 在 generate 阶段会注入 **import.meta.env**、**动态 import 的 chunk 名** 等；代码分割与 tree-shaking 完全由 Rollup 负责。

## 五、插件上下文与工具方法

在插件钩子中，可通过 **this** 或传入的 **context** 访问：**resolve**（解析路径）、**emitFile**（在生产构建中发出额外文件）、**addWatchFile**（添加监听以触发 HMR 或重建）、**getModuleInfo** 等。这些方法由 Vite/Rollup 在创建 PluginContext 时注入，保证在开发与生产环境下行为一致（或合理降级）。例如在 `transform` 里调用 `this.addWatchFile(absolutePath)`，当该文件变化时，开发服务器会使该模块失效并可能触发 HMR；生产构建时会在 watch 模式下重新构建。

## 六、HMR 的实现思路

HMR（Hot Module Replacement）在开发时实现「不刷新页面只替换模块」：当某文件变更，Vite 通过 WebSocket 向浏览器推送 **update 事件**，携带变更的模块 id 与更新后的代码（或边界 URL）；浏览器端运行 **HMR runtime**（由 Vite 在入口注入），根据模块图找到受影响的模块，执行新模块并调用其 `hot.accept` 回调，完成局部更新。

服务端侧：**文件监听**（如 chokidar）发现变更后，调用 **handleHotUpdate** 钩子，插件可过滤或扩展要推送的模块；然后通过 **moduleGraph** 找到该模块的「导入链」与「被谁导入」，决定推送哪些模块的更新。客户端侧：收到 update 后，通过 **dynamic import** 拉取新模块，执行并触发 accept 回调；若为「边界模块」（如根组件），可能做 **full reload**。Vue/React 的 HMR 支持通常由各自生态的 Vite 插件（如 `@vitejs/plugin-vue`）在模块中注入 `hot.accept` 逻辑实现。

## 七、虚拟模块与 config 合并

**虚拟模块**：以 `\0` 开头的 id 或 `virtual:xxx` 形式的模块，不会对应磁盘文件；在 `resolveId` 中返回该 id，在 `load` 中返回字符串内容即可。Vite 自身用虚拟模块注入 **client**（HMR 客户端）、**env** 等；插件也可用其暴露配置或运行时数据。**config 合并**：用户配置与 Vite 内部默认配置会深度合并；`config` 钩子可返回一个对象或函数（返回对象），用于在解析前修改配置；`configResolved` 则在合并完成后拿到最终 config，适合读取或基于最终值再注册逻辑。多环境（dev/build）下部分字段（如 `server`、`build.rollupOptions`）仅在一侧生效，插件需区分当前是开发还是生产。

## 八、源码关键路径

- **入口**：`vite` 包的 `createServer`（开发）、`build`（生产）；开发时 `server.listen()` 前会执行 `configureServer` 并注册中间件。
- **模块请求**：中间件中调用 **transformRequest**（或类似），内部通过 **PluginContainer** 依次执行 `resolveId`、`load`、`transform`；结果缓存在 **ModuleNode** 与 **TransformResult** 的 Map 中。
- **生产构建**：`build` 中调用 `rollup.rollup()`，传入 **resolveConfig** 得到的 config；plugins 在 `config.plugins` 中扁平化并带 enforce 排序。
- **HMR**：`server.watcher` 的 `on('change')` 中调用 `handleFileChange`，更新 moduleGraph，通过 **WebSocket** 发送 `full-reload` 或 `update` 事件；客户端在 `vite/client` 的 HMR 客户端中处理。

阅读时建议从「一次开发时请求」与「一次 `vite build`」两条线分别跟入，对照 [Vite 插件 API 文档](https://cn.vitejs.dev/guide/api-plugin.html) 理解各钩子的入参与返回值。

## 总结

- Vite 的插件体系兼容 Rollup 钩子并扩展了 **config**、**configureServer**、**transformIndexHtml**、**handleHotUpdate** 等，在开发与生产两条流水线中按顺序执行。
- 开发时通过 **resolveId → load → transform** 的管道按需编译模块，依赖预构建用 esbuild 打包 node_modules；生产时完全交给 Rollup 做图构建与 chunk 生成。
- HMR 由服务端监听文件、更新 moduleGraph 并推送 WebSocket 事件，客户端通过 HMR runtime 拉取新模块并执行 accept 回调实现热替换。
- 扩展或排查问题时，重点看 **PluginContainer** 的钩子调度与 **moduleGraph** 的依赖关系，以及开发/生产下插件执行的差异。