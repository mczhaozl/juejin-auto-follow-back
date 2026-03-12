# xx.d.ts 文件有什么用，为什么不引入都能生效？

> TypeScript 的 .d.ts 文件看起来很神奇：不需要 import 就能生效。这背后的原理是什么？本文带你彻底搞懂。

---

## 一、从一个现象说起

你有没有遇到过这种情况：

```typescript
// 没有任何 import
const app = express();  // ✅ 类型正常
const router = Router();  // ✅ 类型正常

// 但是这些类型是哪来的？
```

打开 `node_modules/@types/express/index.d.ts`，发现：

```typescript
declare function express(): Express.Application;
declare namespace Express {
  interface Application {}
}
```

**疑问**：
1. 为什么不需要 `import` 就能用？
2. `declare` 关键字是什么意思？
3. `.d.ts` 文件是如何工作的？

今天就来彻底搞懂这些问题。

## 二、.d.ts 文件是什么

### 2.1 定义

`.d.ts` 文件是 TypeScript 的**类型声明文件**（Type Declaration File），用于描述 JavaScript 代码的类型信息。

**作用**：
- 为 JavaScript 库提供类型定义
- 让 TypeScript 理解 JavaScript 代码
- 提供代码提示和类型检查

### 2.2 为什么需要 .d.ts？

JavaScript 本身没有类型信息：

```javascript
// math.js
export function add(a, b) {
  return a + b;
}
```

TypeScript 不知道 `add` 的参数和返回值类型：

```typescript
import { add } from './math';
add(1, 2);  // ❌ TypeScript 不知道类型
```

解决方案：创建 `.d.ts` 文件

```typescript
// math.d.ts
export function add(a: number, b: number): number;
```

现在 TypeScript 就知道类型了：

```typescript
import { add } from './math';
add(1, 2);  // ✅ 类型正确
add('1', '2');  // ❌ 类型错误
```

## 三、declare 关键字

### 3.1 declare 的作用

`declare` 告诉 TypeScript：「这个东西在运行时存在，但我只是声明它的类型，不提供实现」。

```typescript
// 声明全局变量
declare const API_URL: string;

// 声明全局函数
declare function fetchData(url: string): Promise<any>;

// 声明全局类
declare class User {
  name: string;
  age: number;
}
```

**使用时不需要 import**：

```typescript
// 直接使用，TypeScript 知道类型
console.log(API_URL);  // ✅
fetchData('/api/users');  // ✅
const user = new User();  // ✅
```

### 3.2 declare 的场景

**场景 1：全局变量**

```typescript
// global.d.ts
declare const __DEV__: boolean;
declare const process: {
  env: {
    NODE_ENV: string;
  };
};

// 使用
if (__DEV__) {
  console.log('Development mode');
}
```

**场景 2：第三方库**

```typescript
// jquery.d.ts
declare const $: {
  (selector: string): any;
  ajax(options: any): any;
};

// 使用
$('#app').hide();
$.ajax({ url: '/api' });
```

**场景 3：模块扩展**

```typescript
// express.d.ts
declare namespace Express {
  interface Request {
    user?: User;
  }
}

// 使用
app.get('/', (req, res) => {
  console.log(req.user);  // ✅ TypeScript 知道 user 属性
});
```

## 四、为什么不需要 import？

### 4.1 全局声明 vs 模块声明

**.d.ts 文件有两种模式**：

**模式 1：全局声明**（没有 import/export）

```typescript
// global.d.ts
declare const API_URL: string;
declare function fetchData(url: string): Promise<any>;
```

这些声明是**全局的**，不需要 import 就能用。

**模式 2：模块声明**（有 import/export）

```typescript
// types.d.ts
export interface User {
  name: string;
  age: number;
}

export function getUser(id: string): Promise<User>;
```

这些声明需要 import 才能用：

```typescript
import { User, getUser } from './types';
```

### 4.2 TypeScript 如何找到 .d.ts 文件？

TypeScript 会自动查找 `.d.ts` 文件：

**查找顺序**：

1. **项目根目录**：`*.d.ts`
2. **src 目录**：`src/**/*.d.ts`
3. **node_modules/@types**：`node_modules/@types/*/index.d.ts`
4. **tsconfig.json 的 types**：指定的类型包

```json
// tsconfig.json
{
  "compilerOptions": {
    "types": ["node", "jest", "express"]
  }
}
```

### 4.3 自动包含的 .d.ts 文件

TypeScript 会自动包含：

```
project/
├── src/
│   ├── index.ts
│   └── types.d.ts        # ✅ 自动包含
├── global.d.ts           # ✅ 自动包含
└── node_modules/
    └── @types/
        ├── node/         # ✅ 自动包含
        └── express/      # ✅ 自动包含
```

