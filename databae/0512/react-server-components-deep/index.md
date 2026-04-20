# React Server Components 深度解析

## 一、RSC 架构原理

```
┌───────────────────────┐         ┌───────────────────────┐
│       Browser         │────────▶│      Next.js          │
│  (Client Components)  │◀───────│    (SSR/RSC)          │
└───────────────────────┘         └───────────────────────┘
                                         │
                                         ▼
                                    ┌─────────┐
                                    │ Server  │
                                    │Components│
                                    └─────────┘
```

## 二、RSC 与 Client Components

```tsx
// Server Component (默认)
async function BlogPost({ id }: { id: string }) {
  const post = await fetchPost(id);
  return (
    <article>
      <h1>{post.title}</h1>
      <PostContent content={post.content} />
      <Comments /> {/* 客户端组件 */}
    </article>
  );
}

// Client Component (使用 'use client' 指令)
'use client';

export function Comments() {
  const [comments, setComments] = useState([]);
  
  return (
    <div>
      {comments.map(c => <div key={c.id}>{c.text}</div>)}
    </div>
  );
}
```

## 三、RSC 数据获取

```tsx
// 直接在组件中 fetch (服务端执行)
async function Page() {
  const data = await fetch('https://api.example.com/data');
  const json = await data.json();
  
  return <pre>{JSON.stringify(json)}</pre>;
}

// 与数据库直接通信
import { db } from '@/lib/db';

async function UserProfile({ id }: { id: string }) {
  const user = await db.users.findUnique({ where: { id } });
  return <div>{user.name}</div>;
}
```

## 四、组件组合模式

```tsx
// 1. 瀑布流获取
async function PostWithComments({ postId }: { postId: string }) {
  const post = await fetchPost(postId);      // 第 1 个请求
  const comments = await fetchComments(postId); // 第 2 个请求
  return (
    <>
      <Post post={post} />
      <CommentList comments={comments} />
    </>
  );
}

// 2. 并行获取
async function PostWithCommentsParallel({ postId }: { postId: string }) {
  const [post, comments] = await Promise.all([
    fetchPost(postId),
    fetchComments(postId),
  ]);
  
  return (
    <>
      <Post post={post} />
      <CommentList comments={comments} />
    </>
  );
}
```

## 最佳实践
- 默认使用 Server Components
- 只有需要交互时使用 Client Components
- 合理组织 Server/Client 边界
- 注意 Suspense 的使用
- 避免在 Server Components 使用 hooks
