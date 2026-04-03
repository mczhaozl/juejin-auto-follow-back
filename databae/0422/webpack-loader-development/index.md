# Webpack Loader 开发完全指南：从原理到实战

Loader 是 Webpack 的核心概念之一，它让 Webpack 能够处理各种类型的文件。本文将带你从零开发自己的 Loader。

## 一、Loader 基础

### 1. 什么是 Loader

Loader 是一个 Node.js 模块，它导出一个函数。这个函数接收源文件内容，返回转换后的内容。

```javascript
// simple-loader.js
module.exports = function(source) {
  console.log('Source:', source);
  return source;
};
```

### 2. 最简单的 Loader

```javascript
// uppercase-loader.js
module.exports = function(source) {
  return source.toUpperCase();
};
```

### 3. 使用 Loader

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.txt$/,
        use: './uppercase-loader.js',
      },
    ],
  },
};
```

## 二、Loader API

### 1. 同步 Loader

```javascript
module.exports = function(source) {
  const result = source.toUpperCase();
  return result;
};
```

### 2. 异步 Loader

```javascript
module.exports = function(source) {
  const callback = this.async();
  
  setTimeout(() => {
    const result = source.toUpperCase();
    callback(null, result);
  }, 1000);
};
```

### 3. Loader Options

```javascript
module.exports = function(source) {
  const options = this.getOptions();
  const prefix = options.prefix || '[PREFIX]';
  return `${prefix} ${source}`;
};
```

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.txt$/,
        use: {
          loader: './prefix-loader.js',
          options: {
            prefix: '[LOG]',
          },
        },
      },
    ],
  },
};
```

### 4. Source Maps

```javascript
module.exports = function(source, sourceMap) {
  const result = source.toUpperCase();
  this.callback(null, result, sourceMap);
};
```

### 5. Loader 缓存

```javascript
module.exports = function(source) {
  this.cacheable();
  return source.toUpperCase();
};
```

## 三、实战：开发一个 Markdown Loader

### 1. 项目结构

```
markdown-loader/
├── package.json
├── src/
│   └── index.js
└── example/
    ├── webpack.config.js
    ├── src/
    │   ├── index.js
    │   └── README.md
    └── dist/
```

### 2. package.json

```json
{
  "name": "markdown-loader",
  "version": "1.0.0",
  "main": "src/index.js",
  "dependencies": {
    "marked": "^12.0.0"
  },
  "peerDependencies": {
    "webpack": "^5.0.0"
  }
}
```

### 3. Loader 实现

```javascript
const marked = require('marked');

module.exports = function(source) {
  const options = this.getOptions();
  
  marked.setOptions({
    highlight: options.highlight,
    breaks: options.breaks !== false,
  });
  
  const html = marked.parse(source);
  
  return `
    const html = ${JSON.stringify(html)};
    export default html;
  `;
};
```

### 4. 使用示例

```javascript
// webpack.config.js
const path = require('path');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.md$/,
        use: [
          {
            loader: path.resolve(__dirname, '../src/index.js'),
            options: {
              breaks: true,
            },
          },
        ],
      },
    ],
  },
};
```

```javascript
// src/index.js
import readme from './README.md';

document.getElementById('app').innerHTML = readme;
```

## 四、实战：开发一个 CSS Modules Loader

### 1. Loader 实现

```javascript
const { interpolateName } = require('loader-utils');
const path = require('path');

module.exports = function(source) {
  const options = this.getOptions();
  const localIdentName = options.localIdentName || '[local]_[hash:base64:8]';
  
  const cssModuleMap = {};
  const css = source.replace(/\.([a-zA-Z_][a-zA-Z0-9_-]*)/g, (match, className) => {
    if (!cssModuleMap[className]) {
      const context = this.rootContext;
      const resourcePath = this.resourcePath;
      const hashedClassName = interpolateName(
        this,
        localIdentName,
        { context, resourcePath, content: source }
      ).replace(/\[local\]/g, className);
      cssModuleMap[className] = hashedClassName;
    }
    return '.' + cssModuleMap[className];
  });
  
  const exports = Object.entries(cssModuleMap)
    .map(([key, value]) => `  "${key}": "${value}"`)
    .join(',\n');
  
  return `
    import { injectStyle } from './style-injector';
    const css = \`${css}\`;
    injectStyle(css);
    export default {
${exports}
    };
  `;
};
```

### 2. 配套的 style-injector.js

```javascript
let styleElement;

export function injectStyle(css) {
  if (!styleElement) {
    styleElement = document.createElement('style');
    document.head.appendChild(styleElement);
  }
  styleElement.textContent += css;
}
```

## 五、Loader 链

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
          'style-loader',
          'css-loader',
          'sass-loader',
        ],
      },
    ],
  },
};
```

执行顺序从右到左：
1. sass-loader：Sass → CSS
2. css-loader：CSS → JS
3. style-loader：JS → DOM

## 六、Pitch Loader

```javascript
module.exports = function(source) {
  return source;
};

module.exports.pitch = function(remainingRequest, precedingRequest, data) {
  console.log('Pitch phase');
};
```

## 七、最佳实践

1. 保持 Loader 简单
2. 使用 loader-utils 处理选项
3. 支持 Source Maps
4. 合理使用缓存
5. 编写测试

## 八、测试 Loader

```javascript
const path = require('path');
const webpack = require('webpack');
const { createFsFromVolume, Volume } = require('memfs');

test('uppercase-loader', (done) => {
  const compiler = webpack({
    entry: './test/fixtures/input.txt',
    module: {
      rules: [
        {
          test: /\.txt$/,
          use: path.resolve(__dirname, '../uppercase-loader.js'),
        },
      ],
    },
  });

  const fs = createFsFromVolume(new Volume());
  compiler.outputFileSystem = fs;

  compiler.run((err, stats) => {
    expect(err).toBeNull();
    const output = fs.readFileSync('/main.js', 'utf8');
    expect(output).toContain('HELLO WORLD');
    done();
  });
});
```

## 九、总结

开发 Webpack Loader 并不难：
- Loader 只是一个函数
- 接收源文件，返回转换结果
- 使用 Loader API 获取上下文
- 可以同步或异步
- 支持 Source Maps 和缓存

开始开发你自己的 Loader 吧！
