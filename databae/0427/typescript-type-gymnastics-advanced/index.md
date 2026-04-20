# TypeScript 类型体操高级技巧完全指南

> 深入掌握 TypeScript 高级类型，从零开始学习类型体操，成为类型大师。

## 一、类型体操概述

类型体操是 TypeScript 的高级特性，通过复杂的类型操作实现强大的类型安全。

### 1.1 为什么学类型体操

- 类型安全最大化
- 代码提示更精准
- 库开发必备技能
- 深入理解 TypeScript 类型系统

---

## 二、基础类型操作回顾

### 2.1 泛型基础

```typescript
// 简单泛型
function identity<T>(arg: T): T {
  return arg;
}

// 泛型接口
interface Container<T> {
  value: T;
}

// 泛型约束
interface Lengthwise {
  length: number;
}

function logLength<T extends Lengthwise>(arg: T): number {
  return arg.length;
}
```

### 2.2 条件类型

```typescript
// 基础条件类型
type IsString<T> = T extends string ? true : false;

type A = IsString<'hello'>; // true
type B = IsString<42>;      // false

// 条件类型的分布性
type ToArray<T> = T extends any ? T[] : never;
type C = ToArray<string | number>; // string[] | number[]
```

### 2.3 映射类型

```typescript
// 基础映射
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

// 带修饰符的映射
type Required<T> = {
  [P in keyof T]-?: T[P];
};

type Mutable<T> = {
  -readonly [P in keyof T]: T[P];
};
```

---

## 三、infer 关键字

### 3.1 infer 基础

```typescript
// 提取函数返回类型
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

function add(a: number, b: number): number {
  return a + b;
}

type AddReturn = ReturnType<typeof add>; // number

// 提取函数参数类型
type Parameters<T> = T extends (...args: infer P) => any ? P : never;

type AddParams = Parameters<typeof add>; // [number, number]

// 提取 Promise 中的类型
type Awaited<T> = T extends Promise<infer U> ? U : never;

type D = Awaited<Promise<string>>; // string
```

### 3.2 infer 高级用法

```typescript
// 提取数组元素类型
type ArrayElement<T> = T extends (infer U)[] ? U : never;

type E = ArrayElement<string[]>; // string

// 提取第一个元素
type First<T extends any[]> = T extends [infer F, ...any[]] ? F : never;

type F = First<[1, 2, 3]>; // 1

// 提取最后一个元素
type Last<T extends any[]> = T extends [...any[], infer L] ? L : never;

type G = Last<[1, 2, 3]>; // 3
```

---

## 四、模板字面量类型

### 4.1 基础用法

```typescript
type Hello = `Hello, ${string}!`;

type World = `Hello, ${'World'}!`;

// 事件名称
type EventName<T extends string> = `on${Capitalize<T>}`;

type ClickEvent = EventName<'click'>; // 'onClick'
```

### 4.2 字符串操作类型

```typescript
// 内置类型
type Upper = Uppercase<'hello'>;
type Lower = Lowercase<'HELLO'>;
type Cap = Capitalize<'hello'>;
type Uncap = Uncapitalize<'Hello'>;

// 自定义操作
type Split<S extends string, D extends string> =
  S extends `${infer T}${D}${infer U}` ? [T, ...Split<U, D>] : [S];

type H = Split<'a,b,c', ','>; // ['a', 'b', 'c']
```

---

## 五、递归类型

### 5.1 递归条件类型

```typescript
// 深度 Readonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

interface User {
  name: string;
  address: {
    city: string;
  };
}

type ReadonlyUser = DeepReadonly<User>;

// 深度 Partial
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};
```

### 5.2 递归数组类型

```typescript
// 数组扁平化
type Flatten<T> = T extends [infer F, ...infer R]
  ? (F extends any[] ? [...Flatten<F>, ...Flatten<R>] : [F, ...Flatten<R>])
  : T;

type I = Flatten<[1, [2, 3], [4, [5, 6]]]>; // [1, 2, 3, 4, 5, 6]

// 数组长度
type Length<T extends any[]> = T['length'];

type J = Length<[1, 2, 3]>; // 3
```

---

## 六、实战案例

### 6.1 案例一：函数柯里化类型

```typescript
// 柯里化类型
type Curry<F> = F extends (...args: infer Args) => infer R
  ? Args extends [infer First, ...infer Rest]
    ? (arg: First) => Curry<(...args: Rest) => R>
    : R
  : never;

function add(a: number, b: number, c: number): number {
  return a + b + c;
}

type CurriedAdd = Curry<typeof add>;
// (a: number) => (b: number) => (c: number) => number
```

