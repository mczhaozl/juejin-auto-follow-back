# TypeScript 类型级编程完全指南

## 一、类型算术

```typescript
// 类型级数字
type BuildArray<Length extends number, Ele = unknown, Arr extends Ele[] = []> =
  Arr['length'] extends Length ? Arr : BuildArray<Length, Ele, [Ele, ...Arr]>;

// 加法
type Add<A extends number, B extends number> =
  [...BuildArray<A>, ...BuildArray<B>]['length'];

// 减法
type Subtract<A extends number, B extends number> =
  BuildArray<A> extends [...infer _, ...BuildArray<B>] ? 
    BuildArray<A> extends [...infer Rest, ...BuildArray<B>] ? Rest['length'] : never : never;

// 乘法
type Multiply<A extends number, B extends number, Acc extends unknown[] = []> =
  B extends 0 ? Acc['length'] : Multiply<A, Subtract<B, 1>, [...Acc, ...BuildArray<A>]>;
```

## 二、类型级逻辑

```typescript
// If 类型
type If<C extends boolean, T, F> = C extends true ? T : F;

// And/Or/Not
type And<A extends boolean, B extends boolean> = A extends true ? B : false;
type Or<A extends boolean, B extends boolean> = A extends true ? true : B;
type Not<A extends boolean> = A extends true ? false : true;
```

## 三、类型级数据结构

```typescript
// 类型级链表
type Cons<Head, Tail extends unknown[]> = [Head, ...Tail];

// 链表操作
type Head<List extends unknown[]> = List[0];
type Tail<List extends unknown[]> = List extends [unknown, ...infer T] ? T : never;
```

## 四、实战：ParseQueryString

```typescript
type ParseQueryString<S extends string> = 
  S extends `${infer K}=${infer V}` ? { [key in K]: V } : never;

type Query = ParseQueryString<'q=hello&limit=10'>;
```

## 五、最佳实践

- 使用 Type Challenges 题库练习
- 从简单到复杂的逐步练习
- 理解类型的模式匹配机制
- 注意类型递归深度限制
- 使用 type-fest 等库
- 实际项目中避免过度使用复杂类型
