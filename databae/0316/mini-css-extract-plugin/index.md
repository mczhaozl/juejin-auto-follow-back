# mini-css-extract-plugin：生产环境 CSS 提取的最佳方案

> 告别 style-loader，让 CSS 独立加载并支持缓存

---

## 一、为什么需要提取 CSS

开发环境用 style-loader 将 CSS 注入到 JS 中很方便，但生产环境有问题：

- CSS 包含在 JS 中，增加 JS 体积
- CSS 无法并行加载
- 无法利用浏览器缓存
- 首屏渲染会闪烁（FOUC）

mini-css-extract-plugin 可以将 CSS 提取到独立文件。

---

## 二、基础配置

### 安装

```bash
npm install --save-dev mini-css-extract-plugin
```

### webpack 配置

```javascript
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,  // 替换 style-loader
          'css-loader'
        ]
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash:8].css'
    })
  ]
};
```

---

## 三、环境区分

开发环境用 style-loader（支持 HMR），生产环境用 MiniCssExtractPlugin。

```javascript
const isDev = process.env.NODE_ENV === 'development';

module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          isDev ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      }
    ]
  },
  plugins: [
    !isDev && new MiniCssExtractPlugin({
      filename: 'css/[name].[contenthash:8].css'
    })
  ].filter(Boolean)
};
```

---

## 四、配置选项

```javascript
new MiniCssExtractPlugin({
  // 输出文件名
  filename: '[name].[contenthash:8].css',
  
  // 异步 chunk 的文件名
  chunkFilename: '[id].[contenthash:8].css',
  
  // 是否在运行时插入 <link> 标签
  insert: '#some-element',
  
  // 自定义属性
  attributes: {
    id: 'my-css',
    'data-target': 'head'
  },
  
  // 移除 Order 警告
  ignoreOrder: false
})
```

---

## 五、CSS 压缩

使用 css-minimizer-webpack-plugin 压缩 CSS。

```bash
npm install --save-dev css-minimizer-webpack-plugin
```

```javascript
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  optimization: {
    minimizer: [
      '...',  // 保留默认的 JS 压缩
      new CssMinimizerPlugin()
    ]
  }
};
```

---

## 六、代码分割

### 按入口分割

```javascript
module.exports = {
  entry: {
    home: './src/home.js',
    about: './src/about.js'
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].css'
    })
  ]
};

// 输出：home.css, about.css
```

### 按路由分割

```javascript
// 动态导入
const Home = lazy(() => import('./Home'));
const About = lazy(() => import('./About'));

// 每个路由的 CSS 会被提取到独立文件
```

---

## 七、HMR 支持

mini-css-extract-plugin 在开发环境也支持 HMR，但需要配置。

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
            options: {
              hmr: process.env.NODE_ENV === 'development'
            }
          },
          'css-loader'
        ]
      }
    ]
  }
};
```

---

## 八、完整配置示例

```javascript
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

const isDev = process.env.NODE_ENV === 'development';

module.exports = {
  mode: isDev ? 'development' : 'production',
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          isDev ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader'
        ]
      },
      {
        test: /\.scss$/,
        use: [
          isDev ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
          'sass-loader'
        ]
      }
    ]
  },
  plugins: [
    !isDev && new MiniCssExtractPlugin({
      filename: 'css/[name].[contenthash:8].css',
      chunkFilename: 'css/[id].[contenthash:8].css'
    })
  ].filter(Boolean),
  optimization: {
    minimizer: [
      '...',
      new CssMinimizerPlugin({
        minimizerOptions: {
          preset: [
            'default',
            {
              discardComments: { removeAll: true }
            }
          ]
        }
      })
    ]
  }
};
```

---

## 总结

mini-css-extract-plugin 是生产环境的标准方案，它能：

- 提取 CSS 到独立文件
- 支持代码分割和缓存
- 配合压缩插件优化体积
- 提升首屏加载性能

在生产环境中，务必使用这个插件替代 style-loader。

如果这篇文章对你有帮助，欢迎点赞收藏！
