# webpack-bundle-analyzer：可视化分析打包体积的利器

> 一图看清你的包里都有啥，快速定位体积问题并优化打包结果

---

## 一、为什么需要体积分析

你是否遇到过这些问题：

- 打包后的文件莫名其妙很大
- 不知道哪个依赖占用了最多空间
- 想优化体积但不知道从哪下手
- 怀疑某个库被重复打包了

webpack-bundle-analyzer 就是为了解决这些问题而生的。它能生成一个交互式的树状图，让你直观地看到每个模块的体积占比。

---

## 二、快速上手

### 安装

```bash
npm install --save-dev webpack-bundle-analyzer
```

### 基础配置

```javascript
// webpack.config.js
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin()
  ]
};
```

运行打包后，会自动在浏览器中打开分析报告：

```bash
npm run build
```

---

## 三、配置选项详解

### 1. 分析模式

```javascript
new BundleAnalyzerPlugin({
  analyzerMode: 'server',  // server | static | json | disabled
  analyzerHost: '127.0.0.1',
  analyzerPort: 8888,
  openAnalyzer: true,  // 自动打开浏览器
})
```

模式说明：
- `server`：启动 HTTP 服务器，实时查看（默认）
- `static`：生成 HTML 文件，适合 CI/CD
- `json`：生成 JSON 数据，用于自定义分析
- `disabled`：禁用插件

### 2. 生成静态报告

```javascript
new BundleAnalyzerPlugin({
  analyzerMode: 'static',
  reportFilename: 'bundle-report.html',
  openAnalyzer: false,  // 不自动打开
})
```

适合在 CI 中使用：

```bash
# 打包并生成报告
npm run build

# 报告保存在 dist/bundle-report.html
```

### 3. 体积统计方式

```javascript
new BundleAnalyzerPlugin({
  defaultSizes: 'parsed',  // stat | parsed | gzip
})
```

- `stat`：源文件大小
- `parsed`：打包后大小（默认）
- `gzip`：gzip 压缩后大小

---

## 四、实战案例

### 案例 1：发现重复依赖

打开分析报告后，如果看到同一个库出现多次，说明存在重复打包。

```javascript
// 问题：lodash 被打包了两次
// node_modules/lodash (500KB)
// node_modules/lodash-es (500KB)

// 解决：统一使用 lodash-es
module.exports = {
  resolve: {
    alias: {
      'lodash': 'lodash-es'
    }
  }
};
```

### 案例 2：按需引入

发现某个库体积很大，但只用了一小部分功能。

```javascript
// ❌ 问题：引入整个 antd (1.2MB)
import { Button, Table } from 'antd';

// ✅ 解决：按需引入
import Button from 'antd/es/button';
import Table from 'antd/es/table';

// 或使用 babel-plugin-import
// .babelrc
{
  "plugins": [
    ["import", {
      "libraryName": "antd",
      "style": true
    }]
  ]
}
```

### 案例 3：代码分割

发现某个路由页面的代码被打包到主 bundle 中。

```javascript
// ❌ 问题：所有页面都在主 bundle
import Dashboard from './Dashboard';
import Settings from './Settings';

// ✅ 解决：动态导入
const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));
```

### 案例 4：移除无用代码

发现某个大型库被完整打包，但实际只用了一小部分。

```javascript
// ❌ 问题：引入整个 moment.js (200KB)
import moment from 'moment';

// ✅ 解决：使用更轻量的 day.js (2KB)
import dayjs from 'dayjs';

// 或者只引入需要的 locale
import moment from 'moment';
import 'moment/locale/zh-cn';
```

---

## 五、配合其他工具

### 1. 与 webpack-dev-server 配合

```javascript
// 开发环境不启用，避免影响构建速度
const isProduction = process.env.NODE_ENV === 'production';

module.exports = {
  plugins: [
    isProduction && new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
    })
  ].filter(Boolean)
};
```

### 2. 与 CI/CD 集成

```yaml
# .github/workflows/build.yml
- name: Build and analyze
  run: npm run build
  
- name: Upload bundle report
  uses: actions/upload-artifact@v2
  with:
    name: bundle-report
    path: dist/bundle-report.html
```

### 3. 设置体积预算

```javascript
// webpack.config.js
module.exports = {
  performance: {
    maxAssetSize: 500000,  // 单文件不超过 500KB
    maxEntrypointSize: 1000000,  // 入口不超过 1MB
    hints: 'error'  // 超出时报错
  }
};
```

---

## 六、优化技巧总结

根据分析报告，常见的优化方向：

### 1. 依赖优化

```javascript
// 替换大型库
moment → dayjs  // 200KB → 2KB
lodash → lodash-es  // 支持 tree-shaking
axios → fetch API  // 原生支持
```

### 2. 代码分割

```javascript
// 路由级别分割
const routes = [
  {
    path: '/dashboard',
    component: () => import('./Dashboard')
  }
];

// 组件级别分割
const HeavyChart = lazy(() => import('./HeavyChart'));
```

### 3. Tree Shaking

```javascript
// package.json
{
  "sideEffects": false  // 标记无副作用，支持 tree-shaking
}

// webpack.config.js
module.exports = {
  optimization: {
    usedExports: true,  // 标记未使用的导出
    minimize: true  // 移除未使用的代码
  }
};
```

### 4. 外部化依赖

```javascript
// webpack.config.js
module.exports = {
  externals: {
    'react': 'React',
    'react-dom': 'ReactDOM'
  }
};

// index.html
<script src="https://cdn.jsdelivr.net/npm/react@18/umd/react.production.min.js"></script>
```

---

## 七、进阶用法

### 自定义分析脚本

```javascript
// analyze.js
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const webpack = require('webpack');
const config = require('./webpack.config');

config.plugins.push(
  new BundleAnalyzerPlugin({
    analyzerMode: 'json',
    reportFilename: 'stats.json'
  })
);

webpack(config, (err, stats) => {
  if (err) throw err;
  
  const data = require('./dist/stats.json');
  
  // 自定义分析逻辑
  const largeModules = data.filter(m => m.size > 100000);
  console.log('大于 100KB 的模块：', largeModules);
});
```

### 对比不同版本

```bash
# 保存当前版本的报告
npm run build
mv dist/bundle-report.html reports/v1.html

# 优化后再次构建
npm run build
mv dist/bundle-report.html reports/v2.html

# 对比两个版本
```

---

## 八、常见问题

### 1. 报告中的体积和实际文件大小不一致？

报告显示的是未压缩的大小，实际传输时会经过 gzip 压缩。可以切换到 `gzip` 视图查看压缩后大小。

### 2. 某个模块显示很大，但找不到在哪引入的？

使用 webpack 的 `--display-modules` 查看详细信息：

```bash
webpack --display-modules --display-reasons
```

### 3. 如何分析多个 entry？

插件会自动分析所有 entry，在报告中可以切换查看。

---

## 总结

webpack-bundle-analyzer 是前端性能优化的必备工具。通过可视化的方式，它能帮你快速定位体积问题，找到优化方向。

优化建议：
1. 定期生成分析报告，监控体积变化
2. 设置体积预算，防止体积失控
3. 优先优化占比最大的模块
4. 配合代码分割和 tree-shaking

如果这篇文章对你有帮助，欢迎点赞收藏！
