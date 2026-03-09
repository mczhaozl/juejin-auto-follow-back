# html-webpack-plugin：自动生成 HTML 的必备插件

> 从单页到多页，掌握 html-webpack-plugin 的完整用法与最佳实践

---

## 一、为什么需要这个插件

在使用 webpack 打包时，我们需要一个 HTML 文件来加载打包后的 JS 和 CSS。

手动维护 HTML 的问题：
- 每次打包后文件名变化（contenthash），需要手动更新
- 多个入口需要创建多个 HTML
- 无法自动注入环境变量

html-webpack-plugin 可以自动生成 HTML 并注入资源。

---

## 二、基础用法

### 安装

```bash
npm install --save-dev html-webpack-plugin
```

### 最简配置

```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/index.js',
  plugins: [
    new HtmlWebpackPlugin()
  ]
};
```

生成的 HTML：

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Webpack App</title>
  </head>
  <body>
    <script src="bundle.js"></script>
  </body>
</html>
```

---

## 三、常用配置选项

```javascript
new HtmlWebpackPlugin({
  // 模板文件
  template: './src/index.html',
  
  // 输出文件名
  filename: 'index.html',
  
  // 页面标题
  title: '我的应用',
  
  // 注入位置：true | 'head' | 'body' | false
  inject: 'body',
  
  // 压缩选项
  minify: {
    removeComments: true,
    collapseWhitespace: true,
    removeAttributeQuotes: true
  },
  
  // 添加 hash 到引用的资源
  hash: true,
  
  // 指定使用的 chunk
  chunks: ['main', 'vendor'],
  
  // 排除某些 chunk
  excludeChunks: ['admin'],
  
  // 自定义元数据
  meta: {
    viewport: 'width=device-width, initial-scale=1',
    description: '应用描述'
  },
  
  // 添加 favicon
  favicon: './src/favicon.ico'
})
```

---

## 四、使用模板

### EJS 模板

```html
<!-- src/index.html -->
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title><%= htmlWebpackPlugin.options.title %></title>
    <% if (htmlWebpackPlugin.options.description) { %>
      <meta name="description" content="<%= htmlWebpackPlugin.options.description %>">
    <% } %>
  </head>
  <body>
    <div id="app"></div>
    
    <!-- 注入环境变量 -->
    <script>
      window.API_URL = '<%= htmlWebpackPlugin.options.apiUrl %>';
    </script>
  </body>
</html>
```

```javascript
new HtmlWebpackPlugin({
  template: './src/index.html',
  title: '我的应用',
  description: '这是一个很棒的应用',
  apiUrl: process.env.API_URL || 'https://api.example.com'
})
```

### 访问 webpack 配置

```html
<body>
  <div id="app"></div>
  
  <!-- 开发环境显示调试信息 -->
  <% if (webpackConfig.mode === 'development') { %>
    <div class="debug-info">开发模式</div>
  <% } %>
</body>
```

---

## 五、多页应用配置

```javascript
module.exports = {
  entry: {
    index: './src/index.js',
    about: './src/about.js',
    contact: './src/contact.js'
  },
  plugins: [
    // 首页
    new HtmlWebpackPlugin({
      template: './src/index.html',
      filename: 'index.html',
      chunks: ['index', 'vendor']  // 只注入 index 和 vendor
    }),
    
    // 关于页
    new HtmlWebpackPlugin({
      template: './src/about.html',
      filename: 'about.html',
      chunks: ['about', 'vendor']
    }),
    
    // 联系页
    new HtmlWebpackPlugin({
      template: './src/contact.html',
      filename: 'contact.html',
      chunks: ['contact', 'vendor']
    })
  ]
};
```

---

## 六、与 CDN 结合

### 使用外部 CDN

```javascript
module.exports = {
  externals: {
    'react': 'React',
    'react-dom': 'ReactDOM'
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/index.html',
      cdnScripts: [
        'https://cdn.jsdelivr.net/npm/react@18/umd/react.production.min.js',
        'https://cdn.jsdelivr.net/npm/react-dom@18/umd/react-dom.production.min.js'
      ]
    })
  ]
};
```

模板中使用：

```html
<head>
  <% for (let script of htmlWebpackPlugin.options.cdnScripts) { %>
    <script src="<%= script %>"></script>
  <% } %>
</head>
```

### 使用 webpack-cdn-plugin

```bash
npm install --save-dev webpack-cdn-plugin
```

```javascript
const WebpackCdnPlugin = require('webpack-cdn-plugin');

