# Vite 5+ 插件开发进阶：掌握 Rollup 钩子与 HMR 机制

> Vite 的极速体验（No-bundle）和强大的扩展性，很大程度上归功于其插件系统。Vite 插件本质上是 Rollup 插件的超集，并增加了独有的 HMR（热更新）处理能力。本文将带你深入 Vite 插件底层，实战开发一个具有 HMR 动态拦截能力的进阶插件。

---

## 目录 (Outline)
- [一、 Vite 插件架构：Rollup 兼容性与独有钩子](#一-vite-插件架构rollup-兼容性与独有钩子)
- [二、 插件生命周期：从解析到构建的全流程拦截](#二-插件生命周期从解析到构建的全流程拦截)
- [三、 实战 1：开发一个自定义资源加载器 (Loader)](#三-实战-1开发一个自定义资源加载器-loader)
- [四、 实战 2：深度掌握 HMR API，实现状态保持的热更新](#四-实战-2深度掌握-hmr-api实现状态保持的热更新)
- [五、 总结与最佳实践](#五-总结与最佳实践)

---

## 一、 Vite 插件架构：Rollup 兼容性与独有钩子

### 1. 核心思想
Vite 插件扩展了 Rollup 接口，增加了一些 Vite 特有的钩子（Hooks）。
- **兼容钩子**：如 `resolveId`, `load`, `transform`。
- **Vite 独有钩子**：如 `config`, `configResolved`, `configureServer`, `handleHotUpdate`。

### 2. 标志性事件
- **2021 年**：Vite 2.0 发布，确立了基于 Rollup 插件的插件体系。
- **2023 年底**：Vite 5.0 发布，进一步优化了插件的并行处理性能。

### 3. 解决的问题 / 带来的变化
开发者可以一套代码通吃「开发环境（No-bundle）」和「生产环境（Rollup 打包）」。

---

## 二、 插件生命周期：从解析到构建的全流程拦截

一个插件在不同阶段的工作：
1. **配置阶段**：`config` 钩子允许你修改最终的 `vite.config.js` 配置。
2. **转换阶段**：`transform` 钩子是插件的核心，用于将代码 A 转换为代码 B。
3. **输出阶段**：`generateBundle` 钩子在生产环境构建完成后执行。

---

## 三、 实战 1：开发一个自定义资源加载器 (Loader)

### 痛点场景
假设你想直接在 JS 中 `import` 一个 `.txt` 文件，并将其内容作为字符串返回。

### 实战代码
```javascript
// vite-plugin-text-loader.js
export default function textLoader() {
  return {
    name: 'vite-plugin-text-loader',
    
    // 拦截 .txt 文件的解析
    transform(code, id) {
      if (id.endsWith('.txt')) {
        // 将纯文本包装成 ESM 模块
        return {
          code: `export default ${JSON.stringify(code)}`,
          map: null // 简单转换，无需 source map
        };
      }
    }
  };
}
```

---

## 四、 实战 2：深度掌握 HMR API，实现状态保持的热更新

Vite 的热更新（HMR）允许你在修改代码后，不刷新页面即刻更新 UI。

### 痛点场景
你修改了一个样式或简单的逻辑，但你希望保持当前的「输入框内容」或「滚动位置」。

### 实战代码
```javascript
// 插件内拦截 HMR 更新
export default function hmrInterceptor() {
  return {
    name: 'hmr-interceptor',
    
    handleHotUpdate({ file, server, modules }) {
      if (file.endsWith('.data.json')) {
        console.log(`🔥 检测到数据文件变更: ${file}`);
        
        // 1. 通过服务器广播自定义事件给客户端
        server.ws.send({
          type: 'custom',
          event: 'data-update',
          data: { msg: '数据已刷新' }
        });
        
        // 2. 返回空数组，阻止浏览器刷新整个页面
        return [];
      }
    }
  };
}
```

在客户端接收：
```javascript
if (import.meta.hot) {
  import.meta.hot.on('data-update', (data) => {
    console.log('收到热更新通知:', data.msg);
    // 这里执行局部数据更新逻辑
  });
}
```

---

## 五、 总结与最佳实践

- **插件命名**：Vite 官方推荐插件以 `vite-plugin-` 开头。
- **虚拟模块**：利用 `\0` 前缀（虚拟模块规范）来注入一些运行时代码。
- **建议**：插件逻辑应尽量轻量。耗时操作（如图片压缩）建议只放在生产环境钩子中执行。

掌握了插件开发，你就掌握了 Vite 的核心命门。无论是做性能调优、代码混淆，还是支持自定义文件格式，插件都是你最有力的武器。

---

> **参考资料：**
> - *Vite Official Guide: Plugin API*
> - *Rollup Plugin Development Documentation*
> - *Vite Internals: How HMR Works Under the Hood*
