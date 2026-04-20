# Remix 框架深度实战指南

## 一、Remix 概述

### 1.1 什么是 Remix

基于 Web 标准的全栈 React 框架，注重用户体验。

### 1.2 核心理念

- Web 标准优先
- 渐进增强
- 数据加载优化
- 错误处理

---

## 二、项目初始化

```bash
# 创建 Remix 应用
npx create-remix@latest

# 开发模式
npm run dev

# 生产构建
npm run build
```

---

## 三、路由基础

```typescript
// app/routes/index.tsx
export default function Index() {
  return (
    <div>
      <h1>Welcome to Remix!</h1>
    </div>
  );
}
```

```typescript
// app/routes/posts.$id.tsx
export async function loader({ params }: { params: { id: string } }) {
  const post = await getPost(params.id);
  return { post };
}

export default function PostPage() {
  const { post } = useLoaderData<typeof loader>();
  return <h1>{post.title}</h1>;
}
```

---

## 四、数据加载

### 4.1 Loader

```typescript
import { json } from '@remix-run/node';
import { useLoaderData } from '@remix-run/react';

export async function loader() {
  const posts = await getPosts();
  return json({ posts });
}

export default function PostsPage() {
  const { posts } = useLoaderData<typeof loader>();
  return (
    <div>
      {posts.map(post => (
        <article key={post.id}>{post.title}</article>
      ))}
    </div>
  );
}
```

### 4.2 Action

```typescript
import { redirect } from '@remix-run/node';
import { Form } from '@remix-run/react';

export async function action({ request }: { request: Request }) {
  const formData = await request.formData();
  const title = formData.get('title');
  const content = formData.get('content');
  await createPost({ title, content });
  return redirect('/posts');
}

export default function NewPostPage() {
  return (
    <Form method="post">
      <input type="text" name="title" />
      <textarea name="content" />
      <button type="submit">Create Post</button>
    </Form>
  );
}
```

---

## 五、嵌套路由

```typescript
// app/routes/posts.tsx
import { Outlet } from '@remix-run/react';

export default function PostsLayout() {
  return (
    <div>
      <nav>Posts Nav</nav>
      <Outlet />
    </div>
  );
}

// app/routes/posts.index.tsx
export default function PostsIndex() {
  return <h1>All Posts</h1>;
}

// app/routes/posts.$id.tsx
export default function PostDetail() {
  const { post } = useLoaderData();
  return <h1>{post.title}</h1>;
}
```

---

## 六、错误处理

```typescript
// app/routes/posts.$id.tsx
export async function loader({ params }) {
  const post = await getPost(params.id);
  if (!post) {
    throw new Response('Not Found', { status: 404 });
  }
  return json({ post });
}

export function ErrorBoundary() {
  const error = useRouteError();
  if (isResponse(error)) {
    return <h1>Oops: {error.status}</h1>;
  }
  return <h1>Something went wrong</h1>;
}
```

---

## 七、Meta 与 Links

```typescript
import { MetaFunction } from '@remix-run/node';

export const meta: MetaFunction = () => {
  return [
    { title: 'My Blog' },
    { name: 'description', content: 'A Remix blog' }
  ];
};

export const links = () => [
  { rel: 'stylesheet', href: '/styles.css' }
];
```

---

## 八、实战：博客系统

```typescript
// app/routes/posts.tsx
export async function loader() {
  const posts = await db.post.findMany();
  return json({ posts });
}

export default function Posts() {
  const { posts } = useLoaderData<typeof loader>();
  return (
    <div>
      {posts.map(post => (
        <Link key={post.id} to={`/posts/${post.id}`}>
          {post.title}
        </Link>
      ))}
    </div>
  );
}

// app/routes/posts.$id.tsx
export async function loader({ params }) {
  const post = await db.post.findUnique({ where: { id: params.id } });
  if (!post) throw new Response(null, { status: 404 });
  return json({ post });
}

export async function action({ request, params }) {
  if (request.method === 'DELETE') {
    await db.post.delete({ where: { id: params.id } });
    return redirect('/posts');
  }
}

export default function Post() {
  const { post } = useLoaderData<typeof loader>();
  return (
    <article>
      <h1>{post.title}</h1>
      <Form method="delete">
        <button type="submit">Delete</button>
      </Form>
    </article>
  );
}
```

---

## 九、部署

```bash
# 构建
npm run build

# 生产启动
npm start
```

---

## 总结

Remix 通过标准 Web 技术构建快速、强大的应用，注重数据加载和错误处理，提供优秀的用户体验。
