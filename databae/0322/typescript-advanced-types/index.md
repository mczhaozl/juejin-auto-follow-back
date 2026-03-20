# TypeScript高级类型编程：从入门到精通

> 深入解析TypeScript高级类型系统，从条件类型、映射类型到条件类型，掌握TypeScript类型编程的核心技巧。

---

## 一、基础类型回顾

### 1.1 基本类型

```typescript
// 基本类型
type Primitive = 
  | string      // 字符串
  | number      // 数字
  | boolean     // 布尔值
  | null        // null
  | undefined   // undefined
  | symbol      // 符号
  | bigint;     // 大整数

// 字面量类型
type Status = 'success' | 'error' | 'pending';
type StatusCode = 200 | 404 | 500;
type Flag = true | false;

// 数组和元组
type NumberArray = number[];
type StringArray = Array<string>;
type Tuple = [string, number, boolean];

// 对象类型
type User = {
  id: number;
  name: string;
  email: string;
  age?: number;  // 可选属性
  readonly createdAt: Date;  // 只读属性
};
```

### 1.2 联合类型与交叉类型

```typescript
// 联合类型
type ID = string | number;
type Result<T> = { success: true; data: T } | { success: false; error: string };

// 交叉类型
type Person = {
  name: string;
  age: number;
};

type Employee = {
  id: number;
  department: string;
};

type Staff = Person & Employee;
// 等价于 { name: string; age: number; id: number; department: string; }

// 条件类型
type IsString<T> = T extends string ? true : false;
type Test1 = IsString<'hello'>;  // true
type Test2 = IsString<123>;      // false
```

## 二、条件类型

### 2.1 基础条件类型

```typescript
// 条件类型基础
type TypeName<T> = 
  T extends string ? 'string' :
  T extends number ? 'number' :
  T extends boolean ? 'boolean' :
  T extends undefined ? 'undefined' :
  T extends Function ? 'function' :
  'object';

type T0 = TypeName<string>;      // 'string'
type T1 = TypeName<number>;      // 'number'
type T2 = TypeName<() => void>;  // 'function'

// 分布式条件类型
type ToArray<T> = T extends any ? T[] : never;
type StrArrOrNumArr = ToArray<string | number>;  // string[] | number[]

// 过滤类型
type Filter<T, U> = T extends U ? T : never;
type Filtered = Filter<string | number | boolean, string | number>;  // string | number
```

### 2.2 infer关键字

```typescript
// 使用infer提取类型
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

function getUser() {
  return { id: 1, name: 'Alice' };
}

type UserReturn = ReturnType<typeof getUser>;  // { id: number; name: string }

// 提取数组元素类型
type ElementType<T> = T extends (infer U)[] ? U : never;
type StrElement = ElementType<string[]>;  // string

// 提取Promise类型
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type StringPromise = UnwrapPromise<Promise<string>>;  // string

// 提取函数参数类型
type Parameters<T> = T extends (...args: infer P) => any ? P : never;
type FuncParams = Parameters<(x: number, y: string) => void>;  // [number, string]
```

## 三、映射类型

### 3.1 基础映射类型

```typescript
// 只读映射
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

// 可选映射
type Partial<T> = {
  [P in keyof T]?: T[P];
};

// 必需映射
type Required<T> = {
  [P in keyof T]-?: T[P];
};

// 移除只读
type Mutable<T> = {
  -readonly [P in keyof T]: T[P];
};

// 使用示例
interface User {
  readonly id: number;
  name?: string;
  age: number;
}

type ReadonlyUser = Readonly<User>;
// { readonly id: number; readonly name?: string; readonly age: number; }

type PartialUser = Partial<User>;
// { readonly id?: number; name?: string; age?: number; }

type RequiredUser = Required<User>;
// { readonly id: number; name: string; age: number; }
```

### 3.2 高级映射类型