### 6.2 案例二：路径访问类型

```typescript
// 深度路径访问
type Path<T> = T extends object
  ? {
      [K in keyof T]: K | `${K & string}.${Path<T[K]>}`;
    }[keyof T]
  : never;

type Get<T, P extends string> = P extends `${infer K}.${infer Rest}`
  ? K extends keyof T
    ? Get<T[K], Rest>
    : never
  : P extends keyof T
  ? T[P]
  : never;

interface User {
  name: string;
  address: {
    city: string;
  };
}

type UserPath = Path<User>; // 'name' | 'address' | 'address.city'
type CityType = Get<User, 'address.city'>; // string
```

### 6.3 案例三：事件 Emitter 类型

```typescript
// 类型安全的 EventEmitter
interface Events {
  click: { x: number; y: number };
  scroll: { top: number };
}

type EventKeys = keyof Events;

class TypedEmitter<E extends Record<string, any>> {
  on<K extends keyof E>(event: K, callback: (data: E[K]) => void): void {}
  emit<K extends keyof E>(event: K, data: E[K]): void {}
}

const emitter = new TypedEmitter<Events>();
emitter.on('click', ({ x, y }) => {}); // 类型安全
```

### 6.4 案例四：解析 URL 参数

```typescript
// 解析查询字符串
type ParseQueryParams<S extends string> = S extends `${infer K}=${infer V}`
  ? { [P in K]: V }
  : {};

type MergeParams<A, B> = A & B extends infer AB
  ? { [K in keyof AB]: AB[K] }
  : never;

type ParseURLQuery<S extends string> = S extends `${infer First}&${infer Rest}`
  ? MergeParams<ParseQueryParams<First>, ParseURLQuery<Rest>>
  : ParseQueryParams<S>;

type Query = ParseURLQuery<'a=1&b=2&c=3'>;
// { a: '1'; b: '2'; c: '3' }
```

---

## 七、高级组合

### 7.1 类型体操组合

```typescript
// 实现 Promise.all 类型
type PromiseAll<T extends readonly any[]> = {
  -readonly [P in keyof T]: Awaited<T[P]>;
};

const promises = [Promise.resolve(1), Promise.resolve('hello')] as const;
type Result = PromiseAll<typeof promises>; // [number, string]

// 实现类型版本的 Object.keys
type ObjectKeys<T> = keyof T & string;

// 类型过滤
type Filter<T, U> = T extends U ? T : never;

type Numbers = Filter<string | number | boolean, number>; // number
```

---

## 八、实用工具类型

### 8.1 TypeScript 内置类型

```typescript
// 内置工具类型
type Partial<T> = { [P in keyof T]?: T[P] };
type Required<T> = { [P in keyof T]-?: T[P] };
type Readonly<T> = { readonly [P in keyof T]: T[P] };
type Record<K, T> = { [P in K]: T };
type Pick<T, K extends keyof T> = { [P in K]: T[P] };
type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
type Exclude<T, U> = T extends U ? never : T;
type Extract<T, U> = T extends U ? T : never;
type NonNullable<T> = T & {};
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type Parameters<T> = T extends (...args: infer P) => any ? P : never;
type ConstructorParameters<T> = T extends new (...args: infer P) => any ? P : never;
type InstanceType<T> = T extends new (...args: any[]) => infer R ? R : never;
```

### 8.2 自定义工具类型

```typescript
// 深度 Required
type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

// 可选变为必选，必选变为可选
type InvertPartial<T> = {
  [P in keyof T]-?: T[P] extends object ? InvertPartial<T[P]> : T[P];
} & {
  [P in keyof T]?: never;
};

// 函数重载类型
type OverloadUnion<T> = T extends {
  (...args: infer A1): infer R1;
  (...args: infer A2): infer R2;
} ? ((...args: A1) => R1) | ((...args: A2) => R2) : never;
```

---

## 九、最佳实践

1. **从简单开始**：逐步构建复杂类型
2. **使用类型别名**：提高可读性
3. **注释复杂类型**：方便理解
4. **保持类型可维护**：避免过度复杂
5. **测试类型**：确保类型正确
6. **利用现有工具**：内置类型够用就好

---

## 十、总结

TypeScript 类型体操是高级开发必备技能。通过掌握条件类型、infer、模板字面量类型和递归类型，可以实现强大的类型安全保障。

希望这篇文章对你有帮助！
