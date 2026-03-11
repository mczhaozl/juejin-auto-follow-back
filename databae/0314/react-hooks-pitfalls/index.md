# React Hooks 避坑指南：那些让你 debug 到凌晨的陷阱

> 从闭包陷阱到依赖地狱，从无限循环到内存泄漏，这些 Hooks 的坑我都踩过。这篇文章帮你避开它们。

---

## 一、凌晨三点的 Bug

上周五晚上十点，准备下班。突然测试同学发来消息：「你这个计数器有问题，点了半天还是 0。」

我心想，一个计数器能有什么问题？打开代码一看：

```javascript
function Counter() {
  const [count, setCount] = useState(0);

  const handleClick = () => {
    setTimeout(() => {
      setCount(count + 1);
    }, 3000);
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>+1 (延迟 3 秒)</button>
    </div>
  );
}
```

看起来没问题啊。但实际运行时，快速点击 5 次按钮，3 秒后 count 只变成 1，而不是 5。

这就是 Hooks 的第一个大坑：**闭包陷阱**。

那天晚上我 debug 到凌晨三点，才把所有 Hooks 的坑都踩了一遍。今天就来聊聊这些让人头秃的陷阱，以及怎么避开它们。

## 二、闭包陷阱：useState 的「时光机」

### 2.1 问题重现

```javascript
function Counter() {
  const [count, setCount] = useState(0);

  const handleClick = () => {
    setTimeout(() => {
      setCount(count + 1);  // 这里的 count 是点击时的值
    }, 3000);
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>+1 (延迟 3 秒)</button>
    </div>
  );
}
```

**现象**：
1. 快速点击 5 次按钮
2. 3 秒后，count 只变成 1（而不是 5）

**原因**：

每次点击时，`handleClick` 函数都会捕获当时的 `count` 值（闭包）。5 次点击时 `count` 都是 0，所以 5 个 `setTimeout` 都执行 `setCount(0 + 1)`，最终结果是 1。

### 2.2 解决方案

**方案 1：函数式更新**

```javascript
const handleClick = () => {
  setTimeout(() => {
    setCount(prevCount => prevCount + 1);  // 使用最新的 count
  }, 3000);
};
```

**方案 2：使用 useRef**

```javascript
function Counter() {
  const [count, setCount] = useState(0);
  const countRef = useRef(count);

  useEffect(() => {
    countRef.current = count;
  }, [count]);

  const handleClick = () => {
    setTimeout(() => {
      setCount(countRef.current + 1);
    }, 3000);
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>+1 (延迟 3 秒)</button>
    </div>
  );
}
```

**方案 3：使用 useReducer**

```javascript
function reducer(state, action) {
  switch (action.type) {
    case 'increment':
      return { count: state.count + 1 };
    default:
      return state;
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0 });

  const handleClick = () => {
    setTimeout(() => {
      dispatch({ type: 'increment' });  // 不依赖闭包
    }, 3000);
  };

  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={handleClick}>+1 (延迟 3 秒)</button>
    </div>
  );
}
```

### 2.3 更隐蔽的闭包陷阱

```javascript
function SearchBox() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = () => {
    fetchResults(query).then(data => {
      setResults(data);
    });
  };

  useEffect(() => {
    const timer = setInterval(() => {
      console.log('Current query:', query);  // 永远打印初始值
    }, 1000);

    return () => clearInterval(timer);
  }, []);  // 空依赖数组导致闭包

  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <button onClick={handleSearch}>Search</button>
    </div>
  );
}
```

**问题**：`setInterval` 里的 `query` 永远是初始值（空字符串）。

**原因**：`useEffect` 的依赖数组是空的，effect 只执行一次，闭包捕获的是初始的 `query`。

**解决**：

```javascript
useEffect(() => {
  const timer = setInterval(() => {
    console.log('Current query:', query);
  }, 1000);

  return () => clearInterval(timer);
}, [query]);  // 添加 query 依赖
```

或者用 `useRef`：

```javascript
const queryRef = useRef(query);

useEffect(() => {
  queryRef.current = query;
}, [query]);

useEffect(() => {
  const timer = setInterval(() => {
    console.log('Current query:', queryRef.current);
  }, 1000);

  return () => clearInterval(timer);
}, []);
```

## 三、useEffect 的依赖地狱

### 3.1 缺失依赖导致的 Bug

