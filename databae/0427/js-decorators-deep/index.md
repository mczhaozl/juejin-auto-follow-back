# JavaScript Decorators 深度解析与实战

> 深入理解 JavaScript Decorators 提案，掌握装饰器模式在 JS 中的应用。

## 一、Decorators 概述

Decorators 是 ES 提案，提供了一种声明式方式修改类和类成员。

### 1.1 什么是 Decorators

```javascript
// 装饰器语法
@decorator
class MyClass {}

class MyClass {
  @decorator
  method() {}
  
  @decorator
  property = 1;
}
```

### 1.2 装饰器的应用场景

- 日志记录
- 性能测量
- 自动绑定
- 验证
- 缓存
- 依赖注入

---

## 二、Decorators 提案历史

### 2.1 Stage 1（旧版）

```javascript
// 旧提案语法
function log(target, name, descriptor) {
  const original = descriptor.value;
  descriptor.value = function(...args) {
    console.log(`Calling ${name}`);
    return original.apply(this, args);
  };
  return descriptor;
}

class MyClass {
  @log
  myMethod() {}
}
```

### 2.2 Stage 3（新版 2022-03）

```javascript
// 新提案语法
function logged(originalMethod, context) {
  const { kind, name } = context;
  if (kind === 'method') {
    return function(...args) {
      console.log(`Calling ${String(name)}`);
      return originalMethod.apply(this, args);
    };
  }
}

class MyClass {
  @logged
  myMethod() {}
}
```

---

## 三、装饰器类型

### 3.1 类装饰器

```javascript
function sealed(classDefinition, context) {
  if (context.kind === 'class') {
    Object.seal(classDefinition);
    Object.seal(classDefinition.prototype);
  }
}

@sealed
class MyClass {
  constructor() {}
}
```

### 3.2 方法装饰器

```javascript
function logged(method, context) {
  if (context.kind === 'method') {
    const methodName = context.name;
    return function(...args) {
      console.log(`Calling ${String(methodName)}`);
      return method.apply(this, args);
    };
  }
}

class Calculator {
  @logged
  add(a, b) {
    return a + b;
  }
}
```

### 3.3 Getter/Setter 装饰器

```javascript
function immutable(getter, context) {
  if (context.kind === 'getter') {
    const { name } = context;
    return function() {
      const value = getter.call(this);
      return Object.freeze(value);
    };
  }
}

class User {
  #data = { name: 'John' };
  
  @immutable
  get data() {
    return this.#data;
  }
}
```

### 3.4 字段装饰器

```javascript
function bound(value, context) {
  if (context.kind === 'field') {
    const { name } = context;
    context.addInitializer(function() {
      this[name] = this[name].bind(this);
    });
  }
}

class Button {
  @bound
  handleClick() {
    console.log(this);
  }
}
```

### 3.5 Accessor 装饰器

```javascript
function deprecated(accessor, context) {
  const { name, kind } = context;
  if (kind === 'accessor') {
    return {
      get() {
        console.warn(`Accessing deprecated ${String(name)}`);
        return accessor.get.call(this);
      },
      set(value) {
        console.warn(`Setting deprecated ${String(name)}`);
        return accessor.set.call(this, value);
      }
    };
  }
}

class MyClass {
  @deprecated
  accessor oldValue;
}
```

---

## 四、装饰器工厂

### 4.1 带参数的装饰器

```javascript
function log(message) {
  return function(originalMethod, context) {
    return function(...args) {
      console.log(message);
      return originalMethod.apply(this, args);
    };
  };
}

class MyClass {
  @log('Method called')
  myMethod() {}
}
```

### 4.2 工厂函数示例

```javascript
function measure(enabled = true) {
  return function(method, context) {
    if (!enabled) return method;
    
    const name = context.name;
    return function(...args) {
      console.time(name);
      const result = method.apply(this, args);
      console.timeEnd(name);
      return result;
    };
  };
}

class DataProcessor {
  @measure(true)
  processLargeData() {
    // 耗时操作
  }
}
```

