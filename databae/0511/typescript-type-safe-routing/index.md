# TypeScript 类型安全路由完全指南

## 一、路由配置

```typescript
// 路由定义
type Routes = {
  '/': {};
  '/users/:id': { id: string };
  '/posts/:postId/comments/:commentId': { postId: string; commentId: string };
};
```

## 二、路由匹配

```typescript
// 解析路由参数
type ParseParams<S extends string> = 
  S extends `${infer Prefix}:${infer Param}/${infer Suffix}` 
    ? { [key in Param]: string } & ParseParams<Suffix>
    : S extends `${infer Prefix}:${infer Param}`
    ? { [key in Param]: string }
    : {};

type Path<R extends string> = ParseParams<R>;

type UserParams = Path<'/users/:id'>; // { id: string }
```

## 三、构建 URL

```typescript
function buildUrl<R extends keyof Routes>(
  path: R,
  params: Routes[R]
): string {
  let result = path as string;
  for (const [key, value] of Object.entries(params)) {
    result = result.replace(`:${key}`, value);
  }
  return result;
}

const userUrl = buildUrl('/users/:id', { id: '123' }); // /users/123
```

## 四、类型安全导航

```typescript
function navigate<R extends keyof Routes>(
  path: R,
  params: Routes[R]
) {
  const url = buildUrl(path, params);
  window.location.href = url;
}

navigate('/users/:id', { id: '456' });
```

## 五、最佳实践

- 使用模板字面量类型提取路由参数
- 使用路由对象提供类型安全导航
- 结合 React/Vue Router
- 生成 API 客户端 SDK
- 验证路由参数
