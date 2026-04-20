# JavaScript ES Modules 完全指南：从 import/export 到模块联邦

## 一、模块化概述

### 1.1 模块化的演进

- **CommonJS**：Node.js 原生模块系统
- **AMD**：RequireJS 浏览器模块系统
- **ESM**：ECMAScript Modules（原生）

### 1.2 ESM 特性

- 静态分析，编译时确定依赖
- 浏览器原生支持
- 支持 tree shaking

---

## 二、export 导出

### 2.1 命名导出

```javascript
// utils.js
export const PI = 3.14159;

export function add(a, b) {
  return a + b;
}

export function multiply(a, b) {
  return a * b;
}

export class Calculator {
  add(a, b) { return a + b; }
}
```

### 2.2 默认导出

```javascript
// math.js
export default function add(a, b) {
  return a + b;
}

// 或者
const PI = 3.14159;
export default PI;
```

### 2.3 重命名导出

```javascript
const sum = (a, b) => a + b;
const product = (a, b) => a * b;

export { sum as add, product as multiply };
```

### 2.4 聚合导出

```javascript
export * from './math.js';
export * as utils from './utils.js';
export { add, subtract } from './math.js';
export { default as Calculator } from './calculator.js';
```

---

## 三、import 导入

### 3.1 命名导入

```javascript
import { PI, add, multiply } from './utils.js';

console.log(PI);
console.log(add(1, 2));
```

### 3.2 重命名导入

```javascript
import { add as sum, multiply as product } from './utils.js';
```

### 3.3 命名空间导入

```javascript
import * as utils from './utils.js';

console.log(utils.PI);
console.log(utils.add(1, 2));
```

### 3.4 默认导入

```javascript
import add from './math.js';
console.log(add(1, 2));

// 混合导入
import add, { PI, multiply } from './math.js';
```

### 3.5 动态导入

```javascript
async function loadModule() {
  const module = await import('./utils.js');
  console.log(module.add(1, 2));
}

loadModule();

// 条件导入
if (condition) {
  import('./module.js').then(m => m.default());
}
```

---

## 四、浏览器中使用

### 4.1 script 标签

```html
<script type="module">
  import { add } from './utils.js';
  console.log(add(1, 2));
</script>

<script type="module" src="main.js"></script>
```

### 4.2 importmap

```html
<script type="importmap">
{
  "imports": {
    "lodash": "https://esm.sh/lodash@4.17.21",
    "@/": "./src/"
  }
}
</script>

<script type="module">
  import _ from 'lodash';
  import utils from '@/utils.js';
</script>
```

---

## 五、Node.js 中使用

### 5.1 package.json 配置

```json
{
  "type": "module"
}
```

### 5.2 导入方式

```javascript
// 导入 npm 包
import lodash from 'lodash-es';

// 导入本地文件
import utils from './utils.js';

// 导入 JSON
import data from './data.json' assert { type: 'json' };

// 动态导入
const module = await import('./utils.js');
```

### 5.3 CommonJS 互操作

```javascript
// ESM 导入 CJS
import cjsModule from './commonjs.cjs';

// CJS 导入 ESM（使用 import()）
const esmModule = await import('./esm.js');
```

---

## 六、高级特性

### 6.1 模块元信息

```javascript
console.log(import.meta.url);
console.log(import.meta.resolve('./utils.js'));
```

### 6.2 顶级 await

```javascript
// 可以在模块顶层使用 await
const data = await fetch('data.json').then(r => r.json());
export default data;
```

### 6.3 模块联邦

```javascript
// webpack 配置
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'app1',
      filename: 'remoteEntry.js',
      exposes: {
        './Button': './src/Button'
      },
      remotes: {
        app2: 'app2@http://localhost:3002/remoteEntry.js'
      }
    })
  ]
};

// 消费远程模块
import { Button } from 'app2/Button';
```

---

## 七、Tree Shaking

### 7.1 原理

```javascript
// utils.js
export function used() {}
export function unused() {}

// main.js
import { used } from './utils.js';

// 打包时 unused 会被移除
```

### 7.2 配置

```javascript
// webpack.config.js
module.exports = {
  mode: 'production',
  optimization: {
    usedExports: true,
    sideEffects: false
  }
};

// package.json
{
  "sideEffects": false
}
```

---

## 八、最佳实践

### 8.1 项目结构

```
src/
├── index.js
├── utils/
│   ├── index.js
│   ├── math.js
│   └── string.js
├── components/
│   ├── index.js
│   ├── Button.js
│   └── Input.js
└── services/
    ├── index.js
    └── api.js
```

### 8.2 导出策略

```javascript
// index.js 作为聚合导出
export * from './math.js';
export * from './string.js';
export { default as Calculator } from './calculator.js';

// 使用
import { add, Calculator } from './utils/index.js';
```

---

## 总结

ES Modules 是 JavaScript 的原生模块化方案，通过合理使用 import/export，可以构建清晰、可维护的代码结构。结合构建工具，还能实现 tree shaking 和模块联邦等高级特性。
