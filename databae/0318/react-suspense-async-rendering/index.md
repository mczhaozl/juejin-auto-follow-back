# React Suspense 异步渲染完全指南

> 深入理解 Suspense 的工作原理、实战用法与最佳实践。

## 一、Suspense 是什么

React Suspense 是 React 16.6 引入的一个特性，它让你在组件等待异步数据时显示一个降落的 UI，同时保持良好的用户体验。简单来说，Suspense 允许你声明式地处理组件的「加载状态」，而无需在每个组件中手动编写 loading 逻辑。

在 Suspense 出现之前，如果你有一个组件需要从 API 获取数据，你通常需要这样做：在组件内部维护 loading 状态，数据加载时显示 loading，数据返回后渲染内容。这种方式的问题在于，每个需要异步数据的组件都要重复类似的代码，而且组件之间的加载状态难以统一管理。

Suspense 的核心思想是：**让组件「暂停」渲染，直到它需要的数据准备好**。这与传统的「先渲染再填充数据」的模式完全不同。在 Suspense 的世界里，组件声明它需要什么数据，React 负责在数据准备好之前保持组件的「暂停」状态，并渲染一个 fallback UI。

## 二、Suspense 的基本用法

### 2.1 简单示例

Suspense 的使用非常简单，只需要两个部分：一个或多个 `<Suspense>` 组件，以及它们包装的需要异步加载的子组件。

```jsx
import { Suspense } from 'react';

function App() {
  return (
    <div>
      <h1>My App</h1>
      <Suspense fallback={<Loading />}>
        <Comments />
      </Suspense>
    </div>
  );
}

function Loading() {
  return <div>Loading...</div>;
}

function Comments() {
  // Comments 组件可能需要异步获取数据
  const comments = useQuery(commentsQuery);
  return (
    <ul>
      {comments.map(comment => (
        <li key={comment.id}>{comment.text}</li>
      ))}
    </ul>
  );
}
```

在这个例子中，当 `Comments` 组件正在加载数据时，用户会看到 `<Loading />` 组件。一旦数据准备好，React 会自动用 `Comments` 的实际内容替换掉 loading UI。

### 2.2 多个 Suspense 边界

你可以嵌套使用 Suspense，为不同部分的 UI 提供独立的加载状态：

```jsx
function App() {
  return (
    <div>
      <h1>My App</h1>
      <Suspense fallback={<PageSkeleton />}>
        <MainContent />
      </Suspense>
    </div>
  );
}

function MainContent() {
  return (
    <>
      <Suspense fallback={<UserInfoSkeleton />}>
        <UserInfo />
      </Suspense>
      <Suspense fallback={<PostsSkeleton />}>
        <UserPosts />
      </Suspense>
      <Suspense fallback={<CommentsSkeleton />}>
        <RecentComments />
      </Suspense>
    </>
  );
}
```

这种嵌套结构的好处是：页面的不同部分可以独立加载和渲染。当用户信息正在加载时，帖子和评论部分可以同时显示自己的 loading 状态，而不需要等待所有数据都准备好。

### 2.3 Suspense 的 props

`<Suspense>` 组件接受两个重要的 props：

- `fallback`：在子组件正在「挂起」时渲染的 React 元素。这可以是一个简单的 loading 文本，也可以是一个复杂的动画组件。
- `maxDuration`（实验性）：指定 fallback 应该显示的最长时间。如果数据在指定时间内准备好，React 会直接渲染子组件而不显示 fallback。这对于避免 loading 闪烁很有帮助。

```jsx
<Suspense 
  fallback={<LoadingSpinner />}
  maxDuration={300}
>
  <HeavyComponent />
</Suspense>
```

## 三、Suspense 与数据获取

### 3.1 传统数据获取的问题

在深入 Suspense 之前，让我们回顾一下传统 React 数据获取的方式，以及它们为什么不够理想。

**类组件时代的做法：**

```jsx
class UserProfile extends React.Component {
  state = {
    user: null,
    loading: true,
    error: null
  };

  async componentDidMount() {
    try {
      this.setState({ loading: true });
      const user = await fetchUser(this.props.userId);
      this.setState({ user, loading: false });
    } catch (error) {
      this.setState({ error, loading: false });
    }
  }

  render() {
    const { user, loading, error } = this.state;
    
    if (loading) return <Loading />;
    if (error) return <ErrorPage error={error} />;
    
    return <UserCard user={user} />;
  }
}
```

