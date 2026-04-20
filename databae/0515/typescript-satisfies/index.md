# TypeScript satisfies 完全指南

## 一、基础使用

```typescript
type Config = {
  host: string;
  port: number;
};

const config = {
  host: "localhost",
  port: 3000,
} satisfies Config;
```

## 二、与 as 对比

```typescript
// as 类型断言
const config = {
  host: "localhost",
  port: 3000,
  extra: "value"
} as Config;

// satisfies
const config2 = {
  host: "localhost",
  port: 3000,
  extra: "value"
} satisfies Config;

// config2.extra 仍然有类型!
```

## 三、联合类型

```typescript
type Shape = 
  | { type: 'circle'; radius: number } 
  | { type: 'square'; side: number };

const shape = {
  type: 'circle',
  radius: 5
} satisfies Shape;

// shape 精确类型推导
```

## 四、对象字面量

```typescript
const obj = {
  a: 1,
  b: 2,
  c: 'three'
} satisfies Record<string, number | string>;
```

## 最佳实践
- satisfies 保留类型精确性
- 在配置对象场景非常有用
- 替代 as 保持类型安全
- 与泛型结合
