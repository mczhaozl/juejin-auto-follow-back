# TypeScript Utility Types 完全指南：常用类型工具

> 深入讲解 TypeScript 常用工具类型，包括 Partial、Required、Pick、Omit、Record、Exclude、Extract，以及自定义工具类型实现。

## 一、基础工具类型

### 1.1 Partial<T>

将所有属性变为可选：

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

type PartialUser = Partial<User>;

const user: PartialUser = {
  name: '张三'
  // id 和 email 可选
};
```

实现：

```typescript
type Partial<T> = {
  [P in keyof T]?: T[P];
};
```

### 1.2 Required<T>

将所有属性变为必需：

```typescript
interface Config {
  host?: string;
  port?: number;
}

type RequiredConfig = Required<Config>;

const config: RequiredConfig = {
  host: 'localhost',  // 必须提供
  port: 3000         // 必须提供
};
```

实现：

```typescript
type Required<T> = {
  [P in keyof T]-?: T[P];
};
```

### 1.3 Readonly<T>

将所有属性变为只读：

```typescript
interface User {
  name: string;
}

type ReadonlyUser = Readonly<User>;

const user: ReadonlyUser = {
  name: '张三'
};
// user.name = '李四'; // 错误
```

实现：

```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};
```

## 二、构造工具类型

### 2.1 Pick<T, K>

选择指定属性：

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  password: string;
}

type UserBasicInfo = Pick<User, 'id' | 'name'>;

const user: UserBasicInfo = {
  id: 1,
  name: '张三'
  // email 和 password 不可用
};
```

实现：

```typescript
type Pick<T, K extends keyof T> = {
  [P in K]: T[P];
};
```

### 2.2 Omit<T, K>

排除指定属性：

```typescript
interface User {
  id: number;
  name: string;
  password: string;
}

type UserWithoutPassword = Omit<User, 'password'>;

const user: UserWithoutPassword = {
  id: 1,
  name: '张三'
  // password 不可用
};
```

实现：

```typescript
type Omit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>;
```

### 2.3 Record<K, T>

构造对象类型：

```typescript
type Role = 'admin' | 'user' | 'guest';

type RolePermission = Record<Role, string[]>;

const permissions: RolePermission = {
  admin: ['read', 'write', 'delete'],
  user: ['read', 'write'],
  guest: ['read']
};
```

实现：

```typescript
type Record<K extends keyof any, T> = {
  [P in K]: T;
};
```

## 三、联合类型工具

### 3.1 Exclude<T, U>

排除类型：

```typescript
type T = Exclude<'a' | 'b' | 'c', 'a'>;
// type T = 'b' | 'c'

type Num = Exclude<number | string, string>;
// type Num = number
```

实现：

```typescript
type Exclude<T, U> = T extends U ? never : T;
```

### 3.2 Extract<T, U>

提取类型：

```typescript
type T = Extract<'a' | 'b' | 'c', 'a' | 'f'>;
// type T = 'a'

type Num = Extract<number | string | boolean, number>;
// type Num = number
```

实现：

```typescript
type Extract<T, U> = T extends U ? T : never;
```

### 3.3 NonNullable<T>

排除 null 和 undefined：

```typescript
type T = NonNullable<string | null | undefined>;
// type T = string
```

实现：

```typescript
type NonNullable<T> = T extends null | undefined ? never : T;
```

## 四、参数工具类型

### 4.1 Parameters<T>

获取函数参数类型：

```typescript
function fn(a: string, b: number) {}

type Params = Parameters<fn>;
// type Params = [string, number]

const args: Params = ['hello', 42];
```

实现：

```typescript
type Parameters<T extends (...args: any) => any> = 
  T extends (...args: infer P) => any ? P : never;
```

### 4.2 ReturnType<T>

获取函数返回类型：

```typescript
function fn() { return { id: 1 }; }

type Return = ReturnType<fn>;
// type Return = { id: number }
```

实现：

```typescript
type ReturnType<T extends (...args: any) => any> = 
  T extends (...args: any) => infer R ? R : never;
```

### 4.3 InstanceType<T>

获取构造函数实例类型：

```typescript
class User {
  name: string;
}

type Instance = InstanceType<typeof User>;
// type Instance = User
```

实现：

```typescript
type InstanceType<T extends new (...args: any) => any> = 
  T extends new (...args: any) => infer R ? R : never;
```

## 五、自定义工具类型

### 5.1 DeepPartial

深度可选：

```typescript
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

interface Config {
  server: {
    host: string;
    port: number;
  };
}

type PartialConfig = DeepPartial<Config>;
// server.host 和 server.port 都可选
```

### 5.2 DeepReadonly

深度只读：

```typescript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

interface Config {
  server: {
    host: string;
  };
}

type ReadonlyConfig = DeepReadonly<Config>;
```

### 5.3 Nullable

可null类型：

```typescript
type Nullable<T> = { [P in keyof T]: T[P] | null };

interface User {
  name: string;
  email: string;
}

type NullableUser = Nullable<User>;
// { name: string | null; email: string | null }
```

## 六、总结

TypeScript Utility Types 核心要点：

1. **Partial**：可选属性
2. **Required**：必需属性
3. **Pick**：选择属性
4. **Omit**：排除属性
5. **Record**：对象映射
6. **Exclude/Extract**：联合处理
7. **Parameters/ReturnType**：函数类型

掌握这些，类型编程更高效！

---

**推荐阅读**：
- [TypeScript Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)

**如果对你有帮助，欢迎点赞收藏！**
