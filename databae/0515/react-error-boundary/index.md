# React Error Boundary 完全指南

## 一、类组件错误边界

```tsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong.</div>;
    }
    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <ComponentMightThrow />
    </ErrorBoundary>
  );
}
```

## 二、react-error-boundary 库

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function fallbackRender({ error, resetErrorBoundary }) {
  return (
    <div>
      <p>Something went wrong: {error.message}</p>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

<ErrorBoundary fallbackRender={fallbackRender}>
  <App />
</ErrorBoundary>
```

## 三、错误上报

```tsx
componentDidCatch(error, info) {
  Sentry.captureException(error, {
    extra: { componentStack: info.componentStack }
  });
}
```

## 最佳实践
- 关键组件添加错误边界
- 错误边界尽量细粒度
- 提供友好的 fallback UI
- 记录和上报错误
- 允许用户重试
