# TypeScript 高级类型体操完全指南：从基础到黑魔法

## 一、基础类型操作

### 1.1 泛型基础

```typescript
function identity<T>(arg: T): T {
  return arg;
}

interface Box<T> {
  value: T;
}

const box: Box<string> = { value: 'hello' };
```

---

## 二、条件类型

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>; // true
type B = IsString<number>; // false

type NonNullable<T> = T extends null | undefined ? never : T;

type C = NonNullable<string | null>; // string
```

---

## 三、infer 关键字

```typescript
type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : any;

function fn(): string {
  return 'hello';
}

type FnReturn = ReturnType<typeof fn>; // string

type Parameters<T extends (...args: any) => any> = T extends (...args: infer P) => any ? P : never;

type FnParams = Parameters<typeof fn>; // []
```

---

## 四、映射类型

```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

type Required<T> = {
  [P in keyof T]-?: T[P];
};

interface User {
  name: string;
  age: number;
}

type ReadonlyUser = Readonly<User>;
type PartialUser = Partial<User>;
```

---

## 五、高级映射

```typescript
type Pick<T, K extends keyof T> = {
  [P in K]: T[P];
};

type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;

type Record<K extends keyof any, T> = {
  [P in K]: T;
};

type UserName = Pick<User, 'name'>;
type UserWithoutAge = Omit<User, 'age'>;
type StringRecord = Record<string, string>;
```

---

## 六、模板字面量类型

```typescript
type EventName<T extends string> = `${T}Changed`;

type UserEvent = EventName<'user'>; // 'userChanged'

type RemoveSuffix<T extends string, S extends string> = T extends `${infer P}${S}` ? P : T;

type WithoutChanged = RemoveSuffix<'userChanged', 'Changed'>; // 'user'
```

---

## 七、递归类型

```typescript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

interface Nested {
  a: { b: number };
}

type ReadonlyNested = DeepReadonly<Nested>;
```

---

## 八、工具类型实战

```typescript
type Flatten<T> = T extends Array<infer U> ? Flatten<U> : T;

type DeepFlatten = Flatten<[1, [2, [3]]]>; // 3

type TupleToUnion<T extends any[]> = T[number];

type Tuple = [1, 'a', true];
type Union = TupleToUnion<Tuple>; // 1 | 'a' | true

type PromiseType<T> = T extends Promise<infer U> ? PromiseType<U> : T;

type Unpacked = PromiseType<Promise<Promise<string>>>; // string
```

---

## 九、实战示例

### 9.1 Event Emitter 类型

```typescript
interface Events {
  click: (x: number, y: number) => void;
  focus: () => void;
}

class Emitter<E extends Record<string, (...args: any) => void>> {
  on<K extends keyof E>(event: K, listener: E[K]) {}
  emit<K extends keyof E>(event: K, ...args: Parameters<E[K]>) {}
}

const emitter = new Emitter<Events>();
emitter.on('click', (x, y) => console.log(x, y));
```

### 9.2 路由参数提取

```typescript
type ExtractParams<T extends string> = T extends `${infer _Prefix}:${infer Param}/${infer Rest}`
  ? Param | ExtractParams<Rest>
  : T extends `${infer _Prefix}:${infer Param}`
  ? Param
  : never;

type Route = '/user/:id/post/:postId';
type RouteParams = ExtractParams<Route>; // 'id' | 'postId'
```

---

## 十、挑战与练习

```typescript
// 实现一个 Reverse 类型，反转元组
type Reverse<T extends any[]> = T extends [infer First, ...infer Rest]
  ? [...Reverse<Rest>, First]
  : [];

type Reversed = Reverse<[1, 2, 3]>; // [3, 2, 1]

// 实现一个 Join 类型
type Join<T extends any[], D extends string = ','> = T extends [infer First, ...infer Rest]
  ? Rest extends []
    ? First extends string ? First : never
    : First extends string
    ? `${First}${D}${Join<Rest, D>}`
    : never
  : '';

type Joined = Join<['a', 'b', 'c']>; // 'a,b,c'
```

---

## 十一、最佳实践

1. 避免过度复杂的类型
2. 使用工具类型简化代码
3. 为复杂类型写注释
4. 保持类型安全的同时追求灵活性
5. 学会使用 infer

---

## 十二、总结

TypeScript 的类型系统强大而有趣，掌握高级类型能编写出更安全、更优雅的代码。
