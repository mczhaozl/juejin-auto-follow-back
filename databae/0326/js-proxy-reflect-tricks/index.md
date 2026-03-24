# 你所不知道的 JavaScript：深入理解 Proxy 与 Reflect 的实战技巧

> Proxy 和 Reflect 是现代 JavaScript 的一对孪生兄弟。本文将通过 3 个实战案例，带你掌握如何利用它们实现深度响应式、私有变量保护以及拦截任意对象操作的高级技巧。

## 一、为什么需要 Proxy 和 Reflect？

在 ES6 之前，我们只能用 `Object.defineProperty` 来拦截属性。

**Proxy 的优势：**
1. **拦截面更广**：可以拦截 13 种不同的操作（如 `has`, `deleteProperty`, `ownKeys` 等）。
2. **性能更好**：直接代理整个对象，而不是遍历每个属性。
3. **更语义化**：配合 `Reflect`，让对象的底层操作变得更清晰。

## 二、实战 1：实现一个深度响应式 (Deep Reactive)

Vue 3 的核心就是利用 Proxy 实现的。

```javascript
function reactive(obj) {
  return new Proxy(obj, {
    get(target, key, receiver) {
      const res = Reflect.get(target, key, receiver);
      // 如果是嵌套对象，递归代理
      if (typeof res === 'object' && res !== null) {
        return reactive(res);
      }
      console.log(`GET ${key}:`, res);
      return res;
    },
    set(target, key, value, receiver) {
      const res = Reflect.set(target, key, value, receiver);
      console.log(`SET ${key}:`, value);
      return res;
    }
  });
}

const user = reactive({ name: 'Alice', info: { age: 25 } });
user.info.age = 26; // 完美拦截嵌套修改！
```

## 三、实战 2：私有变量保护 (Private Fields)

如果你不希望外部访问以下划线 `_` 开头的属性：

```javascript
const protector = {
  get(target, key) {
    if (key.startsWith('_')) {
      throw new Error(`Access to private field "${key}" denied.`);
    }
    return Reflect.get(target, key);
  },
  ownKeys(target) {
    // 在 Object.keys() 中过滤掉私有变量
    return Reflect.ownKeys(target).filter(key => !key.startsWith('_'));
  }
};

const secretObj = new Proxy({ _pwd: '123', publicInfo: 'hi' }, protector);
console.log(Object.keys(secretObj)); // ["publicInfo"]
// console.log(secretObj._pwd); // Error!
```

## 四、实战 3：数组负索引访问 (Negative Indexing)

让 JS 数组像 Python 一样支持负数索引：

```javascript
const arrayHandler = {
  get(target, key, receiver) {
    let index = Number(key);
    if (index < 0) {
      index = target.length + index;
    }
    return Reflect.get(target, String(index), receiver);
  }
};

const pyArray = new Proxy([1, 2, 3, 4], arrayHandler);
console.log(pyArray[-1]); // 4
console.log(pyArray[-2]); // 3
```

## 五、总结

`Proxy` 负责拦截，`Reflect` 负责执行默认行为。掌握这对组合，你就能像造物主一样自由定义 JavaScript 对象的行为。

**如果你对 Proxy 的性能瓶颈感兴趣，欢迎在评论区留言讨论！**
