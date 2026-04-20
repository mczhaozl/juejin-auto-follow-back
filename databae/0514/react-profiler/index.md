# React Profiler 完全指南

## 一、Profiler 组件

```tsx
import { Profiler } from 'react';

function onRenderCallback(
  id,
  phase,
  actualDuration,
  baseDuration,
  startTime,
  commitTime,
  interactions
) {
  console.log(id, phase, actualDuration, interactions);
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <MainComponent />
    </Profiler>
  );
}
```

## 二、useEffect 与性能

```tsx
import { useState, useEffect, useRef } from 'react';

function App() {
  const [count, setCount] = useState(0);
  const prevCountRef = useRef(0);
  
  useEffect(() => {
    if (prevCountRef.current !== count) {
      console.log('Count changed from', prevCountRef.current, 'to', count);
    }
    prevCountRef.current = count;
  }, [count]);
}
```

## 三、React DevTools

```tsx
// 1. 打开 DevTools
// 2. 进入 Profiler 标签
// 3. 点击 Record
// 4. 与应用交互
// 5. 停止并查看火焰图
```

## 四、memo 与 useMemo

```tsx
import { memo, useMemo, useCallback } from 'react';

const ExpensiveComponent = memo(function({ data, onClick }) {
  return <div>{data.map(d => d)}</div>;
});

function Parent() {
  const data = useMemo(() => [1, 2, 3], []);
  const onClick = useCallback(() => {}, []);
  
  return <ExpensiveComponent data={data} onClick={onClick} />;
}
```

## 最佳实践
- 使用 Profiler 定位性能问题
- useMemo/useCallback 优化渲染
- React DevTools 火焰图分析
- 避免过度优化
- 定期性能基准测试
