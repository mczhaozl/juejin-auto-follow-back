# React Query (TanStack Query) 完全指南

## 一、基础使用

```tsx
import { useQuery, useQueryClient } from '@tanstack/react-query';

function UserProfile({ userId }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error!</div>;
  return <div>{data.name}</div>;
}
```

## 二、突变操作

```tsx
import { useMutation } from '@tanstack/react-query';

function CreatePostForm() {
  const queryClient = useQueryClient();
  
  const mutation = useMutation({
    mutationFn: createPost,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    }
  });

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      mutation.mutate({ title: 'Hello' });
    }}>
      {/* 表单 */}
    </form>
  );
}
```

## 三、查询配置

```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  enabled: isUserLoggedIn,
  refetchOnWindowFocus: true,
  retry: 3,
  retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
});
```

## 四、分页

```tsx
function TodoList() {
  const [page, setPage] = useState(1);
  
  const { data, isLoading, fetchNextPage, hasNextPage } = useQuery({
    queryKey: ['todos', page],
    queryFn: () => fetchTodos(page),
    keepPreviousData: true
  });
}
```

## 五、无限滚动

```tsx
import { useInfiniteQuery } from '@tanstack/react-query';

function InfiniteList() {
  const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
    queryKey: ['posts'],
    queryFn: ({ pageParam = 1 }) => fetchPosts(pageParam),
    getNextPageParam: (lastPage) => lastPage.nextPage
  });
}
```

## 六、查询缓存

```tsx
const queryClient = useQueryClient();

// 预置缓存
queryClient.setQueryData(['user', id], data);

// 撤销查询
queryClient.cancelQueries({ queryKey: ['posts'] });

// 清除缓存
queryClient.removeQueries();
```

## 七、全局配置

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime: 30 * 60 * 1000
    }
  }
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* 应用 */}
    </QueryClientProvider>
  );
}
```

## 八、DevTools

```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* 应用 */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

## 九、最佳实践

- 合理设计 queryKey
- 优化 staleTime 和 gcTime
- 使用 mutations 进行状态更新
- 利用缓存提高性能
- 实现乐观更新
- 使用 DevTools 调试