```typescript
// 键重映射
type Getters<T> = {
  [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P];
};

interface Person {
  name: string;
  age: number;
  location: string;
}

type PersonGetters = Getters<Person>;
// {
//   getName: () => string;
//   getAge: () => number;
//   getLocation: () => string;
// }

// 过滤键
type PickByType<T, U> = {
  [P in keyof T as T[P] extends U ? P : never]: T[P];
};

interface Mixed {
  id: number;
  name: string;
  age: number;
  email: string;
}

type NumberProps = PickByType<Mixed, number>;  // { id: number; age: number; }
type StringProps = PickByType<Mixed, string>;  // { name: string; email: string; }

// 条件键重映射
type EventHandlers<T> = {
  [P in keyof T as `on${Capitalize<string & P>}Change`]: (value: T[P]) => void;
};

interface FormData {
  username: string;
  email: string;
  age: number;
}

type FormHandlers = EventHandlers<FormData>;
// {
//   onUsernameChange: (value: string) => void;
//   onEmailChange: (value: string) => void;
//   onAgeChange: (value: number) => void;
// }
```

## 四、模板字面量类型

### 4.1 基础模板类型

```typescript
// 模板字面量类型
type World = 'world';
type Greeting = `hello ${World}`;  // "hello world"

// 联合类型模板
type Color = 'red' | 'green' | 'blue';
type Size = 'small' | 'medium' | 'large';

type ButtonClass = `${Color}-${Size}`;
// "red-small" | "red-medium" | "red-large" | 
// "green-small" | "green-medium" | "green-large" | 
// "blue-small" | "blue-medium" | "blue-large"

// 实用工具类型
type EventName = 'click' | 'scroll' | 'mousemove';
type EventHandlerName = `on${Capitalize<EventName>}`;
// "onClick" | "onScroll" | "onMousemove"

// 字符串操作类型
type Getter<T extends string> = `get${Capitalize<T>}`;
type Setter<T extends string> = `set${Capitalize<T>}`;

type NameGetter = Getter<'name'>;  // "getName"
type AgeSetter = Setter<'age'>;    // "setAge"
```

### 4.2 高级模板类型

```typescript
// 字符串解析
type Split<S extends string, D extends string> = 
  S extends `${infer T}${D}${infer U}` ? [T, ...Split<U, D>] : [S];

type PathParts = Split<'user/profile/settings', '/'>;  // ["user", "profile", "settings"]

// 字符串替换
type Replace<S extends string, From extends string, To extends string> = 
  S extends `${infer Prefix}${From}${infer Suffix}` 
    ? `${Prefix}${To}${Suffix}` 
    : S;

type NewPath = Replace<'user/id/profile', 'id', ':id'>;  // "user/:id/profile"

// 字符串包含
type Includes<S extends string, Search extends string> = 
  S extends `${string}${Search}${string}` ? true : false;

type HasHello = Includes<'hello world', 'hello'>;  // true
type HasGoodbye = Includes<'hello world', 'goodbye'>;  // false

// 字符串截取
type Substring<S extends string, Start extends number, End extends number> = 
  S extends `${infer Prefix}${infer Rest}` 
    ? Start extends 0 
      ? End extends 0 
        ? '' 
        : `${Prefix}${Substring<Rest, 0, End-1>}`
      : Substring<Rest, Start-1, End-1>
    : '';

type Hello = Substring<'hello world', 0, 5>;  // "hello"
```

## 五、递归类型

### 5.1 递归类型定义

```typescript
// 链表类型
type ListNode<T> = {
  value: T;
  next: ListNode<T> | null;
};

// 二叉树类型
type BinaryTree<T> = {
  value: T;
  left: BinaryTree<T> | null;
  right: BinaryTree<T> | null;
};

// JSON类型
type JSONValue = 
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue };

// 深度只读
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object 
    ? DeepReadonly<T[P]> 
    : T[P];
};

interface NestedObject {
  a: {
    b: {
      c: number;
      d: string[];
    };
    e: boolean;
  };
  f: number;
}

type ReadonlyNested = DeepReadonly<NestedObject>;
// {
//   readonly a: {
//     readonly b: {
//       readonly c: number;
//       readonly d: readonly string[];
//     };
//     readonly e: boolean;
//   };
//   readonly f: number;
// }
```

### 5.2 递归类型操作

```typescript
// 深度可选
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// 深度必需
type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

// 深度Pick
type DeepPick<T, K extends string> = 
  K extends `${infer First}.${infer Rest}`
    ? First extends keyof T
      ? { [P in First]: DeepPick<T[First], Rest> }
      : never
    : K extends keyof T
      ? { [P in K]: T[K] }
      : never;

interface UserProfile {
  user: {
    name: string;
    address: {
      city: string;
      country: string;
    };
  };
  settings: {
    theme: string;
    notifications: boolean;
  };
}

type UserCity = DeepPick<UserProfile, 'user.address.city'>;
// { user: { address: { city: string } } }
```

