# JavaScript 的 Symbol.iterator：手写一个可迭代对象

> 从迭代器协议到生成器函数，掌握 JavaScript 迭代的底层原理

---

## 一、什么是可迭代对象

在 JavaScript 中，可迭代对象是指实现了 `Symbol.iterator` 方法的对象，可以被 `for...of` 遍历。

```javascript
// 数组是可迭代的
const arr = [1, 2, 3];
for (const item of arr) {
  console.log(item);  // 1, 2, 3
}

// 字符串是可迭代的
const str = 'hello';
for (const char of str) {
  console.log(char);  // h, e, l, l, o
}

// 普通对象不可迭代
const obj = { a: 1, b: 2 };
for (const item of obj) {  // ❌ TypeError: obj is not iterable
  console.log(item);
}
```

---

## 二、迭代器协议

要让对象可迭代，需要实现迭代器协议：

1. 对象必须有 `Symbol.iterator` 方法
2. 该方法返回一个迭代器对象
3. 迭代器对象必须有 `next()` 方法
4. `next()` 返回 `{ value, done }` 格式的对象

```javascript
const iterable = {
  [Symbol.iterator]() {
    let step = 0;
    return {
      next() {
        step++;
        if (step <= 3) {
          return { value: step, done: false };
        }
        return { value: undefined, done: true };
      }
    };
  }
};

for (const num of iterable) {
  console.log(num);  // 1, 2, 3
}
```

---

## 三、手写可迭代对象

### 示例 1：Range 对象

```javascript
class Range {
  constructor(start, end) {
    this.start = start;
    this.end = end;
  }

  [Symbol.iterator]() {
    let current = this.start;
    const end = this.end;
    
    return {
      next() {
        if (current <= end) {
          return { value: current++, done: false };
        }
        return { value: undefined, done: true };
      }
    };
  }
}

// 使用
const range = new Range(1, 5);
for (const num of range) {
  console.log(num);  // 1, 2, 3, 4, 5
}

// 也可以用扩展运算符
console.log([...range]);  // [1, 2, 3, 4, 5]
```

### 示例 2：斐波那契数列

```javascript
class Fibonacci {
  constructor(limit) {
    this.limit = limit;
  }

  [Symbol.iterator]() {
    let prev = 0, curr = 1, count = 0;
    const limit = this.limit;
    
    return {
      next() {
        if (count++ < limit) {
          const value = prev;
          [prev, curr] = [curr, prev + curr];
          return { value, done: false };
        }
        return { value: undefined, done: true };
      }
    };
  }
}

const fib = new Fibonacci(10);
console.log([...fib]);  // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

---

## 四、使用生成器函数

生成器函数是创建迭代器的更简洁方式。

### 基础语法

```javascript
function* generator() {
  yield 1;
  yield 2;
  yield 3;
}

const gen = generator();
console.log(gen.next());  // { value: 1, done: false }
console.log(gen.next());  // { value: 2, done: false }
console.log(gen.next());  // { value: 3, done: false }
console.log(gen.next());  // { value: undefined, done: true }
```

### 用生成器重写 Range

```javascript
class Range {
  constructor(start, end) {
    this.start = start;
    this.end = end;
  }

  *[Symbol.iterator]() {
    for (let i = this.start; i <= this.end; i++) {
      yield i;
    }
  }
}

const range = new Range(1, 5);
console.log([...range]);  // [1, 2, 3, 4, 5]
```

简洁很多！

### 用生成器重写斐波那契

```javascript
function* fibonacci(limit) {
  let prev = 0, curr = 1;
  for (let i = 0; i < limit; i++) {
    yield prev;
    [prev, curr] = [curr, prev + curr];
  }
}

console.log([...fibonacci(10)]);  // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

---

## 五、实战应用

### 应用 1：分页数据迭代

```javascript
class PaginatedAPI {
  constructor(url, pageSize = 10) {
    this.url = url;
    this.pageSize = pageSize;
  }

  async *[Symbol.asyncIterator]() {
    let page = 1;
    let hasMore = true;

    while (hasMore) {
      const response = await fetch(
        `${this.url}?page=${page}&size=${this.pageSize}`
      );
      const data = await response.json();
      
      for (const item of data.items) {
        yield item;
      }
      
      hasMore = data.hasMore;
      page++;
    }
  }
}

// 使用
const api = new PaginatedAPI('/api/users');
for await (const user of api) {
  console.log(user);
}
```

### 应用 2：树结构遍历

