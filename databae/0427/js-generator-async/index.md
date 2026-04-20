# JavaScript Generator 与异步编程深度解析

> 深入理解 Generator 函数，掌握其工作原理，结合异步编程应用，提升代码质量。

## 一、Generator 函数概述

Generator 函数是 ES6 引入的一种特殊函数，可以暂停和恢复执行，为异步编程提供了强大的工具。

### 1.1 什么是 Generator

```javascript
// 普通函数
function normalFunction() {
  console.log('开始执行');
  return '完成';
}

// Generator 函数
function* generatorFunction() {
  console.log('第一步');
  yield '第一步完成';
  console.log('第二步');
  yield '第二步完成';
  console.log('第三步');
  return '全部完成';
}
```

### 1.2 Generator 的特点

- 使用 `function*` 声明
- 使用 `yield` 关键字暂停执行
- 返回一个 Iterator 对象
- 可以多次调用 `next()` 恢复执行

---

## 二、Generator 基础

### 2.1 基本用法

```javascript
function* simpleGenerator() {
  yield 1;
  yield 2;
  yield 3;
}

const gen = simpleGenerator();

console.log(gen.next()); // { value: 1, done: false }
console.log(gen.next()); // { value: 2, done: false }
console.log(gen.next()); // { value: 3, done: false }
console.log(gen.next()); // { value: undefined, done: true }
```

### 2.2 next() 方法详解

```javascript
function* generatorWithReturn() {
  yield '第一次暂停';
  yield '第二次暂停';
  return '完成';
}

const gen = generatorWithReturn();

console.log(gen.next()); // { value: '第一次暂停', done: false }
console.log(gen.next()); // { value: '第二次暂停', done: false }
console.log(gen.next()); // { value: '完成', done: true }
console.log(gen.next()); // { value: undefined, done: true }
```

### 2.3 传递参数给 next()

```javascript
function* generatorWithInput() {
  const input1 = yield '等待输入 1';
  console.log('收到输入 1:', input1);
  
  const input2 = yield '等待输入 2';
  console.log('收到输入 2:', input2);
  
  return '完成';
}

const gen = generatorWithInput();

console.log(gen.next()); // { value: '等待输入 1', done: false }
console.log(gen.next('Hello')); // { value: '等待输入 2', done: false }
console.log(gen.next('World')); // { value: '完成', done: true }
```

---

## 三、Generator 的内部机制

### 3.1 执行上下文栈

Generator 暂停时会保存执行上下文：

```javascript
function* countGenerator() {
  console.log('开始');
  yield 1;
  console.log('继续');
  yield 2;
  console.log('结束');
}

const gen = countGenerator();
gen.next(); // 开始
gen.next(); // 继续
gen.next(); // 结束
```

### 3.2 状态机

Generator 可以看作状态机：

```javascript
// Generator 的状态转换
// S0: 初始状态
// S1: 第一次 yield 后
// S2: 第二次 yield 后
// S3: 完成状态
```

---

## 四、Iterator 协议

### 4.1 Iterator 接口

```javascript
const arr = [1, 2, 3];
const iterator = arr[Symbol.iterator]();

console.log(iterator.next()); // { value: 1, done: false }
console.log(iterator.next()); // { value: 2, done: false }
console.log(iterator.next()); // { value: 3, done: false }
console.log(iterator.next()); // { value: undefined, done: true }
```

### 4.2 自定义 Iterator

```javascript
const customIterator = {
  [Symbol.iterator]() {
    let count = 0;
    return {
      next() {
        if (count < 3) {
          return { value: count++, done: false };
        }
        return { value: undefined, done: true };
      }
    };
  }
};

for (const num of customIterator) {
  console.log(num); // 0, 1, 2
}
```

### 4.3 Generator 返回 Iterator

```javascript
function* generator() {
  yield 1;
  yield 2;
  yield 3;
}

const gen = generator();
console.log(gen[Symbol.iterator]() === gen); // true

for (const num of generator()) {
  console.log(num); // 1, 2, 3
}
```

---

## 五、Generator 的高级用法

### 5.1 yield* 委托

```javascript
function* innerGenerator() {
  yield 'a';
  yield 'b';
}

function* outerGenerator() {
  yield 'start';
  yield* innerGenerator();
  yield 'end';
}

for (const value of outerGenerator()) {
  console.log(value); // start, a, b, end
}
```

### 5.2 return() 方法

```javascript
function* generator() {
  try {
    yield 1;
    yield 2;
    yield 3;
  } finally {
    console.log('finally 执行');
  }
}

const gen = generator();
console.log(gen.next()); // { value: 1, done: false }
console.log(gen.return('提前结束')); // { value: '提前结束', done: true }
console.log(gen.next()); // { value: undefined, done: true }
```

