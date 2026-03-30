# Vite 完全指南：下一代前端构建工具

> 深入讲解 Vite 的原理和使用，包括开发服务器、热更新、构建优化，以及与 Webpack 的对比和迁移指南。

## 一、Vite 简介

### 1.1 为什么 Vite

| 特性 | Webpack | Vite |
|------|---------|------|
| 开发启动 | 慢（打包） | 快（原生 ESM） |
| 热更新 | 较慢 | 极快 |
| 构建速度 | 较慢 | 快（Rollup） |

### 1.2 安装

```bash
npm create vite@latest my-app -- --template vue
cd my-app
npm install
npm run dev
```

## 二、配置

### 2.1 vite.config.js

```javascript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8080'
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
});
```

### 2.2 环境变量

```env
VITE_APP_TITLE=My App
VITE_API_URL=http://api.example.com
```

使用：

```javascript
console.log(import.meta.env.VITE_API_URL);
```

## 三、特性

### 3.1 原生 ESM

```javascript
// 直接导入，无需配置
import { ref } from 'vue';
import './style.css';
import App from './App.vue';
```

### 3.2 HMR

```javascript
// Vite 自动处理 HMR
// 修改代码后立即更新，无需刷新
```

## 四、插件

### 4.1 Vue 支持

```bash
npm install @vitejs/plugin-vue
```

```javascript
import vue from '@vitejs/plugin-vue';
export default defineConfig({
  plugins: [vue()]
});
```

### 4.2 自动导入

```bash
npm install -D unplugin-vue-components
```

```javascript
import Components from 'unplugin-vue-components/vite';

export default defineConfig({
  plugins: [
    Components({
      dts: true
    })
  ]
});
```

## 五、总结

Vite 核心要点：

1. **ESM**：原生模块支持
2. **HMR**：极速热更新
3. **配置**：vite.config.js
4. **插件**：生态丰富
5. **环境变量**：import.meta.env

掌握这些，前端构建更高效！

---

**推荐阅读**：
- [Vite 官方文档](https://vitejs.dev/)

**如果对你有帮助，欢迎点赞收藏！**