```javascript
class TreeNode {
  constructor(value, children = []) {
    this.value = value;
    this.children = children;
  }

  // 深度优先遍历
  *[Symbol.iterator]() {
    yield this.value;
    for (const child of this.children) {
      yield* child;  // 委托给子节点的迭代器
    }
  }

  // 广度优先遍历
  *bfs() {
    const queue = [this];
    while (queue.length > 0) {
      const node = queue.shift();
      yield node.value;
      queue.push(...node.children);
    }
  }
}

const tree = new TreeNode(1, [
  new TreeNode(2, [
    new TreeNode(4),
    new TreeNode(5)
  ]),
  new TreeNode(3)
]);

console.log([...tree]);  // DFS: [1, 2, 4, 5, 3]
console.log([...tree.bfs()]);  // BFS: [1, 2, 3, 4, 5]
```

### 应用 3：无限序列

```javascript
function* naturalNumbers() {
  let n = 1;
  while (true) {
    yield n++;
  }
}

// 取前 10 个自然数
function take(iterable, n) {
  const result = [];
  for (const item of iterable) {
    if (result.length >= n) break;
    result.push(item);
  }
  return result;
}

console.log(take(naturalNumbers(), 10));  // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

---

## 六、for...of 的原理

`for...of` 循环的本质是调用对象的 `Symbol.iterator` 方法。

```javascript
// for...of 循环
for (const item of iterable) {
  console.log(item);
}

// 等价于
const iterator = iterable[Symbol.iterator]();
let result = iterator.next();
while (!result.done) {
  const item = result.value;
  console.log(item);
  result = iterator.next();
}
```

---

## 七、可迭代对象的应用场景

### 1. 扩展运算符

```javascript
const range = new Range(1, 5);
const arr = [...range];  // [1, 2, 3, 4, 5]
```

### 2. 解构赋值

```javascript
const [first, second, ...rest] = range;
console.log(first, second, rest);  // 1 2 [3, 4, 5]
```

### 3. Array.from

```javascript
const arr = Array.from(range);  // [1, 2, 3, 4, 5]
```

### 4. Promise.all

```javascript
async function* asyncGenerator() {
  yield Promise.resolve(1);
  yield Promise.resolve(2);
  yield Promise.resolve(3);
}

const promises = [...asyncGenerator()];
const results = await Promise.all(promises);
console.log(results);  // [1, 2, 3]
```

---

## 八、迭代器的高级技巧

### 1. 迭代器组合

```javascript
function* concat(...iterables) {
  for (const iterable of iterables) {
    yield* iterable;
  }
}

const combined = concat([1, 2], [3, 4], [5, 6]);
console.log([...combined]);  // [1, 2, 3, 4, 5, 6]
```

### 2. 迭代器过滤

```javascript
function* filter(iterable, predicate) {
  for (const item of iterable) {
    if (predicate(item)) {
      yield item;
    }
  }
}

const numbers = new Range(1, 10);
const evens = filter(numbers, n => n % 2 === 0);
console.log([...evens]);  // [2, 4, 6, 8, 10]
```

### 3. 迭代器映射

```javascript
function* map(iterable, mapper) {
  for (const item of iterable) {
    yield mapper(item);
  }
}

const numbers = new Range(1, 5);
const squares = map(numbers, n => n * n);
console.log([...squares]);  // [1, 4, 9, 16, 25]
```

---

## 九、性能注意事项

1. **避免在迭代器中做重计算**

```javascript
// ❌ 每次都重新计算
*[Symbol.iterator]() {
  for (let i = 0; i < this.expensiveCalculation(); i++) {
    yield i;
  }
}

// ✅ 缓存计算结果
*[Symbol.iterator]() {
  const limit = this.expensiveCalculation();
  for (let i = 0; i < limit; i++) {
    yield i;
  }
}
```

2. **注意内存泄漏**

```javascript
// ❌ 无限迭代器可能导致内存泄漏
const infinite = naturalNumbers();
const arr = [...infinite];  // 永远不会结束！

// ✅ 使用 take 限制数量
const arr = take(infinite, 100);
```

---

## 总结

Symbol.iterator 是 JavaScript 迭代机制的核心，理解它能让你：

- 创建自定义的可迭代对象
- 使用生成器函数简化迭代器实现
- 实现复杂的数据结构遍历
- 更好地理解 for...of、扩展运算符等语法

掌握迭代器协议，能让你的代码更加优雅和强大。

如果这篇文章对你有帮助，欢迎点赞收藏！