```javascript
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, []);  // 缺少 userId 依赖

  return <div>{user?.name}</div>;
}
```

**问题**：`userId` 变化时，不会重新获取用户数据。

**解决**：

```javascript
useEffect(() => {
  fetchUser(userId).then(setUser);
}, [userId]);  // 添加 userId 依赖
```

### 3.2 对象/数组依赖导致的无限循环

```javascript
function DataList() {
  const [data, setData] = useState([]);
  const filters = { status: 'active', type: 'user' };  // 每次渲染都是新对象

  useEffect(() => {
    fetchData(filters).then(setData);
  }, [filters]);  // filters 每次都变，导致无限循环

  return <ul>{data.map(item => <li key={item.id}>{item.name}</li>)}</ul>;
}
```

**问题**：`filters` 每次渲染都是新对象，导致 effect 无限执行。

**解决方案 1：提取到组件外**

```javascript
const DEFAULT_FILTERS = { status: 'active', type: 'user' };

function DataList() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchData(DEFAULT_FILTERS).then(setData);
  }, []);  // 依赖空数组

  return <ul>{data.map(item => <li key={item.id}>{item.name}</li>)}</ul>;
}
```

**解决方案 2：useMemo**

```javascript
function DataList() {
  const [data, setData] = useState([]);
  const filters = useMemo(() => ({ status: 'active', type: 'user' }), []);

  useEffect(() => {
    fetchData(filters).then(setData);
  }, [filters]);

  return <ul>{data.map(item => <li key={item.id}>{item.name}</li>)}</ul>;
}
```

**解决方案 3：依赖具体的值**

```javascript
function DataList() {
  const [data, setData] = useState([]);
  const status = 'active';
  const type = 'user';

  useEffect(() => {
    fetchData({ status, type }).then(setData);
  }, [status, type]);  // 依赖原始值，不依赖对象

  return <ul>{data.map(item => <li key={item.id}>{item.name}</li>)}</ul>;
}
```

### 3.3 函数依赖导致的问题

```javascript
function SearchBox() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = () => {
    fetchResults(query).then(setResults);
  };

  useEffect(() => {
    handleSearch();
  }, [handleSearch]);  // handleSearch 每次渲染都是新函数，导致无限循环

  return (
    <input value={query} onChange={e => setQuery(e.target.value)} />
  );
}
```

**解决方案 1：useCallback**

```javascript
const handleSearch = useCallback(() => {
  fetchResults(query).then(setResults);
}, [query]);

useEffect(() => {
  handleSearch();
}, [handleSearch]);
```

**解决方案 2：直接在 effect 中调用**

```javascript
useEffect(() => {
  fetchResults(query).then(setResults);
}, [query]);  // 不依赖函数，直接依赖 query
```

**解决方案 3：useEffectEvent（React 19）**

```javascript
import { useEffectEvent } from 'react';

function SearchBox() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = useEffectEvent(() => {
    fetchResults(query).then(setResults);
  });

  useEffect(() => {
    handleSearch();  // 不需要添加到依赖数组
  }, []);

  return (
    <input value={query} onChange={e => setQuery(e.target.value)} />
  );
}
```


## 四、useCallback 和 useMemo 的误用

### 4.1 过度使用导致的性能下降

```javascript
function TodoList({ todos }) {
  // ❌ 过度优化：简单组件不需要 memo
  const renderItem = useCallback((todo) => {
    return <li key={todo.id}>{todo.title}</li>;
  }, []);

  // ❌ 过度优化：简单计算不需要 useMemo
  const count = useMemo(() => todos.length, [todos]);

  // ❌ 过度优化：每个函数都 useCallback
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);

  return (
    <div>
      <p>Total: {count}</p>
      <ul>{todos.map(renderItem)}</ul>
      <button onClick={handleClick}>Log</button>
    </div>
  );
}
```

**问题**：
- `useCallback` 和 `useMemo` 本身有成本（创建闭包、比较依赖）
- 简单计算的成本可能低于 `useMemo` 的成本
- 过度使用反而降低性能

**原则**：
- 只在真正需要时使用（子组件用了 `React.memo`、计算成本高）
- 先测量，再优化
- 简单组件不需要优化

**正确示例**：

