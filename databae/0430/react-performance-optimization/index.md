# React 性能优化完全指南：从原理到实战技巧

## 一、性能问题定位

### 1.1 React DevTools Profiler

```bash
# 在 DevTools 中启用 Profiler 标签
# 录制和分析组件渲染
```

### 1.2 Chrome Performance

```bash
# Performance 面板录制，查看 React 组件渲染时间
```

---

## 二、React.memo

```jsx
// 只有 props 变化时才重新渲染
const MemoizedComponent = React.memo(function Component({ a, b }) {
  return <div>{a + b}</div>;
});

// 自定义比较函数
const Memoized = React.memo(Component, (prevProps, nextProps) => {
  return prevProps.id === nextProps.id;
});
```

---

## 三、useMemo

```jsx
import { useMemo } from 'react';

function Component({ list, filter }) {
  // 只有 list 或 filter 变化时才重新计算
  const filteredList = useMemo(() => {
    return list.filter(item => item.includes(filter));
  }, [list, filter]);

  return <div>{filteredList.map(item => <div key={item}>{item}</div>)}</div>;
}
```

---

## 四、useCallback

```jsx
import { useCallback } from 'react';

function Parent() {
  const [count, setCount] = useState(0);

  // 函数引用保持稳定
  const handleClick = useCallback(() => {
    setCount(c => c + 1);
  }, []);

  return <Child onClick={handleClick} />;
}

const Child = React.memo(({ onClick }) => {
  return <button onClick={onClick}>Click</button>;
});
```

---

## 五、useTransition

```jsx
import { useState, useTransition, startTransition } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    setQuery(e.target.value);
    
    // 非紧急更新
    startTransition(() => {
      setSearchResults(filterData(e.target.value));
    });
  };

  return (
    <div>
      <input onChange={handleChange} />
      {isPending && <span>Loading...</span>}
      {searchResults.map(result => (
        <div key={result.id}>{result.name}</div>
      ))}
    </div>
  );
}
```

---

## 六、useDeferredValue

```jsx
import { useDeferredValue } from 'react';

function SearchResults({ query }) {
  const deferredQuery = useDeferredValue(query);
  const results = useMemo(() => 
    filterData(deferredQuery), [deferredQuery]
  );

  return (
    <div>
      {results.map(result => (
        <div key={result.id}>{result.name}</div>
      ))}
    </div>
  );
}
```

---

## 七、虚拟化长列表

```jsx
import { FixedSizeList } from 'react-window';

function LongList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>Item {items[index]}</div>
  );

  return (
    <FixedSizeList
      height={600}
      width='100%'
      itemCount={items.length}
      itemSize={50}
    >
      {Row}
    </FixedSizeList>
  );
}
```

---

## 八、代码分割

```jsx
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

---

## 九、状态提升与下推

```jsx
// 不好：整个大组件都重新渲染
function Parent() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
      <ExpensiveTree />
    </div>
  );
}

// 好：状态下推，只重新渲染必要部分
function Parent() {
  return (
    <div>
      <Counter />
      <ExpensiveTree />
    </div>
  );
}

function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>;
}
```

---

## 十、Context 优化

```jsx
// 分离 Context
const ThemeContext = createContext();
const UserContext = createContext();

function App() {
  return (
    <ThemeContext.Provider value={theme}>
      <UserContext.Provider value={user}>
        <Main />
      </UserContext.Provider>
    </ThemeContext.Provider>
  );
}

// 使用 useMemo 优化 Provider 的 value
const MemoizedValue = useMemo(() => ({
  theme,
  toggleTheme
}), [theme]);
```

---

## 十一、最佳实践

1. 使用 Profiler 定位性能问题
2. 合理使用 memo、useMemo、useCallback
3. 避免不必要的重新渲染
4. 使用虚拟化处理大列表
5. 代码分割，按需加载

---

## 十二、总结

React 性能优化需要先测量，再针对性优化，避免过早优化。
