# React Concurrent Features 完全指南

## 一、Suspense

```tsx
import { Suspense, lazy } from 'react';

// 延迟加载
const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        <LazyComponent />
      </Suspense>
    </div>
  );
}
```

## 二、Transitions

```tsx
import { useState, useTransition } from 'react';

function App() {
  const [isPending, startTransition] = useTransition();
  const [query, setQuery] = useState('');

  function handleChange(e) {
    setQuery(e.target.value); // 紧急更新
    startTransition(() => {
      setSearchResults(e.target.value); // 非紧急更新
    });
  }

  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending && <div>Searching...</div>}
    </div>
  );
}
```

## 三、useDeferredValue

```tsx
import { useState, useDeferredValue } from 'react';

function App() {
  const [text, setText] = useState('');
  const deferredText = useDeferredValue(text);

  return (
    <>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      <SlowComponent text={deferredText} />
    </>
  );
}
```

## 四、StartTransition

```tsx
import { startTransition } from 'react';

function handleClick() {
  // 紧急更新
  setActiveTab('profile');
  
  startTransition(() => {
    // 非紧急更新
    setExpensiveData(fetchData());
  });
}
```

## 最佳实践
- 区分紧急与非紧急更新
- 利用 Suspense 展示加载状态
- 注意 SSR 与并发渲染的兼容性
- 使用 useDeferredValue 延迟更新
- 避免过度使用 Transitions
