# 深入理解 JavaScript Proxy 与 Reflect：解锁元编程的超能力

> 全面解析 ES6 Proxy 和 Reflect API，从基础用法到高级实战，带你掌握 JavaScript 元编程的核心技能。

## 一、什么是 Proxy

Proxy 是 ES6 引入的元编程特性，允许你创建一个代理对象，用来拦截和控制目标对象的基本操作。

```javascript
const target = { name: '张三' };
const proxy = new Proxy(target, {
  get(target, property, receiver) {
    console.log(`读取 ${property}`);
    return target[property];
  }
});

console.log(proxy.name); // 输出: 读取 name -> 张三
```

## 二、Proxy 的基本语法

```javascript
const proxy = new Proxy(target, handler);
```

- **target**：目标对象
- **handler**：处理器对象，定义拦截行为

### 2.1 处理器方法一览

| 方法 | 拦截操作 |
|------|----------|
| get | 读取属性 |
| set | 写入属性 |
| has | `in` 操作符 |
| deleteProperty | `delete` 操作符 |
| apply | 函数调用 |
| construct | `new` 操作符 |
| getPrototypeOf | `Object.getPrototypeOf` |
| setPrototypeOf | `Object.setPrototypeOf` |
| defineProperty | `Object.defineProperty` |
| getOwnPropertyDescriptor | `Object.getOwnPropertyDescriptor` |
| preventExtensions | `Object.preventExtensions` |
| isExtensible | `Object.isExtensible` |

## 三、实战案例

### 3.1 数据验证

```javascript
const user = {};

const validator = {
  set(target, property, value) {
    if (property === 'age') {
      if (typeof value !== 'number' || value < 0 || value > 150) {
        throw new Error('年龄必须是 0-150 之间的数字');
      }
    }
    target[property] = value;
    return true;
  }
};

const proxy = new Proxy(user, validator);
proxy.age = 25; // 正常
proxy.age = -5; // 抛出错误
```

### 3.2 私有属性保护

```javascript
class SecureVault {
  constructor() {
    const secrets = { ssn: '123-45-6789' };
    
    return new Proxy(this, {
      get(target, property) {
        if (property.startsWith('_')) {
          return secrets[property.slice(1)];
        }
        return target[property];
      },
      set(target, property, value) {
        if (property.startsWith('_')) {
          throw new Error('私有属性不能直接修改');
        }
        target[property] = value;
        return true;
      }
    });
  }
  
  displaySecrets() {
    console.log(this._ssn);
  }
}

const vault = new SecureVault();
vault.publicData = '可以访问'; // 正常
vault._ssn = 'xxx'; // 抛出错误
```

### 3.3 响应式系统基础

```javascript
function reactive(obj) {
  const handlers = new Set();
  
  return new Proxy(obj, {
    get(target, property, receiver) {
      const value = Reflect.get(target, property, receiver);
      if (typeof value === 'object' && value !== null) {
        return reactive(value);
      }
      return value;
    },
    set(target, property, value, receiver) {
      const result = Reflect.set(target, property, value, receiver);
      handlers.forEach(fn => fn(property, value));
      return result;
    },
    subscribe(fn) {
      handlers.add(fn);
    }
  });
}

const state = reactive({ count: 0 });
state.subscribe((key, value) => {
  console.log(`${key} 变化为 ${value}`);
});

state.count++; // 输出: count 变化为 1
```

### 3.4 懒加载 / 虚拟化

```javascript
class LazyLoader {
  constructor(dataSource) {
    this.cache = new Map();
    this.dataSource = dataSource;
    
    return new Proxy({}, {
      get: (target, property) => {
        if (!this.cache.has(property)) {
          this.cache.set(property, this.dataSource(property));
        }
        return this.cache.get(property);
      }
    });
  }
}

const loader = new LazyLoader(key => fetch(`/api/${key}`));
loader.users; // 首次访问才请求
loader.users; // 第二次从缓存读取
```

## 四、Reflect API

Reflect 是一个内置对象，提供了操作对象的方法，与 Proxy 配合使用。

### 4.1 Reflect 方法一览

