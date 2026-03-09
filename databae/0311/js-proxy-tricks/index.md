# JavaScript Proxy 的 5 个冷门但实用的技巧

> 除了响应式数据，Proxy 还能做这些你可能不知道的事

---

## 一、Proxy 基础回顾

Proxy 可以拦截对象的各种操作，创建一个"代理"对象。

```javascript
const target = { name: 'Alice' };

const proxy = new Proxy(target, {
  get(target, prop) {
    console.log(`读取 ${prop}`);
    return target[prop];
  },
  set(target, prop, value) {
    console.log(`设置 ${prop} = ${value}`);
    target[prop] = value;
    return true;
  }
});

proxy.name;  // 输出：读取 name
proxy.age = 25;  // 输出：设置 age = 25
```

大多数人知道 Proxy 可以用来实现响应式数据（Vue 3），但它还有很多冷门但实用的技巧。

---

## 技巧 1：数据验证

在设置属性时自动验证数据类型和格式。

```javascript
function createValidator(schema) {
  return new Proxy({}, {
    set(target, prop, value) {
      const validator = schema[prop];
      
      if (!validator) {
        throw new Error(`未定义的属性: ${prop}`);
      }
      
      if (!validator(value)) {
        throw new Error(`${prop} 验证失败`);
      }
      
      target[prop] = value;
      return true;
    }
  });
}

// 使用
const user = createValidator({
  name: (v) => typeof v === 'string' && v.length > 0,
  age: (v) => typeof v === 'number' && v >= 0 && v <= 150,
  email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)
});

user.name = 'Alice';  // ✅
user.age = 25;  // ✅
user.age = -1;  // ❌ 抛出错误
user.email = 'invalid';  // ❌ 抛出错误
```

实战应用：表单数据验证、API 参数校验。

---

## 技巧 2：懒加载属性

只在首次访问时才计算属性值，并缓存结果。

```javascript
function lazyLoad(target, loader) {
  const cache = new Map();
  
  return new Proxy(target, {
    get(target, prop) {
      if (cache.has(prop)) {
        return cache.get(prop);
      }
      
      if (prop in loader) {
        console.log(`首次加载 ${prop}`);
        const value = loader[prop]();
        cache.set(prop, value);
        return value;
      }
      
      return target[prop];
    }
  });
}

// 使用
const config = lazyLoad({}, {
  database: () => {
    // 模拟耗时操作
    console.log('连接数据库...');
    return { host: 'localhost', port: 5432 };
  },
  cache: () => {
    console.log('初始化缓存...');
    return new Map();
  }
});

config.database;  // 输出：首次加载 database, 连接数据库...
config.database;  // 直接返回缓存，不再输出
```

实战应用：配置加载、资源初始化、计算密集型属性。

---

## 技巧 3：负索引数组

像 Python 一样支持负索引访问数组。

```javascript
function createArray(arr) {
  return new Proxy(arr, {
    get(target, prop) {
      const index = Number(prop);
      
      if (Number.isInteger(index)) {
        // 负索引：从末尾开始
        if (index < 0) {
          return target[target.length + index];
        }
      }
      
      return target[prop];
    }
  });
}

// 使用
const arr = createArray([1, 2, 3, 4, 5]);

console.log(arr[0]);   // 1
console.log(arr[-1]);  // 5 (最后一个)
console.log(arr[-2]);  // 4 (倒数第二个)
console.log(arr[-5]);  // 1 (倒数第五个)
```

进阶：支持负索引切片

```javascript
function createArray(arr) {
  return new Proxy(arr, {
    get(target, prop) {
      if (prop === 'slice') {
        return (start, end) => {
          const len = target.length;
          const s = start < 0 ? len + start : start;
          const e = end < 0 ? len + end : end;
          return target.slice(s, e);
        };
      }
      
      const index = Number(prop);
      if (Number.isInteger(index) && index < 0) {
        return target[target.length + index];
      }
      
      return target[prop];
    }
  });
}

const arr = createArray([1, 2, 3, 4, 5]);
console.log(arr.slice(-3, -1));  // [3, 4]
```

---

## 技巧 4：只读对象

