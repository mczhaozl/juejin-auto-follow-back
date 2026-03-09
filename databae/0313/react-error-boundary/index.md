# React Error Boundary：优雅处理组件错误的正确姿势

> 从错误捕获到降级 UI，掌握 React 错误边界的完整用法

---

## 一、为什么需要 Error Boundary

在 React 中，组件内部的 JavaScript 错误会导致整个应用崩溃，白屏给用户。

```javascript
function UserProfile() {
  const user = props.user;
  return <div>{user.name}</div>;  // 如果 user 是 null，应用崩溃
}
```

Error Boundary 可以捕获子组件树中的错误，显示降级 UI，而不是让整个应用崩溃。

---

## 二、基础用法

Error Boundary 是一个类组件，实现 `getDerivedStateFromError` 或 `componentDidCatch`。

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // 更新 state，下次渲染显示降级 UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // 可以将错误日志上报给服务器
    console.error('捕获到错误:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>出错了，请刷新页面重试</h1>;
    }

    return this.props.children;
  }
}
```

使用：

```javascript
<ErrorBoundary>
  <UserProfile />
</ErrorBoundary>
```

---

## 三、两个生命周期的区别

### getDerivedStateFromError

- 在渲染阶段调用
- 用于更新 state，显示降级 UI
- 不能有副作用（如日志上报）

```javascript
static getDerivedStateFromError(error) {
  return { hasError: true, error };
}
```

### componentDidCatch

- 在提交阶段调用
- 用于执行副作用（日志上报、错误监控）
- 可以访问错误堆栈信息

```javascript
componentDidCatch(error, errorInfo) {
  // errorInfo.componentStack 包含组件堆栈信息
  logErrorToService(error, errorInfo);
}
```

---

## 四、完整的 Error Boundary 实现

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // 上报错误
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render() {
    if (this.state.hasError) {
      // 自定义降级 UI
      if (this.props.fallback) {
        return this.props.fallback({
          error: this.state.error,
          errorInfo: this.state.errorInfo,
          resetError: this.resetError
        });
      }

      // 默认降级 UI
      return (
        <div style={{ padding: 20 }}>
          <h2>出错了</h2>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </details>
          <button onClick={this.resetError}>重试</button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## 五、实战场景

### 场景 1：路由级别的错误边界

```javascript
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={
          <ErrorBoundary fallback={<PageError />}>
            <Home />
          </ErrorBoundary>
        } />
        <Route path="/profile" element={
          <ErrorBoundary fallback={<PageError />}>
            <Profile />
          </ErrorBoundary>
        } />
      </Routes>
    </Router>
  );
}
```

### 场景 2：组件级别的错误边界

```javascript
function Dashboard() {
  return (
    <div>
      <ErrorBoundary fallback={<WidgetError />}>
        <UserWidget />
      </ErrorBoundary>
      
      <ErrorBoundary fallback={<WidgetError />}>
        <StatsWidget />
      </ErrorBoundary>
      
      <ErrorBoundary fallback={<WidgetError />}>
        <ChartWidget />
      </ErrorBoundary>
    </div>
  );
}
```

一个组件出错不会影响其他组件。

### 场景 3：与 Suspense 配合

```javascript
<ErrorBoundary fallback={<ErrorUI />}>
  <Suspense fallback={<Loading />}>
    <LazyComponent />
  </Suspense>
</ErrorBoundary>
```

- Suspense 处理加载状态
- ErrorBoundary 处理加载失败

### 场景 4：自定义降级 UI

```javascript
<ErrorBoundary
  fallback={({ error, resetError }) => (
    <div className="error-container">
      <h2>加载失败</h2>
      <p>{error.message}</p>
      <button onClick={resetError}>重新加载</button>
      <button onClick={() => window.location.href = '/'}>
        返回首页
      </button>
    </div>
  )}
>
  <DataComponent />
</ErrorBoundary>
```

---

## 六、Error Boundary 的局限

Error Boundary **无法**捕获以下错误：

1. **事件处理器中的错误**

```javascript
function Button() {
  const handleClick = () => {
    throw new Error('点击错误');  // Error Boundary 捕获不到
  };
  
  return <button onClick={handleClick}>点击</button>;
}

