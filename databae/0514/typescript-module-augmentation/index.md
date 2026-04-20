# TypeScript 模块扩充完全指南

## 一、扩充内置类型

```typescript
// string 扩充
declare global {
  interface String {
    reverse(): string;
  }
}

// 实现
String.prototype.reverse = function() {
  return this.split('').reverse().join('');
};

// 使用
"hello".reverse(); // "olleh"
```

## 二、扩充第三方库

```typescript
// express 扩充
declare module 'express' {
  export interface Request {
    user?: { id: string; name: string };
  }
}

// 使用
import express from 'express';
const app = express();
app.get('/', (req, res) => {
  console.log(req.user?.name); // TypeScript 识别
});
```

## 三、扩充 window

```typescript
declare global {
  interface Window {
    myGlobal: string;
  }
}

window.myGlobal = "hello";
```

## 四、模块扩充注意事项

```typescript
// 确保是模块
export {};

declare global {
  // 在这里声明
}
```

## 最佳实践
- module augmentation 补充类型信息
- 不要过度依赖原型扩充
- 声明文件放在独立目录
- 使用 type-only imports
