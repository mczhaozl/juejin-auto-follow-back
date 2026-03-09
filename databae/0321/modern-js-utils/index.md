# 告别 lodash：2024 年最值得用的 JavaScript 工具库

> radash、remeda、es-toolkit 等现代替代方案对比

---

## 一、lodash 的问题

- 包体积大（70KB+）
- Tree Shaking 不友好
- 部分 API 已被原生替代
- TypeScript 支持不完善

---

## 二、现代替代方案

### 1. radash

轻量、现代、TypeScript 优先。

```bash
npm install radash
```

```typescript
import { groupBy, sum, unique } from 'radash';

const users = [
  { name: 'Alice', age: 25, role: 'admin' },
  { name: 'Bob', age: 30, role: 'user' },
  { name: 'Charlie', age: 25, role: 'user' }
];

// 分组
const byAge = groupBy(users, u => u.age);
// { 25: [...], 30: [...] }

// 求和
const totalAge = sum(users, u => u.age);  // 80

// 去重
const ages = unique(users.map(u => u.age));  // [25, 30]
```

### 2. remeda

函数式、类型安全、零依赖。

```bash
npm install remeda
```

```typescript
import * as R from 'remeda';

const data = [1, 2, 3, 4, 5];

const result = R.pipe(
  data,
  R.filter(x => x % 2 === 0),
  R.map(x => x * 2),
  R.sum()
);  // 12
```

### 3. es-toolkit

最快、最小、现代化。

```bash
npm install es-toolkit
```

```typescript
import { debounce, throttle, chunk } from 'es-toolkit';

// 防抖
const search = debounce((query) => {
  console.log('Searching:', query);
}, 300);

// 节流
const scroll = throttle(() => {
  console.log('Scrolling');
}, 100);

// 分块
const chunks = chunk([1, 2, 3, 4, 5], 2);
// [[1, 2], [3, 4], [5]]
```

---

## 三、性能对比

| 库 | 包体积 | Tree Shaking | TypeScript | 性能 |
|----|--------|-------------|-----------|------|
| lodash | 70KB | ❌ | ⚠️ | 中 |
| radash | 15KB | ✅ | ✅ | 快 |
| remeda | 20KB | ✅ | ✅ | 快 |
| es-toolkit | 10KB | ✅ | ✅ | 最快 |

---

## 四、迁移建议

### 从 lodash 迁移

```typescript
// lodash
import _ from 'lodash';
_.debounce(fn, 300);
_.groupBy(arr, 'key');

// radash
import { debounce, group } from 'radash';
debounce({ delay: 300 }, fn);
group(arr, item => item.key);
```

### 使用原生 API

```typescript
// lodash
_.map(arr, fn);
_.filter(arr, fn);
_.find(arr, fn);

// 原生
arr.map(fn);
arr.filter(fn);
arr.find(fn);
```

---

## 五、推荐选择

- **通用项目**：es-toolkit（最小最快）
- **函数式编程**：remeda（类型安全）
- **快速迁移**：radash（API 相似）

---

## 总结

2024 年不再需要 lodash，现代工具库更小、更快、更类型安全。

如果这篇文章对你有帮助，欢迎点赞收藏！