```javascript
function TodoList({ todos }) {
  // ✅ 简单计算，不需要 useMemo
  const count = todos.length;

  // ✅ 子组件没用 memo，不需要 useCallback
  const handleClick = () => {
    console.log('clicked');
  };

  return (
    <div>
      <p>Total: {count}</p>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>{todo.title}</li>
        ))}
      </ul>
      <button onClick={handleClick}>Log</button>
    </div>
  );
}
```

### 4.2 useCallback 的依赖陷阱

```javascript
function SearchBox() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({ status: 'all' });

  // ❌ 缺少 filters 依赖
  const handleSearch = useCallback(() => {
    fetchResults(query, filters).then(setResults);
  }, [query]);  // filters 变化时不会更新

  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <button onClick={handleSearch}>Search</button>
    </div>
  );
}
```

**解决**：

```javascript
const handleSearch = useCallback(() => {
  fetchResults(query, filters).then(setResults);
}, [query, filters]);  // 添加所有依赖
```

但这又导致新问题：`filters` 是对象，每次渲染都变，`useCallback` 失效。

**更好的解决方案**：

```javascript
function SearchBox() {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('all');  // 用原始值代替对象

  const handleSearch = useCallback(() => {
    fetchResults(query, { status }).then(setResults);
  }, [query, status]);  // 依赖原始值

  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <select value={status} onChange={e => setStatus(e.target.value)}>
        <option value="all">All</option>
        <option value="active">Active</option>
      </select>
      <button onClick={handleSearch}>Search</button>
    </div>
  );
}
```

### 4.3 useMemo 的计算时机

```javascript
function ExpensiveComponent({ data }) {
  console.log('Component rendered');

  const result = useMemo(() => {
    console.log('Computing result');
    return data.map(item => item.value * 2);
  }, [data]);

  return <div>{result.join(', ')}</div>;
}
```

**误解**：很多人以为 `useMemo` 会阻止组件重渲染。

**真相**：
- `useMemo` 只缓存计算结果，不阻止组件渲染
- 组件每次渲染都会执行，只是跳过 `useMemo` 内部的计算
- 要阻止组件渲染，需要用 `React.memo`

**正确理解**：

```javascript
// 组件每次都渲染，但计算只在 data 变化时执行
function ExpensiveComponent({ data }) {
  console.log('Component rendered');  // 每次都打印

  const result = useMemo(() => {
    console.log('Computing result');  // 只在 data 变化时打印
    return data.map(item => item.value * 2);
  }, [data]);

  return <div>{result.join(', ')}</div>;
}

// 要阻止组件渲染，需要 React.memo
const ExpensiveComponent = React.memo(function ExpensiveComponent({ data }) {
  console.log('Component rendered');  // 只在 data 变化时打印

  const result = useMemo(() => {
    console.log('Computing result');
    return data.map(item => item.value * 2);
  }, [data]);

  return <div>{result.join(', ')}</div>;
});
```

## 五、useRef 的常见误区

### 5.1 useRef 不会触发重渲染

```javascript
function Counter() {
  const countRef = useRef(0);

  const handleClick = () => {
    countRef.current += 1;
    console.log('Count:', countRef.current);  // 打印正确的值
  };

  return (
    <div>
      <p>Count: {countRef.current}</p>  {/* 页面不更新 */}
      <button onClick={handleClick}>+1</button>
    </div>
  );
}
```

**问题**：`countRef.current` 变化不会触发重渲染，页面显示的值不变。

**原因**：`useRef` 返回的是一个可变对象，修改 `.current` 不会触发重渲染。

**何时使用 useRef**：
- 存储不需要触发渲染的值（定时器 ID、DOM 引用、上一次的值）
- 在多次渲染间保持引用稳定

**何时使用 useState**：
- 存储需要触发渲染的值

### 5.2 useRef 的初始化陷阱

```javascript
function VideoPlayer({ src }) {
  const videoRef = useRef(null);

  useEffect(() => {
    // ❌ 错误：videoRef.current 可能还是 null
    videoRef.current.play();
  }, []);

  return <video ref={videoRef} src={src} />;
}
```

**问题**：`useEffect` 执行时，`videoRef.current` 可能还没有赋值。

**解决**：

```javascript
function VideoPlayer({ src }) {
  const videoRef = useRef(null);

  useEffect(() => {
    // ✅ 检查是否已赋值
    if (videoRef.current) {
      videoRef.current.play();
    }
  }, []);

  return <video ref={videoRef} src={src} />;
}
```