module.exports = {
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/index.html'
    }),
    new WebpackCdnPlugin({
      modules: [
        { name: 'react', var: 'React', path: 'umd/react.production.min.js' },
        { name: 'react-dom', var: 'ReactDOM', path: 'umd/react-dom.production.min.js' }
      ],
      publicPath: '/node_modules'
    })
  ]
};
```

---

## 七、注入环境变量

### 方法 1：通过模板

```javascript
new HtmlWebpackPlugin({
  template: './src/index.html',
  templateParameters: {
    env: process.env.NODE_ENV,
    apiUrl: process.env.API_URL,
    version: require('./package.json').version
  }
})
```

```html
<script>
  window.ENV = '<%= env %>';
  window.API_URL = '<%= apiUrl %>';
  window.VERSION = '<%= version %>';
</script>
```

### 方法 2：使用 DefinePlugin

```javascript
const webpack = require('webpack');

module.exports = {
  plugins: [
    new webpack.DefinePlugin({
      'process.env.API_URL': JSON.stringify(process.env.API_URL)
    }),
    new HtmlWebpackPlugin({
      template: './src/index.html'
    })
  ]
};
```

---

## 八、自定义插件钩子

html-webpack-plugin 提供了多个钩子，可以在生成 HTML 的不同阶段进行自定义。

```javascript
class MyPlugin {
  apply(compiler) {
    compiler.hooks.compilation.tap('MyPlugin', (compilation) => {
      HtmlWebpackPlugin.getHooks(compilation).beforeEmit.tapAsync(
        'MyPlugin',
        (data, cb) => {
          // 修改 HTML 内容
          data.html = data.html.replace(
            '</body>',
            '<script>console.log("injected")</script></body>'
          );
          cb(null, data);
        }
      );
    });
  }
}

module.exports = {
  plugins: [
    new HtmlWebpackPlugin(),
    new MyPlugin()
  ]
};
```

---

## 九、性能优化

### 1. 预加载关键资源

```javascript
new HtmlWebpackPlugin({
  template: './src/index.html',
  inject: 'body',
  scriptLoading: 'defer',  // 或 'module'
})
```

生成的 HTML：

```html
<script defer src="bundle.js"></script>
```

### 2. 资源提示

使用 preload-webpack-plugin：

```bash
npm install --save-dev preload-webpack-plugin
```

```javascript
const PreloadWebpackPlugin = require('preload-webpack-plugin');

module.exports = {
  plugins: [
    new HtmlWebpackPlugin(),
    new PreloadWebpackPlugin({
      rel: 'preload',
      include: 'initial',
      fileBlacklist: [/\.map$/, /hot-update\.js$/]
    })
  ]
};
```

生成的 HTML：

```html
<link rel="preload" href="main.js" as="script">
<link rel="preload" href="styles.css" as="style">
```

---

## 十、常见问题

### 1. 如何在 HTML 中使用图片？

```html
<!-- 模板中 -->
<img src="<%= require('./assets/logo.png') %>" alt="Logo">
```

需要配置 file-loader 或 url-loader。

### 2. 如何自定义 chunk 顺序？

```javascript
new HtmlWebpackPlugin({
  chunks: ['vendor', 'common', 'main'],
  chunksSortMode: 'manual'  // 按 chunks 数组顺序
})
```

### 3. 如何生成多个 HTML 但共享模板？

```javascript
const pages = ['index', 'about', 'contact'];

module.exports = {
  plugins: pages.map(page => new HtmlWebpackPlugin({
    template: './src/template.html',
    filename: `${page}.html`,
    chunks: [page, 'vendor']
  }))
};
```

---

## 十一、完整示例

```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  mode: 'production',
  entry: {
    main: './src/index.js',
    vendor: ['react', 'react-dom']
  },
  output: {
    filename: '[name].[contenthash:8].js',
    path: path.resolve(__dirname, 'dist'),
    clean: true
  },
  optimization: {
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          chunks: 'all'
        }
      }
    }
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash:8].css'
    }),
    new HtmlWebpackPlugin({
      template: './src/index.html',
      filename: 'index.html',
      title: '我的应用',
      minify: {
        removeComments: true,
        collapseWhitespace: true,
        removeAttributeQuotes: true
      },
      meta: {
        viewport: 'width=device-width, initial-scale=1',
        description: '应用描述'
      },
      favicon: './src/favicon.ico'
    })
  ]
};
```

---

## 总结

html-webpack-plugin 是 webpack 生态中不可或缺的插件，它能：

- 自动生成 HTML 并注入资源
- 支持模板和自定义配置
- 轻松实现多页应用
- 与 CDN、环境变量无缝集成

掌握这个插件的用法，能让你的 webpack 配置更加灵活和强大。

如果这篇文章对你有帮助，欢迎点赞收藏！
