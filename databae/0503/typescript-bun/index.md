# Bun + TypeScript 开发完全指南

## 一、Bun 概述

### 1.1 什么是 Bun

快速的 JavaScript/TypeScript 运行时、包管理器、构建工具。

### 1.2 特点

- 极快的启动速度
- 内置 TypeScript
- 兼容 Node.js API
- 内置 SQLite

---

## 二、安装

```bash
# macOS/Linux
curl -fsSL https://bun.sh/install | bash

# 验证
bun --version
```

---

## 三、项目初始化

```bash
# 创建新项目
bun init

# TypeScript 配置
touch tsconfig.json
```

```json
{
  "compilerOptions": {
    "lib": ["ES2020"],
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "noEmit": true
  }
}
```

---

## 四、基础用法

### 4.1 运行脚本

```typescript
// index.ts
console.log('Hello from Bun!');

export function add(a: number, b: number): number {
  return a + b;
}
```

```bash
bun run index.ts
```

### 4.2 包管理

```bash
# 安装依赖
bun add lodash-es
bun add -d @types/lodash-es

# 开发依赖
bun install

# 运行脚本
bun run dev
```

---

## 五、HTTP 服务器

```typescript
const server = Bun.serve({
  port: 3000,
  fetch(req: Request): Response {
    return new Response('Hello from Bun!');
  }
});

console.log(`Listening on ${server.url}`);
```

```typescript
// 路由示例
Bun.serve({
  port: 3000,
  fetch(req: Request): Response {
    const url = new URL(req.url);
    
    if (url.pathname === '/') {
      return new Response('Home');
    }
    if (url.pathname === '/api/users') {
      return Response.json({ users: [] });
    }
    
    return new Response('Not found', { status: 404 });
  }
});
```

---

## 六、文件操作

```typescript
// 读取文件
const text = await Bun.file('./data.txt').text();

// 写入文件
await Bun.write('./output.txt', 'Hello Bun!');

// JSON
const data = { name: 'Bun' };
await Bun.write('./data.json', JSON.stringify(data));
```

---

## 七、SQLite

```typescript
import { Database } from 'bun:sqlite';

const db = new Database('mydb.sqlite');

db.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)');
db.run('INSERT INTO users (name) VALUES (?)', 'Alice');

const users = db.query('SELECT * FROM users').all();
console.log(users);
```

---

## 八、测试

```typescript
import { expect, test } from 'bun:test';
import { add } from './index';

test('add function', () => {
  expect(add(1, 2)).toBe(3);
});
```

```bash
bun test
```

---

## 九、构建

```bash
# 构建可执行文件
bun build index.ts --outdir ./dist

# 编译为可执行
bun build index.ts --compile --outfile myapp
```

---

## 十、性能对比

```bash
# 启动速度对比
time bun run index.ts
time node index.ts
```

---

## 总结

Bun 提供了极速的 TypeScript/JavaScript 开发体验，内置多种工具让开发更高效。
