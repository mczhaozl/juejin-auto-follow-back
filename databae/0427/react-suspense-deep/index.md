# React Suspense 深度解析与实战

> 深入理解 React Suspense，掌握并发特性，构建更好的用户体验。

## 一、Suspense 概述

Suspense 是 React 的并发特性，让组件可以在加载完成前显示 fallback 内容。

### 1.1 解决的问题

```jsx
// 传统方式
function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchUser().then(data => {
      setUser(data);
      setLoading(false);
    });
  }, []);
  
  if (loading) return <Loading />;
  return <Profile user={user} />;
}

// Suspense 方式
function UserProfile() {
  return (
    <Suspense fallback={<Loading />}>
      <Profile user={fetchUser()} />
    </Suspense>
  );
}
```

---

## 二、Suspense 基础

### 2.1 基本用法

```jsx
import { Suspense } from 'react';

function App() {
  return (
    <div>
      <h1>我的应用</h1>
      <Suspense fallback={<Loading />}>
        <DataComponent />
      </Suspense>
    </div>
  );
}

function DataComponent() {
  const data = fetchData(); // 这个函数会抛出 Promise
  return <div>{data}</div>;
}
```

### 2.2 Suspense 的工作原理

1. 子组件抛出 Promise
2. Suspense 捕获 Promise
3. 显示 fallback
4. Promise resolve 后重新渲染
5. 显示实际内容

---

## 三、创建支持 Suspense 的资源

### 3.1 简单的资源包装器

```javascript
function wrapPromise(promise) {
  let status = 'pending';
  let result;
  
  const suspender = promise.then(
    value => {
      status = 'success';
      result = value;
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
      if (status === 'success') return result;
    }
  };
}
```

### 3.2 使用包装器

```jsx
// 创建资源
const userResource = wrapPromise(fetchUser());

function UserProfile() {
  const user = userResource.read(); // 可能抛出 Promise
  return <div>{user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <UserProfile />
    </Suspense>
  );
}
```

---

## 四、Suspense 边界

### 4.1 多层 Suspense

```jsx
function App() {
  return (
    <Suspense fallback={<BigSpinner />}>
      <Header />
      <Suspense fallback={<ContentSpinner />}>
        <MainContent />
      </Suspense>
      <Sidebar />
    </Suspense>
  );
}
```

### 4.2 错误边界配合

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorMessage />;
    }
    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<Loading />}>
        <DataComponent />
      </Suspense>
    </ErrorBoundary>
  );
}
```

---

## 五、SuspenseList 协调多个 Suspense

### 5.1 Reveal Order

```jsx
import { Suspense, SuspenseList } from 'react';

function App() {
  return (
    <SuspenseList revealOrder="forwards">
      <Suspense fallback={<Loading1 />}>
        <Component1 />
      </Suspense>
      <Suspense fallback={<Loading2 />}>
        <Component2 />
      </Suspense>
      <Suspense fallback={<Loading3 />}>
        <Component3 />
      </Suspense>
    </SuspenseList>
  );
}
```

revealOrder 选项：
- `forwards`：从前到后显示
- `backwards`：从后到前显示
- `together`：所有准备好后一起显示

### 5.2 Tail 选项

```jsx
<SuspenseList revealOrder="forwards" tail="collapsed">
  {/* 只显示第一个 fallback */}
</SuspenseList>

<SuspenseList revealOrder="forwards" tail="hidden">
  {/* 不显示后面的 fallback */}
</SuspenseList>
```

---

## 六、实战案例一：数据预加载

### 6.1 路由级预加载

```jsx
// 在路由变化时开始加载
const routes = {
  '/users': () => {
    const users = wrapPromise(fetchUsers());
    return () => <UsersPage users={users} />;
  }
};

function Router() {
  const [path, setPath] = useState('/');
  const PageComponent = routes[path]();
  
  return (
    <Suspense fallback={<Loading />}>
      <PageComponent />
    </Suspense>
  );
}
```

### 6.2 组件预加载

```jsx
// 提前加载数据
const preload = {
  user: wrapPromise(fetchUser()),
  posts: wrapPromise(fetchPosts())
};

function App() {
  return (
    <div>
      <button onClick={() => setShowUser(true)}>
        查看用户
      </button>
      {showUser && (
        <Suspense fallback={<Loading />}>
          <UserProfile user={preload.user} />
        </Suspense>
      )}
    </div>
  );
}
```

---

## 七、实战案例二：图片懒加载

### 7.1 Suspense Image

```jsx
function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(src);
    img.onerror = reject;
    img.src = src;
  });
}

function SuspenseImage({ src, alt }) {
  const resource = wrapPromise(loadImage(src));
  resource.read(); // 抛 Promise
  return <img src={src} alt={alt} />;
}

// 使用
function Gallery() {
  return (
    <SuspenseList revealOrder="together">
      {images.map(img => (
        <Suspense key={img.id} fallback={<Skeleton />}>
          <SuspenseImage src={img.src} alt={img.alt} />
        </Suspense>
      ))}
    </SuspenseList>
  );
}
```

---

## 八、使用 Relay 或 SWR

### 8.1 SWR 与 Suspense

```jsx
import useSWR from 'swr';

function UserProfile() {
  const { data: user } = useSWR('/api/user', fetcher, {
    suspense: true
  });
  
  return <div>{user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <UserProfile />
    </Suspense>
  );
}
```

### 8.2 React Query 与 Suspense

```jsx
import { useQuery } from 'react-query';

function UserProfile() {
  const { data: user } = useQuery('user', fetchUser, {
    suspense: true
  });
  
  return <div>{user.name}</div>;
}
```

---

## 九、Suspense 与并发渲染

### 9.1 useTransition

```jsx
import { useTransition, Suspense } from 'react';

function TabContainer() {
  const [tab, setTab] = useState('home');
  const [isPending, startTransition] = useTransition();
  
  function selectTab(nextTab) {
    startTransition(() => {
      setTab(nextTab);
    });
  }
  
  return (
    <div>
      <button onClick={() => selectTab('home')}>Home</button>
      <button onClick={() => selectTab('profile')}>Profile</button>
      {isPending && <Spinner />}
      <Suspense fallback={<TabFallback />}>
        {tab === 'home' && <HomeTab />}
        {tab === 'profile' && <ProfileTab />}
      </Suspense>
    </div>
  );
}
```

### 9.2 useDeferredValue

```jsx
import { useDeferredValue, Suspense } from 'react';

function SearchResults({ query }) {
  const deferredQuery = useDeferredValue(query);
  
  return (
    <Suspense fallback={<Loading />}>
      <Results query={deferredQuery} />
    </Suspense>
  );
}
```

---

## 十、最佳实践

1. **合理使用 Suspense 边界**
2. **预加载数据**
3. **配合错误边界**
4. **使用 SuspenseList**
5. **避免过度嵌套**
6. **考虑用户体验**

---

## 十一、总结

Suspense 是 React 并发特性的核心，让数据加载声明式化。通过合理使用，可以构建更流畅的用户体验。

希望这篇文章对你有帮助！
