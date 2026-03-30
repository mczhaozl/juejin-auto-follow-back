# React Hooks 深入指南：useState、useEffect 与自定义 Hook

> 深入讲解 React Hooks 核心概念，包括 useState、useEffect、useRef、useContext 等，以及自定义 Hook 的编写技巧。

## 一、useState

### 1.1 基本用法

```javascript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        增加
      </button>
    </div>
  );
}
```

### 1.2 多个状态

```javascript
const [name, setName] = useState('');
const [age, setAge] = useState(0);
const [isActive, setIsActive] = useState(false);
```

### 1.3 函数式更新

```javascript
// 错误的写法
setCount(count + 1);

// 正确的写法（基于前一个值）
setCount(prevCount => prevCount + 1);
```

## 二、useEffect

### 2.1 基本用法

```javascript
import { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => setUser(data));
  }, [userId]);
  
  return <div>{user?.name}</div>;
}
```

### 2.2 清理函数

```javascript
useEffect(() => {
  const subscription = props.source.subscribe();
  
  return () => {
    subscription.unsubscribe();
  };
}, [props.source]);
```

### 2.3 依赖数组

```javascript
// 每次渲染都执行
useEffect(() => {
  console.log('每次渲染');
});

// 只执行一次（类似 componentDidMount）
useEffect(() => {
  console.log('只执行一次');
}, []);

// 依赖变化时执行
useEffect(() => {
  console.log('count 变化');
}, [count]);
```

## 三、useRef

### 3.1 引用 DOM

```javascript
function TextInput() {
  const inputRef = useRef(null);
  
  const focusInput = () => {
    inputRef.current.focus();
  };
  
  return (
    <>
      <input ref={inputRef} />
      <button onClick={focusInput}>聚焦</button>
    </>
  );
}
```

### 3.2 存储可变值

```javascript
function Timer() {
  const countRef = useRef(0);
  const [display, setDisplay] = useState(0);
  
  const increment = () => {
    countRef.current++;
    setDisplay(countRef.current);
  };
  
  return <button onClick={increment}>{display}</button>;
}
```

## 四、useContext

### 4.1 创建 Context

```javascript
const ThemeContext = createContext('light');

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}
```

### 4.2 使用 Context

```javascript
function Toolbar() {
  const theme = useContext(ThemeContext);
  
  return <div className={theme}>内容</div>;
}
```

## 五、自定义 Hook

### 5.1 useWindowSize

```javascript
function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });
  
  useEffect(() => {
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return size;
}
```

### 5.2 useFetch

```javascript
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    setLoading(true);
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, [url]);
  
  return { data, loading, error };
}
```

### 5.3 useLocalStorage

```javascript
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : initialValue;
  });
  
  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);
  
  return [value, setValue];
}
```

## 六、useReducer

### 6.1 基本用法

```javascript
const initialState = { count: 0 };

function reducer(state, action) {
  switch (action.type) {
    case 'increment':
      return { count: state.count + 1 };
    case 'decrement':
      return { count: state.count - 1 };
    default:
      return state;
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, initialState);
  
  return (
    <>
      <p>计数: {state.count}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
    </>
  );
}
```

## 七、性能优化

### 7.1 useCallback

```javascript
const handleClick = useCallback(() => {
  console.log(count);
}, [count]);
```

### 7.2 useMemo

```javascript
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);
```

## 八、总结

React Hooks 核心要点：

1. **useState**：管理组件状态
2. **useEffect**：处理副作用
3. **useRef**：引用和可变值
4. **useContext**：跨组件通信
5. **自定义 Hook**：复用逻辑
6. **useReducer**：复杂状态管理
7. **性能优化**：useCallback、useMemo

掌握这些，React 开发更高效！

---

**推荐阅读**：
- [React Hooks 官方文档](https://react.dev/reference/react)

**如果对你有帮助，欢迎点赞收藏！**
