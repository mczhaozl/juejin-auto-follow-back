# TypeScript 进阶指南：类型系统深入与高级类型

> 深入讲解 TypeScript 高级类型，包括联合类型、交叉类型、类型守卫、映射类型、条件类型等全面提升类型能力。

## 一、联合类型和交叉类型

### 1.1 联合类型

```typescript
type StringOrNumber = string | number;

function print(value: StringOrNumber) {
  if (typeof value === 'string') {
    console.log(value.toUpperCase());
  } else {
    console.log(value.toFixed(2));
  }
}
```

### 1.2 交叉类型

```typescript
interface A {
  a: string;
}

interface B {
  b: number;
}

type C = A & B;

const c: C = {
  a: 'hello',
  b: 123
};
```

## 二、类型守卫

### 2.1 typeof

```typescript
function process(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
  return value.toFixed(2);
}
```

### 2.2 instanceof

```typescript
class Dog {
  bark() { console.log('wang'); }
}

class Cat {
  meow() { console.log('miao'); }
}

function makeSound(animal: Dog | Cat) {
  if (animal instanceof Dog) {
    animal.bark();
  } else {
    animal.meow();
  }
}
```

### 2.3 in

```typescript
interface Fish { swim: () => void }
interface Bird { fly: () => void }

function move(animal: Fish | Bird) {
  if ('swim' in animal) {
    animal.swim();
  } else {
    animal.fly();
  }
}
```

### 2.4 自定义守卫

```typescript
interface Fish { swim: () => void }
interface Bird { fly: () => void }

function isFish(animal: Fish | Bird): animal is Fish {
  return (animal as Fish).swim !== undefined;
}

function move(animal: Fish | Bird) {
  if (isFish(animal)) {
    animal.swim();
  } else {
    animal.fly();
  }
}
```

## 三、映射类型

### 3.1 基本映射

```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

interface User {
  name: string;
  age: number;
}

type ReadonlyUser = Readonly<User>;
type PartialUser = Partial<User>;
```

### 3.2 带修饰符

```typescript
type Optional<T> = {
  [P in keyof T]?: T[P];
};

type Required<T> = {
  [P in keyof T]-?: T[P];
};

type Nullable<T> = {
  [P in keyof T]: T[P] | null;
};
```

## 四、条件类型

### 4.1 基本语法

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false
```

### 4.2 提取和排除

```typescript
type Extract<T, U> = T extends U ? T : never;

type Exclude<T, U> = T extends U ? never : type;

type T = Extract<string | number, string>;  // string
type E = Exclude<string | number, string>;  // number
```

### 4.3 实战应用

```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

type Parameters<T> = T extends (...args: infer P) => any ? P : never;

type F = (name: string, age: number) => void;
type R = ReturnType<F>;  // void
type P = Parameters<F>;  // [string, number]
```

## 五、模板字面量类型

### 5.1 基本用法

```typescript
type EventName = `on${string}`;

const name: EventName = 'onClick';  // OK
const name2: EventName = 'click';    // Error
```

### 5.2 模板组合

```typescript
type Prefix = 'get' | 'set';
type Property = 'User' | 'Post';

type Method = `${Prefix}${Property}`;
// 'getUser' | 'setUser' | 'getPost' | 'setPost'
```

## 六、类型推断

### 6.1 infer

```typescript
type ArrayElement<T> = T extends (infer E)[] ? E : never;

type E = ArrayElement<string[]>;  // string
type E2 = ArrayElement<number[]>; // number
```

### 6.2 递归类型

```typescript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

interface User {
  name: string;
  profile: { age: number };
}

type ReadonlyUser = DeepReadonly<User>;
```

## 七、实战案例

### 7.1 API 类型

```typescript
type APIMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

type Endpoint = `/${string}`;

type APIEndpoint = {
  [method in APIMethod]: (endpoint: Endpoint) => Promise<any>;
};

const api: APIEndpoint = {
  GET: (endpoint) => fetch(endpoint).then(r => r.json()),
  POST: (endpoint) => fetch(endpoint, { method: 'POST' }).then(r => r.json()),
  PUT: (endpoint) => fetch(endpoint, { method: 'PUT' }).then(r => r.json()),
  DELETE: (endpoint) => fetch(endpoint, { method: 'DELETE' }).then(r => r.json())
};
```

### 7.2 表单验证

```typescript
type ValidationRule<T> = {
  [P in keyof T]?: ((value: T[P]) => boolean) | string;
};

interface FormData {
  name: string;
  email: string;
  age: number;
}

const rules: ValidationRule<FormData> = {
  name: (value) => value.length > 0,
  email: (value) => /@/.test(value),
  age: (value) => value >= 18
};
```

## 八、总结

TypeScript 进阶核心要点：

1. **联合类型**：或的关系
2. **交叉类型**：和的关系
3. **类型守卫**：类型收窄
4. **映射类型**：批量生成属性
5. **条件类型**：根据条件生成类型
6. **模板字面量**：字符串字面量联合
7. **类型推断**：infer 关键字

掌握这些，TypeScript 类型编程更精通！

---

**推荐阅读**：
- [TypeScript 高级类型](https://www.typescriptlang.org/docs/handbook/2/types-from-types.html)

**如果对你有帮助，欢迎点赞收藏！**
