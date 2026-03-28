# Vite 6+: 实战自定义环境实现跨平台代码注入与构建

> 随着全栈开发和跨端场景的普及，我们的代码往往需要跑在浏览器、Node.js、Edge Worker、甚至是原生 App 的 WebView 中。传统的构建工具往往通过环境变量（如 `process.env.PLATFORM`）来实现逻辑分支，但这会导致产物体积冗余且难以维护。Vite 6 引入的 Environment API 彻底改变了这一现状。本文将带你实战：如何通过自定义环境实现真正的跨平台代码注入。

---

## 目录 (Outline)
- [一、 跨端构建的挑战：从 if-else 到环境隔离](#一-跨端构建的挑战从-if-else-到环境隔离)
- [二、 Vite 6 Environment API 核心概念回顾](#二-vite-6-environment-api-核心概念回顾)
- [三、 实战 1：定义「小程序」与「Web」双环境](#三-实战-1定义小程序与-web-双环境)
- [四、 实战 2：利用环境特定插件实现自动化代码注入](#四-实战-2利用环境特定插件实现自动化代码注入)
- [五、 进阶：针对不同环境的 HMR 热更新策略](#五-进阶针对不同环境的-hmr-热更新策略)
- [六、 总结与最佳实践](#六-总结与最佳实践)

---

## 一、 跨端构建的挑战：从 if-else 到环境隔离

### 1. 历史背景
在过去，我们要为不同端生成产物，通常需要运行两次构建命令，或者在代码中写满：
```javascript
if (import.meta.env.VITE_PLATFORM === 'app') {
  // WebView 逻辑
} else {
  // Web 逻辑
}
```
这种方式的问题是：**代码树摇（Tree-shaking）往往不彻底，且逻辑耦合严重。**

---

## 二、 Vite 6 Environment API 核心概念回顾

Vite 6 允许你在一次构建生命周期内，启动多个逻辑并行的「环境」。
每个环境都有自己的：
- `Resolve` 规则。
- `Plugins` 列表。
- `Dev Server` 代理逻辑。

---

## 三、 实战 1：定义「小程序」与「Web」双环境

### 配置示例 (vite.config.js)
```javascript
export default {
  environments: {
    // 标准 Web 环境
    web: {
      resolve: { conditions: ['browser'] },
      build: { outDir: 'dist/web' }
    },
    // WebView/小程序环境
    mobile: {
      resolve: { conditions: ['webview'] },
      build: { outDir: 'dist/mobile' },
      // 针对 mobile 端注入特定的全局变量
      define: {
        __PLATFORM_API__: 'window.NativeBridge'
      }
    }
  }
}
```

---

## 四、 实战 2：利用环境特定插件实现自动化代码注入

我们可以编写一个插件，它只在 `mobile` 环境下生效，自动将所有的 `console.log` 转发到真机调试器。

### 代码示例：环境感知插件
```javascript
function mobileDebugPlugin() {
  return {
    name: 'mobile-debug-plugin',
    applyToEnvironment(env) {
      // 关键点：只应用到名为 'mobile' 的环境
      return env.name === 'mobile';
    },
    transform(code, id) {
      if (id.endsWith('.js')) {
        return code.replace(/console\.log/g, '__NativeLogger__.log');
      }
    }
  };
}
```

---

## 五、 进阶：针对不同环境的 HMR 热更新策略

Vite 6 支持为不同环境配置不同的 HMR 频率。例如，在 Web 端我们可以开启毫秒级更新，而在模拟器端，为了稳定性，我们可以设置更长的延迟或手动触发。

---

## 六、 总结与最佳实践

- **解耦业务逻辑**：通过 `resolve.conditions` 让同一份 `import` 根据环境自动指向不同的实现文件。
- **构建效率**：Vite 6 的多环境构建是高度并行的，利用了现代 CPU 的多核优势。
- **建议**：对于需要同时维护「管理后台」、「移动端 H5」、「混合 App」的项目，环境 API 是降维打击般的利器。

Vite 6 正在从一个「前端工具」进化为真正的「通用模块分发引擎」。

---

> **参考资料：**
> - *Vite 6 Environment API Documentation*
> - *Building Cross-platform Apps with Vite - Evan You*
> - *Tree-shaking patterns in Modern Bundlers*
