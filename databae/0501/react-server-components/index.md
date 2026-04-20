# React Server Components 深度实战指南：从原理到应用

## 一、Server Components 概述

### 1.1 什么是 Server Components

React Server Components（RSC）是一种新的组件类型，它们在服务器上渲染，不会增加客户端 bundle 大小。

### 1.2 三种组件类型

| 类型 | 扩展名 | 渲染位置 | 交互 |
|------|--------|----------|------|
| **Server Component** | .tsx | 服务器 | ❌ |
| **Client Component** | .tsx + 'use client' | 客户端 | ✅ |
| **Shared Component** | .tsx | 两者皆可 | 取决于使用位置 |

---

## 二、Server Component 基础

### 2.1 基本结构

```tsx
// page.tsx (自动为 Server Component)
import { fetchUser } from '@/lib/db';

export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

### 2.2 直接数据获取

```tsx
async function BlogPost({ id }: { id: string }) {
  const post = await db.posts.findUnique({ where: { id } });
  
  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
```

### 2.3 使用服务器依赖

```tsx
import fs from 'fs';
import path from 'path';
import { format } from 'date-fns';

async function ReadmePage() {
  const readmePath = path.join(process.cwd(), 'README.md');
  const content = fs.readFileSync(readmePath, 'utf-8');
  const date = format(new Date(), 'yyyy-MM-dd');
  
  return (
    <div>
      <h1>README - {date}</h1>
      <pre>{content}</pre>
    </div>
  );
}
```

---

## 三、Client Component

### 3.1 使用 'use client'

```tsx
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

### 3.2 组件组合

```tsx
// Server Component
import { Counter } from './counter';

async function Page() {
  const data = await fetchData();
  
  return (
    <div>
      <h1>{data.title}</h1>
      <Counter />
    </div>
  );
}
```

---

## 四、数据获取模式

### 4.1 并行数据获取

```tsx
async function Page() {
  const [user, posts] = await Promise.all([
    fetchUser(id),
    fetchPosts(userId)
  ]);
  
  return (
    <div>
      <UserProfile user={user} />
      <PostsList posts={posts} />
    </div>
  );
}
```

### 4.2 顺序数据获取

```tsx
async function Page({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);
  const posts = await fetchPosts(user.id);
  
  return (
    <div>
      <UserProfile user={user} />
      <PostsList posts={posts} />
    </div>
  );
}
```

### 4.3 Suspense 流式渲染

```tsx
import { Suspense } from 'react';

function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<Loading />}>
        <Analytics />
      </Suspense>
      <Suspense fallback={<Loading />}>
        <RecentPosts />
      </Suspense>
    </div>
  );
}
```

---

## 五、路由与导航

### 5.1 App Router 结构

```
app/
├── layout.tsx
├── page.tsx
├── about/
│   └── page.tsx
└── users/
    └── [id]/
        └── page.tsx
```

### 5.2 动态路由

```tsx
// app/users/[id]/page.tsx
export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);
  return <User user={user} />;
}
```

### 5.3 嵌套路由

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <Sidebar />
      <main>{children}</main>
    </div>
  );
}
```

---

## 六、Server Actions

### 6.1 基本用法

```tsx
// Server Action
async function submitForm(formData: FormData) {
  'use server';
  
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;
  
  await db.users.create({ data: { name, email } });
}

// 使用
export default function ContactPage() {
  return (
    <form action={submitForm}>
      <input type="text" name="name" />
      <input type="email" name="email" />
      <button type="submit">Submit</button>
    </form>
  );
}
```

### 6.2 错误处理

```tsx
'use server';

import { revalidatePath } from 'next/cache';

export async function createPost(formData: FormData) {
  try {
    const title = formData.get('title') as string;
    const content = formData.get('content') as string;
    
    await db.posts.create({ data: { title, content } });
    revalidatePath('/posts');
    
    return { success: true };
  } catch (error) {
    return { error: 'Failed to create post' };
  }
}
```

---

## 七、缓存策略

### 7.1 静态生成

```tsx
export const dynamic = 'force-static';

export default async function StaticPage() {
  const data = await fetchData();
  return <div>{data}</div>;
}
```

### 7.2 动态渲染

```tsx
export const dynamic = 'force-dynamic';

export default async function DynamicPage() {
  const data = await fetchData();
  return <div>{data}</div>;
}
```

### 7.3 ISR 增量静态再生成

```tsx
export const revalidate = 60; // 60秒

export default async function ISRPage() {
  const data = await fetchData();
  return <div>{data}</div>;
}
```

---

## 八、实战项目：博客系统

### 8.1 文章列表页面

```tsx
// app/blog/page.tsx
import { getPosts } from '@/lib/posts';
import Link from 'next/link';

export default async function BlogPage() {
  const posts = await getPosts();
  
  return (
    <div>
      <h1>Blog</h1>
      <div className="posts">
        {posts.map(post => (
          <article key={post.id}>
            <Link href={`/blog/${post.id}`}>
              <h2>{post.title}</h2>
            </Link>
            <p>{post.excerpt}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
```

### 8.2 文章详情页面

```tsx
// app/blog/[id]/page.tsx
import { getPost, getComments } from '@/lib/posts';
import { CommentForm } from '@/components/comment-form';

export default async function PostPage({ params }: { params: { id: string } }) {
  const post = await getPost(params.id);
  const comments = await getComments(params.id);
  
  return (
    <article>
      <h1>{post.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
      
      <section>
        <h2>Comments</h2>
        {comments.map(comment => (
          <div key={comment.id}>
            <strong>{comment.author}</strong>
            <p>{comment.content}</p>
          </div>
        ))}
        <CommentForm postId={params.id} />
      </section>
    </article>
  );
}
```

### 8.3 评论表单（Client Component）

```tsx
'use client';

import { useState } from 'react';
import { addComment } from '@/app/actions';

export function CommentForm({ postId }: { postId: string }) {
  const [author, setAuthor] = useState('');
  const [content, setContent] = useState('');
  
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await addComment(postId, author, content);
    setAuthor('');
    setContent('');
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <input value={author} onChange={e => setAuthor(e.target.value)} placeholder="Name" />
      <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Comment" />
      <button type="submit">Submit</button>
    </form>
  );
}
```

---

## 九、性能优化

### 9.1 代码分割

```tsx
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  ssr: false,
  loading: () => <Loading />
});

export default function Page() {
  return <HeavyChart />;
}
```

### 9.2 图片优化

```tsx
import Image from 'next/image';

export default function Page() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero"
      fill
      priority
    />
  );
}
```

---

## 总结

React Server Components 带来了全新的开发模式，通过服务器渲染和客户端交互的明确分离，让我们能构建更快、更高效的应用。
