# css-loader 与 style-loader：CSS 在 webpack 中的加载原理

> 搞懂这两个 loader 的区别和配合，才能真正理解 webpack 如何处理 CSS

---

## 一、为什么需要 loader

webpack 本身只认识 JavaScript，当你在 JS 中引入 CSS 时：

```javascript
import './style.css';
```

webpack 不知道如何处理 `.css` 文件，这时就需要 loader 来转换。

---

## 二、css-loader：解析 CSS

css-loader 的作用是**解析 CSS 文件**，处理 `@import` 和 `url()` 等语句。

### 基础用法

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['css-loader']
      }
    ]
  }
};
```

### css-loader 做了什么

```css
/* style.css */
@import './base.css';

.button {
  background: url('./icon.png');
}
```

经过 css-loader 处理后，会：

1. 解析 `@import`，将 `base.css` 的内容合并进来
2. 解析 `url()`，将图片路径转换为 webpack 可识别的模块引用
3. 返回一个 JavaScript 模块，导出 CSS 字符串

```javascript
// css-loader 的输出（简化版）
module.exports = `
  .base { margin: 0; }
  .button { background: url(${require('./icon.png')}); }
`;
```

---

## 三、style-loader：注入样式

css-loader 只是解析了 CSS，但样式还没有生效。style-loader 的作用是**将 CSS 注入到 DOM 中**。

### 基础用法

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']  // 注意顺序！
      }
    ]
  }
};
```

### style-loader 做了什么

style-loader 会生成一段 JavaScript 代码，在运行时创建 `<style>` 标签并插入到 `<head>` 中。

```javascript
// style-loader 的输出（简化版）
const css = require('!!css-loader!./style.css');
const style = document.createElement('style');
style.textContent = css;
document.head.appendChild(style);
```

---

## 四、为什么顺序是 style-loader 在前

webpack 的 loader 是**从右到左**（或从下到上）执行的：

```javascript
use: ['style-loader', 'css-loader']
// 执行顺序：css-loader → style-loader
```

1. 先用 css-loader 解析 CSS，得到 CSS 字符串
2. 再用 style-loader 将 CSS 注入到 DOM

如果顺序反了，style-loader 会收到原始的 CSS 文件，无法正确处理。

---

## 五、CSS Modules

css-loader 支持 CSS Modules，实现样式的局部作用域。

### 开启 CSS Modules

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.module\.css$/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {
              modules: true  // 开启 CSS Modules
            }
          }
        ]
      }
    ]
  }
};
```

### 使用

```css
/* Button.module.css */
.button {
  background: blue;
}

.primary {
  background: green;
}
```

```javascript
import styles from './Button.module.css';

function Button() {
  return (
    <button className={styles.button}>
      Click me
    </button>
  );
}

// 渲染后的 HTML
// <button class="Button_button__2x3y">Click me</button>
```

类名被转换为唯一的哈希值，避免全局污染。

### 自定义类名格式

```javascript
{
  loader: 'css-loader',
  options: {
    modules: {
      localIdentName: '[path][name]__[local]--[hash:base64:5]'
    }
  }
}

// 生成的类名：src-Button__button--2x3y
```

---

## 六、Source Map

开启 Source Map 可以在浏览器中看到原始的 CSS 文件位置。

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {
              sourceMap: true
            }
          }
        ]
      }
    ]
  }
};
```

---

## 七、生产环境优化

在生产环境中，通常不使用 style-loader，而是将 CSS 提取到单独的文件中。

### 使用 mini-css-extract-plugin

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
      filename: '[name].[contenthash].css'
    })
  ]
};
```

优势：
- CSS 可以并行加载，不阻塞 JS
- 可以利用浏览器缓存
- 减少 JS 文件体积

---

## 八、处理 @import 和 url()

### @import

```css
/* style.css */
@import './base.css';
@import url('https://fonts.googleapis.com/css?family=Roboto');
```

```javascript
{
  loader: 'css-loader',
  options: {
    import: true,  // 处理 @import（默认开启）
    importLoaders: 1  // @import 的文件也经过后面的 loader
  }
}
```

### url()

```css
.icon {
  background: url('./icon.png');
}
```

```javascript
{
  loader: 'css-loader',
  options: {
    url: true  // 处理 url()（默认开启）
  }
}
```

如果不想处理某些 url：

```javascript
{
  loader: 'css-loader',
  options: {
    url: {
      filter: (url) => {
        // 不处理绝对路径
        return !url.startsWith('/');
      }
    }
  }
}
```

---

## 九、完整配置示例

开发环境：

```javascript
module.exports = {
  mode: 'development',
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {
              sourceMap: true,
              importLoaders: 1
            }
          },
          'postcss-loader'  // 处理 autoprefixer 等
        ]
      }
    ]
  }
};
```

生产环境：

```javascript
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  mode: 'production',
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              importLoaders: 1
            }
          },
          'postcss-loader'
        ]
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'css/[name].[contenthash:8].css'
    })
  ],
  optimization: {
    minimizer: [
      new CssMinimizerPlugin()  // 压缩 CSS
    ]
  }
};
```

---

## 十、常见问题

### 1. 样式没有生效？

检查 loader 顺序，确保 style-loader 在 css-loader 前面。

### 2. CSS Modules 不生效？

确保文件名匹配规则（如 `.module.css`），并且 `modules` 选项开启。

### 3. 图片路径错误？

检查 `url-loader` 或 `file-loader` 的配置，确保 `publicPath` 正确。

### 4. HMR 不工作？

style-loader 默认支持 HMR，如果不工作，检查 webpack-dev-server 配置。

---

## 总结

- **css-loader**：解析 CSS，处理 `@import` 和 `url()`
- **style-loader**：将 CSS 注入到 DOM 中
- 开发环境用 style-loader，生产环境用 MiniCssExtractPlugin
- CSS Modules 可以实现样式的局部作用域
- 合理配置 Source Map 和 importLoaders

理解这两个 loader 的工作原理，是掌握 webpack CSS 处理的基础。

如果这篇文章对你有帮助，欢迎点赞收藏！
