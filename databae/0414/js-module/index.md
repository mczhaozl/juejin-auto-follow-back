# JavaScript 模块完全指南：CommonJS 与 ES Module

> 深入讲解 JavaScript 模块系统，包括 CommonJS、ES Module、动态导入，以及模块加载机制和实际项目中的最佳实践。

## 一、CommonJS

### 1.1 导出

```javascript
// math.js
module.exports = {
  add: (a, b) => a + b,
  subtract: (a, b) => a - b
};

// 或
exports.add = (a, b) => a + b;
exports.subtract = (a, b) => a - b;
```

### 1.2 导入

```javascript
const math = require('./math');
console.log(math.add(1, 2));
```

## 二、ES Module

### 2.1 导出

```javascript
// math.js
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;

export default function multiply(a, b) {
  return a * b;
}
```

### 2.2 导入

```javascript
import { add, subtract } from './math.js';
import multiply from './math.js';

console.log(add(1, 2));
console.log(multiply(3, 4));
```

### 2.3 别名

```javascript
import { add as sum } from './math.js';
console.log(sum(1, 2));
```

## 三、动态导入

### 3.1 import()

```javascript
// 动态导入
const module = await import('./math.js');
console.log(module.add(1, 2));
```

### 3.2 懒加载

```javascript
button.addEventListener('click', async () => {
  const { add } = await import('./math.js');
  console.log(add(1, 2));
});
```

## 四、对比

### 4.1 区别

| 特性 | CommonJS | ES Module |
|------|----------|-----------|
| 语法 | require/module.exports | import/export |
| 加载 | 同步 | 异步 |
| 绑定 | 值拷贝 | 实时绑定 |
| 顶层 | 不支持 | 支持 |

### 4.2 互相转换

```javascript
// Node.js 中使用 ES Module
// package.json
{
  "type": "module"
}
```

```javascript
// 或 .mjs 文件
```

## 五、总结

JavaScript 模块核心要点：

1. **CommonJS**：Node.js 标准
2. **ES Module**：浏览器标准
3. **export/import**：导出导入
4. **动态导入**：按需加载
5. **type: module**：Node 支持

掌握这些，模块化开发更自如！

---

**推荐阅读**：
- [MDN Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)

**如果对你有帮助，欢迎点赞收藏！**
