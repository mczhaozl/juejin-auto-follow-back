# TypeScript 类型收窄深度指南：从入门到精通

> 全面掌握 TypeScript 类型收窄机制，写出更安全、更精确的类型代码。

## 一、类型收窄概述

类型收窄是 TypeScript 类型系统中最为核心和强大的特性之一。它允许 TypeScript 在特定的代码路径中，根据条件判断自动缩小变量的类型范围，从而提供更精确的类型信息和更安全的类型检查。

在日常开发中，我们经常需要处理联合类型、可选属性、字面量类型等复杂类型场景。如果没有类型收窄，我们不得不在每次使用时都进行类型断言，这不仅繁琐，还容易引入运行时错误。类型收窄机制让 TypeScript 能够智能地推断变量在特定上下文中的具体类型，大大提升了开发效率和代码质量。

理解类型收窄不仅能帮助你写出更简洁的代码，还能让你在面对复杂类型时游刃有余。本文将从基础概念出发，深入讲解各种类型收窄技巧，并通过大量实例帮助你建立完整的类型收窄知识体系。

## 二、类型守卫与类型收窄

### 2.1 什么是类型守卫

类型守卫（Type Guard）是一种特殊的表达式或函数，它能够告诉 TypeScript 编译器某个变量在特定条件下具有更具体的类型。类型守卫是实现类型收窄的主要手段。

TypeScript 内置了多种类型守卫机制，包括 typeof 操作符、instanceof 操作符、in 操作符等。同时，我们也可以通过自定义类型守卫函数来创建更复杂的类型判断逻辑。

```typescript
// typeof 类型守卫
function processValue(value: string | number) {
  if (typeof value === 'string') {
    // 在这个分支中，value 被收窄为 string 类型
    return value.toUpperCase();
  } else {
    // 在这个分支中，value 被收窄为 number 类型
    return value * 2;
  }
}

// instanceof 类型守卫
class Dog {
  bark() {
    console.log('Woof!');
  }
}

class Cat {
  meow() {
    console.log('Meow!');
  }
}

function makeSound(animal: Dog | Cat) {
  if (animal instanceof Dog) {
    animal.bark();
  } else {
    animal.meow();
  }
}
```

### 2.2 自定义类型守卫

当内置的类型守卫无法满足需求时，我们可以创建自定义的类型守卫函数。自定义类型守卫的返回值类型使用 `value is Type` 的形式，告诉 TypeScript 返回 true 时变量的具体类型。

```typescript
interface Fish {
  swim(): void;
  hasFins: boolean;
}

interface Bird {
  fly(): void;
  hasWings: boolean;
}

function isFish(animal: Fish | Bird): animal is Fish {
  return (animal as Fish).swim !== undefined;
}

function handleAnimal(animal: Fish | Bird) {
  if (isFish(animal)) {
    // animal 被收窄为 Fish 类型
    animal.swim();
    console.log('Has fins:', animal.hasFins);
  } else {
    // animal 被收窄为 Bird 类型
    animal.fly();
    console.log('Has wings:', animal.hasWings);
  }
}
```

自定义类型守卫在处理复杂类型判断时非常有用，可以将类型判断逻辑封装成可复用的函数，使代码更加清晰和易于维护。

### 2.3 类型守卫的组合使用

在实际开发中，我们经常需要组合使用多个类型守卫来处理复杂的类型判断场景。TypeScript 能够正确地追踪多个类型守卫的组合效果，实现多层类型收窄。

```typescript
type Shape = 
  | { kind: 'circle'; radius: number }
  | { kind: 'square'; side: number }
  | { kind: 'rectangle'; width: number; height: number };

function calculateArea(shape: Shape): number {
  if (shape.kind === 'circle') {
    // 收窄为 circle
    return Math.PI * shape.radius ** 2;
  }
  
  if (shape.kind === 'square') {
    // 收窄为 square
    return shape.side ** 2;
  }
  
  // 收窄为 rectangle
  return shape.width * shape.height;
}

// 组合使用多个条件
function describeShape(shape: Shape): string {
  if (shape.kind === 'circle' && shape.radius > 10) {
    return 'Large circle';
  }
  
  if (shape.kind === 'square' || shape.kind === 'rectangle') {
    if ('side' in shape) {
      return 'Square with side ' + shape.side;
    }
    return `Rectangle ${shape.width}x${shape.height}`;
  }
  
  return 'Unknown shape';
}
```

