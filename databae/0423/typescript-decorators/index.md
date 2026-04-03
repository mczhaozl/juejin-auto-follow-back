# TypeScript 装饰器完全指南：从基础到高级应用

装饰器（Decorator）是 TypeScript 的强大特性，它让你可以优雅地修改类和方法的行为。本文将带你全面掌握装饰器。

## 一、装饰器基础

### 1. 什么是装饰器

装饰器是一种特殊类型的声明，它可以附加到类声明、方法、访问器、属性或参数上。

```typescript
// 启用装饰器需要在 tsconfig.json 中设置
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

### 2. 第一个装饰器

```typescript
function simpleDecorator(target: any) {
  console.log('Decorator called on:', target);
}

@simpleDecorator
class MyClass {
  // ...
}

// 输出：Decorator called on: [Function: MyClass]
```

## 二、装饰器类型

### 1. 类装饰器

```typescript
function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
class Greeter {
  greeting: string;
  constructor(message: string) {
    this.greeting = message;
  }
  greet() {
    return "Hello, " + this.greeting;
  }
}
```

### 2. 装饰器工厂

```typescript
function color(value: string) {
  return function (target: any) {
    target.color = value;
  };
}

@color("red")
class Car {
  static color: string;
}

console.log(Car.color); // 'red'
```

### 3. 方法装饰器

```typescript
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey} with args:`, args);
    const result = originalMethod.apply(this, args);
    console.log(`Method returned:`, result);
    return result;
  };
}

class Calculator {
  @log
  add(a: number, b: number) {
    return a + b;
  }
}

const calc = new Calculator();
calc.add(2, 3);
// 输出:
// Calling add with args: [2, 3]
// Method returned: 5
```

### 4. 访问器装饰器

```typescript
function configurable(value: boolean) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    descriptor.configurable = value;
  };
}

class Point {
  private _x: number;
  private _y: number;
  
  constructor(x: number, y: number) {
    this._x = x;
    this._y = y;
  }
  
  @configurable(false)
  get x() { return this._x; }
  
  @configurable(false)
  get y() { return this._y; }
}
```

### 5. 属性装饰器

```typescript
function minLength(length: number) {
  return function (target: any, propertyKey: string) {
    let value: string;
    
    const getter = function () {
      return value;
    };
    
    const setter = function (newValue: string) {
      if (newValue.length < length) {
        throw new Error(`Value must be at least ${length} characters`);
      }
      value = newValue;
    };
    
    Object.defineProperty(target, propertyKey, {
      get: getter,
      set: setter,
      enumerable: true,
      configurable: true
    });
  };
}

class User {
  @minLength(3)
  username: string;
  
  constructor(username: string) {
    this.username = username;
  }
}

const user = new User('alice');
// user.username = 'al'; // 抛出错误
```

### 6. 参数装饰器

```typescript
function required(target: any, propertyKey: string, parameterIndex: number) {
  const existingRequiredParameters = target[`__required_${propertyKey}`] || [];
  existingRequiredParameters.push(parameterIndex);
  target[`__required_${propertyKey}`] = existingRequiredParameters;
}

function validate(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = function (...args: any[]) {
    const requiredParameters = target[`__required_${propertyKey}`] || [];
    
    for (const index of requiredParameters) {
      if (args[index] === undefined || args[index] === null) {
        throw new Error(`Parameter at index ${index} is required`);
      }
    }
    
    return originalMethod.apply(this, args);
  };
}

class UserService {
  @validate
  createUser(@required name: string, @required email: string, age?: number) {
    console.log('Creating user:', name, email, age);
  }
}

const service = new UserService();
// service.createUser('Alice'); // 错误，缺少 email
service.createUser('Alice', 'alice@example.com', 30); // 正常
```

## 三、高级装饰器

### 1. 缓存装饰器

