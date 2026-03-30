# EsBuild 与 Rollup 完全指南：现代构建工具对比

> 深入讲解 EsBuild 和 Rollup，包括构建原理、插件系统、代码分割，以及实际项目中的构建工具选择。

## 一、EsBuild

### 1.1 特点

- **Go 语言编写**：编译为原生代码
- **速度极快**：比 Webpack 快 10-100 倍
- **内置功能**：TypeScript、JSX、CSS 等

### 1.2 使用

```bash
npm install -D esbuild
```

```javascript
import * as esbuild from 'esbuild';

await esbuild.build({
  entryPoints: ['src/index.js'],
  bundle: true,
  outfile: 'dist/bundle.js',
  minify: true,
  sourcemap: true,
  target: ['es2020'],
  format: 'esm'
});
```

### 1.3 开发模式

```javascript
const ctx = await esbuild.context({
  entryPoints: ['src/index.js'],
  bundle: true,
  outfile: 'dist/bundle.js'
});

await ctx.watch();
await ctx.serve({ servedir: 'dist' });
```

## 二、Rollup

### 2.1 特点

- **Tree Shaking**：消除死代码
- **输出格式**：ESM、CJS、UMD
- **插件生态**：丰富

### 2.2 配置

```javascript
export default {
  input: 'src/index.js',
  output: {
    dir: 'dist',
    format: 'es',
    sourcemap: true
  },
  plugins: [
    resolve(),
    commonjs()
  ]
};
```

### 2.3 插件

```javascript
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

export default {
  input: 'src/index.js',
  output: {
    file: 'bundle.js',
    format: 'iife'
  },
  plugins: [
    resolve(),
    commonjs()
  ]
};
```

## 三、对比

### 3.1 选择

| 场景 | 推荐 |
|------|------|
| 库打包 | Rollup |
| 应用打包 | Vite/Rollup |
| 速度优先 | EsBuild |
| 兼容性 | Rollup |

### 3.2 速度对比

```
Webpack:   ████████████████████ 10s
Rollup:    ██████████           5s
EsBuild:   ██                   0.5s
```

## 四、总结

构建工具核心要点：

1. **EsBuild**：极速，原生 Go
2. **Rollup**：Tree Shaking，库打包
3. **Vite**：基于 EsBuild + Rollup
4. **插件**：扩展功能

掌握这些，构建更高效！

---

**推荐阅读**：
- [EsBuild 文档](https://esbuild.github.io/)
- [Rollup 文档](https://rollupjs.org/)

**如果对你有帮助，欢迎点赞收藏！**