## 三、可辨识联合与类型收窄

### 3.1 可辨识联合模式

可辨识联合（Discriminated Union）是 TypeScript 中处理相关类型的一种强大模式。它通过一个共有的字面量属性（可辨识属性）来区分联合中的不同成员，TypeScript 可以根据这个属性的值进行精确的类型收窄。

```typescript
// 定义可辨识联合类型
type PaymentStatus = 
  | { status: 'pending' }
  | { status: 'processing' }
  | { status: 'success'; transactionId: string }
  | { status: 'failed'; errorCode: number; message: string };

// 处理支付状态
function handlePayment(status: PaymentStatus) {
  switch (status.status) {
    case 'pending':
      console.log('Payment is pending...');
      break;
      
    case 'processing':
      console.log('Payment is being processed...');
      break;
      
    case 'success':
      // status 被收窄为 { status: 'success'; transactionId: string }
      console.log('Payment successful! Transaction ID:', status.transactionId);
      break;
      
    case 'failed':
      // status 被收窄为 { status: 'failed'; errorCode: number; message: string }
      console.log('Payment failed:', status.message, 'Code:', status.errorCode);
      break;
  }
}
```

可辨识联合模式的核心在于可辨识属性的选择。这个属性应该是每个类型成员都拥有的字面量类型，且不同成员的值应该互不相同。这样 TypeScript 才能准确地区分和收窄类型。

### 3.2 穷尽性检查

可辨识联合的一个强大特性是支持穷尽性检查（Exhaustiveness Checking）。当我们在 switch 语句或 if-else 链中处理所有可能的类型成员时，TypeScript 能够确保我们不会遗漏任何情况。

```typescript
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

function handleRequest(method: HTTPMethod, url: string, body?: unknown) {
  switch (method) {
    case 'GET':
      return fetch(url, { method: 'GET' });
      
    case 'POST':
      return fetch(url, { 
        method: 'POST',
        body: body ? JSON.stringify(body) : undefined 
      });
      
    case 'PUT':
      return fetch(url, { 
        method: 'PUT',
        body: body ? JSON.stringify(body) : undefined 
      });
      
    case 'DELETE':
      return fetch(url, { method: 'DELETE' });
      
    default:
      // 穷尽性检查：如果遗漏了任何情况，这里会报错
      const _exhaustive: never = method;
      throw new Error(`Unknown HTTP method: ${_exhaustive}`);
  }
}
```

当添加新的 HTTPMethod 类型时，default 分支会产生类型错误，提示开发者需要处理新的情况。这种机制能够有效防止遗漏处理新添加的类型成员。

### 3.3 嵌套可辨识联合

复杂的业务场景往往需要使用嵌套的可辨识联合来处理多层次的数据结构。TypeScript 能够正确地追踪多层嵌套的类型收窄。

```typescript
type APIResponse<T> = 
  | { success: true; data: T }
  | { success: false; error: { code: number; message: string } };

type User = {
  id: number;
  name: string;
  email: string;
};

type Order = {
  orderId: string;
  items: Array<{ productId: string; quantity: number }>;
  total: number;
};

type UserResponse = APIResponse<User>;
type OrderResponse = APIResponse<Order>;

function handleResponse<T>(
  response: APIResponse<T>,
  onSuccess: (data: T) => void,
  onError: (error: { code: number; message: string }) => void
) {
  if (response.success) {
    // response 被收窄为 { success: true; data: T }
    onSuccess(response.data);
  } else {
    // response 被收窄为 { success: false; error: { code: number; message: string } }
    onError(response.error);
  }
}

// 使用示例
const userResponse: UserResponse = {
  success: true,
  data: { id: 1, name: 'John', email: 'john@example.com' }
};

handleResponse(
  userResponse,
  (user) => console.log('User:', user.name),
  (error) => console.error('Error:', error.message)
);
```