**函数组件 + Hooks 的做法：**

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetchUser(userId)
      .then(setUser)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <Loading />;
  if (error) return <ErrorPage error={error} />;
  
  return <UserCard user={user} />;
}
```

这两种方式的共同问题是：**每个需要数据的组件都要重复编写 loading 状态的处理逻辑**。当应用变得复杂时，你会发现自己写了无数个 `if (loading) return <Loading />`。

### 3.2 Suspense 带来的范式转变

Suspense 改变了数据获取的思维方式。它不是问「数据加载完了吗」，而是问「数据准备好了吗」。这种转变带来了几个重要的好处：

首先，**关注点分离**。组件只需要声明它需要什么数据，而不需要关心数据是如何获取的。数据获取的逻辑可以集中在另一个地方。

其次，**统一的加载状态**。所有需要异步数据的组件都可以用同一个 Suspense 边界来管理加载状态，不需要在每个组件中重复编写 loading 逻辑。

第三，**更好的用户体验**。Suspense 允许你精确控制哪些部分显示 loading，以及 loading 状态的过渡动画。

### 3.3 使用 Suspense 的数据获取方案

目前有几种主流的 Suspense 数据获取方案：

**React Query / TanStack Query：**

```jsx
import { useQuery } from '@tanstack/react-query';

function UserProfile({ userId }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId)
  });

  if (isLoading) throw new Promise();
  if (error) throw error;
  
  return <UserCard user={data} />;
}
```

注意这里使用了 `throw new Promise()`。当 Suspense 检测到子组件抛出了 Promise，它会自动渲染 fallback。

**SWR：**

```jsx
import useSWR from 'swr';

function UserProfile({ userId }) {
  const { data, error, isLoading } = useSWR(
    `/api/users/${userId}`,
    fetcher
  );

  if (isLoading) throw new Promise();
  if (error) throw error;
  
  return <UserCard user={data} />;
}
```

**自定义 Suspense 数据源：**

你也可以创建自己的 Suspense 数据获取方案：

```jsx
// createResource.js
function createResource(promise) {
  let status = 'pending';
  let result;

  const suspender = promise.then(
    data => {
      status = 'success';
      result = data;
    },
    error => {
      status = 'error';
      result = error;
    }
  );

  return {
    read() {
      if (status === 'pending') throw suspender;
      if (status === 'error') throw result;
      return result;
    }
  };
}

// 使用
const userResource = createResource(fetchUser(userId));

function UserProfile() {
  const user = userResource.read();
  return <UserCard user={user} />;
}
```

## 四、Suspense 与错误边界

Suspense 只能处理「组件挂起」的情况，不能直接处理渲染错误。对于渲染错误（如组件内部抛出异常），你需要使用错误边界（Error Boundary）。

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    logError(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorPage error={this.state.error} />;
    }
    return this.props.children;
  }
}

// 结合使用
function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<Loading />}>
        <MainContent />
      </Suspense>
    </ErrorBoundary>
  );
}
```

这种组合方式可以同时处理加载状态和渲染错误，提供完整的错误处理方案。

## 五、Suspense 在 React 18 的演进

React 18 对 Suspense 进行了进一步的增强，特别是在并发渲染方面的支持。

### 5.1 过渡效果与 Suspense

React 18 引入了 `startTransition` API，它与 Suspense 配合使用可以实现更精细的渲染控制：

```jsx
import { startTransition, Suspense } from 'react';

function SearchResults({ query }) {
  return (
    <Suspense fallback={<Loading />}>
      <Results query={query} />
    </Suspense>
  );
}

function App() {
  const [query, setQuery] = useState('');
  
  function handleChange(e) {
    // 紧急更新：输入框立即响应
    setQuery(e.target.value);
    
    // 非紧急更新：搜索结果可以等待
    startTransition(() => {
      // 这个更新会被标记为「可中断」
      // 如果用户继续输入，当前的搜索会被取消
      setSearchQuery(e.target.value);
    });
  }
  
  return (
    <>
      <input onChange={handleChange} />
      <SearchResults query={searchQuery} />
    </>
  );
}
```

### 5.2 新的 useDeferredValue

`useDeferredValue` 也可以与 Suspense 配合使用：

```jsx
import { useDeferredValue, Suspense } from 'react';

function SearchResults({ query }) {
  const deferredQuery = useDeferredValue(query);
  
  return (
    <Suspense fallback={<Loading />}>
      <ResultsList query={deferredQuery} />
    </Suspense>
  );
}
```

## 六、Suspense 的性能优化

### 6.1 预加载数据

你可以在用户交互发生之前就开始预加载数据：

```jsx
import { preload } from 'react-dom';

function ProductCard({ product }) {
  const handleMouseEnter = () => {
    // 用户悬停时开始预加载详情数据
    preload(`/api/products/${product.id}`, fetch);
  };

  return (
    <div onMouseEnter={handleMouseEnter}>
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
    </div>
  );
}
```

### 6.2 合理划分 Suspense 边界

Suspense 边界的划分对性能有重要影响。边界太粗会导致不必要的 loading，边界太细会增加代码复杂度。

```jsx
// 不好的例子：整个页面一个 Suspense
function Page() {
  return (
    <Suspense fallback={<PageLoading />}>
      <Header />
      <Sidebar />
      <MainContent />
      <Footer />
    </Suspense>
  );
}

// 好的例子：按需划分边界
function Page() {
  return (
    <>
      <Header />
      <div className="content">
        <Suspense fallback={<SidebarSkeleton />}>
          <Sidebar />
        </Suspense>
        <Suspense fallback={<MainSkeleton />}>
          <MainContent />
        </Suspense>
      </div>
      <Footer />
    </>
  );
}
```