## 六、类型守卫与类型断言

### 6.1 自定义类型守卫

```typescript
// 类型守卫函数
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number';
}

function isArray<T>(value: unknown): value is T[] {
  return Array.isArray(value);
}

// 联合类型守卫
type Animal = Dog | Cat | Bird;

interface Dog {
  type: 'dog';
  bark(): void;
}

interface Cat {
  type: 'cat';
  meow(): void;
}

interface Bird {
  type: 'bird';
  chirp(): void;
}

function isDog(animal: Animal): animal is Dog {
  return animal.type === 'dog';
}

function isCat(animal: Animal): animal is Cat {
  return animal.type === 'cat';
}

function handleAnimal(animal: Animal) {
  if (isDog(animal)) {
    animal.bark();  // 类型安全
  } else if (isCat(animal)) {
    animal.meow();  // 类型安全
  } else {
    animal.chirp(); // 类型安全
  }
}
```

### 6.2 类型断言与类型收缩

```typescript
// 类型断言
const value: unknown = 'hello world';

// 使用as语法
const str1 = value as string;

// 使用尖括号语法（不推荐在JSX中使用）
const str2 = <string>value;

// 非空断言
interface Container {
  value?: string;
}

function getValue(container: Container): string {
  return container.value!;  // 非空断言
}

// 双重断言
const unknownValue: unknown = 'hello';

// 先断言为any，再断言为目标类型
const strValue = unknownValue as any as string;

// 类型收缩
function processValue(value: string | number) {
  if (typeof value === 'string') {
    // 这里value被收缩为string
    console.log(value.toUpperCase());
  } else {
    // 这里value被收缩为number
    console.log(value.toFixed(2));
  }
}

// 使用in操作符
interface Admin {
  admin: true;
  permissions: string[];
}

interface User {
  admin: false;
  name: string;
}

function checkAdmin(person: Admin | User) {
  if ('permissions' in person) {
    // person被收缩为Admin
    console.log(person.permissions);
  } else {
    // person被收缩为User
    console.log(person.name);
  }
}
```

## 七、实用工具类型

### 7.1 内置工具类型

```typescript
// Record - 创建对象类型
type UserRecord = Record<string, { name: string; age: number }>;
// { [key: string]: { name: string; age: number } }

// Pick - 选择属性
interface Todo {
  title: string;
  description: string;
  completed: boolean;
}

type TodoPreview = Pick<Todo, 'title' | 'completed'>;
// { title: string; completed: boolean }

// Omit - 排除属性
type TodoInfo = Omit<Todo, 'completed' | 'description'>;
// { title: string }

// Exclude - 排除类型
type T0 = Exclude<'a' | 'b' | 'c', 'a'>;  // "b" | "c"
type T1 = Exclude<string | number | (() => void), Function>;  // string | number

// Extract - 提取类型
type T2 = Extract<'a' | 'b' | 'c', 'a' | 'f'>;  // "a"
type T3 = Extract<string | number | (() => void), Function>;  // () => void

// NonNullable - 排除null和undefined
type T4 = NonNullable<string | number | null | undefined>;  // string | number

// Parameters - 获取函数参数类型
type T5 = Parameters<(s: string) => void>;  // [string]

// ConstructorParameters - 获取构造函数参数类型
type T6 = ConstructorParameters<ErrorConstructor>;  // [string?]

// ReturnType - 获取函数返回类型
type T7 = ReturnType<() => string>;  // string

// InstanceType - 获取实例类型
type T8 = InstanceType<ErrorConstructor>;  // Error
```

### 7.2 自定义工具类型

