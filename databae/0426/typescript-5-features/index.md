# TypeScript 5.x 高级特性完全指南

TypeScript 5.x 带来了许多强大的新特性。本文将带你全面掌握 TypeScript 5.x 的高级特性。

## 一、TypeScript 5.0 新特性

### 1. const 类型参数

```typescript
// 之前
function createPair<T extends readonly [unknown, unknown]>(
  pair: T
): [T[0], T[1]] {
  return [pair[0], pair[1]];
}

const pair1 = createPair(["hello", 42]);
//    ^? [string, number]

// TypeScript 5.0: const 类型参数
function createPair<const T extends readonly [unknown, unknown]>(
  pair: T
): [T[0], T[1]] {
  return [pair[0], pair[1]];
}

const pair2 = createPair(["hello", 42]);
//    ^? ["hello", 42]

// 实际例子
const config = {
  api: "https://api.example.com",
  timeout: 5000,
} as const;

function createConfig<const T>(config: T): T {
  return config;
}

const typedConfig = createConfig({
  api: "https://api.example.com",
  timeout: 5000,
});
//    ^? { api: "https://api.example.com"; timeout: 5000; }
```

### 2. 装饰器（Decorators）

```typescript
// 类装饰器
function sealed(target: Function) {
  Object.seal(target);
  Object.seal(target.prototype);
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
function enumerable(value: boolean) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    descriptor.enumerable = value;
  };
}

class Greeter {
  greeting: string;
  constructor(message: string) {
    this.greeting = message;
  }

  @enumerable(false)
  greet() {
    return "Hello, " + this.greeting;
  }
}

// 属性装饰器
function format(pattern: string) {
  return function (target: any, propertyKey: string) {
    let value: string;

    const getter = function () {
      return value;
    };

    const setter = function (newVal: string) {
      value = pattern.replace("{}", newVal);
    };

    Object.defineProperty(target, propertyKey, {
      get: getter,
      set: setter,
      enumerable: true,
      configurable: true,
    });
  };
}

class User {
  @format("Hello, {}!")
  name: string;

  constructor(name: string) {
    this.name = name;
  }
}

const user = new User("Alice");
console.log(user.name); // "Hello, Alice!"

// 参数装饰器
function log(target: any, propertyKey: string, parameterIndex: number) {
  const existingLoggedParameters =
    target[propertyKey]?.loggedParameters || [];
  existingLoggedParameters.push(parameterIndex);
  target[propertyKey].loggedParameters = existingLoggedParameters;
}

class Calculator {
  add(@log a: number, @log b: number) {
    return a + b;
  }
}
```

### 3. 联合类型枚举

```typescript
// TypeScript 5.0 之前
const Status = {
  Pending: "pending",
  InProgress: "in-progress",
  Completed: "completed",
} as const;

type Status = (typeof Status)[keyof typeof Status];

// TypeScript 5.0: 更简洁的方式
const Status = ["pending", "in-progress", "completed"] as const;
type Status = (typeof Status)[number];

function handleStatus(status: Status) {
  switch (status) {
    case "pending":
      return "处理中";
    case "in-progress":
      return "进行中";
    case "completed":
      return "已完成";
  }
}
```

## 二、TypeScript 5.1 新特性

### 1. 更容易的异步返回类型

```typescript
// TypeScript 5.1 之前
async function fetchData(): Promise<{ data: string }> {
  const response = await fetch("/api/data");
  return response.json();
}

// TypeScript 5.1: 自动推断 Promise 包装
async function fetchData() {
  const response = await fetch("/api/data");
  return response.json();
  // 自动返回 Promise<{ data: string }>
}

// 泛型函数
async function fetch<T>(url: string): Promise<T> {
  const response = await fetch(url);
  return response.json();
}

const data = await fetch<{ id: number; name: string }>("/api/user");
//    ^? { id: number; name: string }
```

### 2. JSX 元素和 JSX 标签类型之间的解耦

```typescript
// 自定义 JSX 类型
declare global {
  namespace JSX {
    interface Element {
      type: string;
      props: any;
      children: any[];
    }
    interface IntrinsicElements {
      div: { id?: string; class?: string };
      span: { id?: string; class?: string };
    }
  }
}

// React 18 类型支持
import React from "react";

interface Props {
  name: string;
}

const Component: React.FC<Props> = ({ name }) => {
  return <div>Hello, {name}</div>;
};
```