## 四、类型谓词与类型断言

### 4.1 类型谓词详解

类型谓词（Type Predicate）是自定义类型守卫的核心语法，形式为 `parameterName is Type`。它允许我们精确地控制 TypeScript 如何收窄参数的类型。

```typescript
interface Admin {
  role: 'admin';
  permissions: string[];
}

interface User {
  role: 'user';
  username: string;
}

interface Guest {
  role: 'guest';
  visitCount: number;
}

type AuthenticatedUser = Admin | User | Guest;

// 类型谓词函数
function isAdmin(user: AuthenticatedUser): user is Admin {
  return user.role === 'admin';
}

function isUser(user: AuthenticatedUser): user is User {
  return user.role === 'user';
}

function isGuest(user: AuthenticatedUser): user is Guest {
  return user.role === 'guest';
}

// 使用类型谓词
function getUserPermissions(user: AuthenticatedUser): string[] {
  if (isAdmin(user)) {
    // user 被收窄为 Admin
    return user.permissions;
  }
  
  if (isUser(user)) {
    // user 被收窄为 User
    return []; // 普通用户没有特殊权限
  }
  
  // user 被收窄为 Guest
  return [];
}
```

类型谓词的强大之处在于它可以表达复杂的类型判断逻辑，而不仅仅局限于简单的属性检查。这使得我们可以创建高度定制化的类型守卫。

### 4.2 类型断言的使用场景

类型断言（Type Assertion）允许我们显式地告诉 TypeScript 某个值的类型。与类型收窄不同，类型断言是开发者主动告诉编译器「我知道这个类型是什么」，而不是让编译器通过代码逻辑推断。

```typescript
// 使用 as 语法进行类型断言
const myCanvas = document.getElementById('myCanvas') as HTMLCanvasElement;
const ctx = myCanvas.getContext('2d'); // 现在可以访问 Canvas API

// 使用尖括号语法（仅在 .tsx 文件外可用）
const myInput = document.getElementById('myInput') as HTMLInputElement;
const value = myInput.value;

// 非空断言
const elements = document.querySelectorAll('.item')!;
elements.forEach(el => el.textContent);

// 类型断言 vs 类型守卫
interface APIResponse {
  data: unknown;
}

function handleResponse(response: APIResponse) {
  // 类型断言：开发者确信 data 是 User 类型
  const user = response.data as User;
  console.log(user.name);
  
  // 类型守卫：通过代码逻辑验证类型
  if (isUser(response.data)) {
    console.log(response.data.name); // TypeScript 已知这是 User
  }
}
```

需要注意的是，类型断言是信任开发者的，如果断言错误，可能导致运行时错误。因此，应该优先使用类型守卫进行类型收窄，只有在确实知道类型的情况下才使用类型断言。

### 4.3 双重断言与类型断言的风险

在某些情况下，我们需要使用双重断言来绕过 TypeScript 的类型检查。但这种做法存在风险，应该谨慎使用。

```typescript
// 双重断言：从 A 类型断言到 unknown，再断言到目标类型
const value = someValue as unknown as TargetType;

// 示例：处理 DOM 元素
const element = document.getElementById('my-element');
// 正常情况
const input = element as HTMLInputElement;

// 双重断言：当你确定元素是特定类型，但 TypeScript 无法推断时
const widget = element as unknown as CustomWidget;

// 使用双重断言的风险
// 如果元素实际上不是 CustomWidget 类型，运行时可能出错
```

双重断言应该作为最后手段使用。在使用之前，应该考虑是否有更好的类型设计方式，或者是否可以通过类型守卫来实现类型收窄。

## 五、索引访问类型与映射类型

### 5.1 索引访问类型

索引访问类型（Indexed Access Types）允许我们通过索引获取类型的成员，从而创建更灵活的类型定义。

