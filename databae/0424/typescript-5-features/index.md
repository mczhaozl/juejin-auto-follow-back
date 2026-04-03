# TypeScript 5.x 新特性完全指南：从 5.0 到 5.4 的重大改进

TypeScript 5.x 带来了众多激动人心的新特性。本文将带你全面了解从 5.0 到 5.4 的所有重要改进。

## 一、TypeScript 5.0 新特性

### 1. 装饰器（Decorators）

```typescript
// 类装饰器
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

// 方法装饰器
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    return originalMethod.apply(this, args);
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
calc.add(2, 3); // 输出: Calling add with [2, 3]

// 访问器装饰器
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

// 属性装饰器
function format(target: any, propertyKey: string) {
  let value: string;
  const getter = function () {
    return value.toUpperCase();
  };
  const setter = function (newVal: string) {
    value = newVal;
  };
  Object.defineProperty(target, propertyKey, {
    get: getter,
    set: setter,
    enumerable: true,
    configurable: true
  });
}

class Person {
  @format
  name: string;
  constructor(name: string) {
    this.name = name;
  }
}

const person = new Person("alice");
console.log(person.name); // 输出: ALICE

// 参数装饰器
function required(target: any, propertyKey: string, parameterIndex: number) {
  const existingRequiredParameters: number[] = Reflect.getOwnMetadata("requiredParameters", target, propertyKey) || [];
  existingRequiredParameters.push(parameterIndex);
  Reflect.defineMetadata("requiredParameters", existingRequiredParameters, target, propertyKey);
}

function validate(target: any, propertyName: string, descriptor: TypedPropertyDescriptor<Function>) {
  const method = descriptor.value;
  descriptor.value = function (...args: any[]) {
    const requiredParameters: number[] = Reflect.getOwnMetadata("requiredParameters", target, propertyName) || [];
    for (let index of requiredParameters) {
      if (index >= args.length || args[index] === undefined) {
        throw new Error(`Missing required argument at position ${index}`);
      }
    }
    return method.apply(this, args);
  };
}

class UserService {
  @validate
  createUser(@required name: string, @required email: string) {
    return { name, email };
  }
}
```

### 2. const 类型参数

```typescript
// TypeScript 5.0 之前
function createPair<T extends readonly [unknown, unknown]>(
  pair: T
): T {
  return pair;
}

const pair = createPair(["hello", 42]);
// 类型: (string | number)[]

// TypeScript 5.0+
function createPair<const T extends readonly [unknown, unknown]>(
  pair: T
): T {
  return pair;
}

const pair = createPair(["hello", 42]);
// 类型: readonly ["hello", 42]

// 另一个例子
function getNames<const T extends readonly string[]>(names: T): T {
  return names;
}

const names = getNames(["Alice", "Bob", "Charlie"]);
// 类型: readonly ["Alice", "Bob", "Charlie"]
```

### 3. 枚举类型改进

```typescript
// 枚举值可以是任意表达式
enum LogLevel {
  Error = 1 << 0,
  Warning = 1 << 1,
  Info = 1 << 2,
  Debug = 1 << 3,
  All = Error | Warning | Info | Debug
}

const level = LogLevel.Error | LogLevel.Warning;
console.log(level); // 输出: 3

// 字符串枚举
enum Status {
  Pending = "pending",
  Approved = "approved",
  Rejected = "rejected"
}

// 异构枚举
enum Mixed {
  No = 0,
  Yes = "YES"
}
```

### 4. 改进的类型推断

```typescript
// 更好的数组方法类型推断
const arr = [1, 2, 3, 4, 5];
const doubled = arr.map(x => x * 2);
// 类型: number[]

// 更好的泛型推断
function identity<T>(arg: T): T {
  return arg;
}

const num = identity(42); // 类型: number
const str = identity("hello"); // 类型: string
```

## 二、TypeScript 5.1 新特性

### 1. 更简单的隐式返回类型

```typescript
// TypeScript 5.1 之前
function f(): undefined {
  // 必须显式返回 undefined
  return undefined;
}

// TypeScript 5.1+
function f() {
  // 自动推断返回 undefined
  return;
}

// 另一个例子
function g(): void {
  // 可以不返回任何值
}

function h() {
  // 自动推断返回 void
  if (Math.random() > 0.5) {
    return;
  }
}
```

### 2. JSX 标签类型检查改进

```typescript
// 更灵活的 JSX 类型
declare namespace JSX {
  interface IntrinsicElements {
    div: { className?: string; id?: string };
    span: { className?: string };
  }
}

// 更好的类型检查
const element = <div className="container">Hello</div>;
```

### 3. 模块解析改进

```typescript
// 更好的 Node16/NodeNext 模块解析
import { foo } from "./module.js";

// 支持 package.json 的 "exports" 字段
// package.json
// {
//   "exports": {
//     "./foo": "./dist/foo.js"
//   }
// }
import { bar } from "my-package/foo";
```

## 三、TypeScript 5.2 新特性

### 1. using 声明（显式资源管理）

```typescript
// TypeScript 5.2+
class TempFile implements Disposable {
  #path: string;
  constructor(path: string) {
    this.#path = path;
    console.log(`Creating file: ${this.#path}`);
  }

  [Symbol.dispose]() {
    console.log(`Deleting file: ${this.#path}`);
    // 删除文件的逻辑
  }
}

function doWork() {
  using file = new TempFile("temp.txt");
  // 使用文件...
  console.log("Working with file...");
} // 离开作用域时自动调用 Symbol.dispose

doWork();
// 输出:
// Creating file: temp.txt
// Working with file...
// Deleting file: temp.txt

// 异步资源管理
class AsyncResource implements AsyncDisposable {
  async [Symbol.asyncDispose]() {
    console.log("Cleaning up async resource...");
    await new Promise(resolve => setTimeout(resolve, 100));
  }
}