## 三、TypeScript 5.2 新特性

### 1. using 声明和显式资源管理

```typescript
// using 声明
class TempFile implements Disposable {
  #path: string;

  constructor(path: string) {
    this.#path = path;
  }

  [Symbol.dispose]() {
    console.log(`Deleting file: ${this.#path}`);
  }
}

function processFile() {
  using file = new TempFile("/tmp/temp.txt");
  console.log("Using file...");
} // 离开作用域时自动调用 dispose

processFile();
// 输出:
// Using file...
// Deleting file: /tmp/temp.txt

// 异步 using
class AsyncTempFile implements AsyncDisposable {
  #path: string;

  constructor(path: string) {
    this.#path = path;
  }

  async [Symbol.asyncDispose]() {
    console.log(`Deleting file: ${this.#path}`);
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
}

async function processFileAsync() {
  await using file = new AsyncTempFile("/tmp/temp.txt");
  console.log("Using file...");
}

processFileAsync();
```

### 2. 装饰器元数据

```typescript
import "reflect-metadata";

function Injectable() {
  return function (target: Function) {
    Reflect.defineMetadata("injectable", true, target);
  };
}

@Injectable()
class UserService {
  constructor(private logger: Logger) {}
}

class Logger {}

// 检查元数据
const isInjectable = Reflect.getMetadata("injectable", UserService);
console.log(isInjectable); // true
```

## 四、TypeScript 5.3 新特性

### 1. 导入属性

```typescript
// 导入 JSON
import config from "./config.json" with { type: "json" };

// 导入 CSS
import styles from "./styles.css" with { type: "css" };

// 导入 WASM
import module from "./module.wasm" with { type: "webassembly" };

// 动态导入
const config = await import("./config.json", {
  with: { type: "json" },
});
```

### 2. switch (true) 类型缩小

```typescript
function processValue(value: unknown) {
  switch (true) {
    case typeof value === "string":
      return value.toUpperCase();
    //    ^? string

    case typeof value === "number":
      return value.toFixed(2);
    //    ^? number

    case Array.isArray(value):
      return value.length;
    //    ^? any[]

    default:
      return "unknown";
  }
}
```

## 五、TypeScript 5.4 新特性

### 1. 闭包中的类型缩小

```typescript
function example() {
  let value: string | number = "hello";

  if (typeof value === "string") {
    setTimeout(() => {
      console.log(value.toUpperCase()); // TypeScript 5.4 现在可以推断这是 string
    }, 1000);
  }
}

// 泛型类型缩小
function process<T>(input: T) {
  if (typeof input === "string") {
    return input.length;
    //    ^? T & string
  }
  return input;
}
```

### 2. Object.groupBy 和 Map.groupBy

```typescript
interface Person {
  name: string;
  age: number;
}

const people: Person[] = [
  { name: "Alice", age: 25 },
  { name: "Bob", age: 30 },
  { name: "Charlie", age: 25 },
  { name: "David", age: 30 },
];

// 按年龄分组
const groupedByAge = Object.groupBy(people, (person) => person.age);
/*
{
  25: [ { name: 'Alice', age: 25 }, { name: 'Charlie', age: 25 } ],
  30: [ { name: 'Bob', age: 30 }, { name: 'David', age: 30 } ]
}
*/

// Map.groupBy
const mapGroupedByAge = Map.groupBy(people, (person) => person.age);
```

## 六、高级类型

### 1. 条件类型

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>; // true
type B = IsString<number>; // false

// 示例：提取函数返回类型
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

function greet(): string {
  return "Hello";
}

type GreetReturn = ReturnType<typeof greet>; // string

// 示例：提取 Promise 包裹的类型
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;

type Unwrapped = UnwrapPromise<Promise<string>>; // string
```

### 2. 映射类型

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

// 所有属性变为可选
type PartialUser = Partial<User>;
/*
{
  id?: number;
  name?: string;
  email?: string;
}
*/

// 所有属性变为只读
type ReadonlyUser = Readonly<User>;
/*
{
  readonly id: number;
  readonly name: string;
  readonly email: string;
}
*/

// 选择特定属性
type UserNameAndEmail = Pick<User, "name" | "email">;
/*
{
  name: string;
  email: string;
}
*/

// 排除特定属性
type UserWithoutId = Omit<User, "id">;
/*
{
  name: string;
  email: string;
}
*/

// 自定义映射类型
type Nullable<T> = {
  [P in keyof T]: T[P] | null;
};

type NullableUser = Nullable<User>;
/*
{
  id: number | null;
  name: string | null;
  email: string | null;
}
*/
```

### 3. 模板字面量类型

```typescript
type EventName = "click" | "focus" | "blur";
type HandlerName = `on${Capitalize<EventName>}`;
// "onClick" | "onFocus" | "onBlur"

type Status = "pending" | "completed";
type Message = `status_${Status}`;
// "status_pending" | "status_completed"

// 示例：CSS 属性
type CSSProperty = "margin" | "padding";
type CSSDirection = "top" | "right" | "bottom" | "left";
type CSSRule = `${CSSProperty}-${CSSDirection}`;
// "margin-top" | "margin-right" | ... | "padding-left"
```

### 4. 递归类型

```typescript
// 深度 Partial
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

interface NestedObject {
  a: {
    b: {
      c: number;
    };
  };
}

type DeepPartialNested = DeepPartial<NestedObject>;
/*
{
  a?: {
    b?: {
      c?: number;
    };
  };
}
*/

// 深度 Readonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};
```

## 七、实战示例

### 1. 类型安全的状态管理

```typescript
type State = {
  count: number;
  user: {
    name: string;
    age: number;
  };
};

type Action =
  | { type: "increment" }
  | { type: "decrement" }
  | { type: "setName"; payload: string }
  | { type: "setAge"; payload: number };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "increment":
      return { ...state, count: state.count + 1 };
    case "decrement":
      return { ...state, count: state.count - 1 };
    case "setName":
      return { ...state, user: { ...state.user, name: action.payload } };
    case "setAge":
      return { ...state, user: { ...state.user, age: action.payload } };
    default:
      return state;
  }
}

