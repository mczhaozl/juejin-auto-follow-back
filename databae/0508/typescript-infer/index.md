# TypeScript infer 关键字完全指南

## 一、infer 基础

```typescript
// 提取函数返回类型
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// 使用
function add(a: number, b: number): number { return a + b; }
type AddReturnType = MyReturnType<typeof add>; // number
```

## 二、提取函数参数类型

```typescript
// 提取所有参数
type MyParameters<T> = T extends (...args: infer P) => any ? P : never;

type AddParams = MyParameters<typeof add>; // [number, number]

// 提取第一个参数
type FirstParam<T> = T extends (first: infer F, ...rest: any[]) => any ? F : never;
```

## 三、Promise 类型提取

```typescript
// 提取 Promise 值类型
type Awaited<T> = T extends Promise<infer U> ? U : T;

type PromiseResult = Awaited<Promise<string>>; // string

// 嵌套 Promise
type DeepAwaited<T> = T extends Promise<infer U> ? DeepAwaited<U> : T;
```

## 四、数组和元组类型提取

```typescript
// 提取数组元素类型
type ArrayElement<T> = T extends Array<infer U> ? U : never;

// 提取第一个元素
type FirstElement<T extends any[]> = T extends [infer F, ...any[]] ? F : never;
type First = FirstElement<[string, number, boolean]>; // string
```

## 五、字符串字面量推断

```typescript
// 提取前缀/后缀
type Prefix<T extends string> = T extends `${infer P}Suffix` ? P : never;
type Suffix<T extends string> = T extends `Prefix${infer S}` ? S : never;

// 分割字符串
type Split<T extends string> = T extends `${infer A} ${infer B}` ? [A, B] : never;
```

## 六、高级模式：递归 infer

```typescript
// 深度 Readonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P]
}

// 类型链式调用
type Chainable<T = {}> = {
  option<K extends string, V>(key: K, value: V): Chainable<T & { [key in K]: V }>
  get(): T
}
```

## 七、最佳实践

- 从简单的 infer 开始练习
- 使用 Type Challenges 题目练习
- 理解条件类型的执行顺序
- 注意类型兼容性
- 合理使用递归深度限制
- 与其他工具类型组合使用
