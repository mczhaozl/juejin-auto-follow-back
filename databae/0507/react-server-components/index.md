# React Server Components 完全指南

## 一、服务端组件

```tsx
// 直接服务端运行，无客户端 JS
import db from '@/lib/db';

async function BlogPosts() {
  const posts = await db.posts.findMany();
  
  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

## 二、客户端组件

```tsx
'use client';

import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

## 三、组件通信

```tsx
// 服务端传递数据给客户端
async function Page() {
  const data = await fetchData();
  
  return <ClientComponent data={data} />;
}
```

## 四、数据获取

```tsx
// RSC 直接获取数据
async function UserProfile({ id }: { id: string }) {
  const user = await db.users.findUnique({ where: { id } });
  
  if (!user) notFound();
  
  return (
    <div>
      <h1>{user.name}</h1>
    </div>
  );
}
```

## 五、最佳实践

- 使用服务端组件处理数据
- 客户端组件用于交互
- 合理使用 Suspense
- 数据缓存和重新验证
- 代码组织和架构
- 性能优化考虑
