# Webpack 性能优化实战：构建速度与产物体积优化

> 深入讲解 Webpack 性能优化技巧，包括代码分割、Tree Shaking、缓存策略，以及实际项目的优化实践。

## 一、代码分割

### 1.1 动态导入

```javascript
// 静态导入
import './style.css';

// 动态导入 - 代码分割
const module = await import('./module.js');
```

### 1.2 SplitChunks

```javascript
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10
        },
        common: {
          minChunks: 2,
          priority: 5
        }
      }
    }
  }
};
```

## 二、Tree Shaking

### 2.1 开启条件

```javascript
// package.json
{
  "sideEffects": ["*.css"]
}
```

### 2.2 usedExports

```javascript
module.exports = {
  optimization: {
    usedExports: true
  }
};
```

## 三、缓存优化

### 3.1 持久化缓存

```javascript
module.exports = {
  cache: {
    type: 'filesystem',
    buildDependencies: {
      config: [__filename]
    }
  }
};
```

### 3.2 缓存 Loader

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.js$/,
        use: [
          {
            loader: 'babel-loader',
            options: { cacheDirectory: true }
          }
        ]
      }
    ]
  }
};
```

## 四、压缩优化

### 4.1 Terser

```javascript
module.exports = {
  optimization: {
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true
          }
        }
      })
    ]
  }
};
```

### 4.2 CSS 压缩

```javascript
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  optimization: {
    minimizer: [new CssMinimizerPlugin()]
  }
};
```

## 五、构建速度

### 5.1 并行构建

```javascript
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
  optimization: {
    minimizer: [
      new TerserPlugin({
        parallel: true
      })
    ]
  }
};
```

### 5.2 排除依赖

```javascript
module.exports = {
  externals: {
    react: 'React',
    'react-dom': 'ReactDOM'
  }
};
```

## 六、总结

Webpack 优化核心：

1. **代码分割**：动态导入、SplitChunks
2. **Tree Shaking**：消除死代码
3. **缓存**：持久化缓存
4. **压缩**：Terser、CSSMinimizer
5. **速度**：并行构建、外部依赖

掌握这些，构建飞起来！

---

**推荐阅读**：
- [Webpack 官方指南](https://webpack.js.org/guides/production/)

**如果对你有帮助，欢迎点赞收藏！**
