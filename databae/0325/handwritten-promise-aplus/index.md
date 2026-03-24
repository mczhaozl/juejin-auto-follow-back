# 手写 Promise A+ 规范：从零开始实现一个高性能 Promise

> Promise 是 JavaScript 异步编程的基石。虽然现在我们习惯了 `async/await`，但理解 Promise 的底层实现依然是每个高级前端开发的必修课。本文将带你严格遵循 Promise/A+ 规范，手写一个完整的 Promise。

## 一、Promise/A+ 规范概览

在动手之前，我们必须明确规范要求的几个核心点：
1. **三种状态**：`pending`（进行中）、`fulfilled`（已成功）和 `rejected`（已失败）。
2. **状态不可逆**：一旦从 `pending` 变为 `fulfilled` 或 `rejected`，就不能再变。
3. **then 方法**：必须返回一个新的 Promise，且支持链式调用。

---

## 二、基础骨架实现

我们先定义构造函数和基础状态。

```javascript
const PENDING = 'pending';
const FULFILLED = 'fulfilled';
const REJECTED = 'rejected';

class MyPromise {
  constructor(executor) {
    this.status = PENDING; // 初始状态
    this.value = undefined; // 成功的值
    this.reason = undefined; // 失败的原因

    // 成功回调队列
    this.onResolvedCallbacks = [];
    // 失败回调队列
    this.onRejectedCallbacks = [];

    const resolve = (value) => {
      if (this.status === PENDING) {
        this.status = FULFILLED;
        this.value = value;
        // 执行所有成功回调
        this.onResolvedCallbacks.forEach(fn => fn());
      }
    };

    const reject = (reason) => {
      if (this.status === PENDING) {
        this.status = REJECTED;
        this.reason = reason;
        // 执行所有失败回调
        this.onRejectedCallbacks.forEach(fn => fn());
      }
    };

    try {
      executor(resolve, reject);
    } catch (e) {
      reject(e);
    }
  }
}
```

## 三、核心逻辑：then 方法的实现

`then` 是 Promise 的灵魂。它不仅要处理异步，还要支持链式调用（即返回一个新的 Promise）。

```javascript
then(onFulfilled, onRejected) {
  // 参数透传：确保 .then().then() 这种写法依然生效
  onFulfilled = typeof onFulfilled === 'function' ? onFulfilled : v => v;
  onRejected = typeof onRejected === 'function' ? onRejected : err => { throw err; };

  // 返回一个新的 Promise，实现链式调用
  let promise2 = new MyPromise((resolve, reject) => {
    if (this.status === FULFILLED) {
      // 规范要求：onFulfilled 必须在微任务中执行，这里模拟微任务
      setTimeout(() => {
        try {
          let x = onFulfilled(this.value);
          // 解析 x，让它符合规范（resolvePromise 方法后面实现）
          resolvePromise(promise2, x, resolve, reject);
        } catch (e) {
          reject(e);
        }
      }, 0);
    }

    if (this.status === REJECTED) {
      setTimeout(() => {
        try {
          let x = onRejected(this.reason);
          resolvePromise(promise2, x, resolve, reject);
        } catch (e) {
          reject(e);
        }
      }, 0);
    }

    if (this.status === PENDING) {
      // 状态还是 pending，先存起来
      this.onResolvedCallbacks.push(() => {
        setTimeout(() => {
          try {
            let x = onFulfilled(this.value);
            resolvePromise(promise2, x, resolve, reject);
          } catch (e) {
            reject(e);
          }
        }, 0);
      });

      this.onRejectedCallbacks.push(() => {
        setTimeout(() => {
          try {
            let x = onRejected(this.reason);
            resolvePromise(promise2, x, resolve, reject);
          } catch (e) {
            reject(e);
          }
        }, 0);
      });
    }
  });

  return promise2;
}
```

## 四、最难的部分：resolvePromise 解析逻辑

规范 2.3 节详细定义了如何处理 `onFulfilled` 的返回值 `x`。如果 `x` 是一个 Promise，我们需要等待 it 完成；如果是普通值，直接 resolve。

```javascript
function resolvePromise(promise2, x, resolve, reject) {
  // 1. 防止循环引用
  if (promise2 === x) {
    return reject(new TypeError('Chaining cycle detected for promise'));
  }

  // 2. 如果 x 是对象或函数（可能是 Promise）
  if ((x !== null && typeof x === 'object') || typeof x === 'function') {
    let called = false; // 确保 resolve 或 reject 只能调用一次
    try {
      let then = x.then; // 获取 then 方法
      if (typeof then === 'function') {
        // 如果有 then，说明 x 是 thenable（Promise-like）
        then.call(x, (y) => {
          if (called) return;
          called = true;
          // 递归解析 y，因为 y 可能还是个 Promise
          resolvePromise(promise2, y, resolve, reject);
        }, (r) => {
          if (called) return;
          called = true;
          reject(r);
        });
      } else {
        // 虽然是对象，但没有 then 方法，直接当作普通值
        resolve(x);
      }
    } catch (e) {
      if (called) return;
      called = true;
      reject(e);
    }
  } else {
    // 3. 普通值直接 resolve
    resolve(x);
  }
}
```

---

## 五、总结与收获

通过手写 Promise，我们不仅掌握了规范的核心：
- **微任务模拟**：规范要求 onFulfilled/onRejected 必须异步执行。
- **状态转移**：PENDING -> FULFILLED/REJECTED 的唯一性。
- **链式调用**：通过返回一个新的 Promise 实现。
- **递归解析**：处理 Promise 嵌套的情况。

手写 Promise 是面试的「终极杀手锏」，也是通往高级工程师的必经之路。

**如果你对如何测试 Promise 规范（使用 promises-aplus-tests）感兴趣，欢迎关注我的专栏！**
