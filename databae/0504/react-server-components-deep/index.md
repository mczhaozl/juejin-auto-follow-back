# React Server Components 深度解析

## 一、RSC 架构原理

### 1.1 什么是 Server Components

```
Server Components: 在服务器端渲染，无客户端 JavaScript
Client Components: 传统客户端组件
Shared Components: 可在两端使用
```

## 二、使用场景

```tsx
// Server Component
async function BlogPost({ id }) {
  const post = await db.posts.findUnique({ where: { id } });
  return (
    <article>
      <h1>{post.title}</h1>
      <Content content={post.content} />
      <LikeButton postId={id} />
    </article>
  );
}

// Client Component
'use client';

function LikeButton({ postId }) {
  const [likes, setLikes] = useState(0);
  return <button onClick={() => setLikes(l => l + 1)}>❤️ {likes}</button>;
}
```

## 三、数据获取

```tsx
// 直接在组件中获取数据
async function ProductPage({ params }) {
  const product = await fetch(`/api/products/${params.id}`);
  return <div>{product.name}</div>;
}

// 使用 React Query
'use client';

function ProductReviews({ productId }) {
  const { data } = useQuery({
    queryKey: ['reviews', productId],
    queryFn: () => fetchReviews(productId)
  });
  return <div>{data}</div>;
}
```

## 四、性能优化

```tsx
// Streaming
export default function Page() {
  return (
    <>
      <Suspense fallback={<Loading />}>
        <SlowComponent />
      </Suspense>
    </>
  );
}

// Selective Hydration
'use client';
```

## 五、最佳实践

- 数据获取尽量放在 Server Components
- 交互逻辑放在 Client Components
- 合理使用 Suspense
- 优化 Server Actions 处理表单
