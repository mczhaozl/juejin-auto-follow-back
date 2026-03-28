# 微前端架构中的多版本依赖共存实战：隔离与共享的艺术

> 在微前端（Micro Frontends）架构中，最令人头疼的问题莫过于依赖管理。当主应用运行 React 18，而子应用 A 必须使用 React 16，子应用 B 想要尝试 React 19 时，如何实现多版本依赖的完美共存且互不干扰？本文将带你实战微前端中的依赖隔离与共享技术。

---

## 目录 (Outline)
- [一、 微前端的「依赖之战」：为什么共存如此困难？](#一-微前端的依赖之战为什么共存如此困难)
- [二、 隔离方案 1：基于 CSS 与 JS 沙箱的硬隔离](#二-隔离方案-1基于-css-与-js-沙箱的硬隔离)
- [三、 隔离方案 2：Module Federation 的「降维打击」](#三-隔离方案-2module-federation-的降维打击)
- [四、 共享方案：如何优雅地复用公共库？](#四-共享方案如何优雅地复用公共库)
- [五、 总结与最佳实践](#五-总结与最佳实践)

---

## 一、 微前端的「依赖之战」：为什么共存如此困难？

微前端的核心承诺是「技术栈无关」。但现实中，全局变量冲突和单例污染是最大的阻碍。

### 1. 历史背景
早期的微前端通过 iframe 实现，虽然隔离完美，但性能和交互体验极差。随后的 single-spa 开启了 JS 直接加载的时代，但也带来了 `window.React` 被覆盖的风险。

### 2. 核心冲突点
- **全局对象污染**：React、Vue 等库往往会在全局挂载一些状态。
- **样式冲突**：不同版本的 UI 库（如 Ant Design 4 vs 5）共用类名。
- **依赖冗余**：如果不做共享，用户需要下载多个版本的 React，包体积爆炸。

### 3. 解决的问题 / 带来的变化
通过现代微前端框架（如 qiankun, Module Federation），我们可以在「完全隔离」和「部分共享」之间找到一个动态平衡点。

---

## 二、 隔离方案 1：基于 CSS 与 JS 沙箱的硬隔离

qiankun 等框架的核心竞争力在于其强大的沙箱机制。

### 1. JS 沙箱 (Proxy Sandbox)
通过 `Proxy` 拦截子应用对 `window` 的读写。每个子应用看到的 `window` 其实是一个代理对象，所有修改都只局限在沙箱内。

### 2. 实战配置：解决多版本 React 冲突
```javascript
// 主应用注册逻辑
registerMicroApps([
  {
    name: 'legacy-app', // React 16
    entry: '//localhost:8001',
    container: '#sub-container',
    activeRule: '/legacy',
    sandbox: {
      strictStyleIsolation: true, // 开启 Shadow DOM 隔离 CSS
      experimentalStyleIsolation: true, // 或开启属性选择器前缀隔离
    },
  },
  {
    name: 'modern-app', // React 19
    entry: '//localhost:8002',
    container: '#sub-container',
    activeRule: '/modern',
  },
]);
```

---

## 三、 隔离方案 2：Module Federation 的「降维打击」

Webpack 5 的模块联邦（Module Federation）提供了一种更优雅的「依赖降级」机制。

### 1. 核心机制
Module Federation 允许子应用声明自己的依赖及其版本范围。如果版本匹配，就共享；如果不匹配，就各用各的。

### 2. 实战配置
```javascript
// 子应用 webpack.config.js
new ModuleFederationPlugin({
  name: 'sub_app',
  shared: {
    react: {
      singleton: true, // 是否要求单例
      requiredVersion: deps.react, // 版本要求
      strictVersion: false, // 是否严格校验，false 表示版本不符时会自动回退到自己的依赖
    },
    'react-dom': { singleton: true },
  },
});
```

---

## 四、 共享方案：如何优雅地复用公共库？

当多个子应用版本一致时，重复加载是极大的浪费。

### 1. Externals 共享
将公共库标记为 `externals`，通过 CDN 加载，让主子应用共用同一个全局实例。
- **缺点**：版本必须完全锁死，不够灵活。

### 2. 动态依赖加载
在微前端容器层拦截模块请求，根据子应用的版本标签（Tags）动态分发对应的库文件。

---

## 五、 总结与最佳实践

- **小型团队**：优先使用 **qiankun**。它的沙箱几乎是开箱即用的，能解决 90% 的版本冲突。
- **大型中台**：优先使用 **Module Federation**。它的灵活性更高，能更细粒度地控制依赖共享。
- **建议**：尽量让主应用保持「轻量」，不要把太多重量级依赖（如 UI 库）放在主应用里强制共享。

微前端架构不是为了拆分而拆分，而是为了让不同生命周期的项目能在一个容器内和谐共存。掌握了依赖隔离，你就掌握了微前端的命脉。

---

> **参考资料：**
> - *qiankun documentation: JS Sandbox*
> - *Webpack 5 Module Federation: The Future of Micro Frontends*
> - *Micro Frontends: Architecture, Decision, and Implementation*