// 解决：手动 try-catch
const handleClick = () => {
  try {
    // 可能出错的代码
  } catch (error) {
    // 处理错误
  }
};
```

2. **异步代码中的错误**

```javascript
useEffect(() => {
  setTimeout(() => {
    throw new Error('异步错误');  // 捕获不到
  }, 1000);
}, []);

// 解决：手动 try-catch
useEffect(() => {
  setTimeout(() => {
    try {
      // 可能出错的代码
    } catch (error) {
      // 处理错误
    }
  }, 1000);
}, []);
```

3. **服务端渲染（SSR）中的错误**

4. **Error Boundary 自身的错误**

---

## 七、使用第三方库

### react-error-boundary

更强大的 Error Boundary 库，支持函数组件。

```bash
npm install react-error-boundary
```

```javascript
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert">
      <p>出错了:</p>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>重试</button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => {
        // 重置应用状态
      }}
      onError={(error, errorInfo) => {
        // 上报错误
        logError(error, errorInfo);
      }}
    >
      <MyApp />
    </ErrorBoundary>
  );
}
```

使用 Hook：

```javascript
import { useErrorHandler } from 'react-error-boundary';

function AsyncComponent() {
  const handleError = useErrorHandler();
  
  useEffect(() => {
    fetchData().catch(handleError);  // 异步错误也能捕获
  }, []);
  
  return <div>内容</div>;
}
```

---

## 八、错误上报

### 集成 Sentry

```javascript
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: 'your-sentry-dsn',
  environment: process.env.NODE_ENV,
});

class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    Sentry.captureException(error, {
      contexts: {
        react: {
          componentStack: errorInfo.componentStack
        }
      }
    });
  }
  
  // ...
}
```

### 自定义上报

```javascript
function logError(error, errorInfo) {
  fetch('/api/log-error', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: Date.now()
    })
  });
}
```

---

## 九、最佳实践

1. **多层边界**：在不同层级设置 Error Boundary

```javascript
<ErrorBoundary>  {/* 应用级 */}
  <App>
    <ErrorBoundary>  {/* 页面级 */}
      <Page>
        <ErrorBoundary>  {/* 组件级 */}
          <Widget />
        </ErrorBoundary>
      </Page>
    </ErrorBoundary>
  </App>
</ErrorBoundary>
```

2. **提供重试机制**：让用户可以重新加载

```javascript
<ErrorBoundary
  fallback={({ resetError }) => (
    <button onClick={resetError}>重试</button>
  )}
>
  <Component />
</ErrorBoundary>
```

3. **区分环境**：开发环境显示详细错误，生产环境显示友好提示

```javascript
const isDev = process.env.NODE_ENV === 'development';

<ErrorBoundary
  fallback={({ error }) => (
    <div>
      <h2>出错了</h2>
      {isDev && <pre>{error.stack}</pre>}
    </div>
  )}
>
  <Component />
</ErrorBoundary>
```

4. **配合监控**：所有错误都应该上报

```javascript
componentDidCatch(error, errorInfo) {
  // 上报到监控平台
  logError(error, errorInfo);
  
  // 通知开发者（生产环境）
  if (process.env.NODE_ENV === 'production') {
    notifyDevelopers(error);
  }
}
```

---

## 十、常见问题

### 1. 为什么必须是类组件？

React 团队计划在未来支持函数组件的 Error Boundary，但目前还没有。可以使用 `react-error-boundary` 库。

### 2. 如何捕获事件处理器中的错误？

手动 try-catch 或使用 `useErrorHandler` Hook。

### 3. Error Boundary 会影响性能吗？

几乎没有影响，只在出错时才会执行额外逻辑。

---

## 总结

Error Boundary 是 React 应用健壮性的重要保障。通过合理设置错误边界，可以：

- 防止整个应用崩溃
- 提供友好的降级 UI
- 收集错误信息用于改进
- 提升用户体验

建议在每个 React 项目中都配置好 Error Boundary，并集成错误监控服务。

如果这篇文章对你有帮助，欢迎点赞收藏！