或者用回调 ref：

```javascript
function VideoPlayer({ src }) {
  const handleRef = useCallback((node) => {
    if (node) {
      node.play();
    }
  }, []);

  return <video ref={handleRef} src={src} />;
}
```

### 5.3 useRef 存储上一次的值

这是 `useRef` 的经典用法：

```javascript
function usePrevious(value) {
  const ref = useRef();

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
}

function Counter() {
  const [count, setCount] = useState(0);
  const prevCount = usePrevious(count);

  return (
    <div>
      <p>Current: {count}</p>
      <p>Previous: {prevCount}</p>
      <button onClick={() => setCount(count + 1)}>+1</button>
    </div>
  );
}
```

## 六、自定义 Hook 的陷阱

### 6.1 忘记返回清理函数

```javascript
// ❌ 错误：没有清理定时器
function useInterval(callback, delay) {
  useEffect(() => {
    const timer = setInterval(callback, delay);
    // 忘记返回清理函数
  }, [callback, delay]);
}
```

**问题**：组件卸载时定时器没有清除，导致内存泄漏。

**解决**：

```javascript
function useInterval(callback, delay) {
  useEffect(() => {
    const timer = setInterval(callback, delay);
    return () => clearInterval(timer);  // 清理函数
  }, [callback, delay]);
}
```

### 6.2 依赖不稳定导致的问题

```javascript
// ❌ 错误：callback 每次渲染都变
function useInterval(callback, delay) {
  useEffect(() => {
    const timer = setInterval(callback, delay);
    return () => clearInterval(timer);
  }, [callback, delay]);  // callback 变化导致定时器重启
}

// 使用
function Counter() {
  const [count, setCount] = useState(0);

  useInterval(() => {
    console.log('Count:', count);  // 每次 count 变化，定时器都重启
  }, 1000);

  return <div>{count}</div>;
}
```

**解决方案 1：useRef 存储 callback**

```javascript
function useInterval(callback, delay) {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    const timer = setInterval(() => {
      savedCallback.current();
    }, delay);
    return () => clearInterval(timer);
  }, [delay]);  // 只依赖 delay
}
```

**解决方案 2：useEffectEvent（React 19）**

```javascript
import { useEffectEvent } from 'react';

function useInterval(callback, delay) {
  const onTick = useEffectEvent(callback);

  useEffect(() => {
    const timer = setInterval(onTick, delay);
    return () => clearInterval(timer);
  }, [delay]);
}
```

### 6.3 条件调用 Hook

```javascript
function useUser(userId) {
  if (!userId) {
    return null;  // ❌ 错误：条件返回
  }

  const [user, setUser] = useState(null);  // Hook 在条件语句后

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);

  return user;
}
```

**问题**：违反了 Hooks 规则（Hooks 必须在顶层调用）。

**解决**：

```javascript
function useUser(userId) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (!userId) {
      setUser(null);
      return;
    }

    fetchUser(userId).then(setUser);
  }, [userId]);

  return user;
}
```

## 七、内存泄漏的常见场景

### 7.1 异步操作未取消

```javascript
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser(userId).then(user => {
      setUser(user);  // 组件卸载后仍然执行，导致警告
    });
  }, [userId]);

  return <div>{user?.name}</div>;
}
```

**问题**：组件卸载后，`fetchUser` 的回调仍然执行，尝试更新已卸载组件的状态。

**解决方案 1：使用标志位**

```javascript
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    let cancelled = false;

    fetchUser(userId).then(user => {
      if (!cancelled) {
        setUser(user);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return <div>{user?.name}</div>;
}
```

**解决方案 2：使用 AbortController**

```javascript
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch(`/api/users/${userId}`, { signal: controller.signal })
      .then(res => res.json())
      .then(setUser)
      .catch(err => {
        if (err.name !== 'AbortError') {
          console.error(err);
        }
      });

    return () => {
      controller.abort();
    };
  }, [userId]);

  return <div>{user?.name}</div>;
}
```

### 7.2 事件监听器未移除

```javascript
function WindowSize() {
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const handleResize = () => {
      setSize({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener('resize', handleResize);
    // ❌ 忘记移除监听器
  }, []);

  return <div>{size.width} x {size.height}</div>;
}
```

**解决**：

