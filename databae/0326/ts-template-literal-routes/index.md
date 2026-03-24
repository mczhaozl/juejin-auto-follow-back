# TypeScript 进阶：如何利用 Template Literal Types 构建类型安全的路由系统

> 在使用 React Router 或 Next.js 等路由系统时，手写路径字符串往往是 Bug 的温床。本文将分享如何利用 TypeScript 的模板字符串类型，实现一个全自动推导路径参数、类型安全的路由方案。

## 一、场景：痛点在哪里？

假设我们定义了一个动态路由：`/user/:id/posts/:postId`。

在代码中跳转时，我们通常会写：
```typescript
navigate(`/user/${userId}/posts/${postId}`);
```

**问题：**
1. **拼写错误**：路径中的 `user` 或 `posts` 可能会拼错。
2. **参数遗漏**：可能会忘记传入 `userId` 或 `postId`。
3. **类型不匹配**：路径参数通常应该是 `string` 或 `number`，但可能不小心传了对象。

## 二、核心方案：解析路径参数

我们可以定义一个工具类型 `ExtractParams<T>`，它可以从路径字符串中提取出带冒号的参数。

```typescript
type ExtractParams<T extends string> = T extends `${string}:${infer Param}/${infer Rest}`
  ? Param | ExtractParams<Rest>
  : T extends `${string}:${infer Param}`
  ? Param
  : never;

// 使用示例
type Params = ExtractParams<"/user/:id/posts/:postId">;
// Params 会推导为 "id" | "postId"
```

## 三、构建类型安全的路由对象

接下来，我们可以把这个工具应用到路由跳转函数中：

```typescript
type RouteParams<T extends string> = {
  [K in ExtractParams<T>]: string | number;
};

function generateUrl<T extends string>(path: T, params: RouteParams<T>): string {
  let url: string = path;
  for (const [key, value] of Object.entries(params)) {
    url = url.replace(`:${key}`, String(value));
  }
  return url;
}

// 示例用法
const url = generateUrl("/user/:id/posts/:postId", {
  id: 123,
  postId: 456
});

// 如果少传参数或传错参数名，TypeScript 会报错！
// generateUrl("/user/:id", { userId: 123 }); // Error: Property 'id' is missing
```

## 四、更进一步：路径自动推导

如果你所有的路由都定义在一个常量中，我们可以实现全自动的类型提示：

```typescript
const AppRoutes = {
  USER_PROFILE: "/user/:userId",
  POST_DETAIL: "/posts/:postId",
} as const;

type RouteKey = keyof typeof AppRoutes;

function navigate<K extends RouteKey>(
  route: K, 
  params: RouteParams<(typeof AppRoutes)[K]>
) {
  const path = AppRoutes[route];
  // 实现跳转逻辑...
}

// 完美的类型提示与安全保障！
navigate("USER_PROFILE", { userId: "abc" });
```

## 五、总结

模板字符串类型（Template Literal Types）是 TypeScript 4.1 引入的强大特性，它能让我们在编译期就解决掉以前只能在运行时发现的 Bug。

**如果你觉得本文对你有帮助，欢迎点赞收藏！** 
下期我们将介绍更多 TypeScript 在大型项目中的实战技巧。
