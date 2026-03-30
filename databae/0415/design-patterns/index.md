# 设计模式完全指南：JavaScript 常用模式实战

> 深入讲解 JavaScript 设计模式，包括单例、工厂、观察者、装饰器、代理模式，以及实际项目中的代码重构和最佳实践。

## 一、单例模式

### 1.1 什么是单例

确保只有一个实例：

```javascript
class Singleton {
  constructor() {
    if (Singleton.instance) {
      return Singleton.instance;
    }
    Singleton.instance = this;
    this.data = [];
  }
  
  add(item) {
    this.data.push(item);
  }
}

const s1 = new Singleton();
const s2 = new Singleton();
console.log(s1 === s2); // true
```

### 1.2 闭包实现

```javascript
const Singleton = (() => {
  let instance = null;
  
  return () => {
    if (instance) return instance;
    instance = { data: [] };
    return instance;
  };
})();
```

## 二、工厂模式

### 2.1 简单工厂

```javascript
class Car {
  constructor(options) {
    this.doors = options.doors || 4;
    this.state = options.state || 'brand new';
  }
}

class Truck {
  constructor(options) {
    this.doors = options.doors || 2;
    this.state = options.state || 'used';
  }
}

function VehicleFactory(type, options) {
  switch (type) {
    case 'car':
      return new Car(options);
    case 'truck':
      return new Truck(options);
    default:
      throw new Error('Unknown type');
  }
}
```

### 2.2 抽象工厂

```javascript
class AbstractFactory {
  createVehicle() {
    throw new Error('Method not implemented');
  }
}

class CarFactory extends AbstractFactory {
  createVehicle(options) {
    return new Car(options);
  }
}
```

## 三、观察者模式

### 3.1 实现

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
  
  off(event, callback) {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(cb => cb !== callback);
    }
  }
}

// 使用
const emitter = new EventEmitter();
emitter.on('message', (data) => console.log(data));
emitter.emit('message', 'Hello');
```

### 3.2 发布/订阅

```javascript
class PubSub {
  constructor() {
    this.topics = {};
  }
  
  subscribe(topic, callback) {
    if (!this.topics[topic]) {
      this.topics[topic] = [];
    }
    this.topics[topic].push(callback);
  }
  
  publish(topic, data) {
    if (this.topics[topic]) {
      this.topics[topic].forEach(cb => cb(data));
    }
  }
}
```

## 四、装饰器模式

### 4.1 基础实现

```javascript
class Coffee {
  cost() {
    return 5;
  }
}

class MilkDecorator {
  constructor(coffee) {
    this.coffee = coffee;
  }
  
  cost() {
    return this.coffee.cost() + 1;
  }
}

class SugarDecorator {
  constructor(coffee) {
    this.coffee = coffee;
  }
  
  cost() {
    return this.coffee.cost() + 0.5;
  }
}

// 使用
let coffee = new Coffee();
coffee = new MilkDecorator(coffee);
coffee = new SugarDecorator(coffee);
console.log(coffee.cost()); // 6.5
```

### 4.2 ES 装饰器

```javascript
function log(target, name, descriptor) {
  const original = descriptor.value;
  descriptor.value = function(...args) {
    console.log(`Calling ${name} with`, args);
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

## 五、代理模式

### 5.1 保护代理

```javascript
class RealSubject {
  request() {
    return 'Real request';
  }
}

class ProxySubject {
  constructor() {
    this.realSubject = new RealSubject();
  }
  
  request() {
    if (this.checkAccess()) {
      return this.realSubject.request();
    }
    return 'Access denied';
  }
  
  checkAccess() {
    return true;
  }
}
```

### 5.2 虚拟代理

```javascript
class Image {
  constructor(url) {
    this.url = url;
    this.load();
  }
  
  load() {
    console.log(`Loading ${this.url}`);
  }
}

class ImageProxy {
  constructor(url) {
    this.url = url;
    this.image = null;
  }
  
  display() {
    if (!this.image) {
      this.image = new Image(this.url);
    }
    console.log('Displaying image');
  }
}
```

## 六、总结

设计模式核心要点：

1. **单例**：全局唯一
2. **工厂**：对象创建
3. **观察者**：事件机制
4. **装饰器**：动态增强
5. **代理**：访问控制

掌握这些，代码更优雅！

---

**推荐阅读**：
- [JavaScript 设计模式](https://addyosmani.com/resources/essentialjsdesignpatterns/book/)

**如果对你有帮助，欢迎点赞收藏！**
