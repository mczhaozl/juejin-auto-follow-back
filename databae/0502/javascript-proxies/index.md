# JavaScript Proxy 高级应用完全指南

## 一、Proxy 概述

### 1.1 什么是 Proxy

Proxy 可以拦截对象的操作，实现自定义行为。

### 1.2 基本语法

```javascript
const proxy = new Proxy(target, handler);
```

---

## 二、基础用法

### 2.1 属性访问拦截

```javascript
const obj = { name: 'John' };

const proxy = new Proxy(obj, {
  get(target, property) {
    console.log(`访问属性: ${property}`);
    return target[property];
  },
  
  set(target, property, value) {
    console.log(`设置属性: ${property} = ${value}`);
    target[property] = value;
    return true;
  }
});

proxy.name; // 访问属性: name
proxy.age = 30; // 设置属性: age = 30
```

### 2.2 函数调用拦截

```javascript
function add(a, b) {
  return a + b;
}

const proxy = new Proxy(add, {
  apply(target, thisArg, argumentsList) {
    console.log(`调用函数: ${target.name}(${argumentsList})`);
    return target.apply(thisArg, argumentsList);
  }
});

proxy(1, 2); // 调用函数: add(1,2)
```

---

## 三、常见拦截器

### 3.1 get

```javascript
const handler = {
  get(target, prop, receiver) {
    if (prop === '_secret') {
      throw new Error('无权访问');
    }
    
    if (!(prop in target)) {
      return `属性 ${prop} 不存在`;
    }
    
    return Reflect.get(target, prop, receiver);
  }
};
```

### 3.2 set

```javascript
const handler = {
  set(target, prop, value, receiver) {
    if (prop === 'age' && typeof value !== 'number') {
      throw new TypeError('年龄必须是数字');
    }
    
    if (prop === 'age' && (value < 0 || value > 150)) {
      throw new RangeError('年龄无效');
    }
    
    return Reflect.set(target, prop, value, receiver);
  }
};
```

### 3.3 has

```javascript
const handler = {
  has(target, prop) {
    if (prop.startsWith('_')) {
      return false;
    }
    return prop in target;
  }
};
```

### 3.4 deleteProperty

```javascript
const handler = {
  deleteProperty(target, prop) {
    if (prop.startsWith('_')) {
      throw new Error('不能删除私有属性');
    }
    console.log(`删除属性: ${prop}`);
    return delete target[prop];
  }
};
```

---

## 四、实战场景

### 4.1 数据验证

```javascript
function createValidatedObject(schema) {
  return new Proxy({}, {
    set(target, prop, value) {
      const validator = schema[prop];
      
      if (validator) {
        if (!validator.validate(value)) {
          throw new Error(validator.message);
        }
      }
      
      target[prop] = value;
      return true;
    }
  });
}

const user = createValidatedObject({
  name: {
    validate: (v) => typeof v === 'string' && v.length > 0,
    message: '姓名不能为空'
  },
  age: {
    validate: (v) => typeof v === 'number' && v >= 0,
    message: '年龄无效'
  }
});

user.name = 'John';
user.age = 25;
user.age = -1; // 抛出错误
```

### 4.2 响应式数据

```javascript
function createReactive(obj, onChange) {
  return new Proxy(obj, {
    set(target, prop, value) {
      const oldValue = target[prop];
      const changed = oldValue !== value;
      target[prop] = value;
      
      if (changed) {
        onChange(prop, value, oldValue);
      }
      
      return true;
    },
    
    get(target, prop, receiver) {
      const value = target[prop];
      
      if (typeof value === 'object' && value !== null) {
        return createReactive(value, onChange);
      }
      
      return value;
    }
  });
}

const state = createReactive({ count: 0 }, (prop, value) => {
  console.log(`${prop} 改变为 ${value}`);
});

state.count = 1; // count 改变为 1
```

### 4.3 缓存代理

```javascript
function createCache(fn) {
  const cache = new Map();
  
  return new Proxy(fn, {
    apply(target, thisArg, args) {
      const key = JSON.stringify(args);
      
      if (cache.has(key)) {
        console.log('从缓存读取');
        return cache.get(key);
      }
      
      const result = target.apply(thisArg, args);
      cache.set(key, result);
      return result;
    }
  });
}

const expensiveCalculation = (a, b) => {
  console.log('执行计算');
  return a + b;
};

const cachedCalculation = createCache(expensiveCalculation);

cachedCalculation(1, 2); // 执行计算
cachedCalculation(1, 2); // 从缓存读取
```

### 4.4 不可变对象

```javascript
function immutable(obj) {
  return new Proxy(obj, {
    set() {
      throw new Error('对象不可修改');
    },
    deleteProperty() {
      throw new Error('对象不可修改');
    },
    defineProperty() {
      throw new Error('对象不可修改');
    }
  });
}

const config = immutable({ apiUrl: 'https://api.example.com' });
config.apiUrl = 'new'; // 抛出错误
```

### 4.5 观察者模式

```javascript
class Observable {
  constructor() {
    this.handlers = new Map();
  }
  
  observe(prop, handler) {
    if (!this.handlers.has(prop)) {
      this.handlers.set(prop, []);
    }
    this.handlers.get(prop).push(handler);
  }
  
  notify(prop, value) {
    const handlers = this.handlers.get(prop) || [];
    handlers.forEach(h => h(value));
  }
}

function createObservable(obj) {
  const observable = new Observable();
  
  const proxy = new Proxy(obj, {
    set(target, prop, value) {
      target[prop] = value;
      observable.notify(prop, value);
      return true;
    },
    
    get(target, prop) {
      if (prop === 'observe') {
        return (p, h) => observable.observe(p, h);
      }
      return target[prop];
    }
  });
  
  return proxy;
}

const user = createObservable({ name: 'John' });

user.observe('name', newName => {
  console.log(`姓名更新为: ${newName}`);
});

user.name = 'Jane'; // 姓名更新为: Jane
```

---

## 五、Reflect

### 5.1 使用 Reflect

```javascript
const handler = {
  get(target, prop, receiver) {
    console.log('GET', prop);
    return Reflect.get(target, prop, receiver);
  },
  
  set(target, prop, value, receiver) {
    console.log('SET', prop, value);
    return Reflect.set(target, prop, value, receiver);
  }
};
```

---

## 六、性能考虑

### 6.1 注意事项

- Proxy 有性能开销
- 不要过度使用
- 考虑是否真的需要

---

## 总结

Proxy 是强大的元编程工具，可用于数据验证、响应式、缓存、不可变对象等场景。合理使用可以大幅简化代码。