```typescript
// 获取对象值的类型
type ValueOf<T> = T[keyof T];

interface User {
  id: number;
  name: string;
  email: string;
}

type UserValues = ValueOf<User>;  // number | string

// 获取对象键的类型
type KeysOfType<T, U> = {
  [K in keyof T]: T[K] extends U ? K : never;
}[keyof T];

type StringKeys = KeysOfType<User, string>;  // "name" | "email"
type NumberKeys = KeysOfType<User, number>;  // "id"

// 深度合并类型
type DeepMerge<T, U> = {
  [K in keyof T | keyof U]: 
    K extends keyof U
      ? U[K]
      : K extends keyof T
        ? T[K]
        : never;
};

interface Base {
  a: number;
  b: string;
}

interface Extension {
  b: number;  // 覆盖string
  c: boolean;
}

type Merged = DeepMerge<Base, Extension>;
// { a: number; b: number; c: boolean }

// 条件类型工具
type If<Condition extends boolean, Then, Else> = 
  Condition extends true ? Then : Else;

type Result1 = If<true, string, number>;  // string
type Result2 = If<false, string, number>; // number
```

## 八、类型编程实战

### 8.1 API响应类型

```typescript
// API响应类型
type ApiResponse<T = any> = 
  | { success: true; data: T; timestamp: Date }
  | { success: false; error: string; code: number; timestamp: Date };

// 分页响应
type PaginatedResponse<T> = {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
};

// 条件API响应
type ConditionalResponse<T, U extends boolean> = 
  U extends true 
    ? PaginatedResponse<T> 
    : T[];

// 使用示例
type UserResponse = ApiResponse<{ id: number; name: string }>;
type UsersResponse = ConditionalResponse<{ id: number; name: string }, true>;
```

### 8.2 表单验证类型

```typescript
// 表单字段状态
type FieldState<T> = {
  value: T;
  error?: string;
  touched: boolean;
  dirty: boolean;
};

// 表单验证规则
type ValidationRule<T> = {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  validate?: (value: T) => string | undefined;
};

// 表单配置
type FormConfig<T extends Record<string, any>> = {
  [K in keyof T]: {
    initialValue: T[K];
    rules?: ValidationRule<T[K]>;
  };
};

// 表单状态
type FormState<T extends Record<string, any>> = {
  [K in keyof T]: FieldState<T[K]>;
} & {
  isValid: boolean;
  isSubmitting: boolean;
  errors: Record<string, string>;
};

// 使用示例
interface LoginForm {
  username: string;
  password: string;
  rememberMe: boolean;
}

const loginConfig: FormConfig<LoginForm> = {
  username: {
    initialValue: '',
    rules: {
      required: true,
      minLength: 3,
      maxLength: 20
    }
  },
  password: {
    initialValue: '',
    rules: {
      required: true,
      minLength: 6
    }
  },
  rememberMe: {
    initialValue: false
  }
};
```

## 九、总结与最佳实践

### 9.1 类型编程最佳实践

1. **保持类型简单**：避免过度复杂的类型
2. **使用工具类型**：充分利用内置和自定义工具类型
3. **类型安全优先**：确保类型系统的安全性
4. **文档化复杂类型**：为复杂类型添加注释
5. **渐进式类型**：从简单类型开始，逐步增加复杂度

### 9.2 性能考虑

```typescript
// 避免深度递归
// 不推荐：深度递归可能导致性能问题
type DeepRecursive<T> = {
  [K in keyof T]: T[K] extends object ? DeepRecursive<T[K]> : T[K];
};

// 推荐：限制递归深度
type Shallow<T> = {
  [K in keyof T]: T[K];
};

// 使用条件类型优化
type Optimized<T> = T extends object ? Shallow<T> : T;
```

### 9.3 类型测试

```typescript
// 类型测试工具
type Expect<T extends true> = T;
type Equal<X, Y> = 
  (<T>() => T extends X ? 1 : 2) extends
  (<T>() => T extends Y ? 1 : 2) ? true : false;

// 测试用例
type Test1 = Expect<Equal<string, string>>;  // true
type Test2 = Expect<Equal<string, number>>;  // 类型错误

// 类型断言测试
type Assert<T, U> = T extends U ? true : false;

type Test3 = Assert<string, string>;  // true
type Test4 = Assert<string, number>;  // false
```

通过掌握这些高级类型编程技巧，你可以：

1. 编写更类型安全的代码
2. 提高开发效率
3. 减少运行时错误
4. 提供更好的开发体验
5. 构建更健壮的应用架构

TypeScript的类型系统是一个强大的工具，合理使用可以显著提升代码质量和开发效率。