```typescript
interface Person {
  name: string;
  age: number;
  address: {
    city: string;
    zip: string;
  };
}

// 获取单个属性类型
type PersonName = Person['name']; // string
type PersonAge = Person['age']; // number

// 获取嵌套属性类型
type PersonCity = Person['address']['city']; // string

// 使用联合类型作为索引
type PersonAddressKeys = Person['address'][keyof Person['address']]; // string

// 获取数组元素类型
type StringArray = string[];
type StringArrayElement = StringArray[number]; // string

// 在函数中使用索引访问类型
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const person: Person = {
  name: 'Alice',
  age: 30,
  address: { city: 'NYC', zip: '10001' }
};

const name = getProperty(person, 'name'); // string
const city = getProperty(person, 'address'); // { city: string; zip: string }
```

### 5.2 映射类型

映射类型（Mapped Types）允许我们基于现有类型创建新类型，对类型的每个属性进行转换。

```typescript
interface Original {
  id: number;
  name: string;
  age: number;
  email: string;
}

// 将所有属性变为可选
type Partial<T> = {
  [P in keyof T]?: T[P];
};

type PartialPerson = Partial<Person>;
// { id?: number; name?: string; age?: number; email?: string }

// 将所有属性变为只读
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type ReadonlyPerson = Readonly<Person>;
// { readonly id: number; readonly name: string; ... }

// 将所有属性变为可选且只读
type OptionalReadonly<T> = {
  readonly [P in keyof T]?: T[P];
};

// 映射类型的内置实现
type Pick<T, K extends keyof T> = {
  [P in K]: T[P];
};

type PersonBasic = Pick<Person, 'id' | 'name'>;
// { id: number; name: string }

type Omit<T, K extends keyof T> = {
  [P in keyof T as P extends K ? never : P]: T[P];
};

type PersonWithoutEmail = Omit<Person, 'email'>;
// { id: number; name: string; age: number }
```

### 5.3 条件类型与分布式特性

条件类型（Conditional Types）是 TypeScript 类型系统中最灵活的特性之一，它允许我们根据条件选择不同的类型。

```typescript
// 条件类型基本语法
type IsString<T> = T extends string ? true : false;

type Test1 = IsString<string>; // true
type Test2 = IsString<number>; // false

// 分布式条件类型
// 当 T 是联合类型时，条件类型会分别应用于每个成员
type ToArray<T> = T[];

type Test3 = ToArray<string | number>; // string[] | number[]

// 正确实现：分布式
type ToArrayDistributed<T> = T extends any ? T[] : never;

type Test4 = ToArrayDistributed<string | number>; // string[] | number[]

// 实际应用：根据类型选择不同的处理方式
type Response<T> = T extends string 
  ? { type: 'text'; content: T }
  : { type: 'binary'; data: T };

type TextResponse = Response<string>;
// { type: 'text'; content: string }

type BinaryResponse = Response<Blob>;
// { type: 'binary'; data: Blob }
```

## 六、模板字面量类型与类型收窄

### 6.1 模板字面量类型基础

TypeScript 4.1 引入了模板字面量类型（Template Literal Types），允许我们在类型级别使用模板字面量语法。这为类型系统带来了���大的字符串处理能力。

```typescript
// 基本模板字面量类型
type Greeting = `Hello, ${string}`;
// 匹配任何以 "Hello, " 开头的字符串

type Email = `${string}@${string}.${string}`;
// 匹配基本的 email 格式

// 使用联合类型
type EventName = `on${'Click' | 'Hover' | 'Focus'}`;
// "onClick" | "onHover" | "onFocus"

// 模板字面量类型与收窄
type CSSProperty = 
  | `${'margin' | 'padding'}-${'top' | 'right' | 'bottom' | 'left'}`;
// "margin-top" | "margin-right" | ... | "padding-left"

function setCSSProperty(prop: CSSProperty, value: string) {
  // 在函数内部，prop 被收窄为具体的 CSS 属性名
  document.documentElement.style.setProperty(`--${prop}`, value);
}

setCSSProperty('margin-top', '10px'); // OK
setCSSProperty('padding-left', '20px'); // OK
// setCSSProperty('border-radius', '5px'); // Error
```

