# React Remix 完全指南

## 一、路由和数据加载

```tsx
// app/routes/users.$id.tsx
import { LoaderFunction, useLoaderData } from '@remix-run/react';

export const loader: LoaderFunction = async ({ params }) => {
  const user = await fetchUser(params.id!);
  return user;
};

export default function User() {
  const user = useLoaderData<User>();
  return (
    <div>
      <h1>{user.name}</h1>
    </div>
  );
}
```

## 二、表单处理

```tsx
import { ActionFunction, redirect } from '@remix-run/node';

export const action: ActionFunction = async ({ request }) => {
  const formData = await request.formData();
  const name = formData.get('name');
  // 处理表单数据
  return redirect('/success');
};

export default function CreateUser() {
  return (
    <form method="post">
      <input name="name" />
      <button type="submit">提交</button>
    </form>
  );
}
```

## 三、嵌套路由

```tsx
// app/routes/posts.$postId.tsx
import { Outlet } from '@remix-run/react';

export default function PostLayout() {
  return (
    <div>
      <h1>Post</h1>
      <Outlet />
    </div>
  );
}
```

## 四、错误边界

```tsx
import { useErrorBoundary } from '@remix-run/react';

export function ErrorBoundary() {
  const error = useErrorBoundary();
  return (
    <div>
      <h1>出错了</h1>
      <p>{error.message}</p>
    </div>
  );
}
```

## 五、最佳实践

- 使用 loaders 预加载数据
- 渐进式增强（表单支持无 JS）
- 合理组织路由结构
- 使用错误边界处理异常
- 缓存策略优化加载
