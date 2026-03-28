# TanStack Query v5：现代异步状态管理最佳实践

> 在复杂的 Web 应用中，异步状态管理（获取、缓存、同步、更新服务器状态）一直是开发者的噩梦。本文将深度解析 TanStack Query (React Query) v5 的最新特性，并实战如何构建健壮的数据获取层。

---

## 目录 (Outline)
- [一、 从 useEffect 到 React Query：为什么状态管理需要解耦？](#一-从-useeffect-到-react-query为什么状态管理需要解耦)
- [二、 TanStack Query v5 核心：简化、一致与性能](#二-tanstack-query-v5-核心简化一致与性能)
- [三、 快速上手：构建一个带自动重试与缓存的列表页](#三-快速上手构建一个带自动重试与缓存的列表页)
- [四、 核心机制：查询键 (Query Keys) 与缓存失效 (Invalidation)](#四-核心机制查询键-query-keys-与缓存失效-invalidation)
- [五、 实战 1：利用 useMutation 实现乐观更新 (Optimistic Updates)](#五-实战-1利用-usemutation-实现乐观更新-optimistic-updates)
- [六、 实战 2：Infinite Queries——轻松实现无限滚动与分页](#六-实战-2infinite-queries轻松实现无限滚动与分页)
- [七、 进阶：Hydration 与 SSR 支持（Vite 6 场景）](#七-进阶hydration-与-ssr-支持vite-6-场景)
- [八、 总结：TanStack Query 带来的异步编程新范式](#八-总结-tanstack-query-带来的异步编程新范式)

---

## 一、 从 useEffect 到 React Query：为什么状态管理需要解耦？

### 1. 历史局限
过去，我们通常在 `useEffect` 中手动管理数据：
```javascript
useEffect(() => {
  setIsLoading(true);
  fetchData().then(data => {
    setData(data);
    setIsLoading(false);
  }).catch(err => setError(err));
}, []);
```
- **重复请求**：多个组件同时加载时，会发起多次请求。
- **状态混乱**：加载中、错误处理、数据同步逻辑散落在各处。
- **缓存缺失**：没有全局的缓存层，每次进入页面都要重新加载。

### 2. 标志性事件
- **2020 年**：React Query 1.0 发布，引入了「Server State」的概念。
- **2024 年**：TanStack Query v5 正式发布，统一了多框架支持，并大幅简化了 API。

---

## 二、 TanStack Query v5 核心：简化、一致与性能

v5 版本最大的改变是：**单一对象参数**。

### 核心改进
1. **API 统一**：不再支持多参数重载，强制使用对象形式。
2. **性能优化**：底层算法重构，大幅减少了不必要的重绘。
3. **Suspense 支持**：原生支持 React 18+ 的 Suspense 模式。

---

## 三、 快速上手：构建一个带自动重试与缓存的列表页

### 代码示例
```typescript
import { useQuery } from '@tanstack/react-query'

function UserList() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['users'], // 查询键
    queryFn: fetchUsers, // 异步函数
    staleTime: 1000 * 60 * 5, // 数据 5 分钟内不过期
    retry: 3, // 失败自动重试 3 次
  })

  if (isLoading) return <div>Loading...</div>
  if (isError) return <div>Error: {error.message}</div>

  return (
    <ul>
      {data.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  )
}
```

---

## 四、 核心机制：查询键 (Query Keys) 与缓存失效 (Invalidation)

查询键是 TanStack Query 的核心。
- **数组结构**：`['users', userId]`。
- **自动触发**：当数组中的任何一个元素改变时，Query 都会自动重新执行。
- **失效管理**：通过 `queryClient.invalidateQueries({ queryKey: ['users'] })`，你可以手动让相关缓存失效并触发背景更新。

---

## 五、 实战 1：利用 useMutation 实现乐观更新 (Optimistic Updates)

乐观更新是提升用户体验的绝佳手段：在请求返回前，先假设成功并更新 UI。

### 实现代码
```typescript
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    // 1. 取消正在进行的请求
    await queryClient.cancelQueries({ queryKey: ['todos'] })
    // 2. 备份当前数据
    const previousTodos = queryClient.getQueryData(['todos'])
    // 3. 乐观更新
    queryClient.setQueryData(['todos'], (old) => [...old, newTodo])
    return { previousTodos }
  },
  onError: (err, newTodo, context) => {
    // 失败回滚
    queryClient.setQueryData(['todos'], context.previousTodos)
  },
  onSettled: () => {
    // 无论成功失败，最后重新同步一次
    queryClient.invalidateQueries({ queryKey: ['todos'] })
  }
})
```

---

## 六、 实战 2：Infinite Queries——轻松实现无限滚动与分页

`useInfiniteQuery` 完美解决了加载更多的场景。
- 它自动维护了 `pages` 数组。
- 支持 `getNextPageParam` 和 `fetchNextPage`。

---

## 七、 进阶：Hydration 与 SSR 支持（Vite 6 场景）

在服务端渲染（SSR）中，我们可以预取数据并将其序列化。
- **Prefetching**：在服务端执行 `queryClient.prefetchQuery`。
- **Dehydrate**：将状态提取为 JSON 字符串。
- **Hydrate**：在客户端注入状态，实现「零白屏」的首屏加载。

---

## 八、 总结：TanStack Query 带来的异步编程新范式

TanStack Query 已经成为了 React 生态的事实标准。它不仅是一个库，更是一种思维方式：**将复杂的服务器状态从本地 UI 状态中剥离出来**。掌握了它，你的全栈开发效率将得到质的飞跃。

---
> 关注我，掌握现代 Web 开发状态管理之道，助力构建高性能、高可用的全栈应用。
