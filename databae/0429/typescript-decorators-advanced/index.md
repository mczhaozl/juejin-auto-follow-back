# TypeScript 装饰器高级实战完全指南：从基础到企业级

## 一、装饰器基础

### 1.1 什么是装饰器
装饰器是一种特殊类型的声明，它可以附加到类声明、方法、访问器、属性或参数上。

### 1.2 启用装饰器
在 `tsconfig.json` 中启用：
```json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

---

## 二、类装饰器

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

---

## 三、类装饰器工厂

```typescript
function classDecorator<T extends { new(...args: any[]): {} }>(constructor: T) {
  return class extends constructor {
    newProperty = "new property";
    hello = "override";
  };
}

@classDecorator
class ExampleClass {
  property = "property";
  hello: string;
  constructor(m: string) {
    this.hello = m;
  }
}
```

---

## 四、方法装饰器

```typescript
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    const result = originalMethod.apply(this, args);
    console.log(`Method returned`, result);
    return result;
  };
  
  return descriptor;
}

class Calculator {
  @log
  add(a: number, b: number) {
    return a + b;
  }
}

const calc = new Calculator();
calc.add(2, 3);
```

---

## 五、属性装饰器

```typescript
function minLength(min: number) {
  return function(target: any, propertyKey: string) {
    let value: string;
    
    const getter = function() {
      return value;
    };
    
    const setter = function(newVal: string) {
      if (newVal.length < min) {
        throw new Error(`${propertyKey} must be at least ${min} characters`);
      }
      value = newVal;
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
```

---

## 六、参数装饰器

```typescript
function required(target: any, propertyKey: string, parameterIndex: number) {
  const existingRequiredParameters: number[] = 
    Reflect.getOwnMetadata("required", target, propertyKey) || [];
  existingRequiredParameters.push(parameterIndex);
  Reflect.defineMetadata("required", existingRequiredParameters, target, propertyKey);
}

function validate(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const method = descriptor.value;
  
  descriptor.value = function(...args: any[]) {
    const requiredParameters: number[] = 
      Reflect.getOwnMetadata("required", target, propertyKey);
    
    if (requiredParameters) {
      for (let index of requiredParameters) {
        if (args[index] === undefined || args[index] === null) {
          throw new Error(`Missing required argument at index ${index}`);
        }
      }
    }
    
    return method.apply(this, args);
  };
}

class UserService {
  @validate
  createUser(@required name: string, @required email: string) {
    console.log(`Creating user ${name} with email ${email}`);
  }
}
```

---

## 七、访问器装饰器

```typescript
function configurable(value: boolean) {
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
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

---

## 八、装饰器组合

```typescript
function first() {
  console.log("first(): factory evaluated");
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    console.log("first(): called");
  };
}

function second() {
  console.log("second(): factory evaluated");
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    console.log("second(): called");
  };
}

class Example {
  @first()
  @second()
  method() {}
}
```

---

## 九、性能监控装饰器

```typescript
function measure(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = async function(...args: any[]) {
    const start = performance.now();
    const result = await originalMethod.apply(this, args);
    const end = performance.now();
    console.log(`${propertyKey} took ${end - start}ms`);
    return result;
  };
  
  return descriptor;
}

class DataService {
  @measure
  async fetchData() {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return { data: 'test' };
  }
}
```

---

## 十、依赖注入装饰器

```typescript
const Injectable = (): ClassDecorator => {
  return (target: any) => {
    Reflect.defineMetadata('injectable', true, target);
  };
};

const Inject = (token: any): ParameterDecorator => {
  return (target: any, propertyKey: string, parameterIndex: number) => {
    const dependencies = Reflect.getOwnMetadata('dependencies', target) || [];
    dependencies[parameterIndex] = token;
    Reflect.defineMetadata('dependencies', dependencies, target);
  };
};

class Container {
  private services = new Map();
  
  register(token: any, service: any) {
    this.services.set(token, service);
  }
  
  resolve<T>(target: any): T {
    const dependencies = Reflect.getOwnMetadata('dependencies', target) || [];
    const injections = dependencies.map(dep => this.services.get(dep));
    return new target(...injections);
  }
}

@Injectable()
class Logger {
  log(message: string) {
    console.log(message);
  }
}

@Injectable()
class UserService {
  constructor(@Inject(Logger) private logger: Logger) {}
  
  createUser(name: string) {
    this.logger.log(`Creating user: ${name}`);
  }
}

const container = new Container();
container.register(Logger, new Logger());

const userService = container.resolve<UserService>(UserService);
userService.createUser('Alice');
```

---

## 十一、缓存装饰器

```typescript
function cache(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  const cacheStore = new Map();
  
  descriptor.value = function(...args: any[]) {
    const key = JSON.stringify(args);
    
    if (cacheStore.has(key)) {
      console.log('Returning cached result');
      return cacheStore.get(key);
    }
    
    const result = originalMethod.apply(this, args);
    cacheStore.set(key, result);
    return result;
  };
  
  return descriptor;
}

class MathService {
  @cache
  factorial(n: number): number {
    if (n <= 1) return 1;
    return n * this.factorial(n - 1);
  }
}
```

---

## 十二、最佳实践

1. 装饰器应轻量、无副作用
2. 充分利用 Reflect Metadata
3. 注意装饰器执行顺序
4. 提供类型安全的装饰器
5. 文档说明装饰器的使用方法

---

## 十三、总结

装饰器是 TypeScript 强大的元编程能力，能实现 AOP、依赖注入等高级功能。
