# Node.js ESM Loader Hooks 介绍：用 module.register 做转译、Import Map 与自定义解析

> 介绍 Node 里已可用的 ESM Loader Hooks（module.register / registerHooks），版本要求与典型用法：转译、import map、自定义解析。

---

## 一、ESM Loader Hooks 是什么

在 Node.js 中，**ESM Loader Hooks** 是一组在 **ES 模块** 解析与加载过程中被调用的钩子。你可以在「解析模块标识符」和「加载模块内容」两步插入自己的逻辑，从而实现：

- **转译**：在加载前把 TypeScript、CoffeeScript、JSX 等转成 Node 能执行的 JavaScript；
- **Import Map**：把裸说明符（如 `import 'lodash'`）映射到具体 URL 或本地路径；
- **自定义解析**：按自己的规则把 `specifier` 解析成 `url`，或从网络、数据库等来源拉取模块内容。

早期 Node 通过 **`--experimental-loader`** 和 `loaderRunner` 暴露过类似能力，但 API 与稳定性有限。从 **Node 20.8** 起，官方提供了基于 **`module.register()`** 的 Loader 注册方式，成为当前推荐用法；**Node 22+** 更稳定，建议新项目直接使用 22+。

---

## 二、版本与入口 API

- **最低版本**：**Node 20.8** 起支持 `module.register()` 注册 ESM Loader。
- **推荐版本**：**Node 22+**，行为与文档更稳定。
- **入口 API**（来自 `node:module`）：
  - **`module.register(specifier, options?)`**：注册一个 Loader 模块；`specifier` 为 Loader 自身的模块说明符（如文件路径或 `data:` URL），`options` 可携带初始化数据，会传给 Loader 的 `initialize` 钩子。
  - **`module.registerHooks()`**：在部分版本/提案中用于注册或扩展更多钩子（如与执行阶段相关的钩子），具体以当前 Node 文档为准。

Loader 模块需在**应用代码之前**注册，因此通常放在入口文件最顶部，或通过 **`node --import ./loader.js app.mjs`** 在启动时加载。

---

## 三、Loader 模块的钩子结构

通过 `module.register()` 注册的模块需要**导出**以下钩子（函数），Node 会在解析/加载 ESM 时按顺序调用：

| 钩子 | 作用 |
|------|------|
| **`initialize(data)`** | Loader 初始化时调用一次，`data` 即 `module.register(specifier, options)` 传入的 `options`；可返回一个实现 `resolve`/`load` 的对象，作为该 Loader 的实例（部分版本支持）。 |
| **`resolve(specifier, context, nextResolve)`** | 解析模块说明符（如 `'lodash'`、`'./foo.js'`）为绝对 **URL**；可调用 `nextResolve` 走默认解析，或返回 `{ url, shortCircuit? }` 短路后续解析。 |
| **`load(url, context, nextLoad)`** | 根据解析得到的 `url` 加载模块内容；可返回 `{ format, source, shortCircuit? }`，其中 `format` 为 `'module'`、`'json'`、`'commonjs'` 等；可在此做转译再返回 `source`。 |

**链式调用**：每个钩子一般会调用 `nextResolve` / `nextLoad` 把控制权交给下一个 Loader 或默认实现；若返回时带 `shortCircuit: true`，则不再执行后续 Loader。

---

## 四、典型用法示例

### 1. 自定义解析（Import Map 风格）

在 `resolve` 里把裸说明符映射到本地路径或 URL：

```javascript
// loader.mjs
export async function resolve(specifier, context, nextResolve) {
    const map = { 'lodash': new URL('./node_modules/lodash-es/lodash.js', import.meta.url).href };
    if (map[specifier]) {
        return { url: map[specifier], shortCircuit: true };
    }
    return nextResolve(specifier, context);
}
```

入口文件顶部（必须在任何 `import` 之前）：

```javascript
// index.mjs
import { register } from 'node:module';
register('./loader.mjs', import.meta.url);
import 'lodash';  // 会被 resolve 到上面 map 的 url
```

### 2. 转译（在 load 里改 source）

在 `load` 中读取 `url` 对应内容，转译后返回 `source` 与 `format`：

```javascript
// transpile-loader.mjs
export async function load(url, context, nextLoad) {
    const result = await nextLoad(url, context);
    if (result.format === 'module' && url.endsWith('.ts')) {
        // 此处简化：实际可用 esbuild、tsx、swc 等转译
        const code = await fetch(url).then(r => r.text());
        const transformed = code.replace(/:\s*string/g, '');  // 示例
        return { format: 'module', source: transformed, shortCircuit: true };
    }
    return result;
}
```

实际项目里通常会在这里调用 **esbuild**、**tsx**、**swc** 等做真正的 TS/JSX 转译。

### 3. 使用 module.register 注册

```javascript
// run.mjs
import { register } from 'node:module';
register('./transpile-loader.mjs', import.meta.url);
import './app.ts';  // 由 Loader 转译后执行
```

或通过命令行在应用前注入 Loader：

```bash
node --import ./loader.mjs app.mjs
```

---

## 五、注意事项与延伸

- **执行顺序**：`module.register()` 必须在应用内任何 ESM `import` 之前执行，否则不会对该入口的依赖生效；用 `--import` 可保证 Loader 最先执行。
- **Worker**：自 Node 22.2 起，在 `new Worker()` 时通过 `execArgv` 传 Loader 的方式有变，主线程注册的 Loader 会对 Worker 生效，具体见 [Node 文档](https://nodejs.org/api/module.html)。
- **官方文档**：[Node.js module 文档](https://nodejs.org/api/module.html) 中的 `module.register()`、Customization Hooks；[ESM 文档](https://nodejs.org/api/esm.html) 中的 Loader 章节。

---

## 六、总结

- **ESM Loader Hooks** 在 Node 中已实现且可用，通过 **`module.register(specifier, options?)`** 注册 Loader 模块；Loader 实现 **`resolve`** 与 **`load`** 即可参与解析与加载。
- **版本**：需 **Node 20.8+**，建议 **Node 22+**；更多扩展可关注 **`module.registerHooks()`** 及官方文档。
- **典型场景**：转译（TS/JSX）、Import Map 式裸说明符解析、自定义 URL 解析与内容拉取；配合 `--import` 或入口顶部 `register` 使用。

若对你有用，欢迎点赞、收藏；你若有基于 Loader 的转译或 import map 实践，也欢迎在评论区分享。
