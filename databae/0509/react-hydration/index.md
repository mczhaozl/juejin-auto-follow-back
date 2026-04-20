# React 水合完全指南

## 一、基础水合

```tsx
import { hydrateRoot } from 'react-dom/client';

const root = document.getElementById('root');
hydrateRoot(root, <App />);
```

## 二、水合不匹配处理

```tsx
// 客户端与服务端输出不一致
'use client';
import { useState, useEffect } from 'react';

function ClientOnlyComponent() {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  if (!mounted) return null;
  return <div>客户端内容</div>;
}
```

## 三、suppressHydrationWarning

```tsx
function Component() {
  const [date, setDate] = useState(new Date());
  
  useEffect(() => {
    setDate(new Date());
  }, []);
  
  return (
    <div suppressHydrationWarning>
      {date.toString()}
    </div>
  );
}
```

## 四、流式水合

```tsx
// 使用 Suspense 和流式 SSR
import { Suspense } from 'react';

function Page() {
  return (
    <div>
      <Header />
      <Suspense fallback={<Spinner />}>
        <MainContent />
      </Suspense>
      <Suspense fallback={<Spinner />}>
        <Sidebar />
      </Suspense>
    </div>
  );
}
```

## 五、水合优化

```tsx
// 使用 startTransition 延迟非紧急更新
import { startTransition, useState } from 'react';

function App() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    startTransition(() => {
      setData(fetchData());
    });
  }, []);
}
```

## 六、最佳实践

- 确保客户端与服务端输出一致
- 合理组织 Suspense 边界
- 使用 startTransition 优化交互
- 监控 TTI 指标
- 避免在水合前访问浏览器 API
- 处理动态内容的特殊情况
