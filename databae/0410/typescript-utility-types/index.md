# TypeScript 工具类型完全指南：Partial、Required、Pick、Omit 等

> 深入讲解 TypeScript 内置工具类型，包括 Partial、Required、Pick、Omit、Record 等，让你的类型编程更高效。

## 一、Partial 和 Required

### 1.1 Partial<T>

将所有属性变为可选：

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

type PartialUser = Partial<User>;
// 等价于
// { id?: number; name?: string; email?: string; }
```

### 1.2 Required<T>

将所有属性变为必需：

```typescript
type RequiredUser = Required<PartialUser>;
// 所有属性重新变为必需
```

## 二、Pick 和 Omit

### 2.1 Pick<T, K>

选择属性：

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  password: string;
}

type UserPreview = Pick<User, 'id' | 'name'>;
// { id: number; name: string; }
```

### 2.2 Omit<T, K>

排除属性：

```typescript
type UserWithoutPassword = Omit<User, 'password'>;
// { id: number; name: string; email: string; }
```

## 三、Record 和 Map

### 3.1 Record<K, T>

构造对象类型：

```typescript
type Role = 'admin' | 'user' | 'guest';

type Permissions = Record<Role, string[]>;

// { admin: string[]; user: string[]; guest: string[]; }
```

### 3.2 使用场景

```typescript
type UserMap = Record<number, User>;
const users: UserMap = {
  1: { id: 1, name: '张三' },
  2: { id: 2, name: '李四' },
};
```

## 四、Extract 和 Exclude

### 4.1 Extract<T, U>

提取类型：

```typescript
type T = Extract<'a' | 'b' | 'c', 'a' | 'f'>;
// 'a'
```

### 4.2 Exclude<T, U>

排除类型：

```typescript
type T = Exclude<'a' | 'b' | 'c', 'a'>;
// 'b' | 'c'
```

## 五、ReturnType 和 Parameters

### 5.1 ReturnType<T>

获取函数返回类型：

```typescript
function getUser() {
  return { id: 1, name: '张三' };
}

type User = ReturnType<typeof getUser>;
// { id: number; name: string; }
```

### 5.2 Parameters<T>

获取函数参数类型：

```typescript
function createUser(name: string, age: number) {}

type Params = Parameters<typeof createUser>;
// [string, number]
```

## 六、自定义工具类型

### 6.1 DeepPartial

```typescript
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

interface User {
  id: number;
  profile: { name: string; age: number };
}

type PartialUser = DeepPartial<User>;
// { id?: number; profile?: { name?: string; age?: number }; }
```

### 6.2 DeepReadonly

```typescript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};
```

## 七、总结

常用工具类型：

1. **Partial**：所有属性可选
2. **Required**：所有属性必需
3. **Pick**：选择属性
4. **Omit**：排除属性
5. **Record**：构造对象
6. **Extract/Exclude**：联合类型操作
7. **ReturnType/Parameters**：函数类型提取

掌握这些，类型编程更高效！

---

**推荐阅读**：
- [TypeScript Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)

**如果对你有帮助，欢迎点赞收藏！**