### 6.3 避免 Suspense 闪烁

当数据加载非常快时，频繁显示和隐藏 loading UI 会造成视觉闪烁。使用 `maxDuration` 可以缓解这个问题：

```jsx
<Suspense fallback={<Loading />} maxDuration={300}>
  <Content />
</Suspense>
```

如果数据在 300ms 内准备好，React 会直接渲染内容而不显示 loading。

## 七、Suspense 的限制与注意事项

Suspense 虽然强大，但也有一些限制需要注意。

首先，**Suspense 只能捕获 Promise 抛出**。如果你的组件抛出其他类型的错误，Suspense 不会捕获它。确保你的数据获取逻辑只抛出 Promise 来触发 Suspense。

其次，**服务端渲染（SSR）支持有限**。虽然 React 18 的流式 SSR 支持 Suspense，但在某些场景下 Suspense 的行为可能与客户端不同。

第三，**不要在条件渲染中使用 Suspense**。Suspense 组件必须在渲染时存在才能工作：

```jsx
// 错误：条件渲染 Suspense
{showContent && (
  <Suspense fallback={<Loading />}>
    <Content />
  </Suspense>
)}

// 正确：Suspense 始终存在，内容条件渲染
<Suspense fallback={<Loading />}>
  {showContent ? <Content /> : null}
</Suspense>
```

第四，**注意 Suspense 的嵌套层级**。过深的嵌套会增加 React 的协调开销，影响性能。

## 八、实战：构建一个 Suspense 驱动的应用

下面是一个完整的示例，展示如何构建一个 Suspense 驱动的应用：

```jsx
// api.js - 数据获取层
async function fetchUser(userId) {
  const res = await fetch(`/api/users/${userId}`);
  if (!res.ok) throw new Error('Failed to fetch user');
  return res.json();
}

async function fetchUserPosts(userId) {
  const res = await fetch(`/api/users/${userId}/posts`);
  if (!res.ok) throw new Error('Failed to fetch posts');
  return res.json();
}

async function fetchUserComments(userId) {
  const res = await fetch(`/api/users/${userId}/comments`);
  if (!res.ok) throw new Error('Failed to fetch comments');
  return res.json();
}

// resources.js - 资源创建
function createResource(promise) {
  let status = 'pending';
  let result;
  let error;

  const promiseThen = promise.then(
    value => {
      status = 'success';
      result = value;
    },
    err => {
      status = 'error';
      error = err;
    }
  );

  return {
    read() {
      if (status === 'pending') throw promiseThen;
      if (status === 'error') throw error;
      return result;
    }
  };
}

// components.js - 组件层
function UserProfile({ userId }) {
  const userResource = createResource(fetchUser(userId));
  const user = userResource.read();
  
  return (
    <div className="user-profile">
      <img src={user.avatar} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.bio}</p>
    </div>
  );
}

function UserPosts({ userId }) {
  const postsResource = createResource(fetchUserPosts(userId));
  const posts = postsResource.read();
  
  return (
    <div className="user-posts">
      <h3>Posts</h3>
      {posts.map(post => (
        <article key={post.id}>
          <h4>{post.title}</h4>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </div>
  );
}

function UserComments({ userId }) {
  const commentsResource = createResource(fetchUserComments(userId));
  const comments = commentsResource.read();
  
  return (
    <div className="user-comments">
      <h3>Comments</h3>
      {comments.map(comment => (
        <div key={comment.id} className="comment">
          <p>{comment.text}</p>
          <span>{comment.date}</span>
        </div>
      ))}
    </div>
  );
}

// App.js - 主应用
function App() {
  const [userId, setUserId] = useState(1);

  return (
    <div className="app">
      <header>
        <h1>User Dashboard</h1>
        <button onClick={() => setUserId(id => id + 1)}>
          Next User
        </button>
      </header>

      <main>
        <ErrorBoundary>
          <Suspense fallback={<UserProfileSkeleton />}>
            <UserProfile userId={userId} />
          </Suspense>
          
          <div className="grid">
            <Suspense fallback={<PostsSkeleton />}>
              <UserPosts userId={userId} />
            </Suspense>
            
            <Suspense fallback={<CommentsSkeleton />}>
              <UserComments userId={userId} />
            </Suspense>
          </div>
        </ErrorBoundary>
      </main>
    </div>
  );
}
```

这个示例展示了 Suspense 的几个关键特性：独立的 Suspense 边界、错误边界的配合使用，以及资源预加载的模式。

## 总结

React Suspense 为异步数据获取提供了一种全新的编程范式。它让组件能够声明式地表达「我需要这些数据」，而 React 负责处理加载状态的管理和 UI 的切换。通过合理划分 Suspense 边界、配合错误边界使用、以及利用 React 18 的并发特性，你可以构建出用户体验优秀的应用。

如果这篇文章对你有帮助，欢迎点赞、收藏和关注。