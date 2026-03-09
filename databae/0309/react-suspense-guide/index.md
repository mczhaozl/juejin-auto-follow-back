# React Suspense 从入门到实战：让异步加载更优雅

> 从代码分割到数据请求，掌握 React 18 Suspense 的核心用法与最佳实践

---

## 一、Suspense 是什么

Suspense 是 React 提供的一种声明式处理异步操作的机制。它让你可以在组件树的任意位置"等待"某些内容加载完成，并在加载期间显示一个后备 UI。

传统做法：

```javascript
function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchUser().then(data => {
      setUser(data);
      setLoading(false);
    });
  }, []);
  
  if (loading) return <Spinner />;
  return <div>{user.name}</div>;
}
```

使用 Suspense：

```javascript
function Profile() {
  const user = use(fetchUser()); // React 19 use hook
  return <div>{user.name}</div>;
}

<Suspense fallback={<Spinner />}>
  <Profile />
</Suspense>
```

核心优势：
- 关注点分离：组件只关心数据使用，不关心加载状态
- 声明式：父组件统一控制加载 UI
- 更好的用户体验：配合并发特性减少布局抖动

---

## 二、代码分割场景

这是 Suspense 最成熟的应用场景，配合 `React.lazy` 实现组件懒加载。

```javascript
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

多层 Suspense 边界：

```javascript
<Suspense fallback={<AppShell />}>
  <Layout>
    <Suspense fallback={<SidebarSkeleton />}>
      <Sidebar />
    </Suspense>
    <Suspense fallback={<ContentSkeleton />}>
      <Content />
    </Suspense>
  </Layout>
</Suspense>
```

---

## 三、数据请求场景

React 18 开始，Suspense 可以配合支持的数据请求库使用。

使用 SWR：

```javascript
import useSWR from 'swr';

function User({ id }) {
  const { data } = useSWR(`/api/user/${id}`, fetcher, {
    suspense: true  // 开启 Suspense 模式
  });
  
  return <div>{data.name}</div>;
}

<Suspense fallback={<UserSkeleton />}>
  <User id={123} />
</Suspense>
```

使用 React Query：

```javascript
import { useQuery } from '@tanstack/react-query';

function Posts() {
  const { data } = useQuery({
    queryKey: ['posts'],
    queryFn: fetchPosts,
    suspense: true
  });
  
  return data.map(post => <Post key={post.id} {...post} />);
}
```

---

## 四、与 Error Boundary 配合

Suspense 只处理"挂起"状态，错误需要 Error Boundary 捕获。

```javascript
class ErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}

<ErrorBoundary>
  <Suspense fallback={<Loading />}>
    <DataComponent />
  </Suspense>
</ErrorBoundary>
```

---

## 五、与并发特性配合

配合 `useTransition` 避免不必要的 loading 状态：

```javascript
function SearchResults() {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  
  const handleSearch = (value) => {
    startTransition(() => {
      setQuery(value);  // 低优先级更新
    });
  };
  
  return (
    <>
      <input onChange={e => handleSearch(e.target.value)} />
      {isPending && <InlineSpinner />}
      <Suspense fallback={<ResultsSkeleton />}>
        <Results query={query} />
      </Suspense>
    </>
  );
}
```

---

## 六、最佳实践

1. **合理划分边界**：按路由或功能模块设置 Suspense，避免过细或过粗
2. **提供有意义的 fallback**：使用骨架屏而非简单的 loading 文字
3. **避免瀑布流**：并行发起请求，而非串行等待
4. **配合预加载**：在用户交互前提前触发数据请求

```javascript
// 预加载示例
const resource = fetchUser(id);  // 提前发起

function Profile() {
  const user = use(resource);  // 直接使用
  return <div>{user.name}</div>;
}
```

---

## 七、注意事项

- Suspense 在服务端渲染（SSR）中需要特殊处理，React 18 提供了流式 SSR 支持
- 不是所有数据请求库都支持 Suspense，使用前查看文档
- fallback 组件应该是轻量的，避免在其中执行副作用
- 嵌套 Suspense 时，内层边界会优先生效

---

## 总结

Suspense 让异步操作的处理更加优雅和声明式。从代码分割到数据请求，它都能提供更好的开发体验和用户体验。配合 React 18 的并发特性，Suspense 将成为构建现代 React 应用的重要工具。

如果这篇文章对你有帮助，欢迎点赞收藏！
