# 设计模式实战：用 JavaScript 写出可维护的代码

> 全面介绍常见设计模式，包括单例、工厂、观察者、装饰器等，通过 JavaScript/TypeScript 示例帮你写出更优雅的代码。

## 一、为什么需要设计模式

设计模式是前人总结的代码组织经验：

- **可复用**：解决常见问题
- **可维护**：代码结构清晰
- **可扩展**：易于添加新功能

## 二、创建型模式

### 2.1 单例模式

确保只有一个实例：

```javascript
class Singleton {
  constructor() {
    if (Singleton.instance) {
      return Singleton.instance;
    }
    Singleton.instance = this;
    this.data = {};
  }
}

const s1 = new Singleton();
const s2 = new Singleton();
console.log(s1 === s2); // true
```

### 2.2 工厂模式

封装创建过程：

```javascript
class User {
  constructor(type) {
    this.type = type;
  }
}

class Admin extends User {
  constructor() {
    super('admin');
  }
}

class Guest extends User {
  constructor() {
    super('guest');
  }
}

function createUser(type) {
  const types = { admin: Admin, guest: Guest };
  return new types[type]();
}
```

### 2.3 构建者模式

链式创建复杂对象：

```javascript
class QueryBuilder {
  constructor() {
    this.query = {};
  }
  
  select(fields) {
    this.query.select = fields;
    return this;
  }
  
  from(table) {
    this.query.from = table;
    return this;
  }
  
  where(conditions) {
    this.query.where = conditions;
    return this;
  }
  
  build() {
    return this.query;
  }
}

const sql = new QueryBuilder()
  .select(['name', 'email'])
  .from('users')
  .where({ status: 'active' })
  .build();
```

## 三、结构型模式

### 3.1 装饰器模式

动态添加功能：

```javascript
function log(target, name, descriptor) {
  const original = descriptor.value;
  descriptor.value = function (...args) {
    console.log(`调用 ${name}`, args);
    return original.apply(this, args);
  };
  return descriptor;
}

class Calculator {
  @log
  add(a, b) {
    return a + b;
  }
}
```

### 3.2 代理模式

控制访问：

```javascript
class Image {
  constructor(url) {
    this.url = url;
    this.load();
  }
  
  load() {
    console.log('加载图片', this.url);
  }
}

class LazyImage {
  constructor(url) {
    this.url = url;
  }
  
  render() {
    if (!this.image) {
      this.image = new Image(this.url);
    }
  }
}
```

### 3.3 适配器模式

转换接口：

```javascript
class OldAPI {
  getUserData() {
    return { u_name: '张三', u_age: 25 };
  }
}

class NewAPI {
  getUser() {
    return { name: '张三', age: 25 };
  }
}

class Adapter {
  constructor(api) {
    this.api = api;
  }
  
  getUser() {
    const oldData = this.api.getUserData();
    return {
      name: oldData.u_name,
      age: oldData.u_age
    };
  }
}
```

## 四、行为型模式

### 4.1 观察者模式

事件发布/订阅：

```javascript
class EventEmitter {
  constructor() {
    this.events = {};
  }
  
  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }
  
  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(cb => cb(data));
    }
  }
}

const emitter = new EventEmitter();
emitter.on('message', msg => console.log('收到:', msg));
emitter.emit('message', 'Hello');
```

### 4.2 策略模式

封装算法：

```javascript
class PaymentContext {
  constructor(strategy) {
    this.strategy = strategy;
  }
  
  setStrategy(strategy) {
    this.strategy = strategy;
  }
  
  pay(amount) {
    return this.strategy.pay(amount);
  }
}

class Alipay {
  pay(amount) {
    return `支付宝支付 ¥${amount}`;
  }
}

class WechatPay {
  pay(amount) {
    return `微信支付 ¥${amount}`;
  }
}

const payment = new PaymentContext(new Alipay());
console.log(payment.pay(100));
payment.setStrategy(new WechatPay());
console.log(payment.pay(100));
```

### 4.3 命令模式

封装请求：

```javascript
class Command {
  constructor(execute) {
    this.execute = execute;
  }
}

class AddCommand extends Command {
  constructor(receiver, value) {
    super(() => receiver.add(value));
  }
}

class Calculator {
  constructor() {
    this.value = 0;
  }
  
  add(n) {
    this.value += n;
    console.log('加', n, '=', this.value);
  }
}

const calc = new Calculator();
const cmd = new AddCommand(calc, 10);
cmd.execute();
```

## 五、实战应用

### 5.1 状态管理

```javascript
class StateMachine {
  constructor(initial) {
    this.state = initial;
    this.listeners = [];
  }
  
  transition(newState) {
    this.state = newState;
    this.listeners.forEach(fn => fn(newState));
  }
  
  subscribe(fn) {
    this.listeners.push(fn);
  }
}
```

### 5.2 缓存

```javascript
function memoize(fn) {
  const cache = new Map();
  
  return (...args) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
}
```

### 5.3 防抖/节流

```javascript
function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

function throttle(fn, limit) {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}
```

## 六、总结

常用设计模式：

1. **单例**：全局唯一
2. **工厂**：创建对象
3. **装饰器**：动态添加功能
4. **代理**：控制访问
5. **观察者**：事件机制
6. **策略**：封装算法
7. **命令**：封装请求

掌握这些，让代码更优雅！

---

**推荐阅读**：
- [JavaScript 设计模式](https://addyosmani.com/resources/essentialjsdesignpatterns/book/)
- [重构与设计模式](https://refactoring.com/)

**如果对你有帮助，欢迎点赞收藏！**
