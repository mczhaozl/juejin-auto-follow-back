# TypeScript 类型谓词完全指南

## 一、基础类型谓词

```typescript
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number';
}

// 使用
function process(value: unknown) {
  if (isString(value)) {
    console.log(value.toUpperCase()); // TypeScript 知道是 string
  }
}
```

## 二、对象类型判断

```typescript
interface Cat { meow(): void; }
interface Dog { bark(): void; }

function isCat(animal: unknown): animal is Cat {
  return typeof animal === 'object' && animal !== null && 'meow' in animal;
}

function isDog(animal: unknown): animal is Dog {
  return typeof animal === 'object' && animal !== null && 'bark' in animal;
}

// 使用
function speak(animal: unknown) {
  if (isCat(animal)) {
    animal.meow();
  } else if (isDog(animal)) {
    animal.bark();
  }
}
```

## 三、数组类型判断

```typescript
function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(isString);
}

function isNumberArray(value: unknown): value is number[] {
  return Array.isArray(value) && value.every(isNumber);
}

// 类型守卫 + 数组方法
function filterStrings(arr: unknown[]): string[] {
  return arr.filter(isString);
}
```

## 四、类型谓词工具

```typescript
// 1. 属性存在检查
function hasProperty<K extends string>(
  obj: unknown,
  property: K
): obj is { [P in K]: unknown } {
  return typeof obj === 'object' && obj !== null && property in obj;
}

// 2. 联合类型守卫
type Result<T> = { type: 'success'; data: T } | { type: 'error'; message: string };

function isSuccess<T>(result: Result<T>): result is { type: 'success'; data: T } {
  return result.type === 'success';
}
```

## 最佳实践
- 使用类型谓词替代 any 转换
- 类型谓词配合条件语句
- 组合多个类型守卫
- 使用 is/asserts 关键字
