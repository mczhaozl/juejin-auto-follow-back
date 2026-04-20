# Node.js 测试与调试完全指南：从单元测试到生产调试

## 一、测试框架 Jest

### 1.1 基础配置

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  testMatch: ['**/*.test.js']
};
```

### 1.2 基础测试

```javascript
// math.js
function add(a, b) {
  return a + b;
}

module.exports = { add };

// math.test.js
const { add } = require('./math');

describe('add function', () => {
  test('adds two numbers', () => {
    expect(add(1, 2)).toBe(3);
  });
  
  test('handles negative numbers', () => {
    expect(add(-1, -2)).toBe(-3);
  });
});
```

---

## 二、异步测试

```javascript
// api.js
const fetch = require('node-fetch');

async function getUser(id) {
  const res = await fetch(`https://api.example.com/users/${id}`);
  return res.json();
}

module.exports = { getUser };

// api.test.js
const { getUser } = require('./api');
const fetch = require('node-fetch');

jest.mock('node-fetch');

test('getUser returns user', async () => {
  const mockUser = { id: 1, name: 'Test' };
  fetch.mockResolvedValue({ json: () => Promise.resolve(mockUser) });
  
  const user = await getUser(1);
  expect(user).toEqual(mockUser);
});
```

---

## 三、Mock 与 Stub

```javascript
// utils.js
class Database {
  async connect() { /* */ }
  async query() { /* */ }
}

// utils.test.js
const { Database } = require('./utils');

jest.mock('./utils');

test('database test', async () => {
  const mockQuery = Database.mock.instances[0].query;
  mockQuery.mockResolvedValue({ data: 'test' });
  
  const db = new Database();
  await db.connect();
  const result = await db.query();
  
  expect(result).toEqual({ data: 'test' });
  expect(mockQuery).toHaveBeenCalledTimes(1);
});
```

---

## 四、Supertest API 测试

```javascript
// app.js
const express = require('express');
const app = express();

app.use(express.json());

app.get('/users/:id', (req, res) => {
  res.json({ id: req.params.id, name: 'Test' });
});

app.post('/users', (req, res) => {
  res.status(201).json({ id: 1, ...req.body });
});

module.exports = app;

// app.test.js
const request = require('supertest');
const app = require('./app');

describe('GET /users/:id', () => {
  test('returns user', async () => {
    const res = await request(app).get('/users/1');
    expect(res.statusCode).toBe(200);
    expect(res.body.name).toBe('Test');
  });
});

describe('POST /users', () => {
  test('creates user', async () => {
    const res = await request(app)
      .post('/users')
      .send({ name: 'Alice' });
    
    expect(res.statusCode).toBe(201);
    expect(res.body.name).toBe('Alice');
  });
});
```

---

## 五、覆盖率

```bash
npx jest --coverage
```

```javascript
// jest.config.js
module.exports = {
  coverageThreshold: {
    global: {
      lines: 80,
      functions: 80,
      branches: 70
    }
  }
};
```

---

## 六、调试技巧

### 6.1 console.log

```javascript
function debugTest() {
  console.log('Debug info:', value);
}
```

### 6.2 Debugger

```javascript
function complexFunction() {
  debugger; // 断点
  // ...
}
```

### 6.3 Node Inspector

```bash
node --inspect-brk script.js
# Chrome: chrome://inspect
```

---

## 七、VS Code 调试

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Jest Tests",
      "runtimeExecutable": "npx",
      "runtimeArgs": ["jest", "--runInBand"],
      "console": "integratedTerminal"
    }
  ]
}
```

---

## 八、性能测试

```javascript
const { performance } = require('perf_hooks');

function measure(fn, name) {
  const start = performance.now();
  fn();
  const end = performance.now();
  console.log(`${name}: ${end - start}ms`);
}

measure(() => {
  for (let i = 0; i < 1000000; i++) {}
}, 'Loop');
```

---

## 九、E2E 测试 Playwright

```javascript
// e2e.spec.js
const { test, expect } = require('@playwright/test');

test('homepage works', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveTitle(/Example/);
});

test('login flow', async ({ page }) => {
  await page.goto('/login');
  await page.fill('#email', 'test@example.com');
  await page.fill('#password', 'password');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

---

## 十、最佳实践

1. 编写可测试的代码
2. 使用 AAA 模式（Arrange-Act-Assert）
3. 测试行为而非实现
4. 保持测试独立
5. 追求高覆盖率但不唯覆盖率

---

## 十一、总结

完善的测试和调试流程能保证代码质量和开发效率。