```typescript
function cache(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  const cache = new Map();
  
  descriptor.value = function (...args: any[]) {
    const key = JSON.stringify(args);
    
    if (cache.has(key)) {
      console.log('Returning cached result');
      return cache.get(key);
    }
    
    const result = originalMethod.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

class DataService {
  @cache
  async fetchData(id: number) {
    console.log('Fetching data from API');
    await new Promise(resolve => setTimeout(resolve, 1000));
    return { id, data: 'Some data' };
  }
}

const service = new DataService();
service.fetchData(1); // Fetching from API
service.fetchData(1); // Returning cached result
```

### 2. 性能监控装饰器

```typescript
function measure(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = function (...args: any[]) {
    const start = performance.now();
    const result = originalMethod.apply(this, args);
    
    if (result instanceof Promise) {
      return result.finally(() => {
        const end = performance.now();
        console.log(`${propertyKey} took ${end - start}ms`);
      });
    }
    
    const end = performance.now();
    console.log(`${propertyKey} took ${end - start}ms`);
    return result;
  };
}

class Processor {
  @measure
  heavyComputation(n: number) {
    let result = 0;
    for (let i = 0; i < n; i++) {
      result += Math.sqrt(i);
    }
    return result;
  }
}

const processor = new Processor();
processor.heavyComputation(1000000);
```

### 3. 重试装饰器

```typescript
function retry(maxAttempts: number = 3, delay: number = 1000) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      let lastError: Error;
      
      for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
          return await originalMethod.apply(this, args);
        } catch (error) {
          lastError = error as Error;
          console.log(`Attempt ${attempt} failed: ${error}`);
          
          if (attempt < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, delay));
          }
        }
      }
      
      throw lastError!;
    };
  };
}

class APIClient {
  @retry(3, 1000)
  async fetchData() {
    if (Math.random() > 0.5) {
      throw new Error('Network error');
    }
    return { success: true };
  }
}
```

## 四、元数据反射

```typescript
import 'reflect-metadata';

const formatMetadataKey = Symbol('format');

function format(formatString: string) {
  return Reflect.metadata(formatMetadataKey, formatString);
}

function getFormat(target: any, propertyKey: string) {
  return Reflect.getMetadata(formatMetadataKey, target, propertyKey);
}

class User {
  @format('YYYY-MM-DD')
  birthDate: string;
  
  constructor(birthDate: string) {
    this.birthDate = birthDate;
  }
}

const user = new User('1990-01-01');
console.log(getFormat(user, 'birthDate')); // 'YYYY-MM-DD'
```

## 五、依赖注入

```typescript
const injectableMetadataKey = Symbol('injectable');

function Injectable() {
  return function (target: any) {
    Reflect.defineMetadata(injectableMetadataKey, true, target);
  };
}

class Container {
  private services = new Map();
  
  register<T>(token: any, service: T) {
    this.services.set(token, service);
  }
  
  resolve<T>(token: any): T {
    const service = this.services.get(token);
    if (!service) {
      throw new Error(`Service not found: ${token}`);
    }
    return service;
  }
}

@Injectable()
class Logger {
  log(message: string) {
    console.log('[LOG]', message);
  }
}

@Injectable()
class UserService {
  constructor(private logger: Logger) {}
  
  createUser(name: string) {
    this.logger.log(`Creating user: ${name}`);
  }
}

const container = new Container();
const logger = new Logger();
container.register(Logger, logger);
container.register(UserService, new UserService(logger));

const userService = container.resolve(UserService);
userService.createUser('Alice');
```

## 六、最佳实践

1. 装饰器应该是纯函数
2. 使用装饰器工厂增加灵活性
3. 合理使用元数据
4. 注意装饰器执行顺序
5. 添加类型安全

## 七、总结

TypeScript 装饰器是强大的元编程工具：
- 5 种装饰器类型
- 装饰器工厂增加灵活性
- 结合 Reflect Metadata
- 实现依赖注入、缓存、监控等
- 保持代码简洁可维护

开始使用装饰器，让你的 TypeScript 代码更优雅！
