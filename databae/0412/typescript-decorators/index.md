# TypeScript 装饰器完全指南：类装饰器与方法装饰器

> 深入讲解 TypeScript 装饰器，包括类装饰器、方法装饰器、属性装饰器，以及装饰器工厂的实际应用。

## 一、装饰器基础

### 1.1 启用装饰器

```json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

### 1.2 基本语法

```typescript
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.log(`调用 ${propertyKey}`, args);
    return original.apply(this, args);
  };
}
```

## 二、类装饰器

### 2.1 基本用法

```typescript
function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
class User {
  name: string;
}
```

### 2.2 装饰器工厂

```typescript
function version(v: string) {
  return function(constructor: Function) {
    constructor.prototype.version = v;
  };
}

@version('1.0.0')
class App {}
```

## 三、方法装饰器

### 3.1 方法拦截

```typescript
function readonly(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  descriptor.writable = false;
}

class User {
  @readonly
  name() { return '张三'; }
}
```

### 3.2 日志装饰器

```typescript
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const method = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.log(`调用方法 ${propertyKey}`, args);
    return method.apply(this, args);
  };
}

class Calculator {
  @log
  add(a: number, b: number) {
    return a + b;
  }
}
```

## 四、属性装饰器

### 4.1 访问器装饰

```typescript
function format(formatFn: (value: any) => string) {
  return function(target: any, propertyKey: string) {
    let value: any;
    const getter = function() { return formatFn(value); };
    const setter = function(newVal: any) { value = newVal; };
    Object.defineProperty(target, propertyKey, {
      get: getter,
      set: setter,
      enumerable: true,
      configurable: true
    });
  };
}

class User {
  @format(v => v?.toUpperCase())
  name: string;
}
```

## 五、参数装饰器

### 5.1 方法参数装饰

```typescript
function inject(service: string) {
  return function(target: any, propertyKey: string, parameterIndex: number) {
    console.log(`参数 ${parameterIndex} 需要注入 ${service}`);
  };
}

class UserService {
  create(@inject('logger') logger: Logger) {}
}
```

## 六、实战应用

### 6.1 路由装饰器

```typescript
function Get(path: string) {
  return function(target: any, propertyKey: string) {
    if (!target.routes) target.routes = [];
    target.routes.push({ method: 'GET', path, handler: propertyKey });
  };
}

class UserController {
  @Get('/users')
  getUsers() { return []; }
}
```

### 6.2 权限检查

```typescript
function requireRole(role: string) {
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value;
    descriptor.value = function(...args: any[]) {
      const user = getCurrentUser();
      if (user?.role !== role) {
        throw new Error('无权限');
      }
      return method.apply(this, args);
    };
  };
}

class Admin {
  @requireRole('admin')
  deleteUser(id: number) {}
}
```

### 6.3 自动缓存

```typescript
function cached(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const cache = new Map();
  const method = descriptor.value;
  descriptor.value = function(...args: any[]) {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = method.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

class MathService {
  @cached
  fibonacci(n: number): number {
    if (n <= 1) return n;
    return this.fibonacci(n - 1) + this.fibonacci(n - 2);
  }
}
```

## 七、总结

TypeScript 装饰器核心要点：

1. **启用配置**：experimentalDecorators
2. **类装饰器**：装饰类本身
3. **方法装饰器**：装饰方法
4. **属性装饰器**：装饰属性
5. **参数装饰器**：装饰参数
6. **装饰器工厂**：返回装饰器函数

掌握这些，代码更优雅！

---

**推荐阅读**：
- [TypeScript 装饰器](https://www.typescriptlang.org/docs/handbook/decorators.html)

**如果对你有帮助，欢迎点赞收藏！**
