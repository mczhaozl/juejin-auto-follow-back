# TypeScript 抽象类型完全指南

## 一、多态类型

```typescript
// 泛型函数
function identity<T>(arg: T): T {
  return arg;
}

// 泛型接口
interface Box<T> {
  value: T;
}

// 有界泛型
interface Lengthwise {
  length: number;
}

function longest<T extends Lengthwise>(a: T, b: T) {
  return a.length > b.length ? a : b;
}
```

## 二、条件类型

```typescript
// 条件类型
type IsString<T> = T extends string ? true : false;
type A = IsString<string>; // true
type B = IsString<number>; // false

// infer 条件类型
type ReturnType<T> = T extends (...args: any) => infer R ? R : never;
```

## 三、映射类型

```typescript
// 只读
type Readonly<T> = { readonly [K in keyof T]: T[K] };

// 可选
type Partial<T> = { [K in keyof T]?: T[K] };

// 过滤属性
type Pick<T, K extends keyof T> = { [P in K]: T[P] };

// 过滤键
type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
```

## 四、类型推断

```typescript
// 自动推断
const arr = [1, "hello"]; // (string | number)[]

// 上下文类型
const obj = { name: "Alice", age: 30 }; // { name: string; age: number }

// 函数类型推断
const add = (a: number, b: number) => a + b; // (a: number, b: number) => number
```

## 五、最佳实践

- 使用泛型提供类型安全的 API
- 使用条件类型和 infer 构建工具类型
- 使用映射类型转换类型结构
- 合理使用类型断言
- 避免 any 代替 unknown