```javascript
useEffect(() => {
  const handleResize = () => {
    setSize({ width: window.innerWidth, height: window.innerHeight });
  };

  window.addEventListener('resize', handleResize);
  
  return () => {
    window.removeEventListener('resize', handleResize);  // 清理
  };
}, []);
```

### 7.3 定时器未清除

```javascript
function Timer() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setInterval(() => {
      setCount(c => c + 1);
    }, 1000);
    // ❌ 忘记清除定时器
  }, []);

  return <div>{count}</div>;
}
```

**问题**：组件卸载后定时器仍在运行。

**解决**：

```javascript
useEffect(() => {
  const timer = setInterval(() => {
    setCount(c => c + 1);
  }, 1000);

  return () => clearInterval(timer);  // 清理
}, []);
```


## 八、useContext 的性能陷阱

### 8.1 Context 导致的全局重渲染

```javascript
const AppContext = createContext();

function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  const [settings, setSettings] = useState({});

  const value = { user, setUser, theme, setTheme, settings, setSettings };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

function UserName() {
  const { user } = useContext(AppContext);
  return <div>{user?.name}</div>;
}

function ThemeToggle() {
  const { theme, setTheme } = useContext(AppContext);
  return <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>Toggle</button>;
}
```

**问题**：`theme` 变化时，`UserName` 组件也会重渲染（虽然它只用到 `user`）。

**解决方案 1：拆分 Context**

```javascript
const UserContext = createContext();
const ThemeContext = createContext();

function UserName() {
  const { user } = useContext(UserContext);  // 只订阅 user
  return <div>{user?.name}</div>;
}

function ThemeToggle() {
  const { theme, setTheme } = useContext(ThemeContext);  // 只订阅 theme
  return <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>Toggle</button>;
}
```

**解决方案 2：使用 useMemo 稳定 value**

```javascript
function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');

  const value = useMemo(() => ({
    user, setUser, theme, setTheme
  }), [user, theme]);

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
```

**解决方案 3：使用状态管理库**

```javascript
// 使用 Zustand
import create from 'zustand';

const useStore = create((set) => ({
  user: null,
  theme: 'light',
  setUser: (user) => set({ user }),
  setTheme: (theme) => set({ theme })
}));

function UserName() {
  const user = useStore(state => state.user);  // 只订阅 user
  return <div>{user?.name}</div>;
}

function ThemeToggle() {
  const theme = useStore(state => state.theme);  // 只订阅 theme
  const setTheme = useStore(state => state.setTheme);
  return <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>Toggle</button>;
}
```

## 九、useReducer 的常见问题

### 9.1 reducer 中的副作用

```javascript
function reducer(state, action) {
  switch (action.type) {
    case 'fetch_success':
      // ❌ 错误：在 reducer 中执行副作用
      localStorage.setItem('data', JSON.stringify(action.payload));
      return { ...state, data: action.payload };
    default:
      return state;
  }
}
```

**问题**：reducer 应该是纯函数，不应该有副作用。

**解决**：副作用放在 `useEffect` 中

```javascript
function reducer(state, action) {
  switch (action.type) {
    case 'fetch_success':
      return { ...state, data: action.payload };
    default:
      return state;
  }
}

function Component() {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (state.data) {
      localStorage.setItem('data', JSON.stringify(state.data));
    }
  }, [state.data]);
}
```

### 9.2 dispatch 的稳定性

```javascript
function Parent() {
  const [state, dispatch] = useReducer(reducer, initialState);

  return <Child onUpdate={dispatch} />;  // dispatch 是稳定的，不需要 useCallback
}

const Child = React.memo(function Child({ onUpdate }) {
  return <button onClick={() => onUpdate({ type: 'increment' })}>+1</button>;
});
```

**好消息**：`dispatch` 函数是稳定的，不会在重渲染时改变，不需要用 `useCallback` 包裹。

## 十、调试 Hooks 的工具与技巧

### 10.1 React DevTools

**查看 Hooks 状态**：
1. 打开 React DevTools
2. 选择组件
3. 右侧面板显示所有 Hooks 的值

**查看重渲染原因**：
1. 打开 Profiler
2. 录制操作
3. 查看「Why did this render」

### 10.2 自定义调试 Hook

