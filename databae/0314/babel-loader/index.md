# babel-loader：让你的 JS 代码兼容所有浏览器

> 从配置到优化，掌握 babel-loader 的完整用法

---

## 一、为什么需要 Babel

现代 JavaScript 有很多新特性（ES6+），但旧浏览器不支持。

```javascript
// ES6+ 代码
const greet = (name) => `Hello, ${name}!`;
class Person {
  constructor(name) {
    this.name = name;
  }
}

// 旧浏览器需要转换为 ES5
var greet = function(name) {
  return 'Hello, ' + name + '!';
};
function Person(name) {
  this.name = name;
}
```

Babel 就是用来做这个转换的，babel-loader 让 webpack 能够使用 Babel。

---

## 二、基础配置

### 安装

```bash
npm install --save-dev babel-loader @babel/core @babel/preset-env
```

### webpack 配置

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  }
};
```

---

## 三、Babel 配置文件

推荐使用独立的配置文件，而不是写在 webpack 配置中。

### babel.config.js（推荐）

```javascript
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        browsers: ['> 1%', 'last 2 versions', 'not dead']
      },
      useBuiltIns: 'usage',
      corejs: 3
    }]
  ],
  plugins: []
};
```

### .babelrc

```json
{
  "presets": [
    ["@babel/preset-env", {
      "targets": "> 0.25%, not dead"
    }]
  ]
}
```

---

## 四、Preset 详解

### @babel/preset-env

最常用的 preset，根据目标环境自动确定需要的转换。

```javascript
{
  presets: [
    ['@babel/preset-env', {
      // 目标环境
      targets: {
        chrome: '58',
        ie: '11',
        node: '12'
      },
      
      // 或使用 browserslist 查询
      targets: '> 0.25%, not dead',
      
      // 模块转换：'auto' | 'amd' | 'umd' | 'systemjs' | 'commonjs' | false
      modules: false,  // webpack 已处理模块，设为 false
      
      // polyfill 策略
      useBuiltIns: 'usage',  // 'usage' | 'entry' | false
      corejs: 3
    }]
  ]
}
```

### @babel/preset-react

转换 JSX 语法。

```bash
npm install --save-dev @babel/preset-react
```

```javascript
{
  presets: [
    '@babel/preset-env',
    ['@babel/preset-react', {
      runtime: 'automatic'  // React 17+ 不需要 import React
    }]
  ]
}
```

### @babel/preset-typescript

转换 TypeScript。

```bash
npm install --save-dev @babel/preset-typescript
```

```javascript
{
  presets: [
    '@babel/preset-env',
    '@babel/preset-typescript'
  ]
}
```

---

## 五、Polyfill 策略

### useBuiltIns: 'usage'（推荐）

根据代码中实际使用的特性自动引入 polyfill。

```bash
npm install --save core-js@3
```

```javascript
// 源代码
const promise = Promise.resolve();
const arr = [1, 2, 3].includes(2);

// Babel 自动添加需要的 polyfill
import "core-js/modules/es.promise";
import "core-js/modules/es.array.includes";
```

### useBuiltIns: 'entry'

手动在入口引入，Babel 根据目标环境替换为需要的 polyfill。

```javascript
// 入口文件
import 'core-js/stable';
import 'regenerator-runtime/runtime';

// Babel 会替换为具体需要的 polyfill
```

### useBuiltIns: false

不自动引入 polyfill，需要手动管理。

---

## 六、常用插件

### 1. 类属性

```bash
npm install --save-dev @babel/plugin-proposal-class-properties
```

```javascript
// 支持类属性语法
class MyClass {
  count = 0;  // 实例属性
  static version = '1.0';  // 静态属性
  
  handleClick = () => {  // 箭头函数自动绑定 this
    this.count++;
  }
}
```

### 2. 装饰器

```bash
npm install --save-dev @babel/plugin-proposal-decorators
```

```javascript
{
  plugins: [
    ['@babel/plugin-proposal-decorators', { legacy: true }],
    ['@babel/plugin-proposal-class-properties', { loose: true }]
  ]
}
```

```javascript
@connect(mapStateToProps)
class MyComponent extends React.Component {
  // ...
}
```

### 3. 可选链和空值合并

```bash
npm install --save-dev @babel/plugin-proposal-optional-chaining
npm install --save-dev @babel/plugin-proposal-nullish-coalescing-operator
```

```javascript
// 可选链
const name = user?.profile?.name;

