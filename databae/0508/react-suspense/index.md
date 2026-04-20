# React Suspense 完全指南

## 一、基础 Suspense

```tsx
import { Suspense } from 'react';

function AsyncComponent() {
  // 抛出 Promise 触发 Suspense
  if (data === null) throw fetchData();
  return <div>{data}</div>;
}

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <AsyncComponent />
    </Suspense>
  );
}
```

## 二、Suspense 和 React Query

```tsx
import { useQuery } from '@tanstack/react-query';

function UserProfile({ userId }) {
  const { data: user } = useQuery({ 
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    suspense: true
  });
  
  return <div>{user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<LoadingUser />}>
      <UserProfile userId="1" />
    </Suspense>
  );
}
```

## 三、嵌套 Suspense

```tsx
function Dashboard() {
  return (
    <div>
      <Suspense fallback={<MainLoading />}>
        <MainContent />
        <Suspense fallback={<SidebarLoading />}>
          <Sidebar />
        </Suspense>
      </Suspense>
    </div>
  );
}
```

## 四、错误边界与 Suspense

```tsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) return <div>出错了</div>;
    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<Loading />}>
        <MyComponent />
      </Suspense>
    </ErrorBoundary>
  );
}
```

## 五、最佳实践

- 合理组织 Suspense 边界
- 与错误边界配合使用
- 使用 React Query/SWR 等库
- 流式数据获取策略
- 骨架屏优化用户体验
- 监控 Suspense 性能
