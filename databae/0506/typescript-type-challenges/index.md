# TypeScript Type Challenges 类型体操完全指南

## 一、基础工具类型

```typescript
// Partial
type Partial<T> = { [P in keyof T]?: T[P] };

// Required
type Required<T> = { [P in keyof T]-?: T[P] };

// Pick
type Pick<T, K extends keyof T> = { [P in K]: T[P] };

// Omit
type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
```

## 二、条件类型

```typescript
// ReturnType
type ReturnType<T extends Function> = T extends (...args: any) => infer R ? R : never;

// Parameters
type Parameters<T extends Function> = T extends (...args: infer P) => any ? P : never;

// Awaited
type Awaited<T> = T extends Promise<infer U> ? Awaited<U> : T;
```

## 三、递归类型

```typescript
// DeepReadonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

// PromiseAll
type PromiseAll<T extends any[]> = {
  [K in keyof T]: T[K] extends Promise<infer U> ? U : T[K];
};
```

## 四、模板字面量

```typescript
// Capitalize
type Capitalize<S extends string> = S extends `${infer First}${infer Rest}` ? `${Uppercase<First>}${Rest}` : S;

// Trim
type Trim<S extends string> = S extends ` ${infer T} ${infer U}` ? Trim<U> : S extends ` ${infer U}` ? Trim<U> : S;
```

## 五、高级模式

```typescript
// Tuple to Union
type TupleToUnion<T extends any[]> = T[number];

// String to Union
type StringToUnion<T extends string> = T extends `${infer First}${infer Rest}` ? First | StringToUnion<Rest> : never;

// Union to Tuple
type UnionToTuple<T> = ...;

// Diff
type Diff<T, U> = T extends U ? never : T;
```

## 六、实战练习

```typescript
// 练习 1: MyPick
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };

// 练习 2: MyReadonly
type MyReadonly<T> = { readonly [P in keyof T]: T[P] };

// 练习 3: Length of Tuple
type Length<T extends any[]> = T['length'];
```

## 七、最佳实践

- 从简单类型开始逐步进阶
- 掌握 infer 关键字
- 利用条件类型和递归
- 理解类型系统的边界
- 实战练习 Type Challenges
- 参考优秀开源项目的类型设计