// 空值合并
const count = value ?? 0;
```

---

## 七、性能优化

### 1. 缓存

```javascript
{
  test: /\.js$/,
  exclude: /node_modules/,
  use: {
    loader: 'babel-loader',
    options: {
      cacheDirectory: true,  // 开启缓存
      cacheCompression: false  // 不压缩缓存
    }
  }
}
```

### 2. 限制转换范围

```javascript
{
  test: /\.js$/,
  // 只转换 src 目录
  include: path.resolve(__dirname, 'src'),
  // 排除 node_modules
  exclude: /node_modules/,
  use: 'babel-loader'
}
```

### 3. 使用 thread-loader

```bash
npm install --save-dev thread-loader
```

```javascript
{
  test: /\.js$/,
  use: [
    'thread-loader',  // 多线程编译
    'babel-loader'
  ]
}
```

---

## 八、环境区分

### 开发环境

```javascript
// babel.config.js
module.exports = (api) => {
  const isDev = api.env('development');
  
  return {
    presets: [
      ['@babel/preset-env', {
        targets: isDev ? { node: 'current' } : '> 0.25%, not dead',
        modules: false
      }],
      '@babel/preset-react'
    ],
    plugins: [
      isDev && 'react-refresh/babel'  // 开发环境热更新
    ].filter(Boolean)
  };
};
```

### 生产环境

```javascript
{
  presets: [
    ['@babel/preset-env', {
      targets: '> 0.25%, not dead',
      useBuiltIns: 'usage',
      corejs: 3
    }]
  ],
  plugins: [
    ['transform-remove-console', {  // 移除 console
      exclude: ['error', 'warn']
    }]
  ]
}
```

---

## 九、常见问题

### 1. async/await 不工作？

需要 regenerator-runtime：

```bash
npm install --save regenerator-runtime
```

```javascript
// 入口文件
import 'regenerator-runtime/runtime';
```

或使用 @babel/plugin-transform-runtime：

```bash
npm install --save-dev @babel/plugin-transform-runtime
npm install --save @babel/runtime
```

```javascript
{
  plugins: [
    ['@babel/plugin-transform-runtime', {
      regenerator: true
    }]
  ]
}
```

### 2. 某些 ES6+ 特性不转换？

检查 targets 配置，可能目标环境已支持该特性。

### 3. 打包体积太大？

- 使用 `useBuiltIns: 'usage'` 按需引入 polyfill
- 检查是否转换了 node_modules
- 使用 @babel/plugin-transform-runtime 避免重复代码

---

## 十、完整配置示例

```javascript
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        browsers: ['> 1%', 'last 2 versions', 'not dead']
      },
      useBuiltIns: 'usage',
      corejs: 3,
      modules: false
    }],
    ['@babel/preset-react', {
      runtime: 'automatic'
    }],
    '@babel/preset-typescript'
  ],
  plugins: [
    ['@babel/plugin-proposal-decorators', { legacy: true }],
    ['@babel/plugin-proposal-class-properties', { loose: true }],
    '@babel/plugin-proposal-optional-chaining',
    '@babel/plugin-proposal-nullish-coalescing-operator',
    ['@babel/plugin-transform-runtime', {
      corejs: false,
      helpers: true,
      regenerator: true
    }]
  ]
};
```

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        include: path.resolve(__dirname, 'src'),
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            cacheDirectory: true,
            cacheCompression: false
          }
        }
      }
    ]
  }
};
```

---

## 总结

babel-loader 是现代前端工程化的基础设施，掌握它能让你：

- 放心使用最新的 JavaScript 特性
- 兼容各种目标环境
- 优化打包体积和性能
- 支持 React、TypeScript 等生态

合理配置 Babel，能让开发更高效，代码更现代。

如果这篇文章对你有帮助，欢迎点赞收藏！
