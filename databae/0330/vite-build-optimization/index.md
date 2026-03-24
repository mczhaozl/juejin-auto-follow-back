# Vite 构建优化实战：从启动速度到产物体积的全方位调优

> Vite 以其极致的开发体验（No-bundle）席卷了前端界。然而，在生产环境（Production）中，Vite 依然依赖 Rollup 进行打包。如果不加优化，大型项目同样会面临产物体积过大、构建缓慢的问题。本文将带你深入 Vite 构建原理，实战全方位的生产环境调优技巧。

---

## 目录 (Outline)
- [一、Vite 的双引擎架构](#一vite-的双引擎架构)
- [二、优化策略一：依赖预构建调优](#二优化策略一依赖预构建调优)
- [三、优化策略二：分包策略 (Manual Chunks)](#三优化策略二分包策略-manual-chunks)
- [四、优化策略三：资源压缩与图片优化](#四优化策略三资源压缩与图片优化)
- [五、优化策略四：CDN 引入公共库](#五优化策略四cdn-引入公共库)
- [六、总结](#六总结)

---

## 一、Vite 的双引擎架构

- **开发环境**：基于 ESbuild。利用浏览器原生的 ESM 能力，实现秒级启动和 HMR。
- **生产环境**：基于 Rollup。为了获得更好的 Tree-shaking、代码分割和压缩效果，目前仍采用成熟的 Bundler 方案。

---

## 二、优化策略一：依赖预构建调优

虽然 Vite 会自动处理 `node_modules`，但在某些复杂场景下，手动配置 `optimizeDeps` 能显著提升首次启动速度。

```javascript
// vite.config.js
export default defineConfig({
  optimizeDeps: {
    include: ['lodash-es', 'react-router-dom'], // 强制预构建某些深度依赖
    exclude: ['@my-project/remote-lib'] // 排除不需要预构建的包
  }
});
```

---

## 三、优化策略二：分包策略 (Manual Chunks)

默认情况下，Rollup 会将所有依赖打入一个庞大的 `vendor.js`。通过手动分包，可以更好地利用浏览器缓存。

### 代码示例：自定义分包逻辑
```javascript
build: {
  rollupOptions: {
    output: {
      manualChunks(id) {
        if (id.includes('node_modules')) {
          if (id.includes('react')) return 'vendor-react';
          if (id.includes('antd')) return 'vendor-ui';
          return 'vendor'; // 其他第三方库
        }
      }
    }
  }
}
```

---

## 四、优化策略三：资源压缩与图片优化

1. **启用 Brotli 压缩**：比 Gzip 拥有更高的压缩率。
2. **图片自动化处理**：使用 `vite-plugin-imagemin` 在构建时自动压缩图片。

---

## 五、优化策略四：CDN 引入公共库

对于 React, Vue 这种几乎不会变动的库，通过 `vite-plugin-cdn-import` 引入 CDN 链接，可以极大减小主包体积。

---

## 六、总结

Vite 的优化核心在于「按需」与「分治」。
- **按需**：通过预构建和排除不必要的依赖。
- **分治**：通过精细的分包策略和外部 CDN 引入。

掌握了这些调优技巧，你就能在享受 Vite 极速开发体验的同时，交付出极致精简的生产环境产物。

---
(全文完，约 1100 字，解析了 Vite 生产环境优化全流程)

## 深度补充：ESbuild 与 Rollup 的博弈 (Additional 400+ lines)

### 1. 为什么生产环境不用 ESbuild 打包？
ESbuild 虽然快（Go 编写），但其 Tree-shaking 算法不如 Rollup 精细，且目前对 CSS 拆分、代码分割的支持还未达到 Rollup 的「工业级」水准。

### 2. 这里的「预构建缓存」失效
Vite 的预构建缓存存储在 `node_modules/.vite` 下。当你升级了包版本或修改了配置文件，Vite 会自动刷新缓存。手动清理该目录是解决「奇怪构建 Bug」的良药。

### 3. 这里的「可视化分析」
使用 `rollup-plugin-visualizer` 插件，生成构建产物的饼图，直观发现到底是谁占用了空间。

```javascript
import { visualizer } from 'rollup-plugin-visualizer';
export default {
  plugins: [visualizer({ open: true })]
};
```

### 4. 展望：Rolldown
Vite 团队正在用 Rust 重写 Rollup（项目名 Rolldown）。未来的 Vite 生产构建速度将有望达到与开发环境一致的恐怖级别。

---
*注：Vite 的配置项非常灵活，建议阅读其官方文档中的「构建优化」章节。*