async function asyncWork() {
  await using resource = new AsyncResource();
  console.log("Using async resource...");
}

asyncWork();
```

### 2. 装饰器元数据

```typescript
import "reflect-metadata";

function metadata(key: string, value: any) {
  return function (target: any, propertyKey?: string | symbol) {
    if (propertyKey) {
      Reflect.defineMetadata(key, value, target, propertyKey);
    } else {
      Reflect.defineMetadata(key, value, target);
    }
  };
}

@metadata("role", "admin")
class User {
  @metadata("required", true)
  name: string;

  @metadata("default", 0)
  age: number;

  constructor(name: string, age: number) {
    this.name = name;
    this.age = age;
  }
}

const role = Reflect.getMetadata("role", User);
console.log(role); // 输出: admin

const required = Reflect.getMetadata("required", User.prototype, "name");
console.log(required); // 输出: true
```

### 3. 命名和匿名元组标签

```typescript
// 命名元组
type Point = [x: number, y: number];

const point: Point = [10, 20];
console.log(point[0]); // 输出: 10
console.log(point[1]); // 输出: 20

// 函数参数使用命名元组
function createPoint(...coords: [x: number, y: number]) {
  return { x: coords[0], y: coords[1] };
}

const p = createPoint(5, 10);
console.log(p); // 输出: { x: 5, y: 10 }
```

## 四、TypeScript 5.3 新特性

### 1. 导入属性（Import Attributes）

```typescript
// 导入 JSON 模块
import config from "./config.json" with { type: "json" };
console.log(config.apiUrl);

// 导入其他类型的模块
import data from "./data.yaml" with { type: "yaml" };
import wasm from "./module.wasm" with { type: "webassembly" };

// 动态导入
const module = await import("./module.js", {
  with: { type: "javascript" }
});
```

### 2. 更宽松的 instanceof 类型检查

```typescript
// TypeScript 5.3 之前
class Animal {
  move() {}
}

class Dog extends Animal {
  bark() {}
}

function f(obj: object) {
  if (obj instanceof Animal) {
    obj.move(); // 可以
  }
}

// TypeScript 5.3+
interface IAnimal {
  move(): void;
}

class Cat implements IAnimal {
  move() {}
}

function g(obj: object) {
  if (obj instanceof Cat) {
    obj.move();
  }
}
```

### 3. 布尔值类型优化

```typescript
// 更好的布尔值类型推断
function isEven(n: number): boolean {
  return n % 2 === 0;
}

const result = isEven(4);
if (result) {
  console.log("Even");
}
```

## 五、TypeScript 5.4 新特性

### 1. NoInfer 工具类型

```typescript
// TypeScript 5.4+
function createStreetLight<C extends string>(
  colors: C[],
  defaultColor: NoInfer<C>
) {
  return { colors, defaultColor };
}

// 现在 defaultColor 不会影响类型参数的推断
const light = createStreetLight(["red", "yellow", "green"], "red");
// 类型: { colors: ("red" | "yellow" | "green")[]; defaultColor: string; }

// 另一个例子
function useState<T>(initialValue: NoInfer<T>): [T, (value: T) => void] {
  let state = initialValue;
  const setState = (value: T) => { state = value; };
  return [state, setState];
}

const [count, setCount] = useState(0);
// count 的类型是 number
setCount(10); // 可以
```

### 2. 数组和对象字面量的类型改进

```typescript
// 更好的数组类型推断
const numbers = [1, 2, 3];
// 类型: number[]

const mixed = [1, "hello", true];
// 类型: (string | number | boolean)[]

// 更好的对象类型推断
const user = {
  name: "Alice",
  age: 30,
  isAdmin: true
};
// 类型: { name: string; age: number; isAdmin: boolean; }
```

### 3. 参数提示改进

```typescript
// 更好的参数提示
function greet(name: string, greeting: string = "Hello") {
  return `${greeting}, ${name}!`;
}

greet("Alice"); // 提示: greet(name: string, greeting?: string): string
greet("Bob", "Hi");
```

## 六、性能改进

### 1. 更快的编译速度

TypeScript 5.x 版本在编译速度上有显著提升：

```bash
# TypeScript 5.0+ 编译速度提升约 30-50%
tsc --noEmit
```

### 2. 更好的内存使用

```typescript
// 优化的类型检查减少了内存使用
interface User {
  id: number;
  name: string;
  email: string;
  age: number;
}

const users: User[] = [
  { id: 1, name: "Alice", email: "alice@example.com", age: 30 },
  { id: 2, name: "Bob", email: "bob@example.com", age: 25 },
];
```

## 七、实战迁移指南

### 1. 升级 TypeScript 版本

```bash
npm install --save-dev typescript@latest
```

### 2. 更新 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "strict": true,
    "declaration": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": false,
    "allowImportingTsExtensions": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 3. 逐步采用新特性

```typescript
// 1. 先启用 strict 模式
// 2. 使用新的装饰器语法
// 3. 采用 using 声明管理资源
// 4. 使用 NoInfer 优化类型推断
```

## 八、最佳实践

1. 保持 TypeScript 版本最新
2. 启用 strict 模式
3. 合理使用新特性
4. 使用装饰器增强代码
5. 使用 using 管理资源
6. 利用 NoInfer 优化类型推断
7. 关注编译性能
8. 做好类型测试

## 九、总结

TypeScript 5.x 核心改进：
- 装饰器（Decorators）
- const 类型参数
- using 声明和资源管理
- NoInfer 工具类型
- 导入属性（Import Attributes）
- 更好的类型推断
- 显著的性能提升
- 改进的开发体验

开始使用 TypeScript 5.x 的新特性吧！