### 5.3 throw() 方法

```javascript
function* generator() {
  try {
    yield '正常执行';
    yield '继续执行';
  } catch (e) {
    console.log('捕获异常:', e);
  }
}

const gen = generator();
console.log(gen.next());
console.log(gen.throw(new Error('出错了')));
```

---

## 六、Generator 与异步编程

### 6.1 回调地狱问题

```javascript
// 回调地狱
getData(function(data1) {
  getMoreData(data1, function(data2) {
    getEvenMoreData(data2, function(data3) {
      console.log(data3);
    });
  });
});
```

### 6.2 使用 Generator 简化异步

```javascript
function* asyncGenerator() {
  const data1 = yield getData();
  const data2 = yield getMoreData(data1);
  const data3 = yield getEvenMoreData(data2);
  console.log(data3);
}

// 执行器
function run(generator) {
  const gen = generator();
  
  function handle(result) {
    if (result.done) return;
    result.value.then(data => {
      handle(gen.next(data));
    });
  }
  
  handle(gen.next());
}

run(asyncGenerator);
```

### 6.3 Thunk 函数

```javascript
// Thunk 函数
function thunkify(fn) {
  return function(...args) {
    return function(callback) {
      return fn.call(this, ...args, callback);
    };
  };
}

// 使用
const getDataThunk = thunkify(getData);
const thunk = getDataThunk(arg1, arg2);
thunk(callback);
```

---

## 七、深入理解协程

### 7.1 协程概念

协程是一种比线程更轻量的并发执行单位，可以暂停和恢复。

```javascript
function* task1() {
  console.log('任务 1 开始');
  yield;
  console.log('任务 1 继续');
}

function* task2() {
  console.log('任务 2 开始');
  yield;
  console.log('任务 2 继续');
}

const t1 = task1();
const t2 = task2();

t1.next();
t2.next();
t1.next();
t2.next();
```

### 7.2 Generator 实现协程

```javascript
function* producer() {
  for (let i = 0; i < 3; i++) {
    yield i;
  }
}

function* consumer() {
  for (const value of producer()) {
    console.log('消费:', value);
  }
}

for (const _ of consumer()) {}
```

---

## 八、实战案例

### 8.1 无限序列生成器

```javascript
function* infiniteSequence() {
  let i = 0;
  while (true) {
    yield i++;
  }
}

const gen = infiniteSequence();
console.log(gen.next().value); // 0
console.log(gen.next().value); // 1
console.log(gen.next().value); // 2
```

### 8.2 斐波那契数列

```javascript
function* fibonacci() {
  let [prev, curr] = [0, 1];
  while (true) {
    yield curr;
    [prev, curr] = [curr, prev + curr];
  }
}

const fib = fibonacci();
for (let i = 0; i < 10; i++) {
  console.log(fib.next().value);
}
```

### 8.3 异步任务调度器

```javascript
function* taskRunner(tasks) {
  for (const task of tasks) {
    yield task();
  }
}

const tasks = [
  () => Promise.resolve('任务 1'),
  () => Promise.resolve('任务 2'),
  () => Promise.resolve('任务 3')
];

function runTasks(generator) {
  const gen = generator();
  
  function handle(result) {
    if (result.done) return;
    result.value.then(data => {
      console.log(data);
      handle(gen.next());
    });
  }
  
  handle(gen.next());
}

runTasks(() => taskRunner(tasks));
```

---

## 九、async/await 与 Generator 的关系

### 9.1 async/await 是 Generator 的语法糖

```javascript
// Generator 方式
function* fetchData() {
  const data1 = yield fetch('/api/data1');
  const data2 = yield fetch('/api/data2');
  return [data1, data2];
}

// async/await 方式
async function fetchData() {
  const data1 = await fetch('/api/data1');
  const data2 = await fetch('/api/data2');
  return [data1, data2];
}
```

### 9.2 实现简易的 async/await

```javascript
function spawn(genF) {
  return new Promise((resolve, reject) => {
    const gen = genF();
    
    function step(nextF) {
      let next;
      try {
        next = nextF();
      } catch (e) {
        return reject(e);
      }
      if (next.done) {
        return resolve(next.value);
      }
      Promise.resolve(next.value).then(
        v => step(() => gen.next(v)),
        e => step(() => gen.throw(e))
      );
    }
    
    step(() => gen.next());
  });
}
```

---

## 十、总结

Generator 是 JavaScript 中强大的功能，为异步编程提供了优雅的解决方案。掌握 Generator，可以更好地理解 async/await 的工作原理。

要点回顾：
- Generator 使用 `function*` 声明
- 使用 `yield` 暂停执行
- 返回 Iterator 对象
- 可以实现协程和异步编程
- async/await 是 Generator 的语法糖

希望这篇文章对你有帮助！