```javascript
Reflect.get(target, property, receiver)
Reflect.set(target, property, value, receiver)
Reflect.has(target, property)
Reflect.deleteProperty(target, property)
Reflect.apply(fn, thisArg, args)
Reflect.construct(target, args)
Reflect.getPrototypeOf(target)
Reflect.setPrototypeOf(target, prototype)
Reflect.defineProperty(target, property, descriptor)
Reflect.getOwnPropertyDescriptor(target, property)
Reflect.preventExtensions(target)
Reflect.isExtensible(target)
```

### 4.2 为什么用 Reflect

**1. 更语义化的 API**

```javascript
// 旧方式
Object.defineProperty(obj, 'name', descriptor);

// 新方式（返回布尔值而不是抛异常）
Reflect.defineProperty(obj, 'name', descriptor);
```

**2. 配合 Proxy 使用**

```javascript
const proxy = new Proxy(obj, {
  get(target, property, receiver) {
    // 使用 Reflect 确保原型链正确
    return Reflect.get(target, property, receiver);
  },
  set(target, property, value, receiver) {
    return Reflect.set(target, property, value, receiver);
  }
});
```

## 五、进阶用法

### 5.1 可撤销 Proxy

```javascript
const target = { secret: '机密信息' };
const { proxy, revoke } = Proxy.revocable(target, {
  get() { return '已撤销'; }
});

console.log(proxy.secret); // 输出: 已撤销
revoke();
console.log(proxy.secret); // 抛出 TypeError
```

### 5.2 数组负索引

```javascript
function createNegativeArray(array) {
  const handler = {
    get(target, property) {
      if (property < 0) {
        return target[Number(property) + target.length];
      }
      return target[property];
    }
  };
  return new Proxy(array, handler);
}

const arr = createNegativeArray([1, 2, 3, 4, 5]);
console.log(arr[-1]); // 5
console.log(arr[-2]); // 4
```

### 5.3 函数参数校验

```javascript
function validateFn(fn, schema) {
  return new Proxy(fn, {
    apply(target, thisArg, args) {
      for (let i = 0; i < schema.length; i++) {
        if (typeof args[i] !== schema[i]) {
          throw new Error(`参数 ${i} 期望类型 ${schema[i]}`);
        }
      }
      return Reflect.apply(target, thisArg, args);
    }
  });
}

const add = validateFn((a, b) => a + b, ['number', 'number']);
add(1, 2); // 3
add('1', 2); // 抛出错误
```

### 5.4 枚举过滤

```javascript
function createReadOnly(target) {
  return new Proxy(target, {
    set() { throw new Error('只读对象不能修改'); },
    deleteProperty() { throw new Error('只读对象不能删除'); },
    get(target, property) {
      const value = Reflect.get(target, property);
      if (typeof value === 'function') {
        return value.bind(target);
      }
      return value;
    }
  });
}

const config = createReadOnly({ apiKey: 'xxx', debug: true });
config.debug = false; // 抛出错误
```

## 六、与 Vue 3 响应式对比

Vue 3 的响应式系统基于 Proxy 实现：

```javascript
// Vue 3 核心原理简化
function reactive(target) {
  const handler = {
    get(target, property, receiver) {
      const result = Reflect.get(target, property, receiver);
      track(target, property); // 收集依赖
      return result;
    },
    set(target, property, value, receiver) {
      const result = Reflect.set(target, property, value, receiver);
      trigger(target, property); // 触发更新
      return result;
    }
  };
  
  return new Proxy(target, handler);
}
```

## 七、总结

Proxy 和 Reflect 是 JavaScript 元编程的核心：

1. **Proxy**：拦截对象操作，创建代理对象
2. **Reflect**：提供对象操作的标准化方法
3. **配合使用**：实现数据验证、私有属性、响应式系统等功能

掌握这些 API，能让你写出更灵活、更强大的 JavaScript 代码。

---

**推荐阅读**：
- [MDN Proxy 文档](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Proxy)
- [MDN Reflect 文档](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Reflect)

**如果对你有帮助，欢迎点赞收藏！**