```javascript
function useWhyDidYouUpdate(name, props) {
  const previousProps = useRef();

  useEffect(() => {
    if (previousProps.current) {
      const allKeys = Object.keys({ ...previousProps.current, ...props });
      const changedProps = {};

      allKeys.forEach(key => {
        if (previousProps.current[key] !== props[key]) {
          changedProps[key] = {
            from: previousProps.current[key],
            to: props[key]
          };
        }
      });

      if (Object.keys(changedProps).length > 0) {
        console.log('[why-did-you-update]', name, changedProps);
      }
    }

    previousProps.current = props;
  });
}

// 使用
function MyComponent(props) {
  useWhyDidYouUpdate('MyComponent', props);
  return <div>...</div>;
}
```

### 10.3 ESLint 插件

安装 `eslint-plugin-react-hooks`：

```bash
npm install eslint-plugin-react-hooks --save-dev
```

配置 `.eslintrc.js`：

```javascript
module.exports = {
  plugins: ['react-hooks'],
  rules: {
    'react-hooks/rules-of-hooks': 'error',  // 检查 Hooks 规则
    'react-hooks/exhaustive-deps': 'warn'   // 检查依赖数组
  }
};
```

会自动检测：
- Hooks 是否在顶层调用
- 依赖数组是否完整
- 是否在条件语句中调用 Hooks

## 十一、Hooks 最佳实践总结

### 11.1 useState

✅ **推荐**：
- 用函数式更新避免闭包陷阱
- 相关的状态合并成一个对象
- 简单状态用 `useState`，复杂状态用 `useReducer`

❌ **避免**：
- 在异步回调中直接使用 state
- 过度拆分状态（导致多次渲染）
- 用 state 存储可计算的值

### 11.2 useEffect

✅ **推荐**：
- 依赖数组包含所有使用的外部变量
- 返回清理函数
- 一个 effect 只做一件事

❌ **避免**：
- 空依赖数组 + 使用外部变量
- 对象/数组作为依赖
- 在 effect 中修改依赖的值（导致无限循环）

### 11.3 useCallback / useMemo

✅ **推荐**：
- 子组件用了 `React.memo` 时使用
- 计算成本高时使用
- 先测量，再优化

❌ **避免**：
- 过度使用（反而降低性能）
- 依赖数组不完整
- 用于简单计算

### 11.4 useRef

✅ **推荐**：
- 存储不需要触发渲染的值
- 存储 DOM 引用
- 存储上一次的值

❌ **避免**：
- 用 ref 存储需要触发渲染的值
- 在渲染期间修改 ref.current

### 11.5 自定义 Hook

✅ **推荐**：
- 提取可复用的逻辑
- 返回清理函数
- 使用 `use` 前缀命名

❌ **避免**：
- 条件调用 Hook
- 忘记清理副作用
- 依赖不稳定

## 十二、总结

React Hooks 的常见陷阱：

1. **闭包陷阱**：异步操作中使用 state，用函数式更新解决
2. **依赖地狱**：对象/数组依赖导致无限循环，用 `useMemo` 或原始值解决
3. **过度优化**：不要给所有东西都加 `useCallback`/`useMemo`
4. **内存泄漏**：忘记清理定时器、事件监听器、异步操作
5. **Context 性能**：拆分 Context 或使用状态管理库
6. **useRef 误用**：记住它不会触发重渲染

避坑指南：
- 使用 ESLint 插件自动检查
- 用 React DevTools 调试
- 先测量，再优化
- 遵循 Hooks 规则
- 写清理函数
- 依赖数组要完整

记住：**Hooks 很强大，但也很容易踩坑。理解原理比记住规则更重要。**

如果这篇文章对你有帮助，欢迎点赞收藏。有问题欢迎评论区讨论，我会尽量回复。

## 附录：常用自定义 Hooks

```javascript
// 1. useDebounce
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// 2. useLocalStorage
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

// 3. useOnClickOutside
function useOnClickOutside(ref, handler) {
  useEffect(() => {
    const listener = (event) => {
      if (!ref.current || ref.current.contains(event.target)) {
        return;
      }
      handler(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}

// 4. useAsync
function useAsync(asyncFunction, immediate = true) {
  const [status, setStatus] = useState('idle');
  const [value, setValue] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(() => {
    setStatus('pending');
    setValue(null);
    setError(null);

    return asyncFunction()
      .then(response => {
        setValue(response);
        setStatus('success');
      })
      .catch(error => {
        setError(error);
        setStatus('error');
      });
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { execute, status, value, error };
}
```