创建一个完全只读的对象，任何修改都会被拒绝。

```javascript
function readonly(target) {
  return new Proxy(target, {
    set() {
      throw new Error('对象是只读的');
    },
    deleteProperty() {
      throw new Error('对象是只读的');
    },
    defineProperty() {
      throw new Error('对象是只读的');
    },
    setPrototypeOf() {
      throw new Error('对象是只读的');
    }
  });
}

// 使用
const config = readonly({
  apiUrl: 'https://api.example.com',
  timeout: 5000
});

console.log(config.apiUrl);  // ✅ 可以读取
config.timeout = 10000;  // ❌ 抛出错误
delete config.apiUrl;  // ❌ 抛出错误
```

深度只读：

```javascript
function deepReadonly(target) {
  return new Proxy(target, {
    get(target, prop) {
      const value = target[prop];
      
      // 如果是对象，递归代理
      if (value && typeof value === 'object') {
        return deepReadonly(value);
      }
      
      return value;
    },
    set() {
      throw new Error('对象是只读的');
    }
  });
}

const config = deepReadonly({
  database: {
    host: 'localhost',
    port: 5432
  }
});

config.database.host = 'remote';  // ❌ 抛出错误
```

---

## 技巧 5：操作日志

自动记录对象的所有操作，用于调试或审计。

```javascript
function createLogger(target, name = 'Object') {
  const logs = [];
  
  const proxy = new Proxy(target, {
    get(target, prop) {
      const value = target[prop];
      logs.push({
        type: 'get',
        prop,
        value,
        timestamp: Date.now()
      });
      return value;
    },
    set(target, prop, value) {
      const oldValue = target[prop];
      target[prop] = value;
      logs.push({
        type: 'set',
        prop,
        oldValue,
        newValue: value,
        timestamp: Date.now()
      });
      return true;
    },
    deleteProperty(target, prop) {
      const value = target[prop];
      delete target[prop];
      logs.push({
        type: 'delete',
        prop,
        value,
        timestamp: Date.now()
      });
      return true;
    }
  });
  
  proxy.getLogs = () => logs;
  proxy.clearLogs = () => logs.length = 0;
  
  return proxy;
}

// 使用
const user = createLogger({ name: 'Alice' }, 'User');

user.name;  // 读取
user.age = 25;  // 设置
delete user.name;  // 删除

console.log(user.getLogs());
// [
//   { type: 'get', prop: 'name', value: 'Alice', timestamp: ... },
//   { type: 'set', prop: 'age', oldValue: undefined, newValue: 25, timestamp: ... },
//   { type: 'delete', prop: 'name', value: 'Alice', timestamp: ... }
// ]
```

实战应用：调试复杂状态变化、审计敏感操作、性能分析。

---

## 番外：组合使用

多个 Proxy 可以组合使用，实现更复杂的功能。

```javascript
// 先验证，再记录日志
const user = createLogger(
  createValidator({
    name: (v) => typeof v === 'string',
    age: (v) => typeof v === 'number' && v >= 0
  }),
  'User'
);

user.name = 'Alice';  // ✅ 验证通过，记录日志
user.age = -1;  // ❌ 验证失败，抛出错误
```

---

## 性能注意事项

Proxy 会带来一定的性能开销，使用时需要注意：

1. **避免在热路径使用**：频繁调用的代码路径不适合用 Proxy
2. **缓存代理对象**：不要重复创建相同对象的代理
3. **合理使用 Reflect**：Reflect 方法比直接操作性能更好

```javascript
// ✅ 推荐
get(target, prop) {
  return Reflect.get(target, prop);
}

// ❌ 不推荐
get(target, prop) {
  return target[prop];
}
```

---

## 总结

Proxy 不仅可以用来实现响应式数据，还有很多实用的场景：

1. 数据验证：自动校验属性值
2. 懒加载：延迟计算和缓存
3. 负索引：更友好的数组访问
4. 只读对象：防止意外修改
5. 操作日志：追踪对象变化

这些技巧在实际项目中都有用武之地，合理使用可以让代码更优雅、更健壮。

如果这篇文章对你有帮助，欢迎点赞收藏！
