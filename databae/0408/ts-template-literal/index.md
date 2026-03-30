# TypeScript 模板字符串类型完全指南：构建类型安全的路由与API

> 深入讲解 TypeScript 模板字符串字面量类型的强大功能，手把手教你构建类型安全的路由系统和 API 接口。

## 一、什么是模板字符串类型

TypeScript 4.1 引入了模板字符串字面量类型，允许使用模板字面量语法创建新的字符串类型。

```typescript
type World = 'world';
type Greeting = `hello ${World}`; // "hello world"
type Combined = `${'a' | 'b'}${1 | 2}`; // "a1" | "a2" | "b1" | "b2"
```

## 二、基本用法

### 2.1 基础模板

```typescript
type EventName = 'click' | 'focus' | 'blur';
type Handler = `on${EventName}`; // "onclick" | "onfocus" | "onblur"
```

### 2.2 联合类型组合

```typescript
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type APIEndpoint = '/users' | '/posts' | '/comments';
type Route = `${HTTPMethod} ${APIEndpoint}`;
// "GET /users" | "POST /users" | "GET /posts" | ...
```

### 2.3 嵌套模板

```typescript
type Color = 'red' | 'green' | 'blue';
type Size = 'sm' | 'md' | 'lg';
type ClassName = `${Color}-${Size}`;
// "red-sm" | "red-md" | "red-lg" | "green-sm" | ...
```

## 三、实战：类型安全路由

### 3.1 定义路由类型

```typescript
type Path = 'users' | 'posts' | 'comments';
type Method = 'get' | 'post' | 'put' | 'delete';

type Route = `${Method}:/${Path}`;

function handleRoute(route: Route) {
  // ...
}

handleRoute('get:/users'); // OK
handleRoute('post:/posts'); // OK
handleRoute('patch:/users'); // Error: 不能分配给类型
```

### 3.2 动态路径参数

```typescript
type PathParams<T extends string> = 
  T extends `${string}/:${infer P}/${infer Rest}` 
    ? P | PathParams<`/${Rest}`>
    : T extends `${string}/:${infer P}` 
      ? P 
      : never;

type Route = '/users/:id/posts/:postId';
type Params = PathParams<Route>; // "id" | "postId"
```

### 3.3 完整路由系统

```typescript
type ParamKeys<T extends string> = 
  T extends `${string}:${infer K}/${infer R}` 
    ? K | ParamKeys<`/${R}`>
    : T extends `${string}:${infer K}` 
      ? K 
      : never;

type RouteWithParams = '/users/:id/comments/:commentId';
type Keys = ParamKeys<RouteWithParams>; // "id" | "commentId"

type ParamObject<T extends string> = {
  [K in ParamKeys<T>]: string;
};

function buildRoute<T extends string>(route: T, params: ParamObject<T>) {
  let result = route;
  for (const [key, value] of Object.entries(params)) {
    result = result.replace(`:${key}`, value) as T;
  }
  return result;
}

buildRoute('/users/:id/comments/:commentId', {
  id: '123',
  commentId: '456'
}); // "/users/123/comments/456"
```

## 四、实战：类型安全 API

### 4.1 API 定义

```typescript
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

interface Endpoints {
  '/api/users': {
    GET: User[];
    POST: { name: string };
  };
  '/api/users/:id': {
    GET: User;
    PUT: Partial<User>;
    DELETE: void;
  };
  '/api/posts': {
    GET: { page: number };
    POST: { title: string; content: string };
  };
}
```

### 4.2 请求构建器

```typescript
type ExtractPath<T> = T extends keyof Endpoints ? T : never;
type ExtractMethod<T extends string> = 
  T extends `${infer M}:${string}` ? M : never;

async function request<T extends string>(
  route: T,
  options?: {
    method?: ExtractMethod<T>;
    body?: Endpoints[ExtractPath<T>][HTTPMethod];
  }
) {
  const method = options?.method || 'GET';
  const url = route.replace(/:(\w+)/g, (_, key) => options?.body?.[key] || '');
  
  return fetch(url, {
    method,
    body: options?.body ? JSON.stringify(options.body) : undefined
  });
}
```

### 4.3 类型安全的 fetch

```typescript
type RequestConfig<T> = {
  [K in keyof T]?: T[K] extends (infer U)[] ? { page?: number } : T[K]
};

function createApiClient<T extends Record<string, Record<HTTPMethod, any>>>(
  baseUrl: string,
  endpoints: T
) {
  return {
    async request<
      P extends keyof T,
      M extends keyof T[P]
    >(path: P, method: M, data?: T[P][M]) {
      return fetch(`${baseUrl}${path}`, {
        method: method as string,
        body: data ? JSON.stringify(data) : undefined
      });
    }
  };
}

const api = createApiClient('/api', {
  '/users': {
    GET: [] as User[],
    POST: {} as { name: string }
  }
});
```

## 五、字符串操作类型

TypeScript 提供了一些内置的字符串操作类型：

### 5.1 Uppercase / Lowercase

```typescript
type Upper = Uppercase<'hello'>; // "HELLO"
type Lower = Lowercase<'HELLO'>; // "hello"
```

### 5.2 Capitalize / Uncapitalize

```typescript
type Cap = Capitalize<'hello'>; // "Hello"
type Uncap = Uncapitalize<'Hello'>; // "hello"
```

### 5.3 组合使用

```typescript
type Event = 'click' | 'focus';
type Handler = `on${Capitalize<Event>}`; // "onClick" | "onFocus"
```

## 六、进阶技巧

### 6.1 自动补全

```typescript
type EventMap = {
  click: 'onClick';
  focus: 'onFocus';
  blur: 'onBlur';
};

type Handler<T extends keyof EventMap> = 
  `handle${Capitalize<T>}`;

function register<T extends keyof EventMap>(
  handler: Handler<T>
) {
  console.log(handler);
}

register('handleClick'); // 自动补全
register('handleHover'); // 错误
```

### 6.2 CSS 类型

```typescript
type CSSProperty = 'color' | 'margin' | 'padding';
type CSSValue = 'px' | 'em' | 'rem' | '%';
type CSSRule = `${CSSProperty}: ${CSSValue}`;

const styles: CSSRule[] = [
  'color: px', // Error
  'margin: px', // OK
  'padding: em', // OK
];
```

### 6.3 消息格式

```typescript
type Message = 'success' | 'error' | 'warning';
type Prefix = 'user' | 'system';
type LogMessage = `[${Prefix}] ${Message}: ${string}`;

const logs: LogMessage[] = [
  '[user] success: 登录成功',
  '[system] error: 服务器异常',
];
```

## 七、总结

模板字符串类型是 TypeScript 强大的类型系统的重要组成部分：

1. **类型推断**：自动生成精确的类型
2. **类型安全**：编译时检查错误
3. **IDE 支持**：智能提示和自动补全
4. **组合性**：联合类型和模板的灵活组合

熟练运用这些技巧，可以构建出真正类型安全的应用。

---

**推荐阅读**：
- [TypeScript 4.1 官方更新](https://devblogs.microsoft.com/typescript/announcing-typescript-4-1/)
- [模板字符串类型详解](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)

**如果对你有帮助，欢迎点赞收藏！**