const initialState: State = {
  count: 0,
  user: { name: "Alice", age: 25 },
};

const store = {
  state: initialState,
  dispatch(action: Action) {
    this.state = reducer(this.state, action);
  },
};

store.dispatch({ type: "increment" });
store.dispatch({ type: "setName", payload: "Bob" });
```

### 2. 类型安全的 API 客户端

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

interface Post {
  id: number;
  title: string;
  content: string;
  userId: number;
}

type Endpoint = "/users" | "/users/:id" | "/posts" | "/posts/:id";

type ExtractParams<T extends string> =
  T extends `${infer _Start}:${infer Param}/${infer Rest}`
    ? { [K in Param | keyof ExtractParams<Rest>]: string }
    : T extends `${infer _Start}:${infer Param}`
    ? { [K in Param]: string }
    : never;

type ApiResponse<T> = {
  data: T;
  status: number;
};

class ApiClient {
  async get<T>(
    endpoint: Endpoint,
    params?: ExtractParams<typeof endpoint>
  ): Promise<ApiResponse<T>> {
    let url = endpoint as string;
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url = url.replace(`:${key}`, value);
      });
    }
    const response = await fetch(url);
    const data = await response.json();
    return { data, status: response.status };
  }
}

const api = new ApiClient();

// 获取用户列表
const usersResponse = await api.get<User[]>("/users");

// 获取单个用户
const userResponse = await api.get<User>("/users/:id", { id: "1" });

// 获取文章列表
const postsResponse = await api.get<Post[]>("/posts");
```

## 八、最佳实践

1. 始终启用严格模式
2. 使用 const 类型参数保持类型精确
3. 合理使用装饰器
4. 使用 using 管理资源
5. 利用类型缩小提高代码安全性
6. 使用映射类型减少重复
7. 模板字面量类型用于字符串操作
8. 递归类型处理嵌套对象
9. 类型安全的状态管理
10. 类型安全的 API 客户端

## 九、总结

TypeScript 5.x 核心特性：
- const 类型参数
- 装饰器
- using 声明（资源管理）
- 导入属性
- switch (true) 类型缩小
- 闭包中的类型缩小
- Object.groupBy / Map.groupBy
- 高级类型（条件、映射、模板字面量、递归）
- 实战应用

开始使用 TypeScript 5.x 的高级特性吧！
