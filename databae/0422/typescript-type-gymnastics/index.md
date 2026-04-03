# TypeScript 类型体操完全指南：从基础到高级技巧

TypeScript 的类型系统非常强大，掌握类型体操可以让你写出更安全、更优雅的代码。本文将带你从基础到高级，全面掌握 TypeScript 类型体操。

## 一、基础类型工具

### 1. Partial - 所有属性可选

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

type PartialUser = Partial<User>;
// { id?: number; name?: string; email?: string }

function updateUser(user: User, updates: PartialUser): User {
  return { ...user, ...updates };
}
```

### 2. Required - 所有属性必需

```typescript
interface OptionalUser {
  id?: number;
  name?: string;
}

type RequiredUser = Required<OptionalUser>;
// { id: number; name: string }
```

### 3. Readonly - 所有属性只读

```typescript
type ReadonlyUser = Readonly<User>;
// { readonly id: number; readonly name: string; readonly email: string }

const user: ReadonlyUser = { id: 1, name: 'Alice', email: 'alice@example.com' };
// user.id = 2; // 错误！
```

### 4. Pick - 选取部分属性

```typescript
type UserName = Pick<User, 'name' | 'email'>;
// { name: string; email: string }
```

### 5. Omit - 排除部分属性

```typescript
type UserWithoutEmail = Omit<User, 'email'>;
// { id: number; name: string }
```

### 6. Record - 构造对象类型

```typescript
type UserMap = Record<number, User>;
// { [key: number]: User }

const users: UserMap = {
  1: { id: 1, name: 'Alice', email: 'alice@example.com' },
  2: { id: 2, name: 'Bob', email: 'bob@example.com' },
};
```

### 7. Exclude - 从联合类型中排除

```typescript
type T = Exclude<'a' | 'b' | 'c', 'a'>;
// 'b' | 'c'

type Status = 'pending' | 'approved' | 'rejected';
type ActiveStatus = Exclude<Status, 'rejected'>;
// 'pending' | 'approved'
```

### 8. Extract - 从联合类型中提取

```typescript
type T = Extract<'a' | 'b' | 'c', 'a' | 'b'>;
// 'a' | 'b'
```

### 9. NonNullable - 排除 null 和 undefined

```typescript
type T = NonNullable<string | number | null | undefined>;
// string | number
```

### 10. ReturnType - 获取函数返回类型

```typescript
function getUser(): User {
  return { id: 1, name: 'Alice', email: 'alice@example.com' };
}

type UserReturnType = ReturnType<typeof getUser>;
// User
```

### 11. Parameters - 获取函数参数类型

```typescript
function createUser(name: string, email: string): User {
  return { id: 1, name, email };
}

type CreateUserParams = Parameters<typeof createUser>;
// [name: string, email: string]
```

## 二、条件类型

### 1. 基础条件类型

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>; // true
type B = IsString<number>; // false
```

### 2. 分布条件类型

```typescript
type ToArray<T> = T extends any ? T[] : never;

type StringOrNumberArray = ToArray<string | number>;
// string[] | number[]
```

### 3. infer 关键字

```typescript
type GetReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

function foo(): string {
  return 'hello';
}

type FooReturn = GetReturnType<typeof foo>; // string
```

## 三、映射类型

### 1. 基础映射类型

```typescript
type MyPartial<T> = {
  [K in keyof T]?: T[K];
};

type MyReadonly<T> = {
  readonly [K in keyof T]: T[K];
};
```

### 2. 重新映射键

```typescript
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<User>;
// {
//   getId: () => number;
//   getName: () => string;
//   getEmail: () => string;
// }
```

### 3. 过滤键

```typescript
type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};

type StringKeys = PickByType<User, string>;
// { name: string; email: string }
```

## 四、模板字面量类型

### 1. 基础用法

```typescript
type EventName = 'click' | 'focus' | 'blur';
type HandlerName = `on${Capitalize<EventName>}`;
// 'onClick' | 'onFocus' | 'onBlur'
```

### 2. 字符串拼接

```typescript
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type Path = '/users' | '/posts' | '/comments';
type ApiEndpoint = `${HttpMethod} ${Path}`;
// 'GET /users' | 'GET /posts' | ... | 'DELETE /comments'
```

### 3. 实现路由类型

