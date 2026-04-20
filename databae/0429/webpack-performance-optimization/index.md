# Webpack 构建性能优化完全指南：从基础到企业级

## 一、性能优化概述

Webpack 优化主要从两方面入手：
- **构建性能**：加快编译速度
- **打包性能**：减小输出文件大小

---

## 二、开发环境优化

### 2.1 使用 webpack-dev-server

```javascript
// webpack.config.js
module.exports = {
  devServer: {
    hot: true,
    port: 3000,
    open: true,
    historyApiFallback: true
  }
};
```

### 2.2 模块热替换（HMR）

```javascript
module.exports = {
  devServer: { hot: true },
  plugins: [new webpack.HotModuleReplacementPlugin()]
};
```

### 2.3 合理配置 source map

```javascript
module.exports = {
  // 开发环境：快速
  devtool: 'eval-cheap-module-source-map',
  // 生产环境：高质量
  devtool: 'source-map'
};
```

---

## 三、构建缓存

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

### 3.2 babel-loader 缓存

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.js$/,
        use: {
          loader: 'babel-loader',
          options: { cacheDirectory: true }
        },
        exclude: /node_modules/
      }
    ]
  }
};
```

---

## 四、代码分割

### 4.1 入口分割

```javascript
module.exports = {
  entry: {
    main: './src/main.js',
    vendor: './src/vendor.js'
  }
};
```

### 4.2 动态导入

```javascript
// main.js
async function loadChart() {
  const module = await import('./chart.js');
  module.renderChart();
}
```

### 4.3 SplitChunksPlugin

```javascript
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    }
  }
};
```

---

## 五、Tree Shaking

### 5.1 配置

```javascript
// webpack.config.js
module.exports = {
  mode: 'production',
  optimization: {
    usedExports: true
  }
};

// package.json
{
  "sideEffects": false
}
```

---

## 六、压缩优化

### 6.1 JS 压缩

```javascript
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
  optimization: {
    minimizer: [
      new TerserPlugin({
        parallel: true,
        terserOptions: {
          compress: { drop_console: true }
        }
      })
    ]
  }
};
```

### 6.2 CSS 压缩

```javascript
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader']
      }
    ]
  },
  plugins: [new MiniCssExtractPlugin()],
  optimization: {
    minimizer: [
      `...`,
      new CssMinimizerPlugin()
    ]
  }
};
```

### 6.3 图片压缩

```javascript
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');

module.exports = {
  optimization: {
    minimizer: [
      new ImageMinimizerPlugin({
        minimizer: {
          implementation: ImageMinimizerPlugin.sharpMinify,
          options: { encodeOptions: { jpeg: { quality: 80 } } }
        }
      })
    ]
  }
};
```

---

## 七、模块解析优化

```javascript
module.exports = {
  resolve: {
    extensions: ['.js', '.jsx', '.json'],
    alias: {
      '@': path.resolve(__dirname, 'src')
    },
    modules: [path.resolve(__dirname, 'node_modules')]
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        include: path.resolve(__dirname, 'src'),
        exclude: /node_modules/
      }
    ]
  }
};
```

---

## 八、DLL 预编译

```javascript
// webpack.dll.js
const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: {
    vendor: ['react', 'react-dom', 'lodash']
  },
  output: {
    path: path.resolve(__dirname, 'dll'),
    filename: '[name].dll.js',
    library: '[name]'
  },
  plugins: [
    new webpack.DllPlugin({
      name: '[name]',
      path: path.join(__dirname, 'dll', '[name]-manifest.json')
    })
  ]
};

// webpack.config.js
module.exports = {
  plugins: [
    new webpack.DllReferencePlugin({
      manifest: require('./dll/vendor-manifest.json')
    })
  ]
};
```

---

## 九、多进程构建

```javascript
const HappyPack = require('happypack');

module.exports = {
  module: {
    rules: [
      {
        test: /\.js$/,
        use: 'happypack/loader?id=babel',
        exclude: /node_modules/
      }
    ]
  },
  plugins: [
    new HappyPack({
      id: 'babel',
      loaders: ['babel-loader?cacheDirectory']
    })
  ]
};
```

---

## 十、生产环境优化配置

```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  mode: 'production',
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    clean: true
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        use: {
          loader: 'babel-loader',
          options: { cacheDirectory: true }
        },
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader']
      }
    ]
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    },
    minimizer: [
      new TerserPlugin({ parallel: true }),
      new CssMinimizerPlugin()
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({ template: './public/index.html' }),
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css'
    })
  ],
  cache: { type: 'filesystem' }
};
```

---

## 十一、Bundle 分析

```javascript
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  plugins: [new BundleAnalyzerPlugin()]
};
```

---

## 十二、最佳实践

1. 使用持久化缓存加速构建
2. 合理配置代码分割
3. 启用 Tree Shaking
4. 压缩所有资源（JS、CSS、图片）
5. 使用 Bundle Analyzer 分析包大小

---

## 十三、总结

Webpack 优化是一个综合过程，需从构建速度和输出大小两方面同时优化。