### 6.2 模板字面量类型的高级用法

模板字面量类型可以与条件类型、映射类型等组合使用，创建复杂的类型转换逻辑。

```typescript
// 使用 infer 进行类型推断
type GetReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

type Func1 = () => number;
type Func2 = (x: string) => boolean;
type Func3 = (a: number, b: string) => { name: string };

type R1 = GetReturnType<Func1>; // number
type R2 = GetReturnType<Func2>; // boolean
type R3 = GetReturnType<Func3>; // { name: string }

// 模板字面量类型中的 infer
type ExtractEventParams<T> = T extends `on${infer Event}` ? Event : never;

type Events = 'onClick' | 'onHover' | 'onSubmit' | 'customEvent';

type EventNames = ExtractEventParams<Events>;
// "Click" | "Hover" | "Submit" | "customEvent"

// 组合使用：创建完整的 API 路径类型
type HTTPMethod = 'get' | 'post' | 'put' | 'delete';
type BasePath = '/api' | '/v2';
type Resource = 'users' | 'posts' | 'comments';

type APIEndpoint = `${Uppercase<HTTPMethod>} ${BasePath}/${Resource}`;
// "GET /api/users" | "GET /api/posts" | ... | "DELETE /v2/comments"
```

### 6.3 字符串类型收窄的实际应用

模板字面量类型在处理字符串字面量类型时特别有用，可以实现精确的字符串类型收窄。

```typescript
// 状态机类型
type State = 
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'success'; data: unknown }
  | { kind: 'error'; message: string };

// 使用模板字面量类型创建 Action 类型
type Action = 
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: unknown }
  | { type: 'FETCH_ERROR'; error: string }
  | { type: 'RESET' };

// Action 处理函数
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_START':
      return { kind: 'loading' };
      
    case 'FETCH_SUCCESS':
      return { kind: 'success', data: action.payload };
      
    case 'FETCH_ERROR':
      return { kind: 'error', message: action.error };
      
    case 'RESET':
      return { kind: 'idle' };
      
    default:
      // 穷尽性检查
      const _: never = action;
      return state;
  }
}
```

## 七、类型收窄在泛型中的应用

### 7.1 泛型约束与类型收窄

泛型与类型收窄的结合是 TypeScript 类型系统的高级应用。通过泛型约束和类型守卫，我们可以创建灵活且类型安全的通用函数。

```typescript
interface HasId {
  id: number;
}

interface HasName {
  name: string;
}

type WithId<T> = T extends HasId ? T : never;
type WithName<T> = T extends HasName ? T : never;

// 条件类型实现类型收窄
function processItem<T>(item: T): T extends HasId ? T : never {
  if ('id' in item) {
    return item as T extends HasId ? T : never;
  }
  throw new Error('Item must have id');
}

// 使用泛型约束
function getId<T extends HasId>(item: T): number {
  return item.id;
}

function getName<T extends HasName>(item: T): string {
  return item.name;
}

// 泛型函数中的类型收窄
function firstItem<T>(arr: T[]): T | undefined {
  return arr[0];
}

function processArray<T extends HasId>(arr: T[]): number[] {
  const first = firstItem(arr);
  if (first) {
    // first 被收窄为 T & HasId
    return [first.id];
  }
  return [];
}
```

### 7.2 多泛型参数的类型收窄

当函数有多个泛型参数时，类型收窄变得更加复杂。我们需要考虑不同参数之间的类型关系。

```typescript
// 关联类型的类型收窄
function pair<T, U extends T>(first: T, second: U): [T, U] {
  return [first, second];
}

const p1 = pair('hello', 'world'); // [string, string]
const p2 = pair(42, 100); // [number, number]
// const p3 = pair('hello', 42); // Error: second must extend first

// 使用类型守卫进行多泛型收窄
function isSameType<T, U>(a: T, b: U): a is T & U {
  return typeof a === typeof b;
}

function merge<T, U>(a: T, b: U): T & U {
  if (isSameType(a, b)) {
    // a 和 b 被收窄为相同类型
    return { ...a, ...b } as T & U;
  }
  return { ...a, ...b } as T & U;
}
```