```typescript
type RouteParams<T extends string> =
  T extends `${infer _Start}:${infer Param}/${infer Rest}`
    ? Param | RouteParams<Rest>
    : T extends `${infer _Start}:${infer Param}`
    ? Param
    : never;

type UserRouteParams = RouteParams<'/users/:id/posts/:postId'>;
// 'id' | 'postId'
```

## 五、递归类型

### 1. 深度 Partial

```typescript
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object
    ? DeepPartial<T[K]>
    : T[K];
};

interface NestedUser {
  id: number;
  name: string;
  address: {
    street: string;
    city: string;
    country: string;
  };
}

type DeepPartialUser = DeepPartial<NestedUser>;
// {
//   id?: number;
//   name?: string;
//   address?: {
//     street?: string;
//     city?: string;
//     country?: string;
//   };
// }
```

### 2. Promise 展开

```typescript
type Awaited<T> = T extends Promise<infer U> ? Awaited<U> : T;

type NestedPromise = Promise<Promise<Promise<string>>>;
type Unwrapped = Awaited<NestedPromise>; // string
```

## 六、实战案例

### 1. 类型安全的 Event Emitter

```typescript
type EventMap = {
  click: { x: number; y: number };
  focus: undefined;
  submit: { data: Record<string, any> };
};

class TypedEventEmitter<Events extends Record<string, any>> {
  private listeners = new Map<keyof Events, Set<(data: any) => void>>();

  on<E extends keyof Events>(
    event: E,
    listener: (data: Events[E]) => void
  ) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(listener);
  }

  emit<E extends keyof Events>(event: E, data: Events[E]) {
    this.listeners.get(event)?.forEach(listener => listener(data));
  }
}

const emitter = new TypedEventEmitter<EventMap>();
emitter.on('click', ({ x, y }) => console.log(x, y));
emitter.emit('click', { x: 100, y: 200 });
```

### 2. 类型安全的 Redux Action

```typescript
interface Action<Type extends string, Payload = undefined> {
  type: Type;
  payload: Payload;
}

type AddTodo = Action<'ADD_TODO', { text: string }>;
type ToggleTodo = Action<'TOGGLE_TODO', { id: number }>;
type TodoAction = AddTodo | ToggleTodo;

function todoReducer(state: Todo[], action: TodoAction): Todo[] {
  switch (action.type) {
    case 'ADD_TODO':
      return [...state, { id: Date.now(), text: action.payload.text, done: false }];
    case 'TOGGLE_TODO':
      return state.map(todo =>
        todo.id === action.payload.id ? { ...todo, done: !todo.done } : todo
      );
    default:
      return state;
  }
}
```

### 3. 类型安全的路由系统

```typescript
const routes = {
  home: '/',
  users: '/users',
  user: '/users/:id',
  post: '/users/:userId/posts/:postId',
} as const;

type Routes = typeof routes;
type RouteName = keyof Routes;
type RoutePath = Routes[RouteName];

type ExtractParams<Path extends string> =
  Path extends `${infer _}:${infer Param}/${infer Rest}`
    ? Param | ExtractParams<Rest>
    : Path extends `${infer _}:${infer Param}`
    ? Param
    : never;

type RouteParamsByName<Name extends RouteName> = ExtractParams<Routes[Name]>;

type RouteOptionsByName<Name extends RouteName> =
  RouteParamsByName<Name> extends never
    ? { params?: never }
    : { params: Record<RouteParamsByName<Name>, string | number> };

function navigate<Name extends RouteName>(
  name: Name,
  options: RouteOptionsByName<Name>
) {
  let path = routes[name];
  if (options.params) {
    for (const [key, value] of Object.entries(options.params)) {
      path = path.replace(`:${key}`, String(value));
    }
  }
  console.log('Navigating to:', path);
}

navigate('home', {});
navigate('user', { params: { id: 123 } });
navigate('post', { params: { userId: 123, postId: 456 } });
```

## 七、最佳实践

1. 不要过度复杂化类型
2. 优先使用内置工具类型
3. 添加类型注释提高可读性
4. 使用类型测试验证类型

## 八、总结

TypeScript 类型体操是一项强大的技能：
- 掌握内置工具类型
- 理解条件类型和 infer
- 善用映射类型
- 使用模板字面量类型
- 练习递归类型

掌握类型体操，让你的 TypeScript 代码更加类型安全！
