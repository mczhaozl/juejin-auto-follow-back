# TypeScript 高级泛型完全指南

## 一、泛型基础回顾

```typescript
function identity<T>(arg: T): T {
  return arg;
}

identity<string>('hello');
identity(123);
```

## 二、条件类型

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false
```

## 三、映射类型

```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

type Pick<T, K extends keyof T> = {
  [P in K]: T[P];
};
```

## 四、infer 关键字

```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

type GetArrayItem<T> = T extends Array<infer U> ? U : never;
```

## 五、递归条件类型

```typescript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object 
    ? DeepReadonly<T[P]> 
    : T[P];
};
```

## 六、模板字面量类型

```typescript
type EventName<T extends string> = `on${Capitalize<T>}Event`;

type ClickEvent = EventName<'click'>;  // 'onClickEvent'
```

## 七、实战示例

```typescript
// API 响应类型
type ApiResponse<T> = {
  data: T;
  success: boolean;
  error?: string;
};

// 安全访问嵌套属性
type DeepGet<T, K extends string> = K extends `${infer First}.${infer Rest}`
  ? First extends keyof T
    ? DeepGet<T[First], Rest>
    : never
  : K extends keyof T
  ? T[K]
  : never;
```

## 八、最佳实践

- 合理使用泛型避免过度复杂
- 利用内置工具类型
- 提供良好的类型推断
- 测试类型边界