### 7.3 泛型工厂函数中的类型收窄

泛型工厂函数是创建类型安全对象的强大工具，结合类型收窄可以实现复杂的类型转换逻辑。

```typescript
// 工厂函数模式
interface Factory<T> {
  create(): T;
}

class StringFactory implements Factory<string> {
  create() {
    return 'default string';
  }
}

class NumberFactory implements Factory<number> {
  create() {
    return 42;
  }
}

function createFactory<T>(factory: Factory<T>): T {
  return factory.create();
}

// 使用泛型工厂
const str = createFactory(new StringFactory()); // string
const num = createFactory(new NumberFactory()); // number

// 泛型与条件类型
type FactoryReturn<T> = T extends Factory<infer R> ? R : never;

type StringReturn = FactoryReturn<StringFactory>; // string
type NumberReturn = FactoryReturn<NumberFactory>; // number
```

## 八、类型收窄的最佳实践

### 8.1 何时使用类型收窄

类型收窄应该成为 TypeScript 开发的日常实践。以下是一些适合使用类型收窄的场景。

处理联合类型时，类型收窄是最自然的选择。无论是可选属性、可空值还是多态类型，类型收窄都能提供精确的类型信息。

```typescript
// 处理可选属性
interface User {
  name: string;
  email?: string;
}

function sendEmail(user: User) {
  if (user.email) {
    // user.email 被收窄为 string（不再是 string | undefined）
    sendToAddress(user.email);
  }
}

// 处理 null | undefined
function processValue(value: string | null | undefined) {
  if (value != null) {
    // value 被收窄为 string
    console.log(value.toUpperCase());
  }
}
```

### 8.2 避免过度类型断言

虽然类型断言是 TypeScript 的重要特性，但应该优先使用类型收窄。类型断言相当于告诉编译器「我知道我在做什么」，这意味着放弃了 TypeScript 的类型检查。

```typescript
// 不推荐：过度使用类型断言
function badExample(value: unknown) {
  const str = value as string; // 危险！如果 value 不是 string，运行时可能出错
  return str.toUpperCase();
}

// 推荐：使用类型守卫
function goodExample(value: unknown) {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
  return 'Not a string';
}

// 如果必须使用类型断言，使用类型断言函数封装
function assertString(value: unknown): asserts value is string {
  if (typeof value !== 'string') {
    throw new Error('Expected string');
  }
}

function anotherExample(value: unknown) {
  assertString(value);
  // 现在 value 被收窄为 string
  return value.toUpperCase();
}
```

### 8.3 利用类型系统发现潜在问题

类型收窄不仅是一种编码技巧，更是一种发现潜在问题的工具。当 TypeScript 无法正确收窄类型时，往往意味着代码中存在设计问题或逻辑漏洞。

```typescript
// TypeScript 无法收窄时，可能需要重新设计类型
type Response<T> = 
  | { success: true; data: T }
  | { success: false; error: string };

function handleResponse<T>(response: Response<T>) {
  if (response.success) {
    return response.data;
  }
  
  // 在这里，response 被收窄为 { success: false; error: string }
  // 如果忘记处理 error 情况，TypeScript 不会报错
  // 但我们可以添加默认处理
  throw new Error(response.error || 'Unknown error');
}
```

## 九、总结

类型收窄是 TypeScript 类型系统的核心特性，它让我们能够在代码中实现精确的类型推断和安全的类���检查。从简单的 typeof 检查到复杂的可辨识联合，从类型谓词到模板字面量类型，TypeScript 提供了丰富的工具来处理各种类型场景。

掌握类型收窄不仅能写出更安全的代码，还能提升开发效率。当你熟悉了类型收窄的技巧后，你会发现处理复杂类型变得自然而直观。同时，类型收窄也是理解 TypeScript 高级类型系统的基础，对于深入学习 TypeScript 至关重要。

在实际开发中，应该养成使用类型收窄的习惯，优先选择类型守卫而非类型断言，让 TypeScript 的类型系统为你的代码保驾护航。