**不需要手动 import**，TypeScript 会自动加载。

## 五、实战案例

### 5.1 为第三方库添加类型

假设你用了一个没有类型定义的库：

```javascript
// awesome-lib.js
export function doSomething(value) {
  return value * 2;
}
```

创建类型声明：

```typescript
// awesome-lib.d.ts
declare module 'awesome-lib' {
  export function doSomething(value: number): number;
}
```

现在可以安全使用：

```typescript
import { doSomething } from 'awesome-lib';
doSomething(5);  // ✅ 类型正确
doSomething('5');  // ❌ 类型错误
```

### 5.2 扩展全局对象

```typescript
// global.d.ts
declare global {
  interface Window {
    myApp: {
      version: string;
      init(): void;
    };
  }
}

export {};  // 让文件成为模块
```

使用：

```typescript
window.myApp.version;  // ✅
window.myApp.init();   // ✅
```

### 5.3 环境变量类型

```typescript
// env.d.ts
declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: 'development' | 'production' | 'test';
    API_URL: string;
    API_KEY: string;
  }
}
```

使用：

```typescript
const env = process.env.NODE_ENV;  // ✅ 类型是 'development' | 'production' | 'test'
const url = process.env.API_URL;   // ✅ 类型是 string
```

### 5.4 React 组件 Props

```typescript
// components.d.ts
declare namespace JSX {
  interface IntrinsicElements {
    'my-component': {
      value: string;
      onChange: (value: string) => void;
    };
  }
}
```

使用：

```tsx
<my-component value="hello" onChange={(v) => console.log(v)} />
```

## 六、常见问题

### 6.1 .d.ts 文件不生效？

**原因 1：文件不在 TypeScript 的查找路径**

```json
// tsconfig.json
{
  "include": ["src/**/*"],  // 只包含 src 目录
  "exclude": ["node_modules"]
}
```

**解决**：把 `.d.ts` 文件放在 `src` 目录下，或修改 `include`。

**原因 2：文件有 import/export，变成了模块**

```typescript
// global.d.ts
import { Something } from 'somewhere';  // ❌ 变成模块了

declare const API_URL: string;  // 不再是全局声明
```

**解决**：使用 `declare global`

```typescript
import { Something } from 'somewhere';

declare global {
  const API_URL: string;
}
```

### 6.2 如何调试类型问题？

```typescript
// 查看类型
type Test = typeof API_URL;  // 鼠标悬停查看

// 强制类型检查
const _check: string = API_URL;  // 如果类型不对会报错
```

### 6.3 .d.ts 和 .ts 的区别？

| 特性 | .ts | .d.ts |
|------|-----|-------|
| 包含实现 | ✅ | ❌ |
| 包含类型 | ✅ | ✅ |
| 编译成 .js | ✅ | ❌ |
| 自动全局 | ❌ | ✅（无 import/export 时） |

## 七、最佳实践

### 7.1 组织 .d.ts 文件

```
project/
├── src/
│   ├── types/
│   │   ├── global.d.ts      # 全局类型
│   │   ├── modules.d.ts     # 模块扩展
│   │   └── env.d.ts         # 环境变量
│   └── index.ts
└── tsconfig.json
```

### 7.2 命名规范

```typescript
// ✅ 好的命名
global.d.ts
env.d.ts
express.d.ts

// ❌ 不好的命名
types.d.ts  // 太泛化
index.d.ts  // 不清楚内容
```

### 7.3 注释文档

```typescript
/**
 * 全局 API 配置
 * @example
 * ```ts
 * console.log(API_URL);  // 'https://api.example.com'
 * ```
 */
declare const API_URL: string;
```

## 八、总结

**.d.ts 文件的核心概念**：

1. **类型声明文件**：只有类型，没有实现
2. **declare 关键字**：声明类型，不提供实现
3. **全局 vs 模块**：无 import/export 是全局，有则是模块
4. **自动加载**：TypeScript 自动查找并加载

**为什么不需要 import？**

- 全局声明的 `.d.ts` 文件会被 TypeScript 自动加载
- TypeScript 会扫描项目和 `node_modules/@types`
- 全局声明对整个项目可见

**使用场景**：

- 为 JavaScript 库添加类型
- 声明全局变量和函数
- 扩展第三方库的类型
- 定义环境变量类型

**最佳实践**：

- 全局类型放在 `global.d.ts`
- 模块类型使用 export
- 添加注释文档
- 合理组织文件结构

如果这篇文章对你有帮助，欢迎点赞收藏。
