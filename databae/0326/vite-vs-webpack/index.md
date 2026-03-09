# Vite 和 Webpack 的差异：为什么现在的打包工具越来越快

> 从开发服务器、构建原理、生态三个维度对比 Vite 和 Webpack，理解现代打包工具的性能优化思路。

---

## 一、核心差异概览

| 维度 | Webpack | Vite |
|------|---------|------|
| 开发服务器 | Bundle-based（打包后启动） | Native ESM（按需编译） |
| 冷启动速度 | 慢（需要打包全部模块） | 快（直接启动） |
| 热更新速度 | 随项目增大变慢 | 始终快速 |
| 生产构建 | Webpack | Rollup |
| 配置复杂度 | 高 | 低 |
| 生态成熟度 | 非常成熟 | 快速增长 |

## 二、开发服务器：Bundle vs ESM

### Webpack 的 Bundle-based 模式

```
启动流程：
1. 读取入口文件
2. 递归解析所有依赖
3. 打包成 bundle
4. 启动开发服务器
5. 浏览器加载 bundle

问题：项目越大，启动越慢
```

```javascript
// webpack.config.js
module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'bundle.js'
  },
  // 需要配置各种 loader
  module: {
    rules: [
      { test: /\.js$/, use: 'babel-loader' },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] }
    ]
  }
};
```

### Vite 的 Native ESM 模式

```
启动流程：
1. 启动开发服务器（几乎瞬间）
2. 浏览器请求入口文件
3. 按需编译请求的模块
4. 返回 ESM 格式代码

优势：启动快，按需加载
```

```javascript
// vite.config.js
export default {
  // 几乎零配置
  plugins: [vue()]
};
```

浏览器直接加载 ESM：

```html
<!-- Vite 开发环境 -->
<script type="module" src="/src/main.js"></script>
```

```javascript
// main.js - 浏览器直接执行
import { createApp } from 'vue';
import App from './App.vue';

createApp(App).mount('#app');
```

## 三、为什么 Vite 更快

### 1. 依赖预构建

Vite 启动时只预构建 node_modules 中的依赖（用 esbuild，速度极快）：

```javascript
// Vite 自动将 CommonJS 转为 ESM
import _ from 'lodash'; // 预构建后变成 ESM

// 预构建缓存在 node_modules/.vite
```

### 2. 按需编译

```
Webpack：
main.js → 解析 → 打包 100 个模块 → 启动（慢）

Vite：
启动（快）→ 浏览器请求 main.js → 编译 main.js → 返回
         → 浏览器请求 App.vue → 编译 App.vue → 返回
```

只编译浏览器请求的文件，未请求的不编译。

### 3. 热更新（HMR）

```
Webpack HMR：
修改文件 → 重新打包相关模块 → 推送更新（随项目增大变慢）

Vite HMR：
修改文件 → 只编译该文件 → 推送更新（始终快速）
```

```javascript
// Vite HMR API
if (import.meta.hot) {
  import.meta.hot.accept((newModule) => {
    // 模块热替换
  });
}
```

### 4. esbuild 加持

Vite 用 esbuild（Go 编写）处理 TS/JSX，比 Babel（JS 编写）快 10-100 倍：

```javascript
// vite.config.js
export default {
  esbuild: {
    jsxFactory: 'h',
    jsxFragment: 'Fragment'
  }
};
```

## 四、生产构建对比

### Webpack 构建

```javascript
// webpack.config.js
module.exports = {
  mode: 'production',
  optimization: {
    minimize: true,
    splitChunks: {
      chunks: 'all'
    }
  }
};
```

特点：

- 配置灵活，功能强大
- 构建速度较慢
- 生态成熟，插件丰富

### Vite 构建（基于 Rollup）

```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router']
        }
      }
    }
  }
};
```

特点：

- 默认配置已优化
- Tree-shaking 更彻底
- 构建速度快（但不如开发时的差距大）

## 五、实际性能对比

### 冷启动时间

```
小项目（< 100 个模块）：
Webpack: 3-5 秒
Vite: < 1 秒

中型项目（500 个模块）：
Webpack: 10-20 秒
Vite: 1-2 秒

大型项目（2000+ 个模块）：
Webpack: 30-60 秒
Vite: 2-3 秒
```

### 热更新时间

```
Webpack: 随项目增大，从 100ms 到几秒
Vite: 始终 < 100ms
```

## 六、配置复杂度对比

### Webpack 配置（典型 React 项目）

```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js'
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader']
      },
      {
        test: /\.(png|svg|jpg)$/,
        type: 'asset/resource'
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({ template: './public/index.html' }),
    new MiniCssExtractPlugin()
  ],
  devServer: {
    port: 3000,
    hot: true
  }
};
```

### Vite 配置（同样功能）

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()]
  // 其他都是默认配置
});
```

## 七、生态与兼容性

### Webpack 优势

- 插件生态极其丰富
- 支持各种复杂场景
- 社区方案成熟

```javascript
// Webpack 有大量成熟插件
plugins: [
  new WorkboxPlugin.GenerateSW(), // PWA
  new BundleAnalyzerPlugin(), // 分析
  new CompressionPlugin() // 压缩
]
```

### Vite 优势

- 插件生态快速增长
- 兼容 Rollup 插件
- 官方提供常用插件

```javascript
import vue from '@vitejs/plugin-vue';
import legacy from '@vitejs/plugin-legacy'; // 兼容旧浏览器
import { visualizer } from 'rollup-plugin-visualizer'; // Rollup 插件

export default {
  plugins: [
    vue(),
    legacy({
      targets: ['defaults', 'not IE 11']
    }),
    visualizer()
  ]
};
```

## 八、何时选择 Webpack

- 需要兼容 IE11 或更老浏览器（Vite 需要额外配置）
- 项目已有大量 Webpack 配置和插件
- 需要 Webpack 特有的功能（如 Module Federation）
- 团队对 Webpack 更熟悉

## 九、何时选择 Vite

- 新项目，尤其是 Vue 3 / React 项目
- 追求开发体验和速度
- 不需要兼容旧浏览器
- 希望简化配置

## 十、迁移建议

### 从 Webpack 迁移到 Vite

```javascript
// 1. 安装 Vite
npm install vite @vitejs/plugin-vue -D

// 2. 创建 vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': '/src' // 路径别名
    }
  },
  server: {
    port: 3000
  }
});

// 3. 修改 index.html
// 移到项目根目录，添加：
<script type="module" src="/src/main.js"></script>

// 4. 修改 package.json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### 常见问题

```javascript
// 1. require 改为 import
// ❌ Webpack
const config = require('./config');

// ✅ Vite
import config from './config';

// 2. 环境变量
// ❌ Webpack
process.env.VUE_APP_API

// ✅ Vite
import.meta.env.VITE_API

// 3. 动态 import
// ❌ Webpack
require(`./locales/${lang}.json`)

// ✅ Vite
import(`./locales/${lang}.json`)
```

## 总结

Vite 快的核心原因：

- 开发时利用浏览器原生 ESM，按需编译
- 用 esbuild 预构建依赖，速度极快
- HMR 只更新修改的模块，不重新打包

Webpack 仍然强大：

- 生态成熟，插件丰富
- 配置灵活，适合复杂场景
- 生产构建功能完善

选择建议：新项目优先 Vite，老项目根据迁移成本决定。现代打包工具的趋势是「开发快、配置少、体验好」，Vite 代表了这个方向。
