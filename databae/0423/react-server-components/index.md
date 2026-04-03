# React Server Components 完全指南：从原理到实战

React Server Components (RSC) 是 React 18+ 的革命性特性，它彻底改变了我们构建 React 应用的方式。本文将带你全面掌握 RSC。

## 一、什么是 React Server Components

### 1. 核心概念

React Server Components 允许你在服务器端渲染 React 组件，只将必要的 HTML 和交互性组件发送到客户端。

### 2. 为什么需要 Server Components

```javascript
// 传统 Client Component - 所有依赖都发送到客户端
import { useState } from 'react'
import { heavyLibrary } from 'heavy-library' // 100KB
import { anotherLibrary } from 'another-library' // 50KB

export default function Page() {
  const [count, setCount] = useState(0)
  
  return (
    <div>
      <h1>Hello</h1>
      <button onClick={() => setCount(count + 1)}>
        Count: {count}
      </button>
    </div>
  )
}
```

```javascript
// Server Component - 只在服务端执行，无客户端依赖
import fs from 'fs'
import path from 'path'

export default function Page() {
  const data = fs.readFileSync(path.join(process.cwd(), 'data.json'), 'utf8')
  const posts = JSON.parse(data)
  
  return (
    <div>
      <h1>Blog Posts</h1>
      <ul>
        {posts.map(post => (
          <li key={post.id}>{post.title}</li>
        ))}
      </ul>
    </div>
  )
}
```

## 二、Server Components vs Client Components

### 1. 对比表

| 特性 | Server Components | Client Components |
|------|------------------|------------------|
| 运行位置 | 服务器 | 浏览器 |
| 访问文件系统 | ✅ | ❌ |
| 访问环境变量 | ✅ | ✅（客户端暴露的） |
| 使用 Hooks | ❌ | ✅ |
| 使用浏览器 API | ❌ | ✅ |
| 可交互 | ❌ | ✅ |
| 减小包体积 | ✅ | ❌ |

### 2. 如何区分

```javascript
// Server Component（默认，无需标记）
export default function ServerPage() {
  return <h1>Hello from Server</h1>
}

// Client Component（需要 'use client' 指令）
'use client'

import { useState } from 'react'

export default function ClientComponent() {
  const [count, setCount] = useState(0)
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  )
}
```

## 三、数据获取

### 1. 直接在组件中获取

```javascript
// Server Component 直接获取数据
export default async function BlogPage() {
  const posts = await fetch('https://api.example.com/posts', {
    cache: 'force-cache' // 或 'no-store'
  }).then(res => res.json())
  
  return (
    <div>
      <h1>Blog</h1>
      <ul>
        {posts.map(post => (
          <li key={post.id}>{post.title}</li>
        ))}
      </ul>
    </div>
  )
}
```

### 2. 数据库直接查询

```javascript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default async function UsersPage() {
  const users = await prisma.user.findMany({
    include: { posts: true }
  })
  
  return (
    <div>
      {users.map(user => (
        <div key={user.id}>
          <h2>{user.name}</h2>
          <p>{user.email}</p>
          <ul>
            {user.posts.map(post => (
              <li key={post.id}>{post.title}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}
```

### 3. 缓存策略

```javascript
// 缓存数据（默认）
const data = await fetch('https://api.example.com/data', {
  cache: 'force-cache'
})

// 不缓存，每次都请求
const freshData = await fetch('https://api.example.com/data', {
  cache: 'no-store'
})

// 重新验证缓存
const revalidatedData = await fetch('https://api.example.com/data', {
  next: { revalidate: 60 } // 60秒后重新验证
})
```

## 四、组合 Server 和 Client Components

### 1. 嵌套结构

```javascript
// app/page.js (Server Component)
import ClientCounter from './ClientCounter'

export default function Home() {
  return (
    <div>
      <h1>Home Page (Server)</h1>
      <ClientCounter />
    </div>
  )
}
```

```javascript
// app/ClientCounter.js (Client Component)
'use client'

import { useState } from 'react'

export default function ClientCounter() {
  const [count, setCount] = useState(0)
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  )
}
```

### 2. 传递 props

```javascript
// Server Component
import ClientComponent from './ClientComponent'

export default function ServerPage() {
  const serverData = {
    title: 'Hello from Server',
    items: [1, 2, 3]
  }
  
  return (
    <ClientComponent data={serverData} />
  )
}
```

```javascript
// Client Component
'use client'

export default function ClientComponent({ data }) {
  return (
    <div>
      <h1>{data.title}</h1>
      <ul>
        {data.items.map(item => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  )
}
```

## 五、Next.js App Router 实战

### 1. 项目结构

```
app/
├── layout.js
├── page.js
├── about/
│   └── page.js
├── blog/
│   ├── [slug]/
│   │   └── page.js
│   └── page.js
└── api/
    └── posts/
        └── route.js
```

### 2. 动态路由

```javascript
// app/blog/[slug]/page.js
export default async function BlogPost({ params }) {
  const post = await fetch(
    `https://api.example.com/posts/${params.slug}`
  ).then(res => res.json())
  
  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  )
}
```

### 3. 生成静态参数

```javascript
// app/blog/[slug]/page.js
export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts')
    .then(res => res.json())
  
  return posts.map(post => ({
    slug: post.slug
  }))
}
```

### 4. Suspense 与 Streaming

```javascript
import { Suspense } from 'react'
import SlowComponent from './SlowComponent'
import Loading from './Loading'

export default function Page() {
  return (
    <div>
      <h1>Fast Content</h1>
      <Suspense fallback={<Loading />}>
        <SlowComponent />
      </Suspense>
    </div>
  )
}
```

## 六、最佳实践

### 1. 何时使用 Server Components

```javascript
// ✅ 适合 Server Components
- 数据获取
- 数据库查询
- 文件系统操作
- 大型依赖库（如 Markdown 解析）
- 非交互性 UI
```

### 2. 何时使用 Client Components

```javascript
// ✅ 适合 Client Components
- 状态管理（useState, useReducer）
- 生命周期（useEffect）
- 事件处理
- 浏览器 API（window, document）
- 交互性 UI
```

### 3. 组织代码

```
components/
├── ServerHeader.js
├── ServerFooter.js
├── ClientCounter.js
├── ClientForm.js
└── ...
```

## 七、常见问题

### 1. 不能在 Server Components 中使用 Hooks

```javascript
// ❌ 错误
export default function ServerComponent() {
  const [count, setCount] = useState(0) // 错误！
  return <div>{count}</div>
}

// ✅ 正确 - 拆分为 Client Component
'use client'
export default function ClientCounter() {
  const [count, setCount] = useState(0)
  return <div>{count}</div>
}
```

### 2. 不能将函数作为 props 传递

```javascript
// ❌ 错误
<ClientComponent onClick={() => console.log('click')} />

// ✅ 正确 - 在 Client Component 内部定义函数
'use client'
export default function ClientComponent() {
  const handleClick = () => console.log('click')
  return <button onClick={handleClick}>Click</button>
}
```

## 八、总结

React Server Components 带来了：
- 更小的客户端包体积
- 更快的首屏加载
- 更简单的数据获取
- 更好的安全性

掌握 RSC，让你的 React 应用更高效！
