# Jest 完全指南：JavaScript 单元测试实战

> 深入讲解 Jest 单元测试，包括测试编写、Mock 函数、快照测试、异步测试，以及实际项目中的测试策略和覆盖率配置。

## 一、快速开始

### 1.1 安装

```bash
npm install --save-dev jest
```

### 1.2 配置

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  testMatch: ['**/*.test.js'],
  collectCoverage: true,
  coverageDirectory: 'coverage'
};
```

### 1.3 基础测试

```javascript
// sum.test.js
const sum = require('./sum');

test('1 + 2 = 3', () => {
  expect(sum(1, 2)).toBe(3);
});
```

## 二、匹配器

### 2.1 常用匹配器

```javascript
// 相等
expect(value).toBe(3);
expect(value).toEqual({ a: 1 });

// 布尔
expect(value).toBeTruthy();
expect(value).toBeFalsy();

// 空值
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// 数字
expect(value).toBeGreaterThan(10);
expect(value).toBeLessThan(10);
expect(value).toBeCloseTo(0.1, 5);

// 字符串
expect('hello').toMatch(/world/);
expect('hello').toContain('ell');

// 数组
expect([1, 2, 3]).toContain(2);
expect([1, 2, 3]).toHaveLength(3);
```

### 2.2 否定

```javascript
expect(value).not.toBe(3);
expect(value).not.toBeNull();
```

## 三、Mock 函数

### 3.1 基本 Mock

```javascript
const myMock = jest.fn();

myMock('arg1');
myMock('arg2');

expect(myMock).toHaveBeenCalled();
expect(myMock).toHaveBeenCalledWith('arg1');
expect(myMock).toHaveBeenCalledTimes(2);
```

### 3.2 Mock 返回值

```javascript
const myMock = jest.fn();
myMock.mockReturnValue('static return');
myMock.mockResolvedValue('async return');

console.log(myMock()); // 'static return'
```

### 3.3 模块 Mock

```javascript
// mock axios
jest.mock('axios');
import axios from 'axios';

axios.get.mockResolvedValue({ data: {} });
```

## 四、异步测试

### 4.1 Promise

```javascript
test('async data', async () => {
  const data = await fetchData();
  expect(data).toBe('expected');
});
```

### 4.2 .resolves/.rejects

```javascript
test('async data', async () => {
  await expect(fetchData()).resolves.toBe('expected');
});

test('async error', async () => {
  await expect(fetchError()).rejects.toThrow('error');
});
```

### 4.3 Callback

```javascript
test('callback', done => {
  fetchData(data => {
    expect(data).toBe('expected');
    done();
  });
});
```

## 五、快照测试

### 5.1 创建快照

```javascript
test('snapshot', () => {
  const data = { name: 'John', age: 30 };
  expect(data).toMatchSnapshot();
});
```

### 5.2 更新快照

```bash
npm test -- -u
```

## 六、Setup/Teardown

### 6.1 生命周期

```javascript
beforeAll(() => {
  // 所有测试前执行一次
});

afterAll(() => {
  // 所有测试后执行一次
});

beforeEach(() => {
  // 每个测试前执行
});

afterEach(() => {
  // 每个测试后执行
});
```

### 6.2 作用域

```javascript
describe('outer', () => {
  beforeAll(() => {});
  
  describe('inner', () => {
    beforeAll(() => {});
  });
});
```

## 七、总结

Jest 核心要点：

1. **test**：测试函数
2. **expect**：断言
3. **Matchers**：匹配器
4. **Mock**：模拟函数
5. **async**：异步测试
6. **snapshot**：快照测试

掌握这些，单元测试 so easy！

---

**推荐阅读**：
- [Jest 官方文档](https://jestjs.io/docs/getting-started)

**如果对你有帮助，欢迎点赞收藏！**