---

## 五、实战案例

### 5.1 案例一：日志装饰器

```javascript
function logger(target, context) {
  if (context.kind === 'method') {
    const methodName = context.name;
    return function(...args) {
      console.log(`[LOG] ${String(methodName)} called with:`, args);
      const result = target.apply(this, args);
      console.log(`[LOG] ${String(methodName)} returned:`, result);
      return result;
    };
  }
}

class UserService {
  @logger
  getUser(id) {
    return { id, name: 'User' };
  }
}
```

### 5.2 案例二：缓存装饰器

```javascript
function cache(fn, context) {
  if (context.kind === 'method') {
    const cacheMap = new Map();
    return function(...args) {
      const key = JSON.stringify(args);
      if (cacheMap.has(key)) {
        console.log('Cache hit');
        return cacheMap.get(key);
      }
      const result = fn.apply(this, args);
      cacheMap.set(key, result);
      return result;
    };
  }
}

class APIService {
  @cache
  fetchData(id) {
    console.log('Fetching from API');
    return { data: id };
  }
}
```

### 5.3 案例三：验证装饰器

```javascript
function validate(fn, context) {
  if (context.kind === 'method') {
    return function(...args) {
      if (args.some(arg => arg === null || arg === undefined)) {
        throw new Error('Arguments cannot be null or undefined');
      }
      return fn.apply(this, args);
    };
  }
}

class Calculator {
  @validate
  divide(a, b) {
    if (b === 0) throw new Error('Division by zero');
    return a / b;
  }
}
```

### 5.4 案例四：自动绑定

```javascript
function autobind(method, context) {
  if (context.kind === 'method') {
    const { name } = context;
    context.addInitializer(function() {
      this[name] = this[name].bind(this);
    });
  }
}

class Button {
  constructor() {
    this.text = 'Click';
  }
  
  @autobind
  handleClick() {
    console.log(this.text);
  }
}

const button = new Button();
const handler = button.handleClick;
handler(); // 正确输出 'Click'
```

---

## 六、多个装饰器组合

### 6.1 装饰器执行顺序

```javascript
function decorator1(fn, context) {
  console.log('Decorator 1');
  return fn;
}

function decorator2(fn, context) {
  console.log('Decorator 2');
  return fn;
}

class MyClass {
  @decorator1
  @decorator2
  method() {
    console.log('Method');
  }
}

// 执行顺序: Decorator 2 → Decorator 1
// 应用顺序: Decorator 1 → Decorator 2
```

### 6.2 组合示例

```javascript
class APIService {
  @logger
  @cache
  @validate
  fetchData(id) {
    return { data: id };
  }
}
```

---

## 七、TypeScript 中的装饰器

### 7.1 启用装饰器

```json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

### 7.2 TypeScript 装饰器

```typescript
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${propertyKey}`);
    return original.apply(this, args);
  };
}

class MyClass {
  @log
  myMethod() {}
}
```

---

## 八、装饰器与现有代码集成

### 8.1 Babel 配置

```json
{
  "plugins": [
    ["@babel/plugin-proposal-decorators", { "version": "2023-05" }]
  ]
}
```

### 8.2 TypeScript 迁移

```typescript
// 旧版装饰器
function oldDecorator(target, name, descriptor) {}

// 新版装饰器
function newDecorator(method, context) {}
```

---

## 九、最佳实践

1. **保持装饰器纯粹**：不要有副作用
2. **提供良好的错误信息**
3. **文档完善**
4. **测试覆盖**
5. **考虑性能**
6. **合理使用组合**

---

## 十、总结

Decorators 提供了一种优雅的元编程方式，可以在不修改原代码的情况下添加功能。虽然还在提案阶段，但已经在 TypeScript 和 Babel 中广泛使用。

希望这篇文章对你有帮助！
